"""
"""

from typing import Dict, List

import pandas as pd
from unidecode import unidecode


def build_dataframe(data_dict: Dict[str, List]) -> pd.DataFrame:
    # Generar DataFrame con los datos extraidos
    df = pd.DataFrame(
        data_dict["data"],
        columns=data_dict["headers"],
    )
    # Eliminar espacios y caracteres especiales en los encabezados
    df.columns = [unidecode(col.replace(" ", "_")).lower() for col in df.columns]
    # Convertir columna hora en indice y situar la zona horaria en canarias
    df.set_index("hora", inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize("WET")

    # Convertir todas las columnas a float
    df = df.astype(float)

    return df
