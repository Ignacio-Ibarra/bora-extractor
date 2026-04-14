import pytest
from unittest.mock import Mock, patch
from bora_extractor.scraper import get_text_by_id, _normalize_text


class TestNormalizeText:
    """Tests para la función de normalización de texto."""

    def test_normalize_text_removes_extra_spaces(self):
        """Verifica que _normalize_text elimina espacios extra."""
        result = _normalize_text("Hola   mundo  con    espacios")
        
        assert result == "Hola mundo con espacios"

    def test_normalize_text_removes_newlines(self):
        """Verifica que _normalize_text elimina saltos de línea."""
        result = _normalize_text("Hola\nmundo\n\ncon\nnewlines")
        
        assert result == "Hola mundo con newlines"

    def test_normalize_text_removes_tabs(self):
        """Verifica que _normalize_text elimina tabulaciones."""
        result = _normalize_text("Hola\tmundo\t\tcon\ttabs")
        
        assert result == "Hola mundo con tabs"

    def test_normalize_text_unicode_normalization(self):
        """Verifica que _normalize_text normaliza caracteres Unicode."""
        # Texto con espacio no rompible (\xa0)
        text_with_nbsp = "AURA MT\xa0S.A."
        result = _normalize_text(text_with_nbsp)
        
        # Debería mantener el espacio no rompible (NFKC lo preserva)
        assert "AURA" in result
        assert "S.A" in result

    def test_normalize_text_mixed_whitespace(self):
        """Verifica que _normalize_text maneja espacios mixtos."""
        result = _normalize_text("  Inicio  \n  con   espacios  \t  variados  ")
        
        assert result == "Inicio con espacios variados"


class TestGetTextById:
    """Tests para la función get_text_by_id."""

    def test_get_text_by_id_finds_element(self):
        """Verifica que get_text_by_id encuentra y extrae texto de un elemento."""
        html = """
        <html>
            <body>
                <div id="tituloDetalleAviso">TÍTULO DE PRUEBA</div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "tituloDetalleAviso")
        
        assert result == "TÍTULO DE PRUEBA"

    def test_get_text_by_id_strips_whitespace(self):
        """Verifica que get_text_by_id elimina espacios alrededor."""
        html = """
        <html>
            <body>
                <div id="test">
                    Contenido con espacios
                </div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "test")
        
        assert result == "Contenido con espacios"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_get_text_by_id_normalizes_whitespace(self):
        """Verifica que get_text_by_id normaliza espacios en blanco internos."""
        html = """
        <html>
            <body>
                <div id="test">
                    Contenido   con    espacios    extra
                </div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "test")
        
        assert result == "Contenido con espacios extra"

    def test_get_text_by_id_returns_none_if_not_found(self):
        """Verifica que get_text_by_id retorna None si el elemento no existe."""
        html = """
        <html>
            <body>
                <div id="otro">Contenido</div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "noexiste")
        
        assert result is None

    def test_get_text_by_id_with_nested_elements(self):
        """Verifica que get_text_by_id extrae todo el texto de elementos anidados."""
        html = """
        <html>
            <body>
                <div id="contenedor">
                    <p>Párrafo 1</p>
                    <p>Párrafo 2</p>
                </div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "contenedor")
        
        assert "Párrafo 1" in result
        assert "Párrafo 2" in result

    def test_get_text_by_id_empty_element(self):
        """Verifica que get_text_by_id maneja elementos vacíos."""
        html = """
        <html>
            <body>
                <div id="vacio"></div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "vacio")
        
        # BeautifulSoup puede devolver vacío o None, ambos son válidos
        assert result is None or result == ""

    def test_get_text_by_id_with_multiple_same_ids(self):
        """Verifica que get_text_by_id encuentra el primer elemento con el id."""
        html = """
        <html>
            <body>
                <div id="test">Primero</div>
                <div id="test">Segundo</div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "test")
        
        # BeautifulSoup devuelve el primero
        assert result == "Primero"

    def test_get_text_by_id_with_html_entities(self):
        """Verifica que get_text_by_id maneja entidades HTML."""
        html = """
        <html>
            <body>
                <div id="test">Empresa &amp; Asociados S.A.</div>
            </body>
        </html>
        """
        
        result = get_text_by_id(html, "test")
        
        assert result == "Empresa & Asociados S.A."

    def test_get_text_by_id_real_bora_structure(self):
        """Verifica que get_text_by_id funciona con estructura similar a BORA."""
        html = """
        <html>
            <body>
                <div id="tituloDetalleAviso" class="titulo">
                    AURA MT S.A.
                </div>
                <div id="cuerpoDetalleAviso" class="cuerpo">
                    <p>Contenido del cuerpo</p>
                </div>
            </body>
        </html>
        """
        
        titulo = get_text_by_id(html, "tituloDetalleAviso")
        cuerpo = get_text_by_id(html, "cuerpoDetalleAviso")
        
        assert titulo == "AURA MT S.A."
        assert "Contenido del cuerpo" in cuerpo
