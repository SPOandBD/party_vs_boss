from app.battle import Battle
from app.heroes import Warrior, Mage, Healer
from app.boss import Boss



def main():
    party = [
        Warrior("Warrior", level=1, hp=80, mp=20, str_=6, agi=3, int_=1),
        Mage("Mage", level=1, hp=60, mp=30, str_=1, agi=5, int_=7),
        Healer("Healer", level=1, hp=70, mp=30, str_=1, agi=2, int_=6),
    ]
    boss = Boss("Dragon", level=3, hp=120, mp=0, str_=8, agi=4, int_=5)

    battle = Battle(party, boss)
    res = battle.run(max_rounds=6)

if __name__ == "__main__":
    main()
