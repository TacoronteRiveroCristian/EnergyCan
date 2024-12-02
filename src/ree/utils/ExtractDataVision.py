"""
Clase para extraer datos de visiona en REE mediante web scraping a traves de las tablas dinamicas que se encuentran
en la seccion de datos a tiempo real.

El link que se debe de proporcionar debe de tener una estrcutura similña a la siguiente:
https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/2024-11-29/1

En este caso, se va a extraer la informacion de la pagina 1 de la fecha 2024-11-29. La pagina 1 correspone a la Demanda,
la pagina 2 a la Generacion y la pagina 3 a las Emisiones.
"""

from typing import Dict, List, Optional

import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ExtractDataVision:
    """
    Clase para extraer datos de tablas dinamicas desde una pagina web utilizando Selenium.

    :param chromedriver_path: Ruta al ejecutable de ChromeDriver.
    :type chromedriver_path: Optional[str]
    """

    def __init__(self, chromedriver_path: Optional[str] = None):
        """
        Constructor de la clase.

        :param chromedriver_path: Ruta al ejecutable de ChromeDriver.
        :type chromedriver_path: Optional[str]
        :raises ValueError: Si no se proporciona una ruta valida para ChromeDriver.
        """
        self.chromedriver_path = (
            chromedriver_path  # Ruta al ejecutable del ChromeDriver
        )
        self.driver = (
            None  # Driver inicializado como None hasta que se llame a start_driver
        )

    def _init_options(self) -> Options:
        """
        Configura las opciones para el navegador.

        :return: Objeto Options con las configuraciones establecidas.
        :rtype: Options
        """
        options = Options()
        options.add_argument("--headless")  # Ejecutar en modo sin interfaz grafica
        options.add_argument("--no-sandbox")  # Deshabilitar el sandboxing de Chrome
        options.add_argument(
            "--disable-dev-shm-usage"
        )  # Evitar problemas de memoria compartida
        return options

    def _init_service(self) -> Service:
        """
        Configura el servicio del WebDriver.

        :return: Objeto Service configurado con el path del ChromeDriver.
        :rtype: Service
        """
        return Service(
            self.chromedriver_path
        )  # Crear el servicio con la ruta proporcionada

    def start_driver(self):
        """
        Inicializa el WebDriver si aún no esta inicializado.

        :raises RuntimeError: Si ocurre un error al iniciar el WebDriver.
        """
        if self.driver is None:  # Verificar si el driver ya esta iniciado
            self.driver = webdriver.Chrome(
                service=self._init_service(),  # Configurar el servicio con la ruta del ChromeDriver
                options=self._init_options(),  # Aplicar las opciones configuradas
            )

    def stop_driver(self):
        """
        Detiene el WebDriver si esta activo.
        """
        if self.driver:  # Verificar si el driver esta activo
            self.driver.quit()  # Cerrar el WebDriver
            self.driver = None  # Limpiar la referencia al driver

    def _extract_headers(self, table) -> List[str]:
        """
        Extrae los encabezados de la tabla.

        :param table: Elemento de la tabla.
        :type table: WebElement
        :return: Lista de encabezados extraidos.
        :rtype: List[str]
        """
        # Buscar los elementos que representan los encabezados de la tabla
        header_row = table.find_elements(By.CSS_SELECTOR, "tbody > tr > th")
        # Extraer y devolver los textos de los encabezados que no esten vacios
        return [th.text.strip() for th in header_row if th.text.strip()]

    def _extract_data_rows(self, table) -> List[List]:
        """
        Extrae las filas de datos de la tabla.

        :param table: Elemento de la tabla.
        :type table: WebElement
        :return: Lista de filas con los datos extraidos.
        :rtype: List[List]
        :raises ValueError: Si ocurre un error al procesar una celda.
        """
        # Obtener todas las filas de la tabla excepto los encabezados
        rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")[1:]
        data = []  # Lista para almacenar las filas procesadas

        for row in rows:
            try:
                # Obtener las celdas de la fila
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                # Extraer el texto de la primera celda (fecha y hora)
                row_data = [cells[0].text.strip()]
                # Convertir las celdas restantes a flotantes o asignar valores no numericos, nan, si estan vacias
                row_data.extend(
                    float(cell.text.strip()) if cell.text.strip() else np.nan
                    for cell in cells[1:]
                )
                data.append(row_data)  # Agregar la fila procesada a la lista de datos
            except IndexError:
                # Ignorar filas incompletas
                continue
            except ValueError as ve:
                # Lanzar un error si hay problemas con el formato de los datos
                raise ValueError(
                    f"Error al procesar una celda de la fila: {ve}"
                ) from ve
            except Exception as e:
                # Lanzar una excepcion generica para errores inesperados
                raise Exception(f"Error inesperado al procesar una fila: {e}") from e
        return data

    def extract_data(self, url: str) -> Dict[str, List]:
        """
        Extrae datos de una tabla dinamica desde una URL.

        :param url: URL del sitio web que contiene la tabla.
        :type url: str
        :return: Diccionario con encabezados y datos extraidos.
        :rtype: Dict[str, List]
        :raises ValueError: Si la URL proporcionada no es valida.
        :raises RuntimeError: Si ocurre un error al extraer los datos de la tabla.
        """
        if not url:  # Validar que la URL no este vacia
            raise ValueError("La URL proporcionada no es valida.")

        headers, data = [], []  # Inicializar listas para encabezados y datos

        try:
            if self.driver is None:  # Verificar que el WebDriver este inicializado
                raise RuntimeError(
                    "El WebDriver no esta inicializado. Llama a `start_driver` primero."
                )

            self.driver.get(url)  # Abrir la URL en el navegador
            wait = WebDriverWait(
                self.driver, 10
            )  # Configurar un tiempo de espera de 10 segundos

            # Esperar a que la tabla este presente en el DOM
            table = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.tabla-evolucion-content")
                )
            )

            # Extraer encabezados y datos de la tabla
            headers = self._extract_headers(table)
            data = self._extract_data_rows(table)

        except Exception as e:
            # Lanzar un error si ocurre algún problema durante la extraccion
            raise RuntimeError(
                f"Error al extraer datos de la tabla: {e}. Verifique el sitio web o el selector."
            ) from e

        return {
            "headers": headers,
            "data": data,
        }  # Devolver encabezados y datos extraidos


# Ejemplo de uso
if __name__ == "__main__":
    extractor = ExtractDataVision()

    try:
        # Inicia el WebDriver una vez
        extractor.start_driver()

        # Lista de URLs a procesar
        urls = [
            "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/2024-11-29/1",
            "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/2024-11-28/2",
            "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/2024-11-28/3",
        ]

        for url in urls:
            data = extractor.extract_data(url)  # Extraer datos de cada URL
            print(f"Datos extraidos de {url}: {data}")  # Mostrar los datos extraidos

    finally:
        # Detener el WebDriver despues de procesar todas las URLs
        extractor.stop_driver()
