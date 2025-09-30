import pytest
from app.heroes import Warrior, Healer, Mage
from app.items import Inventory, Potion, Ether, Antidote
from app.effects import Poison

def test_potion_heals_and_clamped_by_max_hp():
    w = Warrior("W", level=1, hp=10, mp=0, str_=4, agi=2, int_=1)
    inv = Inventory()
    inv.add(Potion(heal_amount=50))
    before_max = w.max_hp
    msg = inv.use(0, user=w, target=w)
    assert "used Potion" in msg
    assert w.hp <= before_max  # кламп по max_hp
    assert w.hp > 10           # точно подлечило


def test_ether_restores_mp_and_clamped_by_max_mp():
    m = Mage("M", level=1, hp=50, mp=0, str_=1, agi=3, int_=7)
    inv = Inventory()
    inv.add(Ether(mp_amount=999))
    inv.use(0, user=m, target=m)
    assert m.mp == m.max_mp

def test_antidote_removes_poison_only():
    w = Warrior("W", level=1, hp=100, mp=0, str_=5, agi=2, int_=1)
    w.add_effect(Poison(dps=5, duration=3))
    assert any(isinstance(e, Poison) for e in getattr(w, "_effects", []))

    inv = Inventory()
    inv.add(Antidote())  # по умолчанию снимает Poison
    msg = inv.use(0, user=w, target=w)
    assert "removed 1 effect" in msg
    assert not any(isinstance(e, Poison) for e in getattr(w, "_effects", []))

def test_inventory_remove_invalid_index_raises():
    h = Healer("H", level=1, hp=70, mp=20, str_=1, agi=2, int_=6)
    inv = Inventory()
    inv.add(Potion(20))
    inv.remove(0)  # убрали единственный предмет
    with pytest.raises(IndexError):
        inv.use(0, user=h, target=h)
