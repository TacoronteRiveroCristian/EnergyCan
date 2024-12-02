"""
Archivo de configuracion para la seccion energetica de REE.
"""

import os
from datetime import datetime
from pathlib import Path

from ctrutils.database.influxdb.InfluxdbOperation import InfluxdbOperation

# Directorio de trabajo
WORKDIR = Path(os.getenv("WORKDIR"))

# Seccion data extraction paras la Gomera
HISTORICAL_DATA_START = datetime(2024, 1, 1)
HISTORICAL_DATA_END = datetime(2024, 12, 31)
URL_BASE = "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/"
GET_VARIATION_LA_GOMERA_LOG = (
    WORKDIR
    / "src/ree/data_extraction/logs/get_variation_la_gomera/get_variation_la_gomera.log"
)
GET_HISTORICAL_VARIATION_LA_GOMERA_LOG = (
    WORKDIR
    / "src/ree/data_extraction/logs/get_historical_variation_la_gomera/get_historical_variation_la_gomera.log"
)
DATABASE_NAME_LA_GOMERA = "monitoring_ree_la_gomera"

# Clienter de InfluxDB
INFLUXDB_CLIENT = InfluxdbOperation(
    host="10.142.150.64",
    port=8086,
)
