# bora-extractor

Extractor modular para procesar avisos publicados en el Boletín Oficial de la República Argentina (BORA). El paquete descarga contenido HTML de publicaciones, extrae texto estructurado, normaliza caracteres Unicode y valida toda la información mediante esquemas Pydantic robustos. Este paquete utiliza como input los archivos JSON que se generan mediante el paquete [`bora_wrapper`](https://github.com/Ignacio-ibarra/bora_wrapper). 

## Acerca de BORA

El Boletín Oficial de la República Argentina es el medio de publicación oficial del Estado Argentino. Se organiza en diferentes secciones según el tipo de publicación. Este paquete se especializa en procesar avisos de la segunda sección, que contiene publicaciones de inscripciones, asociaciones y otros avisos comerciales.

## Características principales

- **Descarga segura con proxy**: Soporte integrado para configuración de proxy HTTP/HTTPS mediante variables de entorno, permitiendo acceso desde redes corporativas.
- **Extracción flexible de texto**: Utiliza XPath y BeautifulSoup para extraer contenido desde elementos HTML específicos, con fallback a parseo genérico.
- **Normalización Unicode**: Convierte automáticamente caracteres especiales y espacios no rompibles a formas canónicas usando NFKC, asegurando consistencia en textos del BORA.
- **Validación de esquemas con Pydantic**: Todos los datos (metadata JSON, URLs, documentos extraídos) se validan contra esquemas estructurados, garantizando integridad referencial.
- **Procesamiento por lotes**: Lee archivos JSON con enlaces desde `bora_wrapper`, procesa múltiples públicaciones en paralelo y structure los resultados.
- **Metadata estructurada**: Preserva información de origen (rubro, fechas, ID de aviso) junto con contenido extraído en JSON válido.

## Estructura del paquete

```
bora_extractor/
├── __init__.py
├── __main__.py              # Punto de entrada CLI
├── config.py                # Configuración (headers, campos, rutas)
├── metadata.py              # Carga JSON, parseo de URLs, generación de metadata
├── scraper.py               # Extracción de texto con normalización Unicode
├── reqs.py                  # Manejo de requests HTTP y proxy
├── schema.py                # Modelos Pydantic para validación
└── extraction.py            # Extracción de contenido desde HTML (backup)

tests/
├── conftest.py              # Configuración de fixtures pytest
├── test_metadata.py         # Tests de carga, selección y parseo
├── test_schema.py           # Tests de validación Pydantic
└── test_scraper.py          # Tests de extracción de texto

example_data/                # Archivos JSON de ejemplo para tests
├── links_CONSTITUCION SAS_20260201_20260228.json
├── links_CONSTITUCION SA_20260201_20260228.json
└── links_CONTRATO SRL_20260201_20260228.json
```

## Instalación

### Requisitos
- Python 3.9+
- `uv` (gestor de paquetes, recomendado) o `pip`

### Setup básico

```bash
# Clonar o descargar el repositorio
cd bora_extractor

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# o
.venv\Scripts\activate        # Windows

# Instalar dependencias
uv sync
# o
pip install -e .
```

### Configuración de proxy (opcional)

Para ambientes con proxy corporativo, crea un archivo `.env` en la raíz del proyecto:

```bash
PROXY_HOST=proxy.empresa.com
PROXY_PORT=8080
PROXY_USER=usuario
PROXY_PASS=contraseña

JSON_DIR=data/                # Directorio donde se buscan JSONs de entrada
```

Si no defines proxy, el paquete usa conexión directa.

## Uso

### CLI

Procesar avisos de un rubro en un rango de fechas:

```bash
uv run bora_extractor --start-date 01/02/2026 --end-date 28/02/2026 --rubro "CONSTITUCION SAS"
```

Busca automáticamente el archivo `links_CONSTITUCION SAS_20260201_20260228.json` en `JSON_DIR` y procesa todos los enlaces.

### Como librería Python

```python
from bora_extractor.metadata import MetadataGenerator, load_json_file, select_json_by_fields
from bora_extractor.config import JSON_METADATA_KEYS, BORA_SECCION, DEFAULT_ID_FIELDS
from pathlib import Path

# Cargar JSON con enlaces
json_path = select_json_by_fields(
    dir=Path("data/"),
    rubro="CONSTITUCION SAS",
    fecha_desde="2026-02-01",
    fecha_hasta="2026-02-28"
)
json_data = load_json_file(json_path)

# Procesar primer enlace
link = json_data["links"][0]
generator = MetadataGenerator(
    json_data=json_data,
    link=link,
    seccion="segunda",
    json_metadata_keys=JSON_METADATA_KEYS,
    div_id_fields=DEFAULT_ID_FIELDS
)

# Extraer metadata y contenido
result = generator.generate_document_metadata()
print(result)
```

## Validación con Pydantic

Todos los datos se validan contra esquemas estructurados:

- **JsonMetadata**: Rubro, fechas de búsqueda (del JSON original)
- **UrlMetadata**: URL, ID de aviso, fecha de publicación (extraído de la URL)
- **DocumentMetadata**: Título, cuerpo, metadata de URL y JSON
- **Result**: Lista de documentos extraídos

Los esquemas garantizan que todos los campos requeridos están presentes y con tipos correctos. Si los datos son inválidos, se lanza `ValueError` descriptivo.

## Testing

Ejecutar todos los tests:

```bash
pytest -v
```

Tests disponibles:
- **test_metadata.py**: Carga de JSONs, selección por patrón/campos, parseo de URLs BORA
- **test_schema.py**: Validación de todos los modelos Pydantic
- **test_scraper.py**: Extracción y normalización de texto HTML

Los tests usan automáticamente los archivos en `example_data/` sin configuración adicional.

## Flujo de datos

1. **Entrada**: JSON con metadata de búsqueda y lista de URLs BORA (generado por `bora_wrapper`)
2. **Descarga**: Cada URL se descarga vía HTTP con soporte de proxy
3. **Extracción**: Se extrae título y cuerpo de elementos HTML específicos
4. **Normalización**: Texto se normaliza Unicode (NFKC) eliminando espacios raros
5. **Validación**: Datos se validan contra esquemas Pydantic
6. **Salida**: JSON con estructura DocumentMetadata, conteniendo:
   - `titulo_aviso`: Título de la publicación
   - `cuerpo_aviso`: Contenido del aviso
   - `url_metadata`: ID, URL, fecha parseada de la URL
   - `json_metadata`: Rubro, fechas de búsqueda origen

## Configuración avanzada

### Variables de entorno (en `.env`)

- `JSON_DIR`: Directorio de búsqueda para archivos de entrada (default: `example_data/`)
- `PROXY_HOST`, `PROXY_PORT`, `PROXY_USER`, `PROXY_PASS`: Credenciales de proxy

### Customizar campos extraídos

En `bora_extractor/config.py`:

```python
DEFAULT_ID_FIELDS = ['tituloDetalleAviso', 'cuerpoDetalleAviso']
JSON_METADATA_KEYS = ['rubro', 'fecha_desde', 'fecha_hasta']
```

## Limitaciones y consideraciones

- Las páginas de BORA pueden cambiar su estructura HTML; si los IDs de elementos cambian, se requiere actualizar `DEFAULT_ID_FIELDS`
- No incluye descarga de archivos adjuntos o PDFs vinculados
- La normalización Unicode (NFKC) preserva espacios no rompibles; usar `.replace('\xa0', ' ')` si se necesita convertir a espacios normales
- Requiere conexión a internet y acceso a `boletinoficial.gob.ar`

## Desarrollo

Para contribuciones:

```bash
# Instalar con dependencias de desarrollo
uv pip install -e ".[test]"

# Ejecutar tests con cobertura
pytest --cov=bora_extractor -v

# Tests de un archivo específico
pytest tests/test_metadata.py -v
```

## Licencia

Este proyecto está diseñado para procesar datos públicos del Boletín Oficial Argentino conforme a la ley argentina.

## Soporte

Para problemas con estructuras HTML de BORA, incluir:
- URL del aviso problemático
- Output del error
- Fecha de fallo (estructura puede cambiar con el tiempo)

