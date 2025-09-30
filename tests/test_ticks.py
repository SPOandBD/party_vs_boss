import pytest
from app.battle import Battle
from app.heroes import Warrior, Mage, Healer
from app.effects import Poison, Regen, Silence

# Вспомогательный эффект для проверки порядка тиков
class TraceEffect:
    def __init__(self, log, name="Trace", duration=1):
        self.name = name
        self.duration = duration
        self.log = log

    def on_turn_start(self, target):
        self.log.append(("start", target.name))

    def on_turn_end(self, target):
        self.log.append(("end", target.name))
        self.duration -= 1  # чтобы корректно снимался

def test_tick_order_start_then_end_in_battle_one_round():
    w = Warrior("W", level=1, hp=100, mp=0, str_=5, agi=3, int_=1)
    b = Warrior("BOSS", level=1, hp=100, mp=0, str_=5, agi=1, int_=1)  # временный "босс"
    trace = []
    w.add_effect(TraceEffect(trace, duration=1))
    b.add_effect(TraceEffect(trace, duration=1))

    battle = Battle([w], b)
    battle.run(max_rounds=1)

    # ожидаем, что все start пойдут раньше соответствующих end в рамках раунда
    # (точный порядок по персонажам не фиксируем, но start должны идти перед end)
    phases = [p for p, _ in trace]
    assert "start" in phases and "end" in phases
    assert phases.index("start") < phases.index("end")

def test_poison_ticks_on_round_end():
    w = Warrior("W", level=1, hp=100, mp=0, str_=5, agi=3, int_=1)
    b = Warrior("BOSS", level=1, hp=100, mp=0, str_=5, agi=1, int_=1)
    w.add_effect(Poison(dps=7, duration=2))

    battle = Battle([w], b)
    battle.run(max_rounds=1)  # один раунд => один тик "end"
    assert w.hp == w.max_hp - 7

    battle.run(max_rounds=1)  # ещё раунд => ещё один тик "end"
    assert w.hp == w.max_hp - 14  # всего два тика

def test_regen_ticks_on_round_end():
    w = Warrior("W", level=1, hp=60, mp=0, str_=5, agi=3, int_=1)
    b = Warrior("BOSS", level=1, hp=100, mp=0, str_=5, agi=1, int_=1)
    w.add_effect(Regen(hps=8, duration=2))

    battle = Battle([w], b)
    start_hp = w.hp
    battle.run(max_rounds=1)
    battle.run(max_rounds=1)
    assert w.hp == min(w.max_hp, start_hp + 16)

def test_silence_blocks_skills_then_expires_by_end_ticks():
    h = Healer("H", level=1, hp=80, mp=50, str_=1, agi=2, int_=6)
    ally = Warrior("Ally", level=1, hp=30, mp=0, str_=3, agi=2, int_=1)
    b = Warrior("BOSS", level=1, hp=100, mp=0, str_=5, agi=1, int_=1)

    h.add_effect(Silence(duration=2))

    # пока немота — скилл упадёт
    with pytest.raises(RuntimeError):
        h.use_skill(ally, "heal")

    # прогоняем 2 раунда, чтобы сработали "end"-тики и немота спала
    battle = Battle([h, ally], b)
    battle.run(max_rounds=2)

    # теперь можно кастовать
    val = h.use_skill(ally, "heal")
    assert val < 0  # лечение

def test_cooldowns_reduce_each_round_in_battle():
    w = Warrior("W", level=1, hp=100, mp=50, str_=5, agi=3, int_=1)
    d = Warrior("Dummy", level=1, hp=200, mp=0, str_=1, agi=1, int_=1)
    b = Warrior("BOSS", level=1, hp=100, mp=0, str_=5, agi=1, int_=1)

    # поставить кулдаун 2
    w.use_skill(d, "power_strike")
    assert w._cooldowns.get("power_strike") == 2

    battle = Battle([w, d], b)
    battle.run(max_rounds=1)
    assert w._cooldowns.get("power_strike") == 1
    battle.run(max_rounds=1)
    assert w._cooldowns.get("power_strike") == 0
