"""
Integração com APIs externas: IBGE e CPTEC (Brasil API).
Fornece clientes HTTP para consumo de dados de cidades e clima.
"""

import os
from typing import List, Dict, Optional
import httpx2 as httpx
from app.utils.logger import get_logger
from app.utils.cache import get_cache

logger = get_logger(__name__)


# ============================================================================
# Configuração
# ============================================================================

API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))
MAX_RETRIES = 3


# ============================================================================
# IBGE Service - Localidades e Municípios
# ============================================================================

class IBGEService:
    """
    Serviço para integração com a API IBGE (Brasil API).
    Fornece informações sobre estados e municípios brasileiros.
    """
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
    CACHE = get_cache()
    
    @classmethod
    async def get_cities_by_state(cls, state_code: str) -> List[Dict[str, str]]:
        """
        Obtém lista de cidades de um estado.
        
        Args:
            state_code: Sigla do estado (ex: SP, RJ)
        
        Returns:
            List[Dict[str, str]]: Lista de cidades com nome e código
        
        Raises:
            Exception: Se a requisição falhar após retries
        """
        cache_key = f"ibge_cities_{state_code.upper()}"
        
        # Verificar cache
        cached = cls.CACHE.get(cache_key)
        if cached is not None:
            logger.info(f"Cidades do estado encontradas em cache", state=state_code)
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        logger.info(
                            f"Buscando cidades no IBGE",
                            state=state_code,
                            attempt=attempt
                        )
                        response = await client.get(
                            f"{cls.BASE_URL}/estados/{state_code}/municipios",
                            timeout=API_TIMEOUT
                        )
                        response.raise_for_status()
                        
                        data = response.json()
                        # Converter resposta para formato consistente
                        cities = [
                            {
                                "name": city.get("nome", ""),
                                "code": str(city.get("id", ""))
                            }
                            for city in data
                        ]
                        
                        # Armazenar no cache por 1 hora
                        ttl = int(os.getenv("CACHE_CITIES_TTL", 3600))
                        cls.CACHE.set(cache_key, cities, ttl=ttl)
                        
                        logger.info(
                            f"Cidades encontradas no IBGE",
                            state=state_code,
                            count=len(cities)
                        )
                        
                        return cities
                    
                    except httpx.HTTPError as e:
                        logger.warning(
                            f"Erro ao buscar cidades no IBGE",
                            attempt=attempt,
                            error=str(e)
                        )
                        if attempt == MAX_RETRIES:
                            raise
        
        except Exception as e:
            logger.error(f"Erro ao buscar cidades no IBGE", state=state_code, error=str(e))
            raise
    
    @classmethod
    async def find_city_by_name(
        cls,
        city_name: str,
        state_code: str = "SP"
    ) -> Optional[Dict[str, str]]:
        """
        Busca uma cidade específica no estado.
        
        Args:
            city_name: Nome da cidade
            state_code: Sigla do estado
        
        Returns:
            Optional[Dict[str, str]]: Informações da cidade ou None se não encontrada
        """
        try:
            cities = await cls.get_cities_by_state(state_code)
            
            # Buscar cidade (case-insensitive)
            city_lower = city_name.lower().strip()
            for city in cities:
                if city["name"].lower() == city_lower:
                    return city
            
            logger.warning(f"Cidade não encontrada no IBGE", city=city_name, state=state_code)
            return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar cidade no IBGE", city=city_name, error=str(e))
            raise


# ============================================================================
# CPTEC Service - Dados Meteorológicos (Brasil API)
# ============================================================================

class CPTECService:
    """
    Serviço para integração com CPTEC via Brasil API.
    Fornece busca de cidades e dados meteorológicos brasileiros.
    
    Endpoints:
    - GET /api/cptec/v1/cidade/{cidade}: Busca cidades por nome
    - GET /api/cptec/v1/clima/previsao/{codigo_cidade}: Previsão de clima
    """
    
    BASE_URL = "https://brasilapi.com.br/api/cptec/v1"
    CACHE = get_cache()
    CITY_SEARCH_CACHE_TTL = 3600  # 1 hora
    FORECAST_CACHE_TTL = 1800  # 30 minutos
    
    @classmethod
    async def search_cities_by_name(cls, city_name: str) -> List[Dict]:
        """
        Busca cidades pelo nome na Brasil API CPTEC.
        
        Args:
            city_name: Nome da cidade a buscar
        
        Returns:
            List[Dict]: Lista de cidades encontradas com id, nome, latitude, longitude
        
        Raises:
            Exception: Se a requisição falhar após retries
        """
        cache_key = f"cptec_cities_{city_name.lower()}"
        
        # Verificar cache
        cached = cls.CACHE.get(cache_key)
        if cached:
            logger.info(f"Cidades encontradas em cache", city=city_name)
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        logger.info(f"Buscando cidades no CPTEC", city_name=city_name, attempt=attempt)
                        
                        response = await client.get(
                            f"{cls.BASE_URL}/cidade/{city_name}",
                            timeout=API_TIMEOUT
                        )
                        response.raise_for_status()
                        
                        cities = response.json()
                        
                        # Cache resultado
                        cls.CACHE.set(cache_key, cities, ttl=cls.CITY_SEARCH_CACHE_TTL)
                        logger.info(f"Cidades encontradas no CPTEC", city=city_name, count=len(cities))
                        
                        return cities
                    
                    except httpx.HTTPError as e:
                        logger.warning(
                            f"Erro ao buscar cidades no CPTEC",
                            attempt=attempt,
                            error=str(e)
                        )
                        if attempt == MAX_RETRIES:
                            raise
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Cidade não encontrada no CPTEC", city=city_name)
                return []
            logger.error(f"Erro ao buscar cidades no CPTEC", city=city_name, status=e.response.status_code)
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar cidades no CPTEC", city=city_name, error=str(e))
            raise
    
    @classmethod
    async def find_city_by_name(cls, city_name: str) -> Optional[Dict]:
        """
        Busca uma cidade pelo nome e retorna a primeira match.
        Wrapper para search_cities_by_name que retorna um único resultado.
        
        Args:
            city_name: Nome da cidade
        
        Returns:
            Optional[Dict]: Dados da cidade (id, nome, latitude, longitude) ou None
        
        Raises:
            Exception: Se a busca falhar
        """
        try:
            cities = await cls.search_cities_by_name(city_name)
            
            if not cities:
                return None
            
            # Retornar primeira match (melhor resultado)
            return cities[0]
        
        except Exception as e:
            logger.error(f"Erro ao procurar cidade no CPTEC", city=city_name, error=str(e))
            raise
    
    @classmethod
    async def get_forecast(cls, city_code: int) -> Optional[Dict]:
        """
        Obtém previsão meteorológica para uma cidade.
        
        Args:
            city_code: Código CPTEC da cidade
        
        Returns:
            Optional[Dict]: Dados de previsão com clima para próximos dias
        
        Raises:
            Exception: Se a requisição falhar após retries
        """
        cache_key = f"cptec_forecast_{city_code}"
        
        # Verificar cache
        cached = cls.CACHE.get(cache_key)
        if cached:
            logger.info(f"Previsão encontrada em cache", city_code=city_code)
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        logger.info(f"Buscando previsão do CPTEC", city_code=city_code, attempt=attempt)
                        
                        response = await client.get(
                            f"{cls.BASE_URL}/clima/previsao/{city_code}",
                            timeout=API_TIMEOUT
                        )
                        response.raise_for_status()
                        
                        forecast = response.json()
                        
                        # Cache resultado
                        cls.CACHE.set(cache_key, forecast, ttl=cls.FORECAST_CACHE_TTL)
                        logger.info(f"Previsão obtida do CPTEC", city_code=city_code)
                        
                        return forecast
                    
                    except httpx.HTTPError as e:
                        logger.warning(
                            f"Erro ao buscar previsão do CPTEC",
                            attempt=attempt,
                            error=str(e)
                        )
                        if attempt == MAX_RETRIES:
                            raise
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Previsão não encontrada no CPTEC", city_code=city_code)
                return None
            logger.error(f"Erro ao buscar previsão do CPTEC", city_code=city_code, status=e.response.status_code)
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar previsão do CPTEC", city_code=city_code, error=str(e))
            raise
