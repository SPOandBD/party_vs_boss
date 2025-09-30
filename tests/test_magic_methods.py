from app.heroes import Warrior

def test_eq_and_hash_work():
    a = Warrior("Same", level=1, hp=50, mp=0, str_=3, agi=2, int_=1)
    b = Warrior("Same", level=1, hp=70, mp=10, str_=5, agi=3, int_=2)
    c = Warrior("Other", level=1, hp=50, mp=0, str_=3, agi=2, int_=1)

    assert a == b
    assert a != c
    assert len({a, b, c}) == 2  # множества используют __hash__

def test_iter_yields_stats():
    w = Warrior("Iter", level=1, hp=50, mp=20, str_=3, agi=2, int_=4)
    stats = dict(iter(w))
    assert "hp" in stats and "mp" in stats
    assert stats["hp"] == w.hp
    assert stats["agi"] == w.agi
