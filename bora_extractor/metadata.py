# Maneja input (json) y output (metadata + texto extraído) de la extracción.
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse
from bora_extractor.schema import validate_document_metadata, validate_json_metadata, validate_url_metadata, validate_result_metadata
from bora_extractor.scraper import get_text_by_id
from bora_extractor.reqs import make_request
from bora_extractor.config import DEFAULT_ID_FIELDS
from datetime import datetime


def formatear_fecha(fecha_str: str, input_format: str, output_format: str) -> str:
    return datetime.strptime(fecha_str, input_format).strftime(output_format)

def load_json_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def select_json_file(dir: Path, pattern: Optional[str] = None) -> Optional[Path]:
    if not dir.is_dir():
        raise ValueError(f"Directory {dir} is not a valid directory")
    
    json_files = list(dir.glob(pattern or "*.json"))
    if not json_files:
        raise ValueError(f"No JSON files found in directory {dir} with pattern {pattern or '*.json'}")
    result_json_file = json_files[0]
    if len(json_files) == 1:
        return result_json_file
    else:
        raise ValueError(f"Multiple JSON files found for pattern {pattern}: {[str(f) for f in json_files]}. Please refine your search.")

def select_json_by_fields(dir: Path, rubro: str, fecha_desde: str, fecha_hasta: str) -> Optional[Path]:
    pattern = f"*{rubro}_{fecha_desde.replace('-', '')}_{fecha_hasta.replace('-', '')}.json" 
    return select_json_file(dir, pattern=pattern)


def build_json_metadata(json_metadata: dict) -> dict:
    return validate_json_metadata(json_metadata).model_dump()

def build_document_metadata(document_metadata: dict) -> dict:
    return validate_document_metadata(document_metadata).model_dump()

def build_url_metadata(url_metadata: dict) -> dict:
    return validate_url_metadata(url_metadata).model_dump()

def build_result_metadata(result_metadata: dict) -> dict:
    return validate_result_metadata(result_metadata).model_dump()

def get_sub_dict(data: dict, keys: list) -> dict:
    return {key: data[key] for key in keys if key in data}

def collect_links_from_json(json_data: dict, link_key: str) -> list:
    return [link for link in json_data.get(link_key, []) if isinstance(link, str)]

def parse_aviso_url(url, seccion):
    
    # Nos quedamos solo con el path (sin query params)
    path = urlparse(url).path
    parts = path.strip("/").split("/")
    
    try:
        idx = parts.index(seccion)
    except ValueError:
        raise ValueError(f"La sección '{seccion}' no está en la URL")
    
    id_aviso = parts[idx + 1]
    fecha_aviso = formatear_fecha(parts[idx + 2], "%Y%m%d", "%d/%m/%Y")
    
    return {
        "url": url,
        "id_aviso": id_aviso,
        "fecha_aviso": fecha_aviso
    }



class MetadataGenerator:
    json_data: Dict[str, Any]
    link: str
    seccion:str
    json_metadata_keys : List[str]


    def __init__(self, json_data: Dict[str, Any], link: str, seccion: str, json_metadata_keys: List[str], div_id_fields: List[str]) -> None:
        self.json_data = json_data
        self.link = link
        self.seccion = seccion
        self.json_metadata_keys = json_metadata_keys
        self.div_id_fields = div_id_fields

    def generate_json_metadata(self) -> dict:
        json_metadata = get_sub_dict(self.json_data, self.json_metadata_keys)
        json_metadata["rubro"] = json_metadata['rubro'][0]
        return build_json_metadata(json_metadata)
    
    def generate_url_metadata(self) -> dict:
        url_metadata = parse_aviso_url(self.link, self.seccion)
        return build_url_metadata(url_metadata)
    
    def generate_document_metadata(self) -> dict:
        
        html = make_request(self.link)
        
        titulo_aviso = get_text_by_id(html, self.div_id_fields[0])
        cuerpo_aviso = get_text_by_id(html, self.div_id_fields[1])

        document_metadata = {
            "titulo_aviso": titulo_aviso,
            "cuerpo_aviso": cuerpo_aviso,
            "url_metadata": self.generate_url_metadata(),
            "json_metadata": self.generate_json_metadata()
        }
        return build_document_metadata(document_metadata)

        

        



if __name__ == "__main__":
    rubro = "CONSTITUCION SA"
    fecha_desde = "2026-02-01"
    fecha_hasta = "2026-02-28"
    sample_json_path = select_json_by_fields(rubro, fecha_desde, fecha_hasta)
    if sample_json_path:
        json_data = load_json_file(sample_json_path)
        link = json_data.get('links')[6] # Ejemplo
        metadata_generator = MetadataGenerator(json_data, link=link, seccion="segunda")
        document_metadata = metadata_generator.generate_document_metadata()
        # print("JSON Metadata:", json_metadata)
        print("Document Metadata:", document_metadata)
    else:
        print(f"No JSON file found for rubro={rubro}, fecha_desde={fecha_desde}, fecha_hasta={fecha_hasta}")
