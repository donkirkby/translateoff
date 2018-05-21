from collections import Counter

from sentence import Sentence


def test_source():
    expected_source = Counter('我想我可以。')
    sentence = Sentence('我想我可以。', 'I think I can.')

    source = Counter(sentence.source)

    assert expected_source == source


def test_source_shuffled():
    original_source = list('我想我可以。')

    for _ in range(1000):
        sentence = Sentence('我想我可以。', 'I think I can.')
        source = sentence.source

        assert original_source != source


def test_buttons_cannot_shuffle():
    expected_source = list('谢谢')
    sentence = Sentence('谢谢', 'Thank you')

    source = sentence.source

    assert expected_source == source


def test_state():
    state = '可以我想我。'
    expected_source = list(state)
    sentence = Sentence('我想我可以。', 'I think I can.', state=state)

    source = sentence.source

    assert expected_source == source


def test_selected_start():
    expected_selected = list('      ')
    sentence = Sentence('我想我可以。', 'I think I can.', state='可以我想我。')

    selected = sentence.selected

    assert expected_selected == selected


def test_select():
    expected_selected = list('以     ')
    expected_source = list('可 我想我。')
    sentence = Sentence('我想我可以。', 'I think I can.', state='可以我想我。')

    sentence.select(1)

    assert expected_selected == sentence.selected
    assert expected_source == sentence.source


def test_is_solved():
    state = """\
CABED
ABCD
"""
    expected_selected = list('ABCDE')
    expected_source = list('     ')
    sentence = Sentence('ABCDE', 'First five letters.', state=state)

    is_solved_before = sentence.is_solved
    sentence.select(3)
    is_solved_after = sentence.is_solved

    assert expected_selected == sentence.selected
    assert expected_source == sentence.source
    assert not is_solved_before
    assert is_solved_after


def test_replace():
    state = "CABED"
    expected_selected = list('     ')
    expected_source = list('CABED')
    sentence = Sentence('ABCDE', 'First five letters.', state=state)

    sentence.select(1)
    sentence.replace(0)

    assert expected_selected == sentence.selected
    assert expected_source == sentence.source


def test_get_hint():
    state = """\
ACEBD
ACBD
"""
    sentence = Sentence('ABCDE', 'First five letters.', state=state)
    expected_hint = list('AB')
    expected_selected = list('AB   ')

    hint = sentence.get_hint()

    assert expected_hint == hint
    assert expected_selected == sentence.selected
    assert 2 == sentence.hint_size
