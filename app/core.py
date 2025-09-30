from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

class BoundedStat:
    def __init__(self, name: str, *, min_value: int = 0, max_attr: Optional[str] = None):
        self.public_name = name
        self.storage_name = f"_{name}"
        self.min_value = min_value
        self.max_attr = max_attr  # имя метода/свойства, возвращающего максимум

    def __get__(self, instance: Any, owner: type | None = None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name, 0)

    def __set__(self, instance: Any, value: int):
        lo = self.min_value
        hi = None
        if self.max_attr:
            max_val = getattr(instance, self.max_attr)
            hi = max_val() if callable(max_val) else max_val
        if hi is not None:
            value = max(lo, min(int(value), int(hi)))
        else:
            value = max(lo, int(value))
        instance.__dict__[self.storage_name] = value

    def __delete__(self, instance: Any):
        raise AttributeError(f"Can't delete stat '{self.public_name}'")


class Human:
    hp = BoundedStat("hp", min_value=0, max_attr="max_hp")
    mp = BoundedStat("mp", min_value=0, max_attr="max_mp")
    str_ = BoundedStat("str_", min_value=1)
    agi = BoundedStat("agi", min_value=1)
    int_ = BoundedStat("int_", min_value=1)

    def __init__(self, name: str, level: int = 1, *, hp: int = 1, mp: int = 0, str_: int = 1, agi: int = 1, int_: int = 1):
        self.name = name
        self.level = max(1, int(level))
        self.str_ = str_
        self.agi = agi
        self.int_ = int_
        self.hp = hp or self.max_hp
        self.mp = mp or self.max_mp

    @property
    def max_hp(self) -> int:
        return 50 + self.level * 10 + self.str_ * 5

    @property
    def max_mp(self) -> int:
        return 10 + self.level * 5 + self.int_ * 5

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, L{self.level}, HP={self.hp}/{self.max_hp}, MP={self.mp}/{self.max_mp})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} lvl={self.level}>"


class Character(Human, ABC):
    # флаги статусов
    _silenced: bool = False


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._effects = []     # type: list
        self._cooldowns = {}   # type: dict[str, int]

    @abstractmethod
    def basic_attack(self, target: "Character") -> int:
        raise NotImplementedError

    @abstractmethod
    def use_skill(self, target: "Character", skill_id: str) -> int:
        raise NotImplementedError
    
    # --- helpers for skills (если уже добавлял, пропусти) ---
    def _start_cooldown(self, skill_id: str, turns: int):
        self._cooldowns[skill_id] = int(turns)

    def _spend_mp(self, amount: int):
        if self.mp < amount:
            raise ValueError(f"Not enough MP for {self.name}: need {amount}, have {self.mp}")
        self.mp = self.mp - amount

    # --- combat helpers ---
    def receive_damage(self, amount: int) -> int:
        """Принять урон с учётом щитов/эффектов. Возвращает фактический урон по HP."""
        if amount <= 0 or not self.is_alive:
            return 0
        # дать эффектам шанс поглотить/изменить урон (например, Shield)
        remaining = int(amount)
        for eff in list(self._effects):
            on_dmg = getattr(eff, "on_damage", None)
            if callable(on_dmg):
                remaining = int(on_dmg(self, remaining))
                if remaining <= 0:
                    remaining = 0
                    break
        before = self.hp
        self.hp = self.hp - remaining
        return before - self.hp

    def heal(self, amount: int) -> int:
        """Лечение с клампом по max_hp. Возвращает восстановленное значение."""
        if amount <= 0 or not self.is_alive:
            return 0
        before = self.hp
        self.hp = self.hp + int(amount)
        return self.hp - before

    def is_silenced(self) -> bool:
        return bool(getattr(self, "_silenced", False))

    # эффекты
    def add_effect(self, effect: Any):
        self._effects.append(effect)
        on_apply = getattr(effect, "on_apply", None)
        if callable(on_apply):
            on_apply(self)

    def tick_effects(self, phase: str):
        """phase: 'start' или 'end' — вызывает хуки эффектов и снимает истёкшие."""
        to_remove = []
        for eff in list(self._effects):
            if phase == "start" and hasattr(eff, "on_turn_start"):
                eff.on_turn_start(self)
            if phase == "end" and hasattr(eff, "on_turn_end"):
                eff.on_turn_end(self)
            # у эффекта должна уменьшаться duration внутри on_turn_end или здесь:
            if getattr(eff, "duration", None) is not None and eff.duration <= 0:
                to_remove.append(eff)
        for eff in to_remove:
            on_expire = getattr(eff, "on_expire", None)
            if callable(on_expire):
                on_expire(self)
            try:
                self._effects.remove(eff)
            except ValueError:
                pass

    def can_use(self, skill_id: str) -> bool:
        return self._cooldowns.get(skill_id, 0) == 0 and not self.is_silenced()

    def reduce_cooldowns(self):
        for k, v in list(self._cooldowns.items()):
            self._cooldowns[k] = max(0, v - 1)
