class TurnOrder:
    def __init__(self, entities):
        self.entities = list(entities)

    def __iter__(self):
        for e in self.entities:
            if getattr(e, "is_alive", True):
                yield e
