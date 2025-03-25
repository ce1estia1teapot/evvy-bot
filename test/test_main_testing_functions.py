import pytest

from main_testing_functions import addition, remove_es

def test_addition():
    assert addition(1, 1) == 2
    assert addition(None, 1) is None
    assert addition(1) is None
    assert addition(None, None) is None
    assert addition('1', 1) is None

def test_remove_es():
    assert remove_es('test') == 'tst'
    assert remove_es('this is a test sentence') == 'this is a tst sntnc'
    assert remove_es('car') == 'car'
    assert remove_es(None) is None
    assert remove_es(1) is None