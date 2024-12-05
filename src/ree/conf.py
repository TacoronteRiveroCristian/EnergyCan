"""
Archivo de configuracion para la seccion energetica de REE.
"""

import os
from datetime import datetime
from pathlib import Path

from ctrutils.database.influxdb.InfluxdbOperation import InfluxdbOperation
from ctrutils.handlers.ErrorHandlerBase import ErrorHandler
from ctrutils.handlers.LoggingHandlerBase import LoggingHandler

# Instanciar manejador de error y logger
error_handler = ErrorHandler()
logging_handler = LoggingHandler()

# Directorio de trabajo
WORKDIR = Path(os.getenv("WORKDIR"))

# Clienter de InfluxDB
INFLUXDB_CLIENT = InfluxdbOperation(
    host="10.142.150.64",
    port=8086,
)

##### SECCION REE #####
# Url base para la extraccion de datos mediante selenium
URL_BASE = "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/"
DATABASE_NAME_LA_GOMERA = "monitoring_ree_la_gomera"
# get_historical_variation_la_gomera.py
HISTORICAL_DATA_START = datetime(2024, 2, 1)
HISTORICAL_DATA_END = datetime(2024, 2, 2)
GET_HISTORICAL_VARIATION_LA_GOMERA_LOG = (
    WORKDIR
    / "src/ree/data_extraction/logs/get_historical_variation_la_gomera/get_historical_variation_la_gomera.log"
)
# get_current_variation_la_gomera.py
GET_CURRENT_VARIATION_LA_GOMERA_LOG = (
    WORKDIR
    / "src/ree/data_extraction/logs/get_current_variation_la_gomera/get_current_variation_la_gomera.log"
)
