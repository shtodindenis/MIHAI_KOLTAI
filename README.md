# ZHOSKO

Игровой проект на Python с использованием Arcade и UV.

## Структура проекта

```
ZHOSKO/
├── src/                    # Исходный код игры
│   ├── locations/          # Локации игры
│   ├── components/         # Компоненты и их рендеринг
│   ├── states/             # Состояния игры
│   ├── minigames/          # Логика мини-игр
│   ├── ui/                 # Элементы интерфейса
│   ├── shared/             # Константы, типы, утилиты
│   └── core/               # Основные механики, asset manager
├── assets/                 # Ресурсы игры (не входят в билд)
│   ├── images/             # Изображения
│   │   ├── raw/            # Исходные изображения для атласов
│   │   ├── *.png           # Сгенерированные атласы
│   │   └── *.json          # Конфиги атласов
│   ├── sounds/             # Звуковые файлы
│   ├── video/              # Видео файлы
│   ├── stories/            # JSON диалоги из Inky
│   └── maps/               # Карты Tiled (TMX)
├── tools/                  # Утилиты и скрипты
│   ├── atlas_gen.py        # Генератор атласов
│   └── atlas_config.json   # Конфигурация генератора
├── main.py                 # Точка входа
└── pyproject.toml          # Конфигурация проекта
```

## Установка

```bash
# Установка uv (если не установлен)
powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"

# Установка зависимостей
uv sync
```

## Использование

### Запуск игры

```bash
uv run python main.py
```

### Генерация атласов

```bash
# Собрать все атласы с auto_build=true
uv run python tools/atlas_gen.py

# Собрать все атласы
uv run python tools/atlas_gen.py --all

# Собрать конкретный атлас
uv run python tools/atlas_gen.py --atlas test
uv run python tools/atlas_gen.py -a test
```

## Конфигурация атласов

Файл `tools/atlas_config.json`:

```json
{
    "atlas_test": {
        "atlas": "test.png",           // Имя выходного PNG (по умолчанию: имя папки)
        "config": "test.json",         // Имя выходного JSON (по умолчанию: имя папки)
        "scale": 0.5,                  // Масштаб спрайтов (по умолчанию: 1)
        "auto_build": true,            // Собирать ли с флагом по умолчанию
        "sprites": {                   // Кастомные имена спрайтов
            "ppl4.png": "Rapestain"
        },
        "custom": "test"               // Имя для флага --atlas
    }
}
```

## Зависимости

- **arcade** - игровой движок
- **orjson** - быстрый JSON парсер
- **pytexturepacker** - упаковка текстур в атласы

## Разработка

```bash
# Запуск с автoreload (если нужно)
uv run python main.py

# Форматирование кода
uv run ruff format .

# Линтинг
uv run ruff check .
```
