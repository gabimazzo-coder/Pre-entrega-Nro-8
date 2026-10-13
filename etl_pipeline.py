import os
import sqlite3
import pandas as pd
import logging

# Configuración de logs para monitorear la automatización
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

DB_NAME = "analytics_vault.sqlite"
TABLE_NAME = "fact_ventas_mensuales"

def extraer_datos(file_path: str = "ventas_raw.csv") -> pd.DataFrame:
    """Extrae datos desde un dataset local con control de excepciones."""
    logging.info(f"Iniciando fase de EXTRACCIÓN desde {file_path}...")
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Extracción exitosa. Registros extraídos: {len(df)}")
        return df
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo fuente en la ruta: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error inesperado durante la extracción: {e}")
        raise


def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza la limpieza de datos y una agregación básica."""
    logging.info("Iniciando fase de TRANSFORMACIÓN...")
    
    # 1. Limpieza: Remover filas con fechas nulas y montos inválidos
    df_clean = df.dropna(subset=["fecha"]).copy()
    df_clean = df_clean[df_clean["monto"] > 0]
    
    # 2. Normalización: Asegurar tipos de datos correctos
    df_clean["fecha"] = pd.to_datetime(df_clean["fecha"])
    df_clean["mes"] = df_clean["fecha"].dt.to_period("M").astype(str)
    
    # 3. Agregación: Total de ventas y productos por mes y tienda
    df_transformed = df_clean.groupby(["mes", "tienda"]).agg(
        total_ingresos=("monto", "sum"),
        total_productos=("productos_vendidos", "sum"),
        transacciones=("monto", "count")
    ).reset_index()
    
    logging.info(f"Transformación completada. Filas resultantes: {len(df_transformed)}")
    return df_transformed

def cargar_datos(df: pd.DataFrame):
    """Conecta a la base de datos local y carga los datos de forma segura."""
    logging.info("Iniciando fase de CARGA (Persistencia)...")
    conn = None
    try:
        # Conexión a la base de datos SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Diseño del esquema de la tabla de destino
        cursor.execute(f"""
        cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        mes TEXT,
        tienda TEXT,
        total_ingresos REAL,
        total_productos INTEGER,
        transacciones INTEGER,
        PRIMARY KEY (mes, tienda)
    )
""")

# Carga preservando el esquema definido:
df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)

        """)
        
        # Carga de datos utilizando la estrategia 'replace' para evitar duplicados
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.commit()
        logging.info(f"¡Datos cargados exitosamente en la tabla '{TABLE_NAME}' de '{DB_NAME}'!")
        
    except sqlite3.OperationalError as e:
        logging.error(f"Error operacional en la base de datos: {e}")
    except sqlite3.Error as e:
        logging.error(f"Error inesperado de SQLite: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Conexión a la base de datos cerrada de manera segura.")

if __name__ == "__main__":
    try:
        df_raw = extraer_datos()
        df_ready = transformar_datos(df_raw)
        cargar_datos(df_ready)
    except Exception as e:
        logging.critical(f"El pipeline ETL falló críticamente: {e}")
