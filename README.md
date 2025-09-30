# Мини-игра «Пати против Босса» (ООП в Python)

## Описание проекта
Проект представляет собой учебную мини-игру, созданную в рамках практического занятия по дисциплине "СПОиБД".  
Игрок управляет группой героев (пати), которые сражаются против одного сильного босса.  
Бой пошаговый: каждый персонаж действует в порядке инициативы, применяя атаки, навыки, предметы и эффекты.

Игра реализована с целью закрепления принципов объектно-ориентированного программирования:
- **Инкапсуляция** — приватные и защищённые поля.
- **Наследование** — иерархия классов Human -> Character -> [Warrior, Mage, Healer, Boss].
- **Полиморфизм** — разные реализации метода `use_skill` у наследователей.
- **Абстракция** — класс `Character` с абстрактными методами.
- **Дескрипторы** — для валидации HP, MP и характеристик.
- **Свойства** — например, `is_alive`.
- **Магические методы** — `__str__`, `__repr__`, `__eq__`, `__hash__`, `__iter__`.
- **Миксины** — CritMixin (критические атаки), LoggerMixin (логирование раундов).

## 📂 Структура проекта
```
party_vs_boss/
│
├── app/
│   ├── __init__.py       # пакет приложения
│   ├── core.py           # Human, Character, дескриптор BoundedStat
│   ├── heroes.py         # классы героев: Warrior, Mage, Healer
│   ├── boss.py           # класс Boss и стратегии (Strategy) для фаз
│   ├── effects.py        # система эффектов (Poison, Shield, Regen, Silence)
│   ├── items.py          # предметы (Item, Potion, Ether, Antidote, Inventory)
│   ├── turn.py           # очередь ходов (TurnOrder)
│   ├── battle.py         # логика пошагового боя
│   ├── mixins.py         # CritMixin и LoggerMixin
│   ├── save_load.py      # заготовка для сохранений в JSON
│   └── utils.py          # вспомогательные функции
│
├── tests/                # тесты (pytest)
├── logs/                 # логи боёв
├── requirements.txt      # зависимости проекта
└── README.md             # документация проекта
```

## Реализованные возможности
- Создание героев (Warrior, Mage, Healer) с уникальными навыками.
- Класс `Boss` с фазами и стратегиями поведения (паттерн Strategy).
- Система эффектов:
  - **Poison** — урон по времени.
  - **Regen** — восстановление HP по времени.
  - **Shield** — поглощение урона.
  - **Silence** — блокировка навыков.
- Система предметов (Potion, Ether, Antidote, Inventory).
- Очередь ходов `TurnOrder` (по ловкости, при равенстве — по имени).
- Пошаговый бой с:
  - применением навыков и предметов,
  - тиканием эффектов,
  - кулдаунами умений,
  - фазами босса,
  - проверкой условий победы.
- Логирование раундов через `LoggerMixin` (контекстный менеджер).

## 🔧 Установка и запуск
1. Клонировать репозиторий или скачать архив:
```bash
git clone https://github.com/SPOandBD/party_vs_boss.git
cd party_vs_boss
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Запустить CLI-заглушку:
```bash
python -m app.cli
```

4. Запустить тесты:
```bash
pytest -q
```

## 🎮 Пример боя и логов
Сценарий генерации логов:

```python
from app.battle import Battle
from app.heroes import Warrior, Mage, Healer
from app.boss import Boss

party = [
    Warrior("Warrior", level=1, hp=80, mp=20, str_=6, agi=3, int_=1),
    Mage("Mage", level=1, hp=60, mp=30, str_=1, agi=5, int_=7),
    Healer("Healer", level=1, hp=70, mp=30, str_=1, agi=2, int_=6),
]
boss = Boss("Dragon", level=3, hp=120, mp=0, str_=8, agi=4, int_=5)

battle = Battle(party, boss)
result = battle.run(max_rounds=5)
print("Result:", result)
```

Пример лога (`logs/battle_log.txt`):
```
[ROUND 1] ---- start
Mage uses fireball on Dragon for 24
Dragon uses toxic_spit on Warrior
Warrior hits Dragon for 14
Healer heals Warrior for 18
[ROUND 1] ---- end
...
>>> Party wins!
Result: {"result": "party"}
```

## ✅ Покрытие требований ТЗ
- Исходный код с модулями — **есть**  
- README.md с описанием и инструкцией — **есть**  
- Логи боя (txt) — **генерируются через LoggerMixin**  
- Набор тестов (pytest) — **есть, покрывают все ключевые компоненты**  

---
**Автор:** Студенты группы М3О-234БВ-24 Газизулин Д.И, Кудалин И.А., Павлов К.В  
**Учебный проект: «Пати против Босса»**
