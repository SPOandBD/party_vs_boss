from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .core import Character
from .effects import Poison


class Strategy(ABC):
    """Абстрактная стратегия поведения босса на фазу."""

    @abstractmethod
    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        """
        Возвращает действие:
        {
            "type": "basic" | "skill" | "wait",
            "skill_id": str | None,
            "target": Character | None
        }
        """
        raise NotImplementedError


class Phase1Aggro(Strategy):
    """Фаза 1: агрессивные базовые атаки по самому быстрому противнику."""

    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "skill_id": None, "target": None}
        target = max(live, key=lambda x: x.agi)
        return {"type": "basic", "skill_id": None, "target": target}


class Phase2Poison(Strategy):
    """Фаза 2: использует ядовитую атаку против самого хилого (низкий HP)."""

    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "skill_id": None, "target": None}
        target = min(live, key=lambda x: x.hp)
        return {"type": "skill", "skill_id": "toxic_spit", "target": target}


class Phase3Enrage(Strategy):
    """Фаза 3: ярость — мощный удар по самому сильному (высокий STR)."""

    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "skill_id": None, "target": None}
        target = max(live, key=lambda x: getattr(x, "str_", 0))
        return {"type": "skill", "skill_id": "enraged_blow", "target": target}


class Boss(Character):
    """
    Босс с фазами и стратегиями.

    thresholds=(0.7, 0.3) → фазы:
      0: hp >= 70%
      1: 30% <= hp < 70%
      2: hp < 30%
    """

    def __init__(self, *args, thresholds=(0.7, 0.3), strategies: List[Strategy] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresholds = tuple(sorted(thresholds, reverse=True))
        self.strategies: List[Strategy] = strategies or [Phase1Aggro(), Phase2Poison(), Phase3Enrage()]
        self.current_phase = 0
        self.update_phase(initial=True)

    # === обязательные методы от Character ===
    def basic_attack(self, target: Character) -> int:
        """Обычная атака босса: физический урон от силы."""
        dmg = 6 + self.str_ * 2
        return target.receive_damage(dmg)

    def use_skill(self, target: Character, skill_id: str) -> int:
        """Навыки босса по фазам."""
        if self.is_silenced():
            raise RuntimeError("Silenced")

        if skill_id == "toxic_spit":
            # яд: накладывает Poison на 2 хода
            target.add_effect(Poison(dps=8 + self.int_, duration=2))
            self._start_cooldown("toxic_spit", 2)
            return 0

        if skill_id == "enraged_blow":
            # мощный удар: сильный урон от STR
            dmg = 12 + self.str_ * 3
            dealt = target.receive_damage(dmg)
            self._start_cooldown("enraged_blow", 2)
            return dealt

        raise ValueError(f"Unknown boss skill: {skill_id}")

    # === работа с фазами ===
    def hp_ratio(self) -> float:
        return 0.0 if self.max_hp == 0 else self.hp / self.max_hp

    def _phase_from_ratio(self, ratio: float) -> int:
        t1, t2 = (self.thresholds + (0.0,))[:2]
        if ratio >= t1:
            return 0
        if ratio >= t2:
            return 1
        return 2

    def update_phase(self, initial: bool = False):
        new_phase = self._phase_from_ratio(self.hp_ratio())
        if new_phase != self.current_phase or initial:
            self.current_phase = new_phase
            # точка расширения: можно добавить эффекты при входе в фазу

    def decide(self, opponents: list[Character]) -> dict:
        """Выбор действия текущей стратегией."""
        strat = self.strategies[self.current_phase]
        return strat.choose_action(self, opponents)
