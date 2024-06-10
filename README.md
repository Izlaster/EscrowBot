# EscrowBot

Установить python 3.10

Для локальной разработки (бекенд + БД):
```bash
pip install poetry

cd backend

poetry shell

poetry install

cd ../local_database && docker compose up -d

alembic upgrade <последняя версия> (смотреть migraions/versions *переменная: revision*)

fastapi dev main.py
```
Для запуска бота:
```bash
cd front

poetry shell

poetry install

python bot.py
```
