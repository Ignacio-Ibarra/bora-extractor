from bora_extractor.metadata import MetadataGenerator
from bora_extractor.config import JSON_METADATA_KEYS, BORA_SECCION, DEFAULT_ID_FIELDS

def extract_document(link: str, input_metadata: dict) -> dict:
    """
    Extrae metadata de un link del BORA.
    
    Args:
        link: URL del aviso
        input_metadata: dict con las claves 'rubro', 'fecha_desde', 'fecha_hasta'
    
    Returns:
        dict con titulo_aviso, cuerpo_aviso, fecha, etc.
    """
    metadata_gen = MetadataGenerator(
        input_metadata,
        link=link,
        seccion=BORA_SECCION,
        json_metadata_keys=JSON_METADATA_KEYS,
        div_id_fields=DEFAULT_ID_FIELDS
    )
    return metadata_gen.generate_document_metadata()