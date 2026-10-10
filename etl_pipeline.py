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

def extraer_datos() -> pd.DataFrame:
    """Simula la extracción de datos desde una fuente local o remota."""
    logging.info("Iniciando fase de EXTRACCIÓN...")
    # Simulación de un dataset con datos crudos (ventas en tiendas)
    data = {
        "fecha": ["2026-01-15", "2026-01-20", "2026-02-11", "2026-02-14", None, "2026-03-01"],
        "tienda": ["Norte", "Sur", "Norte", "Sur", "Este", "Norte"],
        "monto": [150.50, 200.00, 350.00, 120.25, 99.99, -50.00],  # Incluye un valor negativo erróneo
        "productos_vendidos": [5, 8, 12, 4, 2, 1]
    }
    return pd.DataFrame(data)

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
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                mes TEXT,
                tienda TEXT,
                total_ingresos REAL,
                total_productos INTEGER,
                transacciones INTEGER,
                PRIMARY KEY (mes, tienda)
            )
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
