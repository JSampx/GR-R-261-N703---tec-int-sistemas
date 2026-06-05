"""
Módulo principal da aplicação FastAPI.
Inicializa a aplicação e configura middleware, documentação e logging.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


# ============================================================================
# Configuração de Logging
# ============================================================================

def setup_logging() -> None:
    """Configura logging estruturado da aplicação."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events (Startup/Shutdown)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação (startup e shutdown)."""
    # Startup
    logger.info("🚀 Iniciando API de Agregação Climática...")
    yield
    # Shutdown
    logger.info("🛑 Encerrando API de Agregação Climática...")


# ============================================================================
# Configuração da Aplicação FastAPI
# ============================================================================

app = FastAPI(
    title="API de Agregação Climática e Geográfica",
    description="API que integra dados climáticos e geográficos de cidades brasileiras.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ============================================================================
# Configuração de CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Importação de Routers (Endpoints)
# ============================================================================

from app.api.endpoints import router as api_router

# Registrar router da API
app.include_router(api_router)


# ============================================================================
# Endpoint de Health Check (Temporário)
# ============================================================================

# @app.get("/api/v1/health", tags=["Health"])
# async def health_check() -> dict:
#     """
#     Verifica o status da saúde da aplicação.
    
#     Returns:
#         dict: Status da aplicação
#     """
#     return {
#         "status": "healthy",
#         "message": "API está operacional"
#     }


# ============================================================================
# Tratamento de Exceções Global
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Tratador para erros de validação."""
    logger.error(f"Erro de validação: {str(exc)}")
    return {"detail": str(exc)}, 400


# ============================================================================
# Evento de Startup
# ============================================================================

# @app.on_event("startup")
async def on_startup():
    """Executa configurações iniciais."""
    setup_logging()
    logger.info("Logging configurado com sucesso")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> dict:
    """Endpoint raiz da API."""
    return {
        "nome": "API de Agregação Climática e Geográfica",
        "versão": "1.0.0",
        "documentacao": "http://localhost:3000/docs"
    }


if __name__ == "__main__":
    # Para rodar localmente durante desenvolvimento
    import uvicorn
    port = int(os.getenv("API_PORT", 3000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
