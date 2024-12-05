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


def process_page(extractor, logger, current_date, n_page, page) -> bool:
    # Generar url para la fecha actual
    current_date_str = current_date.strftime("%Y-%m-%d")
    url = f"{URL_BASE}{current_date_str}/{n_page}"

    logger.info(f"\tExtrayendo datos la direccion: '{url}'...")
    try:
        # Extraer datos de la pagina actual
        data_dict = extractor.extract_data(url)

        # Convertir datos a DataFrame
        data = build_dataframe(data_dict)

        # Guardar DataFrame en InfluxDB
        INFLUXDB_CLIENT.write_dataframe(
            database=DATABASE_NAME_LA_GOMERA,
            measurement=page,
            data=data,
            tags={"fecha": current_date_str},
        )

        return True
    except KeyError:
        warning_msg = f"\t\tError al extraer datos de la Gomera para la fecha '{current_date_str}/{page}'."
        logger.warning(warning_msg)
        return False
    except Exception as e:
        warning_msg = f"\t\tError al extraer datos de la Gomera para la fecha '{current_date_str}/{page}'. Error: '{e}'"
        logger.warning(warning_msg)
        return False


def main():
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
        current_date = HISTORICAL_DATA_START
        while current_date <= HISTORICAL_DATA_END:
            # Procesar para cada dia, las tres paginas correspondientes
            for n_page, page in enumerate(
                ["demanda", "generacion", "emision"], start=1
            ):
                # Para cada pagina, intentar al menos una vez la extraccion y como maximo 3 veces mas
                # en caso de error
                for i in range(1, 4):
                    if process_page(extractor, logger, current_date, n_page, page):
                        break
                    else:
                        warning_msg = f"\t\tError al extraer datos de la Gomera para la fecha '{current_date.strftime('%Y-%m-%d')}/{n_page}'. Intento {i} de 3."
                        logger.warning(warning_msg)
                        if i == 3:
                            warning_msg = f"\t\tError al extraer datos de la Gomera para la fecha '{current_date.strftime('%Y-%m-%d')}/{n_page}'."
                            logger.warning(warning_msg)
                    # Realizar una pausa entre intentos
                    sleep(0.5)

            # Avanzar al siguiente dia
            current_date += timedelta(days=1)

        # Detener el WebDriver
        extractor.stop_driver()
        logger.info("Extraccion de datos de la Gomera finalizada.\n")
    except Exception as e:
        error_msg = f"Error al extraer datos de la Gomera. Error: '{e}'"
        error_handler.throw_error(error_msg, logger)


if __name__ == "__main__":
    main()
