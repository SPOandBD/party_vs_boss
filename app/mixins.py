from contextlib import contextmanager
import os

class CritMixin:
    def crit_chance(self) -> float:
        return 0.1

    def roll_crit(self, rnd) -> bool:
        return rnd.random() < self.crit_chance()

    def crit_multiplier(self) -> float:
        return 1.5

class LoggerMixin:
    LOG_DIR = "logs"

    @contextmanager
    def log_round(self, round_no: int):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        print(f"[ROUND {round_no}] ---- start")
        try:
            yield
        finally:
            print(f"[ROUND {round_no}] ---- end")
