import pytest
from app.heroes import Warrior, Healer
from app.effects import Poison, Shield, Silence, Regen

def test_poison_ticks_each_end_turn_until_expire():
    w = Warrior("W", level=1, hp=100, mp=0, str_=5, agi=3, int_=1)
    w.add_effect(Poison(dps=7, duration=3))
    # имитируем 3 конца хода владельца
    for _ in range(3):
        w.tick_effects("end")
    assert w.hp == w.max_hp - 7*3  # получил суммарно 21 урона

def test_shield_absorbs_damage_and_expires():
    w = Warrior("W", level=1, hp=100, mp=0, str_=5, agi=3, int_=1)
    w.add_effect(Shield(amount=20, duration=2))
    dealt = w.receive_damage(15)
    assert dealt == 0          # щит всё поглотил
    # остаток щита = 5; прилетает 10
    dealt = w.receive_damage(10)
    # 5 поглотил щит, 5 прошли
    assert dealt == 5
    # окончания хода — щит спадёт (duration уменьшится до 0)
    w.tick_effects("end")
    assert w.hp == w.max_hp - 5
    # ещё урон теперь идёт по HP полностью
    dealt = w.receive_damage(7)
    assert dealt == 7
    assert w.hp == w.max_hp - 12

def test_silence_blocks_skills_and_then_expires():
    h = Healer("H", level=1, hp=80, mp=50, str_=1, agi=2, int_=6)
    ally = Warrior("Ally", level=1, hp=10, mp=0, str_=3, agi=2, int_=1)

    h.add_effect(Silence(duration=2))
    with pytest.raises(RuntimeError):
        h.use_skill(ally, "heal")   # немота

    # 2 конца хода — немота спадёт
    h.tick_effects("end")
    h.tick_effects("end")
    assert not h.is_silenced()

    # теперь скилл проходит
    val = h.use_skill(ally, "heal")
    assert val < 0

def test_regen_heals_each_end_turn():
    w = Warrior("W", level=1, hp=50, mp=0, str_=5, agi=3, int_=1)
    w.add_effect(Regen(hps=8, duration=2))
    w.tick_effects("end")
    w.tick_effects("end")
    assert w.hp == min(w.max_hp, 50 + 16)
