from typing import Any, Dict, List
from pydantic import BaseModel


class JsonMetadata(BaseModel):
    rubro: str
    fecha_desde: str
    fecha_hasta: str

class UrlMetadata(BaseModel):
    url: str
    id_aviso: str
    fecha_aviso: str

class DocumentMetadata(BaseModel):
    titulo_aviso: str
    cuerpo_aviso: str
    url_metadata: UrlMetadata
    json_metadata : JsonMetadata

class Result(BaseModel):
    result: List[DocumentMetadata]


def validate_json_metadata(data: Dict[str, Any]) -> JsonMetadata:
    try:
        return JsonMetadata.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid JSON metadata: {e}")
    
def validate_url_metadata(data: Dict[str, Any]) -> UrlMetadata:
    try:
        return UrlMetadata.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid URL metadata: {e}")

def validate_document_metadata(data: Dict[str, Any]) -> DocumentMetadata:
    try:
        return DocumentMetadata.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid document metadata: {e}")
    
def validate_result_metadata(data: Dict[str, Any]) -> Result:
    try:
        return Result.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid result metadata: {e}")