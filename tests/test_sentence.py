from collections import Counter

from sentence import Sentence


def test_buttons():
    expected_buttons = Counter('我想我可以。')
    sentence = Sentence('我想我可以。', 'I think I can.')

    buttons = Counter(sentence.get_buttons())

    assert expected_buttons == buttons


def test_buttons_shuffled():
    original_buttons = list('我想我可以。')
    sentence = Sentence('我想我可以。', 'I think I can.')

    for _ in range(1000):
        buttons = sentence.get_buttons()

        assert original_buttons != buttons


def test_buttons_cannot_shuffle():
    expected_buttons = list('谢谢')
    sentence = Sentence('谢谢', 'Thank you')

    buttons = sentence.get_buttons()

    assert expected_buttons == buttons


def test_is_solved():
    solution = list('我想我可以。')
    sentence = Sentence('我想我可以。', 'I think I can.')

    is_solved = sentence.is_solved(solution)

    assert is_solved


def test_not_solved():
    bad_solution = list('我我想以可。')
    sentence = Sentence('我想我可以。', 'I think I can.')

    is_solved = sentence.is_solved(bad_solution)

    assert not is_solved
