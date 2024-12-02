"""
Script para obtener los datos historicos del visor de datos en tiempo real de La Gomera.
"""

from datetime import timedelta
from time import sleep

from src.ree.conf import DATABASE_NAME_LA_GOMERA
from src.ree.conf import GET_HISTORICAL_VARIATION_LA_GOMERA_LOG as LOG_FILE
from src.ree.conf import (
    HISTORICAL_DATA_END,
    HISTORICAL_DATA_START,
    INFLUXDB_CLIENT,
    URL_BASE,
    error_handler,
    logging_handler,
)
from src.ree.utils.data_extraction_funcs import build_dataframe
from src.ree.utils.ExtractDataVision import ExtractDataVision

# Contador de errores
error_count = 0

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

        # Iniciar bucle para extraer los datos del periodo de interes seleccionado
        # y a la vez recorrer las 3 paginas: demanda, generacion, emisiones
        current_date = HISTORICAL_DATA_START
        while current_date <= HISTORICAL_DATA_END:
            # Generar url para la fecha actual
            for n, page in enumerate(["demanda", "generacion", "emision"], start=1):
                logger.info(
                    f"\tExtrayendo datos de la Gomera para la fecha '{current_date}/{n}'..."
                )
                url = f"{URL_BASE}{current_date.strftime('%Y-%m-%d')}/{n}"

                # Extraer datos de la tabla dinamica
                data_dict = extractor.extract_data(url)

                # Construir DataFrame
                try:
                    data = build_dataframe(data_dict)
                except KeyError as e:
                    error_count += 1
                    warning_msg = f"No se han obtenido datos de la Gomera para la fecha '{current_date}/{n}'. Error: '{e}'"
                    error_handler.throw_warning(warning_msg, logger)
                    # Agregar pausa para evitar que en la siguiente iteracion inicie la extraccion demasiado rapido
                    sleep(0.5)
                    # Y repetir bucle para intentar obtener los datos o pasar ya a la siguiente fecha si se han originado 3 errores seguidos
                    if error_count == 3:
                        current_date += timedelta(days=1)
                        error_count = 0
                    continue

                # Guardar DataFrame en InfluxDB
                INFLUXDB_CLIENT.write_dataframes(
                    database=DATABASE_NAME_LA_GOMERA,
                    measurement=page,
                    data=data,
                )

            # Incrementar 1 dia para la siguiente iteracion
            current_date += timedelta(days=1)
            # Agregar pausa para evitar que en la siguiente iteracion inicie la extraccion demasiado rapido
            sleep(0.5)

    except Exception as e:
        error_msg = f"Error al extraer datos de la Gomera para la fecha '{current_date}/{n}'. Error: '{e}'"
        error_handler.throw_error(error_msg, logger)
    finally:
        # Detener el WebDriver
        extractor.stop_driver()
        logger.info("Extraccion de datos de la Gomera finalizada.\n")
