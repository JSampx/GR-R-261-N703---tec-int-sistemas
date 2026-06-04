# Guia de Desenvolvimento

## Setup Local para Desenvolvimento

### Pré-requisitos
- Python 3.9+
- pip ou poetry
- Git (opcional)

### Instalação de Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Executar Aplicação Localmente

```bash
# Com reload automático (desenvolvimento)
uvicorn app.main:app --reload --port 3000

# Ou use o main.py diretamente
python app/main.py
```

A API estará disponível em: **http://localhost:3000**
- Documentação Swagger: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

### Variáveis de Ambiente

Copiar `.env.example` para `.env` e ajustar conforme necessário:

```bash
cp .env.example .env
```

## Executar Testes

```bash
# Rodar todos os testes
pytest

# Rodar com verbose
pytest -v

# Rodar teste específico
pytest tests/test_endpoints.py::TestCityClimateEndpoint::test_valid_city_weather_returns_200

# Rodar com cobertura
pytest --cov=app tests/
```

## Estrutura do Projeto

```
.
├── app/                          # Aplicação principal
│   ├── main.py                   # Inicialização FastAPI
│   ├── api/
│   │   └── endpoints.py          # Definição de endpoints
│   ├── models/
│   │   └── schemas.py            # Modelos Pydantic
│   ├── services/
│   │   ├── external_apis.py      # Integração com APIs externas
│   │   └── weather_aggregator.py # Orquestração de serviços
│   └── utils/
│       ├── logger.py             # Sistema de logging
│       └── cache.py              # Cache simples em memória
├── tests/                        # Testes automatizados
│   ├── conftest.py               # Configuração pytest
│   ├── test_endpoints.py         # Testes de endpoints
│   └── test_services.py          # Testes de serviços
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore                    # Padrões para ignorar no Git
├── Dockerfile                    # Configuração Docker
├── .dockerignore                 # Padrões para ignorar no Docker
├── pytest.ini                    # Configuração pytest
├── README.md                     # Documentação principal
└── SPECS.md                      # Especificações técnicas
```

## Padrões de Código

### Logging

Use o logger estruturado do módulo `app.utils.logger`:

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Mensagem de informação", context_key="value")
logger.error("Erro ocorreu", error_details="...")
```

### Async/Await

Todos os endpoints devem ser `async`. Use `async with` para clients HTTP:

```python
async def get_data() -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        return response.json()
```

### Validação com Pydantic

Sempre defina schemas Pydantic para respostas:

```python
from pydantic import BaseModel, Field

class MyResponse(BaseModel):
    field1: str = Field(..., description="Descrição do campo")
    field2: int = Field(default=0, ge=0, le=100)
```

### Tratamento de Exceções

Use HTTPException do FastAPI para retornar erros padronizados:

```python
raise HTTPException(
    status_code=400,
    detail="Descrição do erro"
)
```

## Adicionar Nova API Externa

1. Criar serviço em `app/services/external_apis.py`:

```python
class NewAPIService:
    BASE_URL = "https://api.example.com"
    
    @classmethod
    async def get_data(cls, param: str) -> Dict:
        # Implementar integração
        pass
```

2. Atualizar `app/services/weather_aggregator.py` para usar o novo serviço

3. Adicionar testes em `tests/test_services.py`

## Build Docker

```bash
# Build da imagem
docker build -t clima-api .

# Executar container
docker run -p 3000:3000 \
  -e API_PORT=3000 \
  -e LOG_LEVEL=INFO \
  clima-api

# Testar API dentro do container
curl http://localhost:3000/api/v1/health
```

## Troubleshooting

### "Module not found" errors
- Verificar se ambiente virtual está ativado: `source venv/bin/activate`
- Reinstalar dependências: `pip install -r requirements.txt`

### Portas em uso
- Verificar qual processo está usando porta 3000: `lsof -i :3000`
- Usar porta diferente: `uvicorn app.main:app --port 3001`

### Testes falhando
- Verificar se `.env` existe e está configurado corretamente
- Limpar cache pytest: `rm -rf .pytest_cache`
- Rodar teste específico com verbose: `pytest -vv tests/test_file.py`

## Leitura Adicional

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [Pytest Documentation](https://docs.pytest.org/)
