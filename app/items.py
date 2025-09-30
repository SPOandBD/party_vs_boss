from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Type, Iterable
from .core import Character
from .effects import Poison


class Item(ABC):
    """Базовый предмет: должен уметь применяться пользователем к цели."""
    name: str = "Item"

    @abstractmethod
    def use(self, user: Character, target: Character) -> str:
        """Возвращает человекочитаемое описание эффекта применения."""
        raise NotImplementedError


class Potion(Item):
    """Зелье лечения: восстанавливает фиксированное количество HP цели."""
    name = "Potion"

    def __init__(self, heal_amount: int):
        self.heal_amount = int(heal_amount)

    def use(self, user: Character, target: Character) -> str:
        healed = target.heal(self.heal_amount)
        return f"{user.name} used {self.name} on {target.name}: +{healed} HP"


class Ether(Item):
    """Эфир: восстанавливает MP цели (клампится по max_mp)."""
    name = "Ether"

    def __init__(self, mp_amount: int):
        self.mp_amount = int(mp_amount)

    def use(self, user: Character, target: Character) -> str:
        before = target.mp
        target.mp = target.mp + self.mp_amount
        gained = target.mp - before
        return f"{user.name} used {self.name} on {target.name}: +{gained} MP"


class Antidote(Item):
    """Антидот: снимает эффекты-яд (Poison). Можно расширить списком классов."""
    name = "Antidote"

    def __init__(self, removes: Iterable[Type] | None = None):
        # по умолчанию снимаем яд
        self.removes = list(removes) if removes is not None else [Poison]

    def use(self, user: Character, target: Character) -> str:
        removed = 0
        # мягко работаем с приватным списком эффектов
        to_remove = []
        for eff in list(getattr(target, "_effects", [])):
            if any(isinstance(eff, cls) for cls in self.removes):
                to_remove.append(eff)
        for eff in to_remove:
            # вызовем on_expire, чтобы корректно снять флаги, если вдруг есть
            on_expire = getattr(eff, "on_expire", None)
            if callable(on_expire):
                on_expire(target)
            try:
                target._effects.remove(eff)  # type: ignore[attr-defined]
                removed += 1
            except ValueError:
                pass
        return f"{user.name} used {self.name} on {target.name}: removed {removed} effect(s)"


class Inventory:
    """Простой инвентарь: хранит предметы и умеет их применять по индексу."""
    def __init__(self):
        self._items: List[Item] = []

    def add(self, item: Item) -> None:
        self._items.append(item)

    def remove(self, index: int) -> Item:
        try:
            return self._items.pop(index)
        except IndexError as e:
            raise IndexError("Invalid item index") from e

    def list(self) -> List[Item]:
        return list(self._items)

    def use(self, index: int, user: Character, target: Character) -> str:
        item = self.remove(index)
        return item.use(user, target)
