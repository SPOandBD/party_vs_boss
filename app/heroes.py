from __future__ import annotations
from .core import Character
from .mixins import CritMixin

class Warrior(CritMixin, Character):
    """Физический дамагер. Навык: power_strike (CD=2, MP=10)."""
    def basic_attack(self, target: Character) -> int:
        dmg = 5 + self.str_ * 2
        target.hp = target.hp - dmg
        return dmg

    def use_skill(self, target: Character, skill_id: str) -> int:
        if self.is_silenced():
            raise RuntimeError("Silenced")
        if skill_id != "power_strike":
            raise ValueError("Unknown skill for Warrior")
        if not self.can_use(skill_id):
            raise RuntimeError("Skill on cooldown")
        cost = 10
        self._spend_mp(cost)
        dmg = 10 + self.str_ * 3
        target.hp = target.hp - dmg
        self._start_cooldown(skill_id, 2)
        return dmg


class Mage(CritMixin, Character):
    """Магический дамагер. Навык: fireball (CD=2, MP=12)."""
    def basic_attack(self, target: Character) -> int:
        dmg = 3 + max(0, self.int_ // 2)
        target.hp = target.hp - dmg
        return dmg

    def use_skill(self, target: Character, skill_id: str) -> int:
        if self.is_silenced():
            raise RuntimeError("Silenced")
        if skill_id != "fireball":
            raise ValueError("Unknown skill for Mage")
        if not self.can_use(skill_id):
            raise RuntimeError("Skill on cooldown")
        cost = 12
        self._spend_mp(cost)
        dmg = 12 + self.int_ * 4
        target.hp = target.hp - dmg
        self._start_cooldown(skill_id, 2)
        return dmg


class Healer(Character):
    """Поддержка. Навык: heal (CD=2, MP=10) — лечит союзника."""
    def basic_attack(self, target: Character) -> int:
        dmg = 2 + max(0, self.int_ // 3)
        target.hp = target.hp - dmg
        return dmg

    def use_skill(self, target: Character, skill_id: str) -> int:
        if self.is_silenced():
            raise RuntimeError("Silenced")
        if skill_id != "heal":
            raise ValueError("Unknown skill for Healer")
        if not self.can_use(skill_id):
            raise RuntimeError("Skill on cooldown")
        cost = 10
        self._spend_mp(cost)
        heal = 10 + self.int_ * 3
        target.hp = target.hp + heal  # дескриптор сам заклампит по max_hp
        self._start_cooldown(skill_id, 2)
        return -heal  # отрицательное значение = лечение
