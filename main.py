from bora_extractor.metadata import MetadataGenerator, load_json_file, select_json_by_fields, build_result_metadata, formatear_fecha
from bora_extractor.config import JSON_METADATA_KEYS, BORA_SECCION, JSON_DIR, DEFAULT_ID_FIELDS
from bora_extractor.reqs import set_proxy_config
import argparse
from pathlib import Path
from typing import Callable
from tqdm import tqdm
import json
import time




metadata_generator : Callable = lambda json_data, link: MetadataGenerator(json_data, 
                                                                        link=link, 
                                                                        seccion=BORA_SECCION, 
                                                                        json_metadata_keys=JSON_METADATA_KEYS,
                                                                        default_id_fields=DEFAULT_ID_FIELDS)

json_dir = Path(JSON_DIR)


def main():
    parser = argparse.ArgumentParser(description="Extrae textos de avisos del BORA según rubro y fechas de búsqueda")
    parser.add_argument("--start-date", required=True, help="Fecha de inicio en formato dd/mm/YYYY")
    parser.add_argument("--end-date", required=True, help="Fecha de fin en formato dd/mm/YYYY")
    parser.add_argument("--rubro", required=True, help="Rubro a buscar")
    parser.add_argument("--save", default=False, action="store_true", help="Si se especifica, guarda el resultado en un archivo JSON")

    args = parser.parse_args()

    fecha_desde: str = formatear_fecha(args.start_date, "%d/%m/%Y", "%Y%m%d")
    fecha_hasta: str = formatear_fecha(args.end_date, "%d/%m/%Y", "%Y%m%d")
    rubro: str = args.rubro

    result = [] 
    set_proxy_config()
    json_path = select_json_by_fields(dir=json_dir, rubro=rubro, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta) # Tiene un raise
    
    json_data = load_json_file(json_path)
    links = json_data.get('links', [])
    
    if not links:
        print(f"No se encontraron links en el JSON para rubro={rubro}, fecha_desde={fecha_desde}, fecha_hasta={fecha_hasta}")
        
    for link in tqdm(links, desc="Procesando avisos"):
        try:
            document_metadata = metadata_generator(json_data, link=link).generate_document_metadata()
            result.append(document_metadata)
            time.sleep(1)  # Para evitar sobrecargar el servidor con demasiadas solicitudes rápidas
        except Exception as e:
            print(f"Error procesando {link}: {e}")
    
    if args.save:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"result_{rubro}_{fecha_desde}_{fecha_hasta}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f)
        print(f"Resultados guardados en {output_path}")

    return build_result_metadata({"result": result})
    
    
    


if __name__ == "__main__":
    result_metadata = main()
    print("Result Metadata:", result_metadata)