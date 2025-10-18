import itertools

import pytest

from keybard._xterm_parser import XTermParser
from keybard.events import Key, Paste
from keybard.messages import TerminalSupportsSynchronizedOutput


def chunks(data, size):
    if size == 0:
        yield data
        return

    chunk_start = 0
    chunk_end = size
    while True:
        yield data[chunk_start:chunk_end]
        chunk_start = chunk_end
        chunk_end += size
        if chunk_end >= len(data):
            yield data[chunk_start:chunk_end]
            break


@pytest.fixture
def parser():
    return XTermParser()


@pytest.mark.parametrize("chunk_size", [2, 3, 4, 5, 6])
def test_varying_parser_chunk_sizes_no_missing_data(parser, chunk_size):
    end = "\x1b[8~"
    text = "ABCDEFGH"

    data = end + text
    events = []
    for chunk in chunks(data, chunk_size):
        events.append(parser.feed(chunk))

    events = list(itertools.chain.from_iterable(list(event) for event in events))

    assert events[0].key == "end"
    assert [event.key for event in events[1:]] == list(text)


def test_bracketed_paste(parser):
    """When bracketed paste mode is enabled in the terminal emulator and
    the user pastes in some text, it will surround the pasted input
    with the escape codes "\x1b[200~" and "\x1b[201~". The text between
    these codes corresponds to a single `Paste` event in Textual.
    """
    pasted_text = "PASTED"
    events = list(parser.feed(f"\x1b[200~{pasted_text}\x1b[201~"))

    assert len(events) == 1
    assert isinstance(events[0], Paste)
    assert events[0].text == pasted_text


def test_bracketed_paste_content_contains_escape_codes(parser):
    """When performing a bracketed paste, if the pasted content contains
    supported ANSI escape sequences, it should not interfere with the paste,
    and no escape sequences within the bracketed paste should be converted
    into Textual events.
    """
    pasted_text = "PAS\x0fTED"
    events = list(parser.feed(f"\x1b[200~{pasted_text}\x1b[201~"))
    assert len(events) == 1
    assert events[0].text == pasted_text


def test_bracketed_paste_amongst_other_codes(parser):
    pasted_text = "PASTED"
    events = list(parser.feed(f"\x1b[8~\x1b[200~{pasted_text}\x1b[201~\x1b[8~"))
    assert len(events) == 3  # Key.End -> Paste -> Key.End
    assert events[0].key == "end"
    assert events[1].text == pasted_text
    assert events[2].key == "end"


def test_cant_match_escape_sequence_too_long(parser):
    """The sequence did not match, and we hit the maximum sequence search
    length threshold, so each character should be issued as a key-press instead.
    """
    sequence = "\x1b[123456789123456789123123456789123456789123"
    events = list(parser.feed(sequence))

    # Every character in the sequence is converted to a key press
    assert len(events) == len(sequence)
    assert all(isinstance(event, Key) for event in events)

    # When we backtrack '\x1b' is translated to '^'
    assert events[0].key == "circumflex_accent"

    # The rest of the characters correspond to the expected key presses
    events = events[1:]
    for index, character in enumerate(sequence[1:]):
        assert events[index].character == character


@pytest.mark.parametrize(
    "chunk_size",
    [
        2,
        3,
        4,
        5,
        6,
    ],
)
def test_unknown_sequence_followed_by_known_sequence(parser, chunk_size):
    """When we feed the parser an unknown sequence followed by a known
    sequence. The characters in the unknown sequence are delivered as keys,
    and the known escape sequence that follows is delivered as expected.
    """
    unknown_sequence = "\x1b[?"
    known_sequence = "\x1b[8~"  # key = 'end'

    sequence = unknown_sequence + known_sequence

    events = []

    for chunk in chunks(sequence, chunk_size):
        events.append(parser.feed(chunk))

    events = list(itertools.chain.from_iterable(list(event) for event in events))
    print(repr([event.key for event in events]))

    assert [event.key for event in events] == [
        "escape",
        "left_square_bracket",
        "question_mark",
        "end",
    ]


def test_simple_key_presses_all_delivered_correct_order(parser):
    sequence = "123abc"
    events = parser.feed(sequence)
    assert "".join(event.key for event in events) == sequence


def test_simple_keypress_non_character_key(parser):
    sequence = "\x09"
    events = list(parser.feed(sequence))
    assert len(events) == 1
    assert events[0].key == "tab"


def test_key_presses_and_escape_sequence_mixed(parser):
    sequence = "abc\x1b[13~123"
    events = list(parser.feed(sequence))

    assert len(events) == 7
    assert "".join(event.key for event in events) == "abcf3123"


def test_single_escape(parser):
    """A single \x1b should be interpreted as a single press of the Escape key"""
    events = list(parser.feed("\x1b"))
    events.extend(parser.feed(""))
    assert [event.key for event in events] == ["escape"]


def test_double_escape(parser):
    """Test double escape."""
    events = list(parser.feed("\x1b\x1b"))
    events.extend(parser.feed(""))
    print(events)
    assert [event.key for event in events] == ["escape", "escape"]


def test_escape_sequence_with_modifiers(parser):
    """Escape sequences can include modifier keys"""
    events = list(parser.feed("\x1b[2;4~"))
    assert len(events) == 1
    assert events[0].key == "alt+shift+insert"


@pytest.mark.parametrize("parameter", range(1, 5))
def test_terminal_mode_reporting_synchronized_output_supported(parser, parameter):
    sequence = f"\x1b[?2026;{parameter}$y"
    events = list(parser.feed(sequence))
    assert len(events) == 1
    assert isinstance(events[0], TerminalSupportsSynchronizedOutput)


def test_terminal_mode_reporting_synchronized_output_not_supported(parser):
    sequence = "\x1b[?2026;0$y"
    events = list(parser.feed(sequence))
    assert events == []
