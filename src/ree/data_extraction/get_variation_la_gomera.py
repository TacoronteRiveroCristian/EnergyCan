"""
"""

from datetime import datetime

import pandas as pd
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode

# Configurar opciones de Chrome para Docker
options = Options()
options.add_argument("--headless")  # Modo sin cabeza
options.add_argument(
    "--no-sandbox"
)  # Requerido para Docker ya que no existe ventana interactiva de Chrome

# Configura el path del ChromeDriver
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# URL de la página
url = "https://demanda.ree.es/visiona/canarias/la_gomera5m/tablas/2024-11-28/1"

# Nombre de los dataframes
names = ["demanda", "generacion", "emision"]

# Diccionario para almacenar los DataFrames
dataframes = {}

# Zona horaria de Canarias
canary_timezone = pytz.timezone("Atlantic/Canary")

try:
    # Abre la página
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Itera sobre los botones y extrae las tablas
    for name, i in zip(
        names, range(1, 4)
    ):  # Se sabe que hay 3 botones (Demanda, Generacion, Emisiones)
        # Refresca los botones cada vez que se repite el bucle porque el DOM de la pagina se modifica
        # ul siginifca que se va a seleccionar un elemento ordenado con la clase pagination-menu. Luego, se va a seleccionar
        # todas las listas heredades y de esas listas se seleccionan los enlaces que es donde se encuentran los datos de las tablas
        buttons = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "ul.pagination-menu > li > a")
            )
        )

        # Se selecciona el boton correspondiente. Indices 0, 1, 2 corresponden a botones 1, 2, 3
        button = buttons[i - 1]
        button.click()

        # Extrae la tabla correspondiente
        try:
            # Esperar hasta que se cargue la tabla correspondiente y seleccionar el texto
            table = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.tabla-evolucion-content")
                )
            )

            # Seleccionar el header de la tabla
            header_row = table.find_elements(By.CSS_SELECTOR, "tbody > tr > th")
            header = [unidecode(td.text.lower()).replace(" ", "_") for td in header_row]

            # Seleccionar el contenido de la tabla
            rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")

            # Itera sobre cada fila ignorando el primer registro que es el header
            rows_data = []
            for row in rows[1:]:
                # Localiza todas las columnas (celdas) de la fila
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                row_data = []

                try:
                    cell_datetime = datetime.strptime(cells[0].text, "%Y-%m-%d %H:%M")
                    row_data.append(canary_timezone.localize(cell_datetime))

                    for cell in cells[1:]:
                        # Si la celda está vacía, añade un 0; si no, añade su texto
                        cell_text = cell.text
                        row_data.append(cell_text if cell_text else "0")

                    # Agregar la lista de datos a la lista general de datos. Cada lista representa una fila
                    rows_data.append(row_data)
                except IndexError:
                    print(
                        "Error al intentar seleccionar el indice... saltando fila actual"
                    )
                    continue

            # Asume que la primera fila son los headers
            df = pd.DataFrame(rows_data, columns=header).dropna().set_index("hora")

            # # Guarda el DataFrame en el diccionario y forzar a que sean todas las columnas de tipo float
            dataframes[name] = df.astype(float)
        except Exception as e:
            print(f"Error extrayendo la tabla {i}: {e}")
finally:
    # Cierra el navegador
    driver.quit()
