"""
Script para obtener los datos historicos del visor de datos en tiempo real de La Gomera.
"""

from datetime import datetime

from src.ree.conf import DATABASE_NAME_LA_GOMERA
from src.ree.conf import GET_VARIATION_LA_GOMERA_LOG as LOG_FILE
from src.ree.conf import INFLUXDB_CLIENT, URL_BASE, error_handler, logging_handler
from src.ree.utils.data_extraction_funcs import build_dataframe
from src.ree.utils.ExtractDataVision import ExtractDataVision

if __name__ == "__main__":
    # Instanciar clase para extrar los datos del visor
    extractor = ExtractDataVision()
    # Configurar logger
    logger = logging_handler.configure_logger(
        log_file=LOG_FILE,
        log_retention_period="3d",
        log_backup_period=3,
    )

    # Iniciar extraccion de datos
    logger.info("Iniciando extraccion de datos de la Gomera...")

    try:
        # Iniciar el WebDriver
        extractor.start_driver()

        # Iniciar extraccion para el dia actual
        # y a la vez recorrer las 3 paginas: demanda, generacion, emisiones
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Generar url para la fecha actual
        for n, page in enumerate(["demanda", "generacion", "emision"], start=1):
            logger.info(
                f"\tExtrayendo datos de la Gomera para la fecha '{current_date}/{n}'..."
            )
            url = f"{URL_BASE}{current_date}/{n}"

            # Extraer datos de la tabla dinamica
            data_dict = extractor.extract_data(url)

            # Construir DataFrame
            data = build_dataframe(data_dict)

            # Guardar DataFrame en InfluxDB
            INFLUXDB_CLIENT.write_dataframes(
                database=DATABASE_NAME_LA_GOMERA,
                measurement=page,
                data=data,
            )

    except Exception as e:
        error_msg = f"Error al extraer datos de la Gomera para la fecha '{current_date}/{n}'. Error: '{e}'"
        error_handler.throw_error(error_msg, logger)
    finally:
        # Detener el WebDriver
        extractor.stop_driver()
        logger.info("Extraccion de datos de la Gomera finalizada.\n")
