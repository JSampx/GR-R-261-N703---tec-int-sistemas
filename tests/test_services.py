"""
Testes unitários para os serviços de integração com APIs externas.
Usa mocks para evitar dependências reais em testes.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.external_apis import IBGEService, OpenMeteoService
from app.services.weather_aggregator import WeatherAggregator
from app.utils.cache import get_cache


class TestIBGEService:
    """Testes para IBGEService"""
    
    @pytest.mark.asyncio
    async def test_get_cities_by_state_success(self):
        """Deve retornar lista de cidades para estado válido."""
        mock_response = [
            {"nome": "São Paulo", "id": 3550308},
            {"nome": "Campinas", "id": 3509007},
            {"nome": "Santos", "id": 3548708},
        ]
        
        with patch("app.services.external_apis.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_instance.get.return_value = mock_response_obj
            
            # Limpar cache antes do teste
            get_cache().clear()
            
            result = await IBGEService.get_cities_by_state("SP")
            
            assert len(result) == 3
            assert result[0]["name"] == "São Paulo"
            assert result[0]["code"] == "3550308"
    
    @pytest.mark.asyncio
    async def test_get_cities_uses_cache(self):
        """Deve usar cache em chamadas subsequentes."""
        # Limpar cache
        get_cache().clear()
        
        mock_response = [
            {"nome": "Rio de Janeiro", "id": 3304557},
        ]
        
        with patch("app.services.external_apis.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_instance.get.return_value = mock_response_obj
            
            # Primeira chamada
            result1 = await IBGEService.get_cities_by_state("RJ")
            
            # Segunda chamada (deve usar cache)
            result2 = await IBGEService.get_cities_by_state("RJ")
            
            # get() deve ter sido chamado apenas uma vez (cache evita segundo chamada)
            assert mock_instance.get.call_count == 1
            assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_find_city_by_name_success(self):
        """Deve encontrar cidade por nome em um estado."""
        mock_cities = [
            {"name": "São Paulo", "code": "3550308"},
            {"name": "Campinas", "code": "3509007"},
        ]
        
        with patch.object(IBGEService, "get_cities_by_state", return_value=mock_cities):
            result = await IBGEService.find_city_by_name("São Paulo", "SP")
            
            assert result is not None
            assert result["name"] == "São Paulo"
            assert result["code"] == "3550308"
    
    @pytest.mark.asyncio
    async def test_find_city_by_name_not_found(self):
        """Deve retornar None se cidade não encontrada."""
        mock_cities = [
            {"name": "São Paulo", "code": "3550308"},
        ]
        
        with patch.object(IBGEService, "get_cities_by_state", return_value=mock_cities):
            result = await IBGEService.find_city_by_name("CidadeInexistente", "SP")
            
            assert result is None


class TestOpenMeteoService:
    """Testes para OpenMeteoService"""
    
    @pytest.mark.asyncio
    async def test_get_coordinates_success(self):
        """Deve retornar coordenadas para cidade válida."""
        mock_response = {
            "results": [
                {
                    "name": "São Paulo",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "country": "Brazil"
                }
            ]
        }
        
        with patch("app.services.external_apis.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_instance.get.return_value = mock_response_obj
            
            # Limpar cache
            get_cache().clear()
            
            result = await OpenMeteoService.get_coordinates_by_city_name("São Paulo")
            
            assert result is not None
            assert result[0] == -23.5505  # latitude
            assert result[1] == -46.6333  # longitude
            assert result[2] == "São Paulo"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self):
        """Deve retornar dados climáticos para coordenadas válidas."""
        mock_response = {
            "current": {
                "temperature_2m": 28.5,
                "relative_humidity_2m": 65,
                "weather_code": 2,
                "wind_speed_10m": 12.3,
                "pressure_msl": 1013.25,
                "precipitation": 0.0
            }
        }
        
        with patch("app.services.external_apis.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_instance.get.return_value = mock_response_obj
            
            # Limpar cache
            get_cache().clear()
            
            result = await OpenMeteoService.get_current_weather(-23.5505, -46.6333)
            
            assert result["temperature"] == 28.5
            assert result["humidity"] == 65
            assert result["wind_speed"] == 12.3
            assert "weather_condition" in result
    
    def test_weather_code_mapping(self):
        """Deve mapear corretamente os códigos WMO para descrições."""
        assert OpenMeteoService._get_weather_description(0) == "Céu limpo"
        assert OpenMeteoService._get_weather_description(2) == "Parcialmente nublado"
        assert OpenMeteoService._get_weather_description(61) == "Chuva"
        assert OpenMeteoService._get_weather_description(95) == "Trovoada"


class TestWeatherAggregator:
    """Testes para WeatherAggregator"""
    
    @pytest.mark.asyncio
    async def test_get_city_weather_success(self):
        """Deve agregar dados de cidade com clima com sucesso."""
        # Mock de IBGE
        mock_city_info = {"name": "São Paulo", "code": "3550308"}
        
        # Mock de coordenadas
        mock_coords = (-23.5505, -46.6333, "São Paulo", "Brazil")
        
        # Mock de clima
        mock_weather = {
            "temperature": 28.5,
            "humidity": 65,
            "weather_condition": "Parcialmente nublado",
            "wind_speed": 12.3,
            "pressure": 1013,
            "precipitation": 0.0
        }
        
        with patch.object(IBGEService, "find_city_by_name", return_value=mock_city_info):
            with patch.object(OpenMeteoService, "get_coordinates_by_city_name", return_value=mock_coords):
                with patch.object(OpenMeteoService, "get_current_weather", return_value=mock_weather):
                    result = await WeatherAggregator.get_city_weather("São Paulo", "SP")
                    
                    assert result["city_name"] == "São Paulo"
                    assert result["temperature"] == 28.5
                    assert result["latitude"] == -23.5505
                    assert result["humidity"] == 65
    
    @pytest.mark.asyncio
    async def test_get_city_weather_city_not_found(self):
        """Deve lançar ValueError se cidade não encontrada."""
        with patch.object(IBGEService, "find_city_by_name", return_value=None):
            with pytest.raises(ValueError):
                await WeatherAggregator.get_city_weather("CidadeInexistente")
    
    @pytest.mark.asyncio
    async def test_get_cities_by_state(self):
        """Deve retornar lista paginada de cidades."""
        mock_cities = [
            {"name": "São Paulo", "code": "3550308"},
            {"name": "Campinas", "code": "3509007"},
            {"name": "Santos", "code": "3548708"},
        ]
        
        with patch.object(IBGEService, "get_cities_by_state", return_value=mock_cities):
            result = await WeatherAggregator.get_cities_by_state("SP", limit=2)
            
            assert result["state"] == "SP"
            assert result["total"] == 3
            assert result["limit"] == 2
            assert len(result["cities"]) == 2
    
    @pytest.mark.asyncio
    async def test_check_health_success(self):
        """Deve retornar status de saúde positivo."""
        with patch.object(IBGEService, "get_cities_by_state", return_value=[{"name": "São Paulo", "code": "3550308"}]):
            with patch.object(OpenMeteoService, "get_coordinates_by_city_name", return_value=(-23.5505, -46.6333, "São Paulo", "Brazil")):
                result = await WeatherAggregator.check_health()
                
                assert result["status"] in ["healthy", "degraded"]
                assert "services" in result
