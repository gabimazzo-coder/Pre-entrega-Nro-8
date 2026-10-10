# Pipeline Automatizado ETL - Capa de Persistencia

Este repositorio contiene un script de automatización en **Python** que implementa un flujo ETL (Extraction, Transformation, Load) básico, procesando un flujo de datos transaccionales para estructurarlo en una capa de persistencia analítica utilizando **SQLite**.

## 📊 Patrón de Datos Utilizado

El diseño de datos sigue el concepto de **Tablas de Hechos Agregadas**. 
* **Origen (Raw Data):** Representa transacciones individuales con alta granularidad (Fechas, Tiendas, Montos específicos). Presenta inconsistencias como registros nulos y valores negativos.
* **Destino (Analytics Layer):** Una tabla estructurada llamada `fact_ventas_mensuales` optimizada para tableros de control o reportes rápidos. Consolida las métricas clave agrupadas por **Mes** y **Tienda**.

### Esquema de la Tabla Destino

| Campo | Tipo de Datos | Descripción |
| :--- | :--- | :--- |
| `mes` (PK) | TEXT | Periodo de la agregación (Formato: YYYY-MM) |
| `tienda` (PK)| TEXT | Región geográfica o sucursal |
| `total_ingresos`| REAL | Suma total de dinero recaudado |
| `total_productos`| INTEGER | Cantidad total de ítems vendidos |
| `transacciones`| INTEGER | Número de operaciones válidas en el mes |

---

## 🛠️ Configuración del Entorno y Ejecución

Sigue estos pasos para clonar el repositorio, configurar tu entorno local y ejecutar el pipeline.

### Prerrequisitos
* Python 3.8 o superior instalado.
* Git configurado en tu equipo.

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com
cd TU_REPOSITORIO
```

### Paso 2: Crear y activar un entorno virtual
En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
En macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
Instala la biblioteca encargada del procesamiento y modelado de datos:
```bash
pip install pandas
```

### Paso 4: Ejecutar el Pipeline ETL
Ejecuta el script principal de automatización:
```bash
python etl_pipeline.py
```

## 🔍 Tratamiento de Errores y Robustez
El script cuenta con un sistema defensivo que mitiga los siguientes problemas comunes:
1. **Control de Conexiones:** Cierra de forma segura la conexión a SQLite en el bloque `finally` para evitar bloqueos del archivo de base de datos (`.sqlite`).
2. **Excepciones de Base de Datos:** Captura errores operativos específicos de SQL (`sqlite3.Error`) sin interrumpir o corromper el entorno del sistema.
3. **Calidad de Datos:** Filtra valores nulos y registros erróneos (montos de venta negativos) en la capa de transformación antes de impactar la base de datos de producción.
