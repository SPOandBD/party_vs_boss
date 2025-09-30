from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .core import Character

class Strategy(ABC):
    """Стратегия босса на фазу."""
    @abstractmethod
    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        """
        Возвращает декларативное действие:
        {"type": "basic"|"skill","skill_id":str|None,"target": Character|None}
        """
        raise NotImplementedError


class Phase1Aggro(Strategy):
    """Фаза 1: одиночные удары по самому агошному противнику (самый высокий agi)."""
    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "target": None, "skill_id": None}
        # бьём самого быстрого
        target = max(live, key=lambda x: x.agi)
        return {"type": "basic", "skill_id": None, "target": target}


class Phase2Poison(Strategy):
    """Фаза 2: предпочитает навык 'toxic_spit' по самому хилому (низкий HP)."""
    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "target": None, "skill_id": None}
        target = min(live, key=lambda x: x.hp)
        return {"type": "skill", "skill_id": "toxic_spit", "target": target}


class Phase3Enrage(Strategy):
    """Фаза 3: ярость — мощный одиночный удар по самому опасному (высокая STR)."""
    def choose_action(self, boss: "Boss", opponents: list[Character]) -> Dict[str, Any]:
        live = [o for o in opponents if o.is_alive]
        if not live:
            return {"type": "wait", "target": None, "skill_id": None}
        # атакуем с наибольшей силой
        target = max(live, key=lambda x: getattr(x, "str_", 0))
        return {"type": "skill", "skill_id": "enraged_blow", "target": target}


class Boss(Character):
    """
    Босс с фазами; пороги фаз задаются в процентах HP.
    Пример: thresholds=(0.7, 0.3) → фазы:
      phase 0: hp >= 70%
      phase 1: 30% <= hp < 70%
      phase 2: hp < 30%
    """
    def __init__(self, *args, thresholds=(0.7, 0.3), strategies: List[Strategy] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresholds = tuple(sorted(thresholds, reverse=True))  # (0.7, 0.3)
        self.strategies: List[Strategy] = strategies or [Phase1Aggro(), Phase2Poison(), Phase3Enrage()]
        self.current_phase = 0
        self.update_phase(initial=True)

    def hp_ratio(self) -> float:
        return 0.0 if self.max_hp == 0 else self.hp / self.max_hp

    def _phase_from_ratio(self, ratio: float) -> int:
        t1, t2 = (self.thresholds + (0.0,))[:2]  # безопасно
        if ratio >= t1:
            return 0
        if ratio >= t2:
            return 1
        return 2

    def update_phase(self, initial: bool = False):
        new_phase = self._phase_from_ratio(self.hp_ratio())
        if new_phase != self.current_phase or initial:
            self.current_phase = new_phase
            # здесь можно навешивать фазовые эффекты типа Enrage/Resist, если захочешь
            # пока — ничего не делаем, оставим точкой расширения

    def decide(self, opponents: list[Character]) -> dict:
        """Выбор действия текущей стратегией."""
        strat = self.strategies[self.current_phase]
        return strat.choose_action(self, opponents)
