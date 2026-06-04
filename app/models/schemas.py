"""
Esquemas (Schemas) Pydantic para validação e serialização de dados.
Definem a estrutura das respostas da API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Modelos Aninhados para Resposta de Clima
# ============================================================================

class UnidadesClima(BaseModel):
    """Unidades de medida para dados climáticos."""
    temperatura: str = Field(default="°C", description="Unidade de temperatura")

class CidadeInfo(BaseModel):
    """Informações geográficas de uma cidade."""
    nome: str = Field(..., description="Nome da cidade")
    id: int = Field(..., description="ID da cidade")
    estado: str = Field(..., description="Sigla do estado (UF)")
    regiao: str = Field(..., description="Código IBGE da cidade")

class CidadeList(BaseModel):
    data: List[CidadeInfo] = Field(..., description="Lista de cidades encontradas")

class ClimaData(BaseModel):
    """Dados climáticos de uma cidade."""
    date: datetime = Field(..., description="Data e hora da previsão climática", alias="data")
    condicao: str = Field(..., description="Condição climática (ex: Parcialmente Nublado)")
    condicao_desc: str = Field(..., description="Condição climática (ex: Parcialmente Nublado)")
    temperatura_min: float = Field(..., description="Temperatura mínima em °C", alias="min")
    temperatura_max: float = Field(..., description="Temperatura máxima em °C", alias="max")
    # unidades: UnidadesClima = Field(default_factory=UnidadesClima, description="Unidades de medida")


# ============================================================================
# Resposta de Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Modelo de resposta do health check."""
    status: str = Field(..., description="Status da aplicação (healthy ou degraded)")
    message: str = Field(..., description="Mensagem descritiva")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "API está operacional"
            }
        }


# ============================================================================
# Resposta de Cidade com Clima
# ============================================================================

class CityClimate(BaseModel):
    """Modelo de resposta de informações de cidade com dados climáticos."""
    
    cidade: str = Field(..., description="Nome da cidade", alias="nome")
    estado: str = Field(..., description="Sigla do estado (UF)", alias="state")
    clima: ClimaData = Field(..., description="Dados climáticos da cidade")
    atualizado_em: datetime = Field(..., description="Data e hora da consulta dos dados climáticos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Fortaleza",
                "estado": "CE",
                "clima": {
                    "temperatura_min": 24,
                    "temperatura_max": 32,
                    "condicao": "Parcialmente Nublado",
                    "unidades": {
                        "temperatura": "°C"
                    }
                },
                "consultado_em": "2025-03-15T14:30:00Z"
            }
        }
        populate_by_name = True  # Permite usar alias


class CityClimateListResponse(BaseModel):
    """Modelo de resposta de informações de cidade com dados climáticos."""
    
    cidades: list[CityClimate] = Field(..., description="Lista de informações de cidades com dados climáticos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Fortaleza",
                "estado": "CE",
                "clima": {
                    "temperatura_min": 24,
                    "temperatura_max": 32,
                    "condicao": "Parcialmente Nublado",
                    "unidades": {
                        "temperatura": "°C"
                    }
                },
                "consultado_em": "2025-03-15T14:30:00Z"
            }
        }
        populate_by_name = True  # Permite usar alias


# ============================================================================
# Modelos de Resposta de Erro
# ============================================================================

class ErrorBadRequest(BaseModel):
    """Modelo de resposta para erro 400 (Nome inválido)."""
    erro: bool = Field(default=True, description="Indica que houve erro")
    codigo: str = Field(..., description="Código do erro (ex: NOME_INVALIDO)")
    mensagem: str = Field(..., description="Mensagem descritiva do erro")
    nome_informado: str = Field(..., description="Nome da cidade que foi informado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "erro": True,
                "codigo": "NOME_INVALIDO",
                "mensagem": "O nome da cidade deve conter pelo menos 2 caracteres",
                "nome_informado": "X"
            }
        }


class ErrorNotFound(BaseModel):
    """Modelo de resposta para erro 404 (Cidade não encontrada)."""
    erro: bool = Field(default=True, description="Indica que houve erro")
    codigo: str = Field(..., description="Código do erro (CIDADE_NAO_ENCONTRADA)")
    mensagem: str = Field(..., description="Mensagem descritiva do erro")
    nome_informado: str = Field(..., description="Nome da cidade procurada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "erro": True,
                "codigo": "CIDADE_NAO_ENCONTRADA",
                "mensagem": "Cidade não encontrada nos registros disponíveis",
                "nome_informado": "CidadeInexistente"
            }
        }


class ErrorServiceUnavailable(BaseModel):
    """Modelo de resposta para erro 503 (Serviço indisponível)."""
    erro: bool = Field(default=True, description="Indica que houve erro")
    codigo: str = Field(..., description="Código do erro (SERVICO_EXTERNO_INDISPONIVEL)")
    mensagem: str = Field(..., description="Mensagem descritiva do erro")
    servico: str = Field(..., description="Nome do serviço que falhou (ex: CPTEC, IBGE)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "erro": True,
                "codigo": "SERVICO_EXTERNO_INDISPONIVEL",
                "mensagem": "Não foi possível obter dados do serviço externo. Tente novamente em alguns instantes",
                "servico": "CPTEC"
            }
        }


class ErrorInvalidState(BaseModel):
    """Modelo de resposta para erro 400 (Sigla de estado inválida)."""
    erro: bool = Field(default=True, description="Indica que houve erro")
    codigo: str = Field(..., description="Código do erro (ESTADO_INVALIDO)")
    mensagem: str = Field(..., description="Mensagem descritiva do erro")
    sigla_informada: str = Field(..., description="Sigla do estado que foi informada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "erro": True,
                "codigo": "ESTADO_INVALIDO",
                "mensagem": "Sigla de estado inválida. Use 2 caracteres (ex: SP, RJ, CE)",
                "sigla_informada": "XY"
            }
        }


# ============================================================================
# Item de Cidade (para listas)
# ============================================================================

class CityItem(BaseModel):
    """Modelo para um item de cidade em uma lista."""
    name: str = Field(..., description="Nome da cidade")
    code: str = Field(..., description="Código IBGE da cidade")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "São Paulo",
                "code": "3550308"
            }
        }


# ============================================================================
# Resposta de Lista de Cidades
# ============================================================================

class CityListResponse(BaseModel):
    """Modelo de resposta para listagem de cidades por estado."""
    
    state: str = Field(..., description="Sigla do estado (UF)")
    total: int = Field(..., description="Total de cidades encontradas no estado")
    limit: int = Field(..., description="Limite de cidades retornadas")
    cities: List[CityItem] = Field(..., description="Lista de cidades")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "SP",
                "total": 645,
                "limit": 10,
                "cities": [
                    {"name": "São Paulo", "code": "3550308"},
                    {"name": "Campinas", "code": "3509007"},
                ]
            }
        }


# ============================================================================
# Resposta de Erro (Formato antigo - removido)
# ============================================================================
# Os modelos de erro estão definidos acima: ErrorBadRequest, ErrorNotFound, 
# ErrorServiceUnavailable, ErrorInvalidState
