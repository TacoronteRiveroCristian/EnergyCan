"""
Script para obtener los datos historicos del visor de datos en tiempo real de La Gomera.
"""

from datetime import datetime

from ctrutils.handlers.ErrorHandlerBase import ErrorHandler
from ctrutils.handlers.LoggingHandlerBase import LoggingHandler

from src.ree.conf import DATABASE_NAME_LA_GOMERA
from src.ree.conf import GET_VARIATION_LA_GOMERA_LOG as LOG_FILE
from src.ree.conf import INFLUXDB_CLIENT, URL_BASE
from src.ree.utils.data_extraction_funcs import build_dataframe
from src.ree.utils.ExtractDataVision import ExtractDataVision

# Configurar logger
logging_handler = LoggingHandler(
    log_file=LOG_FILE, log_retention_period="1d", log_backup_period=7
)
logger = logging_handler.configure_logger()
# Configurar manejador de errores
error_handler = ErrorHandler()
# Instanciar clase de extraccion de datos del visor a tiempo real
extractor = ExtractDataVision()

if __name__ == "__main__":
    logger.info("Iniciando extraccion de datos de la Gomera...")

    try:
        # Iniciar el WebDriver
        extractor.start_driver()

        # Iniciar extraccion para el dia actual
        # y a la vez recorrer las 3 paginas: demanda, generacion, emisiones
        current_date = datetime.now()

        # Generar url para la fecha actual
        for n, page in enumerate(["demanda", "generacion", "emision"], start=1):
            logger.info(
                f"\tExtrayendo datos de la Gomera para la fecha '{current_date}/{n}'..."
            )
            url = f"{URL_BASE}{current_date.strftime('%Y-%m-%d')}/{n}"

            # Extraer datos de la tabla dinamica
            data_dict = extractor.extract_data(url)

            # Construir DataFrame
            data = build_dataframe(data_dict)

            # Guardar DataFrame en InfluxDB
            INFLUXDB_CLIENT.write_points(
                database=DATABASE_NAME_LA_GOMERA,
                measurement=page,
                data=data,
            )

    except Exception as e:
        error_msg = f"Error al extraer datos de la Gomera para la fecha '{current_date}/{n}'. Error: '{e}'"
        error_handler.handle_error(error_msg, logger)
    finally:
        # Detener el WebDriver
        extractor.stop_driver()
        logger.info("Extraccion de datos de la Gomera finalizada.\n")
