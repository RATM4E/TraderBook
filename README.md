# 📈 TraderBook

> Персональный журнал трейдера — анализ сделок, статистика, Монте-Карло симуляции.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-active%20development-yellow)]()

---

## 🗺️ Roadmap

| Этап | Статус | Описание |
|------|--------|----------|
| v1.x | ✅ В работе | Python / Streamlit версия |
| v2.0 | 🔜 Планируется | Порт на C# → standalone `.exe` |

---

## ✨ Возможности

- 📝 **Журнал сделок** — ввод, редактирование, скриншоты входа/выхода
- 📊 **Аналитика** — Crypto / Forex, статистика по сетапам, таймфреймам, сессиям
- 🎲 **Монте-Карло** — симуляция кривых капитала и просадок
- 📄 **Экспорт PDF** — отчёты с графиками (ReportLab + Plotly)
- 💾 **Резервные копии** — автоматическое создание бэкапов
- 🌍 **Мультиязычность** — RU / EN / UK
- 🎨 **Кастомные сетапы** — библиотека торговых паттернов с изображениями

---

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- pip

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/traderbook.git
cd traderbook

# 2. Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить приложение
python run.py
```

Приложение откроется в браузере по адресу `http://localhost:8501`

---

## 🗂️ Структура проекта

```
traderbook/
├── run.py                    # Точка входа
├── requirements.txt
├── .gitignore
│
└── src/
    ├── trader_journal.py     # Главная страница Streamlit
    ├── sidebar.py            # Боковая панель (язык, рынок, настройки)
    ├── trade_input.py        # Форма ввода сделки
    ├── trade_list.py         # Список и редактирование сделок
    ├── setups.py             # Управление торговыми сетапами
    │
    ├── core/                 # Бизнес-логика и данные
    │   ├── config.py         # Пути и конфигурация
    │   ├── paths.py          # Управление директориями
    │   ├── data_manager.py   # CRUD операции с CSV
    │   ├── file_manager.py   # Инициализация файловой системы
    │   ├── backup_manager.py # Резервные копии
    │   ├── calculations.py   # Финансовые расчёты (RR, P&L, %)
    │   ├── logging_setup.py  # Логирование
    │   └── translations.py   # Загрузка переводов
    │
    ├── ui/
    │   └── analytics/        # Модуль аналитики
    │       ├── data_processing.py  # Фильтрация и подготовка данных
    │       ├── metrics.py          # Расчёт метрик
    │       ├── monte_carlo.py      # Монте-Карло симуляции
    │       ├── plotting.py         # Plotly графики
    │       ├── tabs.py             # Вкладки аналитики
    │       ├── ui_components.py    # UI компоненты
    │       └── export_pdf.py       # Экспорт в PDF
    │
    └── locales/
        ├── en.json
        ├── ru.json
        └── uk.json
```

---

## 🛠️ Разработка

### Ветки
| Ветка | Назначение |
|-------|-----------|
| `main` | Стабильная версия |
| `dev` | Текущая разработка |
| `feature/*` | Новые фичи |
| `fix/*` | Баг-фиксы |
| `csharp-port` | Порт на C# |

### Запуск в режиме разработки
```bash
streamlit run src/trader_journal.py --server.runOnSave=true
```

---

## 🏗️ C# Port (v2.0)

Планируется полный порт на **C# + WPF / MAUI** для получения самостоятельного `.exe` без зависимостей.

Технологический стек C# версии:
- **UI**: WPF или .NET MAUI
- **Данные**: SQLite (вместо CSV) через Entity Framework Core
- **Графики**: LiveCharts2 или OxyPlot
- **PDF**: QuestPDF
- **Сборка**: single-file publish (`dotnet publish -r win-x64 --self-contained`)

Детали в ветке [`csharp-port`](../../tree/csharp-port).

---

## 🐛 Известные проблемы / Backlog

Смотри [Issues](../../issues).

---

## 📄 Лицензия

MIT © 2025 TraderBook Contributors
