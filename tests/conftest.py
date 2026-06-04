"""
Configuração do pytest.
Define fixtures e configuração global para testes.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.cache import get_cache


@pytest.fixture
def client():
    """Fixture que fornece cliente de teste para a API."""
    return TestClient(app)


@pytest.fixture
def clear_cache():
    """Fixture que limpa o cache antes e depois de cada teste."""
    cache = get_cache()
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_city_data():
    """Fixture que fornece dados simulados de cidades."""
    return {
        "name": "São Paulo",
        "code": "3550308"
    }


@pytest.fixture
def mock_weather_data():
    """Fixture que fornece dados simulados de clima."""
    return {
        "city_name": "São Paulo",
        "state": "SP",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "temperature": 28.5,
        "feels_like": 29.2,
        "humidity": 65,
        "weather_condition": "Parcialmente Nublado",
        "wind_speed": 12.3,
        "precipitation": 0.0,
        "pressure": 1013
    }


@pytest.fixture
def mock_cities_list():
    """Fixture que fornece lista simulada de cidades."""
    return {
        "state": "SP",
        "total": 645,
        "limit": 10,
        "cities": [
            {"name": "São Paulo", "code": "3550308"},
            {"name": "Campinas", "code": "3509007"},
            {"name": "Santos", "code": "3548708"},
            {"name": "Sorocaba", "code": "3552707"},
            {"name": "Ribeirão Preto", "code": "3543402"},
        ]
    }
