import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }

DEFAULT_ID_FIELDS = ['tituloDetalleAviso', 'cuerpoDetalleAviso']

JSON_DIR = os.getenv("JSON_DIR", "example_data/")

JSON_METADATA_KEYS = [
    "rubro",
    "fecha_desde",
    "fecha_hasta"
]

BORA_SECCION = "segunda"
