from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ✅ Obtener URL desde Railway
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Fix típico de Railway (postgres:// → postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class Base(DeclarativeBase):
    pass


# ✅ engine con configs útiles en producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# 🔥 IMPORTANTE: retry para Railway (la DB tarda en levantar)
def init_db(retries: int = 5, delay: int = 2) -> None:
    from app import models  # noqa

    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ DB conectada y tablas creadas")
            return
        except Exception as e:
            print(f"⏳ Esperando DB... intento {attempt + 1}")
            time.sleep(delay)

    raise Exception("❌ No se pudo conectar a la DB después de varios intentos")
