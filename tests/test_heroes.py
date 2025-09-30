import pytest
from app.heroes import Warrior, Mage, Healer

def test_warrior_power_strike_spends_mp_and_sets_cooldown():
    w = Warrior("W", level=1, hp=100, mp=20, str_=5, agi=3, int_=1)
    dummy = Warrior("Dummy", level=1, hp=200, mp=0, str_=1, agi=1, int_=1)

    dmg = w.use_skill(dummy, "power_strike")
    assert dmg > 0
    assert w.mp == 10  # 20 - 10
    assert w._cooldowns.get("power_strike") == 2
    assert dummy.hp < dummy.max_hp  # получил урон

def test_skill_on_cooldown_raises():
    w = Warrior("W", level=1, hp=100, mp=50, str_=5, agi=3, int_=1)
    dummy = Warrior("D", level=1, hp=200, mp=0, str_=1, agi=1, int_=1)

    w.use_skill(dummy, "power_strike")
    with pytest.raises(RuntimeError):
        w.use_skill(dummy, "power_strike")  # сразу повторить нельзя

def test_reduce_cooldowns_allows_use_again():
    w = Warrior("W", level=1, hp=100, mp=50, str_=5, agi=3, int_=1)
    dummy = Warrior("D", level=1, hp=200, mp=0, str_=1, agi=1, int_=1)

    w.use_skill(dummy, "power_strike")
    w.reduce_cooldowns()
    assert w._cooldowns["power_strike"] == 1
    w.reduce_cooldowns()
    assert w._cooldowns["power_strike"] == 0
    # теперь можно
    w.use_skill(dummy, "power_strike")

def test_not_enough_mp_raises():
    m = Mage("M", level=1, hp=60, mp=5, str_=1, agi=3, int_=7)
    dummy = Warrior("D", level=1, hp=200, mp=0, str_=1, agi=1, int_=1)
    with pytest.raises(ValueError):
        m.use_skill(dummy, "fireball")

def test_healer_heals_and_clamped_by_max_hp():
    h = Healer("H", level=1, hp=70, mp=30, str_=1, agi=2, int_=6)
    ally = Warrior("Ally", level=1, hp=10, mp=0, str_=3, agi=2, int_=1)
    before_max = ally.max_hp
    val = h.use_skill(ally, "heal")
    assert val < 0  # отрицательное = лечение
    assert ally.hp <= before_max
    assert h._cooldowns.get("heal") == 2
