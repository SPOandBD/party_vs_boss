from app.boss import Boss, Phase1Aggro, Phase2Poison, Phase3Enrage
from app.heroes import Warrior, Mage, Healer

def mk_party():
    return [
        Warrior("War", level=1, hp=80, mp=0, str_=6, agi=3, int_=1),
        Mage("Mag", level=1, hp=60, mp=0, str_=1, agi=5, int_=7),
        Healer("Heal", level=1, hp=70, mp=0, str_=1, agi=2, int_=6),
    ]

def test_boss_phase_transitions_by_hp_ratio():
    boss = Boss("Dragon", level=5, hp=300, mp=0, str_=8, agi=4, int_=4, thresholds=(0.7, 0.3))
    # начальная фаза при полном HP
    assert boss.current_phase == 0

    # урон до 65% → фаза 1
    boss.hp = int(boss.max_hp * 0.65)
    boss.update_phase()
    assert boss.current_phase == 1

    # урон до 20% → фаза 2 (ярость)
    boss.hp = int(boss.max_hp * 0.2)
    boss.update_phase()
    assert boss.current_phase == 2

    # лечение обратно до 80% → фаза 0
    boss.hp = int(boss.max_hp * 0.8)
    boss.update_phase()
    assert boss.current_phase == 0

def test_strategies_choose_correct_action_types():
    party = mk_party()
    boss = Boss("Dragon", level=5, hp=300, mp=0, str_=8, agi=4, int_=4)

    # Фаза 0
    boss.hp = boss.max_hp
    boss.update_phase()
    act = boss.decide(party)
    assert act["type"] in ("basic", "skill")
    assert act["target"] in party

    # Фаза 1 (между 30% и 70%)
    boss.hp = int(boss.max_hp * 0.5)
    boss.update_phase()
    act = boss.decide(party)
    assert act["type"] in ("basic", "skill")
    assert act["target"] in party

    # Фаза 2 (<30%)
    boss.hp = int(boss.max_hp * 0.25)
    boss.update_phase()
    act = boss.decide(party)
    assert act["type"] in ("basic", "skill")
    assert act["target"] in party

def test_phase1_targets_fastest():
    party = mk_party()
    boss = Boss("Dragon", level=5, hp=300, mp=0, str_=8, agi=4, int_=4)
    boss.hp = boss.max_hp  # фаза 0
    boss.update_phase()
    act = boss.decide(party)
    # должен целить самого быстрого: у Mage agi=5 — самый быстрый
    assert act["target"].name == "Mag"

def test_phase3_targets_strongest():
    party = mk_party()
    boss = Boss("Dragon", level=5, hp=300, mp=0, str_=8, agi=4, int_=4)
    boss.hp = int(boss.max_hp * 0.2)  # фаза 2
    boss.update_phase()
    act = boss.decide(party)
    # самый сильный по STR — Warrior
    assert act["target"].name == "War"
