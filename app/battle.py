import random
from typing import List, Dict, Any
from .mixins import LoggerMixin, CritMixin
from .turn import TurnOrder
from .heroes import Warrior, Mage, Healer
from .boss import Boss


class Battle(LoggerMixin):
    """
    Основной игровой цикл:
      - начало раунда: обновить фазу босса, тик эффектов (start)
      - порядок действий по ловкости (TurnOrder)
      - каждое действие: базовая атака или скилл (у героев простая авто-логика, у босса — Strategy)
      - уменьшение кулдаунов актёра
      - конец раунда: тик эффектов (end)
      - проверка конца боя
    """

    def __init__(self, party: List, boss: Boss, rng: random.Random | None = None):
        self.party = party
        self.boss = boss
        self.rng = rng or random.Random()

    # --------- утилиты ---------
    def _living(self, entities):
        return [e for e in entities if getattr(e, "is_alive", True)]

    def _any_heroes_alive(self) -> bool:
        return any(h.is_alive for h in self.party)

    def _log(self, msg: str):
        # сейчас просто print; LoggerMixin уже помечает начало/конец раунда
        print(msg)

    # --------- выбор действий ---------
    def _choose_hero_action(self, hero, enemies) -> Dict[str, Any]:
        """
        Простая авто-логика (детерминированная), чтобы соответствовать ТЗ:
          - Warrior: basic_attack по боссу
          - Mage:   fireball при доступности (MP и КД), иначе basic_attack по боссу
          - Healer: heal самого раненого союзника, если у кого-то HP<50% и навык доступен, иначе basic_attack по боссу
        """
        if isinstance(hero, Warrior):
            return {"type": "basic", "target": self.boss}

        if isinstance(hero, Mage):
            if hero.can_use("fireball") and hero.mp >= 12:
                return {"type": "skill", "skill_id": "fireball", "target": self.boss}
            return {"type": "basic", "target": self.boss}

        if isinstance(hero, Healer):
            injured = [a for a in self.party if a.is_alive and a.hp < (a.max_hp // 2)]
            if injured and hero.can_use("heal") and hero.mp >= 10:
                target = min(injured, key=lambda x: x.hp)
                return {"type": "skill", "skill_id": "heal", "target": target}
            return {"type": "basic", "target": self.boss}

        # дефолт для неизвестных героев
        return {"type": "basic", "target": self.boss}

    # --------- выполнение действий ---------
    def _apply_crit(self, actor, base_damage: int) -> int:
        """
        Если актёр умеет критовать (CritMixin), прокидываем шанс и множитель.
        Криты вешаем только на урон (не на лечение), и только если base_damage > 0.
        """
        if base_damage <= 0:
            return base_damage
        if isinstance(actor, CritMixin):
            if actor.roll_crit(self.rng):
                return int(round(base_damage * actor.crit_multiplier()))
        return base_damage

    def _exec_basic(self, actor, target):
        # базовая атака возвращает нанесённый урон (у героев это «сырой» dmg),
        # но для щитов/резистов лучше переложить получателя на receive_damage в самих классах.
        raw = actor.basic_attack(target)
        dmg = self._apply_crit(actor, raw)
        # если basic_attack у героя писал напрямую в target.hp, скорректируем разницу для лога
        if hasattr(target, "receive_damage"):
            # компенсируем: считаем, сколько уже списано (raw), и если крит → добавим недостающую часть
            extra = max(0, dmg - raw)
            if extra:
                # докинем «поверх» через нормальную механику урона
                dealt_extra = target.receive_damage(extra)
                self._log(f"{actor.name} crits! extra damage {dealt_extra}")
        self._log(f"{actor.name} hits {target.name} for {max(dmg,0)}")

    def _exec_skill(self, actor, skill_id: str, target):
        result = actor.use_skill(target, skill_id)
        if result > 0:
            # урон (можно критовать урон скилла, если захочешь; в ТЗ не обязательно)
            self._log(f"{actor.name} uses {skill_id} on {target.name} for {result}")
        elif result < 0:
            # лечение отдаём как положительное число
            self._log(f"{actor.name} heals {target.name} for {abs(result)}")
        else:
            # 0 — возможно накладка эффекта (яд/щит), без мгновенного урона
            self._log(f"{actor.name} uses {skill_id} on {target.name}")

    def _execute_action(self, actor, action: Dict[str, Any]):
        if not actor.is_alive:
            return
        kind = action.get("type", "basic")
        target = action.get("target")

        if kind == "basic":
            self._exec_basic(actor, target)
        elif kind == "skill":
            skill_id = action.get("skill_id")
            self._exec_skill(actor, skill_id, target)
        elif kind == "wait":
            self._log(f"{actor.name} waits...")
        else:
            self._log(f"{actor.name} does nothing (unknown action)")

    # --------- основной цикл ---------
    def run(self, max_rounds: int = 20) -> Dict[str, Any]:
        entities = self.party + [self.boss]

        for r in range(1, max_rounds + 1):
            with self.log_round(r):
                # актуализируем фазу босса
                if hasattr(self.boss, "update_phase"):
                    self.boss.update_phase()

                # эффекты старт-фазы
                for e in self._living(entities):
                    e.tick_effects("start")

                # ходят по ловкости
                for actor in TurnOrder(self._living(entities)):
                    # выберем действие
                    if actor in self.party:
                        action = self._choose_hero_action(actor, [self.boss])
                    else:
                        # Если это настоящий босс со стратегией — используем её.
                        # ИНАЧЕ (например, Warrior как временный "босс" в тестах) — ПРОПУСК ХОДА (wait),
                        # чтобы тесты тиков не искажались входящим уроном.
                        if hasattr(actor, "decide") and callable(getattr(actor, "decide")):
                            action = actor.decide(self._living(self.party))
                        else:
                            action = {"type": "wait"}
                    # выполнить
                    self._execute_action(actor, action)
                    # уменьшить кулдауны актёра
                    actor.reduce_cooldowns()

                    # проверка конца боя прямо по ходу
                    if not self.boss.is_alive:
                        self._log(">>> Party wins!")
                        return {"result": "party"}
                    if not self._any_heroes_alive():
                        self._log(">>> Boss wins!")
                        return {"result": "boss"}

                # эффекты энд-фазы
                for e in self._living(entities):
                    e.tick_effects("end")

                # проверка конца боя после тиков
                if not self.boss.is_alive:
                    self._log(">>> Party wins!")
                    return {"result": "party"}
                if not self._any_heroes_alive():
                    self._log(">>> Boss wins!")
                    return {"result": "boss"}

        self._log(">>> Draw (round limit)")
        return {"result": "draw"}
