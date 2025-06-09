from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv
import sys

# Добавляем путь к проекту, чтобы работал импорт
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Загружаем .env
load_dotenv()

# Импортируем модели
from app.main import SQLModel
from sqlalchemy import create_engine  # ❗ sync-движок для Alembic

# Alembic config
config = context.config
fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))  # или SYNC_DATABASE_URL

# Указываем метаданные
target_metadata = SQLModel.metadata

# 🔸 Вот это — функция фильтрации чужих таблиц
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name not in target_metadata.tables:
        return False  # НЕ включать таблицу в сравнение
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object  # 🔸 добавили сюда
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object  # 🔸 добавили сюда
        )

        with context.begin_transaction():
            context.run_migrations()

# Выбор режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
