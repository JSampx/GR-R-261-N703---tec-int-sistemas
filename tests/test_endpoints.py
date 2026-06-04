"""
Testes para os endpoints da API.
Inclui os testes obrigatórios e testes adicionais.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


class TestHealthEndpoint:
    """Testes do endpoint /api/v1/health"""
    
    def test_health_check_returns_200(self, client):
        """Health check deve retornar status 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_health_check_has_status_field(self, client):
        """Health check deve retornar JSON com campo 'status'."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
    
    def test_health_check_has_message_field(self, client):
        """Health check deve retornar JSON com campo 'message'."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "message" in data


class TestCityClimateEndpoint:
    """Testes do endpoint /api/v1/clima/{nome_cidade}"""
    
    @pytest.mark.asyncio
    async def test_valid_city_weather_returns_200(self, client, mock_weather_data):
        """
        TESTE OBRIGATÓRIO #1: Requisição com cidade válida deve retornar 200 com dados corretos.
        """
        # Mock das funções de agregação de clima
        with patch("app.api.endpoints.WeatherAggregator.get_city_weather") as mock_get_weather:
            mock_get_weather.return_value = mock_weather_data
            
            response = client.get("/api/v1/clima/São Paulo")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar campos principais
            assert data["city_name"] == "São Paulo"
            assert data["state"] == "SP"
            assert data["temperature"] == 28.5
            assert data["humidity"] == 65
            assert "weather_condition" in data
            assert "latitude" in data
            assert "longitude" in data
    
    @pytest.mark.asyncio
    async def test_invalid_city_name_returns_400(self, client):
        """Requisição com nome de cidade inválido deve retornar 400."""
        # Teste com string vazia
        response = client.get("/api/v1/clima/")
        assert response.status_code == 404  # FastAPI retorna 404 para path vazio
        
        # Teste com caracteres inválidos
        response = client.get("/api/v1/clima/123!@#")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_city_not_found_returns_404(self, client):
        """
        TESTE OBRIGATÓRIO #2: Requisição com cidade inexistente deve retornar 404.
        """
        # Mock para lançar ValueError (cidade não encontrada)
        with patch("app.api.endpoints.WeatherAggregator.get_city_weather") as mock_get_weather:
            mock_get_weather.side_effect = ValueError("Cidade não encontrada")
            
            response = client.get("/api/v1/clima/CidadeInexistente123")
            
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "não encontrada" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_external_service_error_returns_503(self, client):
        """Erro em serviço externo deve retornar 503."""
        # Mock para lançar Exception genérica (erro externo)
        with patch("app.api.endpoints.WeatherAggregator.get_city_weather") as mock_get_weather:
            mock_get_weather.side_effect = Exception("API externa indisponível")
            
            response = client.get("/api/v1/clima/São Paulo")
            
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
    
    def test_city_name_with_special_characters_is_valid(self, client):
        """Nomes de cidades com acentos devem ser aceitos."""
        with patch("app.api.endpoints.WeatherAggregator.get_city_weather") as mock_get_weather:
            mock_weather = {
                "city_name": "São Paulo",
                "state": "SP",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "temperature": 25.0,
                "feels_like": None,
                "humidity": 70,
                "weather_condition": "Nublado",
                "wind_speed": 10.0,
                "precipitation": 0.0,
                "pressure": 1013
            }
            mock_get_weather.return_value = mock_weather
            
            response = client.get("/api/v1/clima/São Paulo")
            assert response.status_code == 200


class TestCitiesListEndpoint:
    """Testes do endpoint /api/v1/cidades/{sigla_uf}"""
    
    @pytest.mark.asyncio
    async def test_list_cities_by_valid_state_returns_200(self, client, mock_cities_list):
        """Requisição com estado válido deve retornar 200 com lista de cidades."""
        with patch("app.api.endpoints.WeatherAggregator.get_cities_by_state") as mock_get_cities:
            mock_get_cities.return_value = mock_cities_list
            
            response = client.get("/api/v1/cidades/SP")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estrutura de resposta
            assert data["state"] == "SP"
            assert data["total"] >= 0
            assert data["limit"] > 0
            assert "cities" in data
            assert isinstance(data["cities"], list)
            assert len(data["cities"]) <= data["limit"]
    
    def test_list_cities_with_invalid_state_returns_400(self, client):
        """Requisição com sigla de estado inválida deve retornar 400."""
        response = client.get("/api/v1/cidades/XY")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_list_cities_with_limit_parameter(self, client, mock_cities_list):
        """Requisição com parâmetro limite deve respeitar o limite."""
        with patch("app.api.endpoints.WeatherAggregator.get_cities_by_state") as mock_get_cities:
            limited_list = mock_cities_list.copy()
            limited_list["limit"] = 5
            limited_list["cities"] = limited_list["cities"][:5]
            mock_get_cities.return_value = limited_list
            
            response = client.get("/api/v1/cidades/SP?limite=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["limit"] == 5
            assert len(data["cities"]) <= 5
    
    def test_list_cities_with_invalid_limit_returns_400(self, client):
        """Limite fora do intervalo (1-100) deve retornar 400."""
        # Limite muito alto
        response = client.get("/api/v1/cidades/SP?limite=101")
        assert response.status_code == 422  # Validation error
        
        # Limite negativo
        response = client.get("/api/v1/cidades/SP?limite=0")
        assert response.status_code == 422  # Validation error
    
    def test_list_cities_default_limit_is_10(self, client, mock_cities_list):
        """Limite padrão deve ser 10."""
        with patch("app.api.endpoints.WeatherAggregator.get_cities_by_state") as mock_get_cities:
            mock_cities_list["limit"] = 10
            mock_get_cities.return_value = mock_cities_list
            
            response = client.get("/api/v1/cidades/SP")
            
            assert response.status_code == 200
            data = response.json()
            assert data["limit"] == 10


class TestRootEndpoint:
    """Testes do endpoint raiz /"""
    
    def test_root_endpoint_returns_200(self, client):
        """Endpoint raiz deve retornar 200."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_returns_api_info(self, client):
        """Endpoint raiz deve retornar informações da API."""
        response = client.get("/")
        data = response.json()
        
        assert "nome" in data
        assert "versão" in data
        assert "documentacao" in data


class TestSwaggerDocumentation:
    """Testes da documentação Swagger"""
    
    def test_swagger_docs_available(self, client):
        """Documentação Swagger deve estar disponível em /docs."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self, client):
        """ReDoc deve estar disponível em /redoc."""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Schema OpenAPI deve estar disponível."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
