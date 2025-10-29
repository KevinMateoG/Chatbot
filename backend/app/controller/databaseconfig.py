from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import sys
# Agregar el directorio raíz del backend al PATH
backend_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_path))

import secretconfig as sc
"""coneccion con base de datos"""
DATABASE_URL = f"postgresql://{sc.PGUSER}:{sc.PGPASSWORD}@{sc.PGHOST}/{sc.PGDATABASE}?sslmode={sc.PGSSLMODE}&channel_binding={sc.PGCHANNELBINDING}"

"""motor de base de datos"""
engine = create_engine(
    DATABASE_URL
)

"""se crea la secion"""
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""base para los modelos"""
base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()