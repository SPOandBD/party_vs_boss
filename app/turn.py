from typing import Iterable

class TurnOrder:
    """
    Итератор на один раунд: отдаёт живых сущностей, отсортированных по убыванию agi.
    При равной agi — по имени (стабильность).
    """
    def __init__(self, entities: Iterable):
        self.entities = list(entities)

    def _living_sorted(self):
        live = [e for e in self.entities if getattr(e, "is_alive", True)]
        return sorted(live, key=lambda x: (-getattr(x, "agi", 0), getattr(x, "name", "")))

    def __iter__(self):
        for e in self._living_sorted():
            yield e
