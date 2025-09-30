from app.heroes import Warrior, Mage, Healer
from app.turn import TurnOrder

def test_turn_order_by_agi_desc_then_name():
    a = Warrior("A", level=1, hp=50, mp=0, str_=3, agi=5, int_=1)
    b = Mage("B", level=1, hp=40, mp=0, str_=1, agi=7, int_=5)
    c = Healer("C", level=1, hp=45, mp=0, str_=1, agi=5, int_=4)

    order = [e.name for e in TurnOrder([a, b, c])]
    # b имеет agi=7, дальше a и c оба с 5 — сортируем по имени A, C
    assert order == ["B", "A", "C"]
