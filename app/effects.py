from __future__ import annotations

class Effect:
    """Базовый эффект: хранит имя, длительность (в ходах) и стаки."""
    def __init__(self, name: str, duration: int, stacks: int = 1):
        self.name = name
        self.duration = int(duration)
        self.stacks = int(stacks)

    # хуки жизненного цикла
    def on_apply(self, target):
        pass

    def on_turn_start(self, target):
        pass

    def on_turn_end(self, target):
        # по умолчанию уменьшаем длительность в конце хода владельца
        self.duration -= 1

    def on_expire(self, target):
        pass


class Poison(Effect):
    """Яд: наносит фиксированный урон каждый конец хода владельца."""
    def __init__(self, dps: int, duration: int):
        super().__init__("Poison", duration)
        self.dps = int(dps)

    def on_turn_end(self, target):
        if target.is_alive and self.dps > 0:
            target.receive_damage(self.dps)
        self.duration -= 1


class Regen(Effect):
    """Регенерация: лечит каждый конец хода владельца."""
    def __init__(self, hps: int, duration: int):
        super().__init__("Regen", duration)
        self.hps = int(hps)

    def on_turn_end(self, target):
        if target.is_alive and self.hps > 0:
            target.heal(self.hps)
        self.duration -= 1


class Shield(Effect):
    """Щит: поглощает входящий урон, пока не исчерпается или не истечёт по времени."""
    def __init__(self, amount: int, duration: int):
        super().__init__("Shield", duration)
        self.capacity = int(amount)

    def on_damage(self, target, incoming: int) -> int:
        if incoming <= 0 or self.capacity <= 0:
            return max(0, incoming)
        absorbed = min(self.capacity, incoming)
        self.capacity -= absorbed
        remaining = incoming - absorbed
        return max(0, remaining)

    def on_turn_end(self, target):
        self.duration -= 1
        # если щит кончился раньше времени — пусть спадёт при следующей проверке duration<=0
        if self.capacity <= 0 and self.duration > 0:
            self.duration = 0  # принудительно снять на конце хода


class Silence(Effect):
    """Немота: запрещает использование навыков."""
    def __init__(self, duration: int):
        super().__init__("Silence", duration)

    def on_apply(self, target):
        target._silenced = True

    def on_turn_end(self, target):
        self.duration -= 1

    def on_expire(self, target):
        target._silenced = False
