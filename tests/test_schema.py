import pytest
from bora_extractor.schema import (
    JsonMetadata,
    UrlMetadata,
    DocumentMetadata,
    Result,
    validate_json_metadata,
    validate_url_metadata,
    validate_document_metadata,
    validate_result_metadata,
)


class TestJsonMetadata:
    """Tests para el modelo JsonMetadata."""

    def test_json_metadata_creation(self):
        """Verifica que JsonMetadata se crea correctamente con datos válidos."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            "fecha_hasta": "28/02/2026",
        }
        
        metadata = JsonMetadata(**data)
        
        assert metadata.rubro == "CONSTITUCION SAS"
        assert metadata.fecha_desde == "01/02/2026"
        assert metadata.fecha_hasta == "28/02/2026"

    def test_json_metadata_model_dump(self):
        """Verifica que JsonMetadata.model_dump() devuelve un diccionario."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            "fecha_hasta": "28/02/2026",
        }
        metadata = JsonMetadata(**data)
        
        dumped = metadata.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["rubro"] == "CONSTITUCION SAS"

    def test_json_metadata_missing_required_field(self):
        """Verifica que JsonMetadata lanza error si falta campo requerido."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            # falta fecha_hasta
        }
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            JsonMetadata(**data)


class TestUrlMetadata:
    """Tests para el modelo UrlMetadata."""

    def test_url_metadata_creation(self):
        """Verifica que UrlMetadata se crea correctamente."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            "fecha_aviso": "02/02/2026",
        }
        
        metadata = UrlMetadata(**data)
        
        assert metadata.url == data["url"]
        assert metadata.id_aviso == "A1464579"
        assert metadata.fecha_aviso == "02/02/2026"

    def test_url_metadata_model_dump(self):
        """Verifica que UrlMetadata.model_dump() devuelve un diccionario."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            "fecha_aviso": "02/02/2026",
        }
        metadata = UrlMetadata(**data)
        
        dumped = metadata.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["id_aviso"] == "A1464579"

    def test_url_metadata_missing_field(self):
        """Verifica que UrlMetadata lanza error si falta un campo."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            # falta fecha_aviso
        }
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            UrlMetadata(**data)


class TestDocumentMetadata:
    """Tests para el modelo DocumentMetadata."""

    def test_document_metadata_creation(self):
        """Verifica que DocumentMetadata se crea correctamente con datos válidos."""
        json_meta = JsonMetadata(
            rubro="CONSTITUCION SAS",
            fecha_desde="01/02/2026",
            fecha_hasta="28/02/2026",
        )
        url_meta = UrlMetadata(
            url="https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            id_aviso="A1464579",
            fecha_aviso="02/02/2026",
        )
        
        doc_meta = DocumentMetadata(
            titulo_aviso="AURA MT S.A.",
            cuerpo_aviso="Contenido del aviso",
            url_metadata=url_meta,
            json_metadata=json_meta,
        )
        
        assert doc_meta.titulo_aviso == "AURA MT S.A."
        assert doc_meta.cuerpo_aviso == "Contenido del aviso"
        assert doc_meta.url_metadata.id_aviso == "A1464579"
        assert doc_meta.json_metadata.rubro == "CONSTITUCION SAS"

    def test_document_metadata_model_dump(self):
        """Verifica que DocumentMetadata.model_dump() devuelve estructura correcta."""
        json_meta = JsonMetadata(
            rubro="CONSTITUCION SAS",
            fecha_desde="01/02/2026",
            fecha_hasta="28/02/2026",
        )
        url_meta = UrlMetadata(
            url="https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            id_aviso="A1464579",
            fecha_aviso="02/02/2026",
        )
        doc_meta = DocumentMetadata(
            titulo_aviso="AURA MT S.A.",
            cuerpo_aviso="Contenido del aviso",
            url_metadata=url_meta,
            json_metadata=json_meta,
        )
        
        dumped = doc_meta.model_dump()
        
        assert isinstance(dumped, dict)
        assert "titulo_aviso" in dumped
        assert "url_metadata" in dumped
        assert "json_metadata" in dumped
        assert isinstance(dumped["url_metadata"], dict)
        assert isinstance(dumped["json_metadata"], dict)


class TestResult:
    """Tests para el modelo Result."""

    def test_result_creation(self):
        """Verifica que Result se crea correctamente."""
        json_meta = JsonMetadata(
            rubro="CONSTITUCION SAS",
            fecha_desde="01/02/2026",
            fecha_hasta="28/02/2026",
        )
        url_meta = UrlMetadata(
            url="https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            id_aviso="A1464579",
            fecha_aviso="02/02/2026",
        )
        doc_meta = DocumentMetadata(
            titulo_aviso="AURA MT S.A.",
            cuerpo_aviso="Contenido",
            url_metadata=url_meta,
            json_metadata=json_meta,
        )
        
        result = Result(result=[doc_meta])
        
        assert len(result.result) == 1
        assert result.result[0].titulo_aviso == "AURA MT S.A."

    def test_result_multiple_documents(self):
        """Verifica que Result puede contener múltiples documentos."""
        json_meta = JsonMetadata(
            rubro="TEST",
            fecha_desde="01/02/2026",
            fecha_hasta="28/02/2026",
        )
        url_meta = UrlMetadata(
            url="https://example.com",
            id_aviso="A1",
            fecha_aviso="01/02/2026",
        )
        
        docs = [
            DocumentMetadata(
                titulo_aviso=f"TITULO {i}",
                cuerpo_aviso=f"Contenido {i}",
                url_metadata=url_meta,
                json_metadata=json_meta,
            )
            for i in range(3)
        ]
        
        result = Result(result=docs)
        
        assert len(result.result) == 3
        assert result.result[0].titulo_aviso == "TITULO 0"
        assert result.result[2].titulo_aviso == "TITULO 2"


class TestValidationFunctions:
    """Tests para las funciones de validación."""

    def test_validate_json_metadata_success(self):
        """Verifica que validate_json_metadata valida correctamente."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            "fecha_hasta": "28/02/2026",
        }
        
        result = validate_json_metadata(data)
        
        assert isinstance(result, JsonMetadata)

    def test_validate_json_metadata_invalid_data(self):
        """Verifica que validate_json_metadata lanza error con datos inválidos."""
        data = {
            "rubro": "CONSTITUCION SAS",
            # faltan campos requeridos
        }
        
        with pytest.raises(ValueError, match="Invalid JSON metadata"):
            validate_json_metadata(data)

    def test_validate_url_metadata_success(self):
        """Verifica que validate_url_metadata valida correctamente."""
        data = {
            "url": "https://example.com",
            "id_aviso": "A1464579",
            "fecha_aviso": "02/02/2026",
        }
        
        result = validate_url_metadata(data)
        
        assert isinstance(result, UrlMetadata)

    def test_validate_url_metadata_invalid_data(self):
        """Verifica que validate_url_metadata lanza error con datos inválidos."""
        data = {
            "url": "https://example.com",
            # faltan campos requeridos
        }
        
        with pytest.raises(ValueError, match="Invalid URL metadata"):
            validate_url_metadata(data)

    def test_validate_document_metadata_success(self):
        """Verifica que validate_document_metadata valida correctamente."""
        data = {
            "titulo_aviso": "TITULO",
            "cuerpo_aviso": "CUERPO",
            "url_metadata": {
                "url": "https://example.com",
                "id_aviso": "A1",
                "fecha_aviso": "01/02/2026",
            },
            "json_metadata": {
                "rubro": "TEST",
                "fecha_desde": "01/02/2026",
                "fecha_hasta": "28/02/2026",
            },
        }
        
        result = validate_document_metadata(data)
        
        assert isinstance(result, DocumentMetadata)

    def test_validate_result_metadata_success(self):
        """Verifica que validate_result_metadata valida correctamente."""
        data = {
            "result": [
                {
                    "titulo_aviso": "TITULO",
                    "cuerpo_aviso": "CUERPO",
                    "url_metadata": {
                        "url": "https://example.com",
                        "id_aviso": "A1",
                        "fecha_aviso": "01/02/2026",
                    },
                    "json_metadata": {
                        "rubro": "TEST",
                        "fecha_desde": "01/02/2026",
                        "fecha_hasta": "28/02/2026",
                    },
                }
            ]
        }
        
        result = validate_result_metadata(data)
        
        assert isinstance(result, Result)
        assert len(result.result) == 1
