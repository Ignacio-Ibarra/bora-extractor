import pytest
from pathlib import Path
from bora_extractor.metadata import (
    load_json_file,
    select_json_file,
    select_json_by_fields,
    parse_aviso_url,
    formatear_fecha,
    get_sub_dict,
    build_json_metadata,
    build_url_metadata,
)
from bora_extractor.schema import (
    validate_json_metadata,
    validate_url_metadata,
    JsonMetadata,
    UrlMetadata,
)


class TestMetadataLoadingFunctions:
    """Tests para las funciones de carga y selección de archivos JSON."""

    def test_load_json_file(self):
        """Verifica que se puede cargar un archivo JSON correctamente."""
        example_dir = Path(__file__).parent.parent / "example_data"
        json_path = example_dir / "links_CONSTITUCION SAS_20260201_20260228.json"
        
        data = load_json_file(json_path)
        
        assert isinstance(data, dict)
        assert "links" in data
        assert "rubro" in data
        assert "fecha_desde" in data
        assert "fecha_hasta" in data
        assert isinstance(data["links"], list)
        assert len(data["links"]) > 0

    def test_select_json_file_with_pattern(self):
        """Verifica que select_json_file lanza error si hay múltiples coincidencias."""
        example_dir = Path(__file__).parent.parent / "example_data"
        
        # Hay 2 archivos que coinciden con este patrón, por lo que debe lanzar error
        with pytest.raises(ValueError, match="Multiple JSON files found"):
            select_json_file(example_dir, pattern="links_CONSTITUCION*")

    def test_select_json_file_no_pattern(self):
        """Verifica que select_json_file lanza error sin patrón si hay múltiples archivos."""
        example_dir = Path(__file__).parent.parent / "example_data"
        
        # Hay 3 archivos en example_data, por lo que debe lanzar error sin patrón específico
        with pytest.raises(ValueError, match="Multiple JSON files found"):
            select_json_file(example_dir)

    def test_select_json_file_raises_on_invalid_dir(self):
        """Verifica que select_json_file lanza error si el directorio no existe."""
        invalid_dir = Path("/nonexistent/directory")
        
        with pytest.raises(ValueError, match="is not a valid directory"):
            select_json_file(invalid_dir)

    def test_select_json_file_raises_on_no_matches(self):
        """Verifica que select_json_file lanza error si no encuentra archivos."""
        example_dir = Path(__file__).parent.parent / "example_data"
        
        with pytest.raises(ValueError, match="No JSON files found"):
            select_json_file(example_dir, pattern="nonexistent_*.json")

    def test_select_json_by_fields(self):
        """Verifica que select_json_by_fields encuentra el archivo correcto."""
        example_dir = Path(__file__).parent.parent / "example_data"
        
        result = select_json_by_fields(
            example_dir,
            rubro="CONSTITUCION SAS",
            fecha_desde="2026-02-01",
            fecha_hasta="2026-02-28",
        )
        
        assert result is not None
        assert result.exists()
        assert "CONSTITUCION SAS" in result.name
        assert "20260201" in result.name
        assert "20260228" in result.name


class TestUrlParsing:
    """Tests para las funciones de parseo de URLs BORA."""

    def test_parse_aviso_url_valid(self):
        """Verifica que parse_aviso_url extrae correctamente id y fecha."""
        url = "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202?busqueda=1"
        
        result = parse_aviso_url(url, "segunda")
        
        assert result["id_aviso"] == "A1464579"
        assert result["fecha_aviso"] == "02/02/2026"
        assert result["url"] == url

    def test_parse_aviso_url_different_seccion(self):
        """Verifica que parse_aviso_url funciona con diferentes secciones."""
        url = "https://www.boletinoficial.gob.ar/detalleAviso/primera/B1234567/20260215"
        
        result = parse_aviso_url(url, "primera")
        
        assert result["id_aviso"] == "B1234567"
        assert result["fecha_aviso"] == "15/02/2026"

    def test_parse_aviso_url_raises_on_missing_seccion(self):
        """Verifica que parse_aviso_url lanza error si no encuentra la sección."""
        url = "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202"
        
        with pytest.raises(ValueError, match="no está en la URL"):
            parse_aviso_url(url, "tercera")


class TestDateFormatting:
    """Tests para la función de formateo de fechas."""

    def test_formatear_fecha_basic(self):
        """Verifica que formatear_fecha convierte el formato correctamente."""
        result = formatear_fecha("01/02/2026", "%d/%m/%Y", "%Y%m%d")
        
        assert result == "20260201"

    def test_formatear_fecha_reverse(self):
        """Verifica que formatear_fecha puede hacer conversiones inversas."""
        result = formatear_fecha("20260202", "%Y%m%d", "%d/%m/%Y")
        
        assert result == "02/02/2026"

    def test_formatear_fecha_different_formats(self):
        """Verifica que formatear_fecha funciona con diferentes formatos."""
        result = formatear_fecha("2026-02-01", "%Y-%m-%d", "%d/%m/%Y")
        
        assert result == "01/02/2026"


class TestDictOperations:
    """Tests para operaciones con diccionarios."""

    def test_get_sub_dict_extracts_existing_keys(self):
        """Verifica que get_sub_dict extrae las claves requeridas."""
        data = {"a": 1, "b": 2, "c": 3, "d": 4}
        keys = ["a", "c", "e"]
        
        result = get_sub_dict(data, keys)
        
        assert result == {"a": 1, "c": 3}
        assert "b" not in result
        assert "d" not in result
        assert "e" not in result

    def test_get_sub_dict_empty_keys(self):
        """Verifica que get_sub_dict maneja lista vacía."""
        data = {"a": 1, "b": 2}
        
        result = get_sub_dict(data, [])
        
        assert result == {}

    def test_get_sub_dict_missing_keys(self):
        """Verifica que get_sub_dict ignora claves no presentes."""
        data = {"a": 1}
        keys = ["a", "b", "c"]
        
        result = get_sub_dict(data, keys)
        
        assert result == {"a": 1}


class TestSchemaValidation:
    """Tests para la validación de esquemas Pydantic."""

    def test_validate_json_metadata_valid(self):
        """Verifica que validate_json_metadata acepta datos válidos."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            "fecha_hasta": "28/02/2026",
        }
        
        result = validate_json_metadata(data)
        
        assert isinstance(result, JsonMetadata)
        assert result.rubro == "CONSTITUCION SAS"
        assert result.fecha_desde == "01/02/2026"
        assert result.fecha_hasta == "28/02/2026"

    def test_validate_json_metadata_missing_field(self):
        """Verifica que validate_json_metadata rechaza datos incompletos."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            # falta fecha_hasta
        }
        
        with pytest.raises(ValueError, match="Invalid JSON metadata"):
            validate_json_metadata(data)

    def test_validate_url_metadata_valid(self):
        """Verifica que validate_url_metadata acepta datos válidos."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            "fecha_aviso": "02/02/2026",
        }
        
        result = validate_url_metadata(data)
        
        assert isinstance(result, UrlMetadata)
        assert result.id_aviso == "A1464579"

    def test_validate_url_metadata_missing_field(self):
        """Verifica que validate_url_metadata rechaza datos incompletos."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            # falta fecha_aviso
        }
        
        with pytest.raises(ValueError, match="Invalid URL metadata"):
            validate_url_metadata(data)


class TestBuildMetadataFunctions:
    """Tests para las funciones que construyen y validan metadata."""

    def test_build_json_metadata(self):
        """Verifica que build_json_metadata construye y valida correctamente."""
        data = {
            "rubro": "CONSTITUCION SAS",
            "fecha_desde": "01/02/2026",
            "fecha_hasta": "28/02/2026",
        }
        
        result = build_json_metadata(data)
        
        assert isinstance(result, dict)
        assert result["rubro"] == "CONSTITUCION SAS"
        assert result["fecha_desde"] == "01/02/2026"

    def test_build_url_metadata(self):
        """Verifica que build_url_metadata construye y valida correctamente."""
        data = {
            "url": "https://www.boletinoficial.gob.ar/detalleAviso/segunda/A1464579/20260202",
            "id_aviso": "A1464579",
            "fecha_aviso": "02/02/2026",
        }
        
        result = build_url_metadata(data)
        
        assert isinstance(result, dict)
        assert result["id_aviso"] == "A1464579"


class TestIntegration:
    """Tests de integración que combinan múltiples funciones."""

    def test_load_and_parse_example_json(self):
        """Verifica que se puede cargar un JSON de ejemplo y acceder a sus datos."""
        example_dir = Path(__file__).parent.parent / "example_data"
        json_path = select_json_by_fields(
            example_dir,
            rubro="CONSTITUCION SAS",
            fecha_desde="2026-02-01",
            fecha_hasta="2026-02-28",
        )
        
        data = load_json_file(json_path)
        
        # Validar estructura del JSON cargado
        assert "links" in data
        assert len(data["links"]) > 0
        
        # Parsear la primera URL
        first_url = data["links"][0]
        parsed = parse_aviso_url(first_url, "segunda")
        
        assert parsed["id_aviso"].startswith("A")
        assert len(parsed["fecha_aviso"]) == 10  # dd/mm/YYYY

    def test_multiple_example_files_exist(self):
        """Verifica que existen múltiples archivos de ejemplo."""
        example_dir = Path(__file__).parent.parent / "example_data"
        json_files = list(example_dir.glob("*.json"))
        
        assert len(json_files) >= 3, "Se esperan al menos 3 archivos JSON de ejemplo"
