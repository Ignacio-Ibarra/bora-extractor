import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def configure_example_data():
    """Configura JSON_DIR para apuntar a example_data/ durante los tests."""
    example_data_dir = Path(__file__).parent.parent / "example_data"
    os.environ["JSON_DIR"] = str(example_data_dir)
    yield
    # Cleanup si es necesario (opcional)
