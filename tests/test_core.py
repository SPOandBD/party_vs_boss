import pytest
from app.core import Human

def test_hp_clamped_not_below_zero():
    h = Human("Test", level=1, hp=5, mp=0, str_=1, agi=1, int_=1)
    h.hp = -100
    assert h.hp == 0

def test_hp_not_exceed_max():
    h = Human("Test", level=1, hp=9999, mp=0, str_=5, agi=1, int_=1)
    assert h.hp == h.max_hp

def test_is_alive_flag():
    h = Human("Test", level=1, hp=1, mp=0, str_=1, agi=1, int_=1)
    assert h.is_alive
    h.hp = 0
    assert not h.is_alive