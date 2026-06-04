"""
Agregador de dados climáticos e geográficos.
Orquestra as chamadas aos serviços de APIs externas (IBGE e CPTEC).
"""

from typing import Optional, List, Dict
from datetime import datetime
from app.services.external_apis import IBGEService, CPTECService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WeatherAggregator:
    """
    Agregador que orquestra múltiplos serviços para fornecer dados integrados
    de clima e geográfica de cidades brasileiras.
    """
    
    @staticmethod
    async def get_city_weather(city_name: str, state_code: Optional[str] = None) -> Dict:
        """
        Obtém informações completas de uma cidade (clima + geográfica).
        
        Fluxo:
        1. Busca a cidade via CPTEC
        2. Obtém a previsão de tempo
        3. Formata os dados no padrão esperado
        
        Args:
            city_name: Nome da cidade
            state_code: Sigla do estado (opcional)
        
        Returns:
            Dict: Informações da cidade com dados climáticos formatados
        
        Raises:
            ValueError: Se cidade não for encontrada
            Exception: Se algum serviço externo falhar
        """
        logger.info(f"Iniciando agregação de dados da cidade", city=city_name, state=state_code)
        
        try:
            # PASSO 1: Buscar cidade no CPTEC
            city_info = await CPTECService.find_city_by_name(city_name)
            
            if not city_info:
                logger.warning(f"Cidade não encontrada no CPTEC", city=city_name)
                raise ValueError(f"Cidade '{city_name}' não encontrada")
            
            city_code = city_info.get("id")
            logger.info(f"Cidade encontrada no CPTEC", city=city_info.get("nome"), code=city_code)
            
            # PASSO 2: Obter previsão de tempo
            forecast = await CPTECService.get_forecast(city_code)
            
            if not forecast:
                logger.warning(f"Previsão não encontrada", city=city_name)
                raise ValueError(f"Previsão não encontrada para '{city_name}'")
            
            logger.info(f"Previsão obtida com sucesso", city=city_name)
            
            # PASSO 3: Extrair dados climáticos (primeiro dia de previsão)
            clima_list = forecast.get("clima", [])
            current_weather = clima_list[0] if clima_list else {}
            
            # PASSO 4: Agregar informações no novo formato
            result = {
                "city_name": city_info.get("nome", city_name),
                "state": state_code or city_info.get("estado", "N/A"),
                "clima": {
                    "temperatura_min": float(current_weather.get("temp_min", 0)),
                    "temperatura_max": float(current_weather.get("temp_max", 0)),
                    "condicao": current_weather.get("condicao", "Desconhecido"),
                    "unidades": {
                        "temperatura": "°C"
                    }
                },
                "consultado_em": datetime.now().isoformat() + "Z"
            }
            
            logger.info(f"Agregação de dados concluída com sucesso", city=city_name)
            return result
        
        except ValueError as e:
            logger.error(f"Erro na agregação: {str(e)}", city=city_name)
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na agregação", city=city_name, error=str(e))
            raise
    
    @staticmethod
    async def get_cities_by_state(state_code: str, limit: int = 10) -> Dict:
        """
        Obtém lista paginada de cidades de um estado.
        
        Args:
            state_code: Sigla do estado (ex: SP, RJ)
            limit: Número máximo de cidades a retornar (1-100)
        
        Returns:
            Dict: Informações de cidades do estado
        
        Raises:
            Exception: Se a busca falhar
        """
        logger.info(f"Iniciando listagem de cidades", state=state_code, limit=limit)
        
        try:
            cities = await IBGEService.get_cities_by_state(state_code)
            
            # Aplicar limite
            limited_cities = cities[:limit]
            
            result = {
                "state": state_code.upper(),
                "total": len(cities),
                "limit": limit,
                "cities": limited_cities
            }
            
            logger.info(f"Listagem de cidades concluída", state=state_code, count=len(limited_cities))
            return result
        
        except Exception as e:
            logger.error(f"Erro ao listar cidades", state=state_code, error=str(e))
            raise
    
    @staticmethod
    async def check_health() -> Dict:
        """
        Verifica o status de saúde da aplicação e serviços externos.
        
        Returns:
            Dict: Status de saúde (healthy ou degraded) com detalhes
        """
        logger.info("Executando health check de serviços externos")
        
        status = {
            "status": "healthy",
            "services": {
                "cptec": "unknown",
            }
        }
        
        # Testar CPTEC
        try:
            # Fazer uma chamada simples ao CPTEC para testar
            cities = await CPTECService.search_cities_by_name("São Paulo")
            if cities and len(cities) > 0:
                status["services"]["cptec"] = "operational"
        except Exception as e:
            logger.warning("CPTEC health check falhou", error=str(e))
            status["services"]["cptec"] = "degraded"
            status["status"] = "degraded"
        
        logger.info(f"Health check concluído", status=status["status"])
        return status
