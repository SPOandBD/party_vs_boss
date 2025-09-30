import random
from .mixins import LoggerMixin
from .turn import TurnOrder

class Battle(LoggerMixin):
    def __init__(self, party, boss, rng: random.Random | None = None):
        self.party = party
        self.boss = boss
        self.rng = rng or random.Random()

    def run(self, max_rounds: int = 1):
        for r in range(1, max_rounds + 1):
            with self.log_round(r):
                for entity in TurnOrder(self.party + [self.boss]):
                    print(f"- {entity} is ready to act (stub)")
        return {"result": "stub"}
