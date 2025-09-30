import random
from .mixins import LoggerMixin
from .turn import TurnOrder

class Battle(LoggerMixin):
    def __init__(self, party, boss, rng: random.Random | None = None):
        self.party = party
        self.boss = boss
        self.rng = rng or random.Random()

    def _living(self, entities):
        return [e for e in entities if getattr(e, "is_alive", True)]

    def run(self, max_rounds: int = 1):
        entities = self.party + [self.boss]
        for r in range(1, max_rounds + 1):
            with self.log_round(r):
                # актуализируем фазу босса
                if getattr(self.boss, "update_phase", None):
                    self.boss.update_phase()

                # эффекты старт-фазы
                for e in self._living(entities):
                    e.tick_effects("start")

                # ходы (пока заглушки)
                for e in TurnOrder(self._living(entities)):
                    print(f"- {e} acts (stub)")
                    e.reduce_cooldowns()

                # эффекты энд-фазы
                for e in self._living(entities):
                    e.tick_effects("end")
        return {"result": "stub"}
