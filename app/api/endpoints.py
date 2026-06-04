"""
Endpoints da API REST.
Define os 3 endpoints principais da aplicação:
  1. GET /api/v1/clima/{nome_cidade} - Informações de cidade com clima
  2. GET /api/v1/cidades/{sigla_uf} - Listagem de cidades por estado
  3. GET /api/v1/health - Health check
"""
import asyncio
from datetime import datetime, timezone
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    CityClimate,
    CityClimateListResponse,
    CidadeInfo,
    CidadeList,
    CityListResponse,
    CityItem,
    HealthResponse,
    ErrorBadRequest,
    ErrorNotFound,
    ErrorServiceUnavailable,
    ErrorInvalidState
)
from app.services.weather_aggregator import WeatherAggregator
from app.services.external_apis import CPTECService, IBGEService 
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Criar router para endpoints da API
router = APIRouter(prefix="/api/v1", tags=["API"])


# ============================================================================
# Validadores
# ============================================================================

def validate_city_name(city_name: str) -> str:
    """
    Valida o nome da cidade.
    
    Args:
        city_name: Nome da cidade a validar
    
    Returns:
        str: Nome da cidade validado
    
    Raises:
        ValueError: Se o nome for inválido
    """
    # Remover espaços em branco extras
    city_name = city_name.strip()
    
    # Verificar se está vazio
    if not city_name:
        raise ValueError("Nome da cidade não pode estar vazio")
    
    # Verificar comprimento (mínimo 2 caracteres, máximo 100)
    if len(city_name) < 2 or len(city_name) > 100:
        raise ValueError("Nome da cidade deve ter entre 2 e 100 caracteres")
    
    # Permitir apenas letras, espaços, hífens e acentos
    if not re.match(r"^[a-zA-Záàâãéèêíïóôõöúçñ\s\-]+$", city_name):
        raise ValueError("Nome da cidade contém caracteres inválidos")
    
    return city_name


def validate_state_code(state_code: str) -> str:
    """
    Valida a sigla do estado (UF).
    
    Args:
        state_code: Sigla do estado a validar (ex: SP, RJ)
    
    Returns:
        str: Sigla do estado validada em maiúsculas
    
    Raises:
        ValueError: Se a sigla for inválida
    """
    state_code = state_code.strip().upper()
    
    # UFs brasileiras válidas
    valid_states = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    }
    
    if state_code not in valid_states:
        raise ValueError(f"Sigla de estado inválida: {state_code}")
    
    return state_code


# ============================================================================
# Endpoint 1: Informações da Cidade com Clima
# ============================================================================

@router.get(
    "/clima/{nome_cidade}",
    # response_model=CityClimateListResponse,
    # response_model=CidadeList,
    responses={
        200: {"description": "Informações da cidade com dados climáticos"},
        400: {"model": ErrorBadRequest, "description": "Nome de cidade inválido"},
        404: {"model": ErrorNotFound, "description": "Cidade não encontrada"},
        503: {"model": ErrorServiceUnavailable, "description": "Serviço externo indisponível"},
    },
    summary="Obter informações de cidade com dados climáticos",
    description="Retorna informações geográficas e dados climáticos de uma cidade brasileira."
)
async def get_city_climate(nome_cidade: str) -> CityClimateListResponse:
    """
    Obtém informações climáticas de uma cidade brasileira.
    
    O sistema:
    1. Valida o nome da cidade
    2. Busca a cidade no CPTEC
    3. Obtém as coordenadas geográficas e dados climáticos
    
    Args:
        nome_cidade: Nome da cidade (obrigatório)
    
    Returns:
        CityClimateListResponse: Informações da cidade com dados climáticos
    
    Raises:
        HTTPException 400: Se o nome da cidade for inválido
        HTTPException 404: Se a cidade não for encontrada
        HTTPException 503: Se algum serviço externo falhar
    """
    # Validar nome da cidade
    try:
        validated_city = validate_city_name(nome_cidade)
    except ValueError as e:
        logger.error(f"Validação de nome de cidade falhou", error=str(e), city=nome_cidade)
        raise HTTPException(
            status_code=400,
            detail={
                "erro": True,
                "codigo": "NOME_INVALIDO",
                "mensagem": str(e),
                "nome_informado": nome_cidade
            }
        )
    
    logger.info(f"Buscando informações da cidade", city=validated_city)
    
    try:
        # Chamar WeatherAggregator para obter dados completos
        # result = await WeatherAggregator.get_city_weather(validated_city)
        # result = await CPTECService.search_cities_by_name(validated_city)
        # cidades_list = []
        # for cidade in result:
        #      cidade =  await CPTECService.get_forecast(cidade["id"])
        #      cidades_list.append(cidade)
        # print(cidades_list)
        # cidades = dict(enumerate(cidades_list))
        # # result = [{"nome":"Teresina","id":"245","estado":"PI","regiao": "Nordeste"}]
        # # print(result.type())
        # # return CidadeList(data=[CidadeInfo(**city) for city in result])
        # return CityClimateListResponse(**cidades)
        # return cidades
        #  # Desempacotar o dicionário para os campos do modelo
        # # return CidadeInfo(*result 
        #     nome=result["city_name"],
        #     estado=result["state"],
        #     clima=result["clima"],
        #     consultado_em=result["consultado_em"]
        # )
        # 1. Fazemos a busca
        cidades_encontradas = await CPTECService.search_cities_by_name(validated_city)

        # 2. PROTEÇÃO: Se a lista for vazia, interrompemos a função IMEDIATAMENTE
        if not cidades_encontradas:
            # Isso vai pular direto para o bloco 'except ValueError' do 404
            raise ValueError("Nenhuma cidade encontrada")

        # 3. Como passamos da linha acima, temos 100% de certeza que a lista tem itens.
        # O Python vai rodar tranquilamente.
        tarefas_clima = [CPTECService.get_forecast(city["id"]) for city in cidades_encontradas]
        # 4. Monta a lista estruturada combinando os dados geográficos com os climáticos
        resultados_clima = await asyncio.gather(*tarefas_clima)
        # 4. Monta a lista estruturada combinando os dados geográficos com os climáticos
        lista_cidades_com_clima = []
        
        for cidade, dados_clima in zip(cidades_encontradas, resultados_clima):
            # A API do CPTEC retorna o clima como uma lista de dias. 
            # Pegamos o primeiro item (índice 0), que corresponde à previsão de hoje.
            lista_previsao = dados_clima.get("clima", [])
            previsao_hoje = lista_previsao[0] if lista_previsao else {}
            
            # Construímos o dicionário usando EXATAMENTE os aliases que o seu Pydantic pede
            item_cidade = {
                "nome": cidade.get("nome", "Desconhecido"), # Atende ao alias="nome"
                "state": cidade.get("estado", "XX"),        # Atende ao alias="state"
                "clima": previsao_hoje,                     # Passamos o dict bruto do CPTEC, o Pydantic filtra data, min, max, etc.
                "atualizado_em": dados_clima.get("atualizado_em", datetime.now())
            }
            
            lista_cidades_com_clima.append(item_cidade)
            
        # 5. Passa a lista completa para o modelo de resposta
        return CityClimateListResponse(cidades=lista_cidades_com_clima)
    
    except ValueError as e:
        logger.warning(f"Cidade não encontrada", city=validated_city, error=str(e))
        raise HTTPException(
            status_code=404,
            detail={
                "erro": True,
                "codigo": "CIDADE_NAO_ENCONTRADA",
                "mensagem": f"A cidade '{validated_city}' não foi encontrada nos registros disponíveis.",
                "nome_informado": validated_city
            }
        )
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados climáticos", city=validated_city, error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "erro": True,
                "codigo": "SERVICO_EXTERNO_INDISPONIVEL",
                "mensagem": "Não foi possível obter dados do serviço externo. Tente novamente em alguns instantes.",
                "servico": "CPTEC"
            }
        )


# ============================================================================
# Endpoint 2: Listagem de Cidades por Estado
# ============================================================================

@router.get(
    "/cidades/{sigla_uf}",
    response_model=CityListResponse,
    responses={
        200: {"description": "Lista de cidades do estado"},
        400: {"model": ErrorInvalidState, "description": "Sigla de estado inválida"},
        503: {"model": ErrorServiceUnavailable, "description": "Serviço externo indisponível"},
    },
    summary="Listar cidades de um estado",
    description="Retorna uma lista paginada de cidades de um estado brasileiro."
)
async def get_cities_by_state(
    sigla_uf: str,
    limite: Optional[int] = Query(10, ge=1, le=100, description="Limite de cidades a retornar")
) -> CityListResponse:
    """
    Lista cidades de um estado brasileiro.
    
    Args:
        sigla_uf: Sigla do estado (ex: SP, RJ) - obrigatório
        limite: Limite de cidades a retornar (padrão: 10, intervalo: 1-100)
    
    Returns:
        CityListResponse: Lista de cidades do estado
    
    Raises:
        HTTPException 400: Se a sigla do estado for inválida
        HTTPException 503: Se algum serviço externo falhar
    """
    # Validar sigla do estado
    try:
        validated_state = validate_state_code(sigla_uf)
    except ValueError as e:
        logger.error(f"Validação de sigla de estado falhou", error=str(e), state=sigla_uf)
        raise HTTPException(
            status_code=400,
            detail={
                "erro": True,
                "codigo": "ESTADO_INVALIDO",
                "mensagem": "Sigla de estado inválida. Use 2 caracteres (ex: SP, RJ, CE).",
                "sigla_informada": sigla_uf
            }
        )
    
    logger.info(f"Buscando cidades do estado", state=validated_state, limit=limite)
    
    try:
        # Chamar WeatherAggregator para obter lista de cidades
        result = await WeatherAggregator.get_cities_by_state(validated_state, limite)
        
        # Transformar em CityItem
        cities_items = [CityItem(**city) for city in result["cities"]]
        
        return CityListResponse(
            state=result["state"],
            total=result["total"],
            limit=result["limit"],
            cities=cities_items
        )
    
    except Exception as e:
        logger.error(f"Erro ao listar cidades", state=validated_state, error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "erro": True,
                "codigo": "SERVICO_EXTERNO_INDISPONIVEL",
                "mensagem": "Não foi possível obter dados do serviço externo. Tente novamente em alguns instantes.",
                "servico": "IBGE"
            }
        )


# ============================================================================
# Endpoint 3: Health Check
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar saúde da API",
    description="Retorna o status da saúde da aplicação e serviços externos."
)
async def health_check() -> HealthResponse:
    """
    Verifica o status de saúde da aplicação.
    
    Returns:
        HealthResponse: Status da aplicação
    """
    logger.debug("Health check solicitado")
    
    try:
        # Chamar WeatherAggregator para verificar saúde de serviços externos
        health_status = await WeatherAggregator.check_health()
        
        return HealthResponse(
            status=health_status["status"],
            message=f"Status: {health_status['status']} - Serviços: {health_status['services']}"
        )
    
    except Exception as e:
        logger.error(f"Erro ao verificar saúde", error=str(e))
        return HealthResponse(
            status="degraded",
            message="Erro ao verificar saúde de serviços externos"
        )
