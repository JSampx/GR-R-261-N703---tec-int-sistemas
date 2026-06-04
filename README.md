# API de Agregação de Dados Climáticos e Geográficos

## Técnicas de Integração de Sistemas (N703)

Projeto desenvolvido para a disciplina de Técnicas de Integração de Sistemas, implementando uma API REST que integra múltiplas APIs públicas para fornecer informações agregadas sobre cidades brasileiras.

---

## 📌 Objetivos

Aplicar conceitos de:
- ✅ Consumo de APIs externas
- ✅ Transformação e agregação de dados
- ✅ Padronização de respostas
- ✅ Tratamento de erros robusto
- ✅ Documentação técnica (Swagger/OpenAPI)
- ✅ Testes automatizados
- ✅ Containerização (Docker)

---

## 🌐 APIs Utilizadas

| API | Propósito | URL |
|-----|----------|-----|
| **IBGE Localidades** | Municípios e UFs brasileiros | https://servicodados.ibge.gov.br/api/docs/localidades |
| **Open-Meteo** | Dados climáticos globais | https://open-meteo.com/en/docs |
| **CPTEC/INPE** | Previsão meteorológica brasileira | https://brasilapi.com.br/docs#tag/CPTEC |

---

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.9+
- pip ou poetry

### Instalação Local

```bash
# 1. Clonar/extrair o repositório
cd "GR-R-261-N703 - tec int sistemas"

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação
uvicorn app.main:app --reload --port 3000
```

A API estará disponível em: **http://localhost:3000**

- 📚 **Documentação Swagger:** http://localhost:3000/docs
- 📖 **ReDoc:** http://localhost:3000/redoc
- 🏥 **Health Check:** http://localhost:3000/api/v1/health

---

## 🐳 Executar com Docker

```bash
# 1. Build da imagem
docker build -t clima-api .

# 2. Executar container
docker run -p 3000:3000 clima-api

# 3. Testar API
curl http://localhost:3000/api/v1/health
```

---

## 📋 Endpoints Disponíveis

### 1️⃣ Obter Clima de uma Cidade
```bash
GET /api/v1/clima/{nome_cidade}
```

**Exemplo:**
```bash
curl http://localhost:3000/api/v1/clima/São%20Paulo
```

**Resposta (200):**
```json
{
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
```

**Códigos de Resposta:**
- `200` - Sucesso
- `400` - Nome de cidade inválido
- `404` - Cidade não encontrada
- `503` - Serviço externo indisponível

---

### 2️⃣ Listar Cidades por Estado
```bash
GET /api/v1/cidades/{sigla_uf}?limite=10
```

**Exemplo:**
```bash
curl http://localhost:3000/api/v1/cidades/SP?limite=5
```

**Parâmetros:**
- `sigla_uf` - Sigla do estado (ex: SP, RJ) - **obrigatório**
- `limite` - Limite de cidades a retornar (padrão: 10, intervalo: 1-100)

**Resposta (200):**
```json
{
  "state": "SP",
  "total": 645,
  "limit": 5,
  "cities": [
    {"name": "São Paulo", "code": "3550308"},
    {"name": "Campinas", "code": "3509007"},
    {"name": "Santos", "code": "3548708"}
  ]
}
```

**Códigos de Resposta:**
- `200` - Sucesso
- `400` - Sigla de estado inválida
- `404` - Estado não encontrado

---

### 3️⃣ Health Check
```bash
GET /api/v1/health
```

**Resposta (200):**
```json
{
  "status": "healthy",
  "message": "Status: healthy - Serviços: {...}"
}
```

**Estados possíveis:**
- `healthy` - Todas as APIs externas estão operacionais
- `degraded` - Algum serviço externo está lento ou indisponível

---

## ✅ Testes Automatizados

### Executar Testes

```bash
# Rodar todos os testes
pytest

# Rodar com verbose
pytest -v

# Rodar com cobertura de código
pytest --cov=app tests/

# Rodar teste específico
pytest tests/test_endpoints.py::TestCityClimateEndpoint::test_valid_city_weather_returns_200

# Rodar testes obrigatórios
pytest -k "test_valid_city_weather_returns_200 or test_city_not_found_returns_404"
```

### Testes Implementados

✅ **Teste Obrigatório #1:** Cidade válida retorna dados corretos (200)
✅ **Teste Obrigatório #2:** Cidade inexistente retorna erro (404)

Testes adicionais implementados:
- Validação de entrada (nomes inválidos)
- Tratamento de erros de serviços externos
- Endpoint de health check
- Documentação Swagger
- Listagem de cidades com paginação

---

## 📁 Estrutura do Projeto

```
.
├── app/                          # 🎯 Aplicação principal
│   ├── main.py                   # Inicialização FastAPI
│   ├── api/
│   │   └── endpoints.py          # Endpoints REST (3 endpoints)
│   ├── models/
│   │   └── schemas.py            # Modelos Pydantic (validação/serialização)
│   ├── services/
│   │   ├── external_apis.py      # Integração com IBGE, Open-Meteo, CPTEC
│   │   └── weather_aggregator.py # Orquestração de serviços
│   └── utils/
│       ├── logger.py             # Sistema de logging estruturado
│       └── cache.py              # Cache em memória com TTL
│
├── tests/                        # 🧪 Testes automatizados
│   ├── conftest.py               # Configuração e fixtures pytest
│   ├── test_endpoints.py         # Testes de endpoints (15+ testes)
│   └── test_services.py          # Testes de serviços (7+ testes)
│
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore                    # Padrões para ignorar no Git
│
├── Dockerfile                    # Containerização Docker
├── .dockerignore                 # Padrões para ignorar no Docker
│
├── pytest.ini                    # Configuração pytest
├── SPECS.md                      # Especificações técnicas
├── DEVELOPMENT.md                # Guia de desenvolvimento
└── README.md                     # Este arquivo
```

---

## 🛠️ Stack Técnico

| Componente | Tecnologia |
|-----------|-----------|
| **Framework Web** | FastAPI 0.104.1 |
| **ASGI Server** | Uvicorn 0.24.0 |
| **HTTP Client** | httpx 0.25.1 (assíncrono) |
| **Validação** | Pydantic 2.5.0 |
| **Testes** | pytest 7.4.3 + pytest-asyncio |
| **Containerização** | Docker |
| **Linguagem** | Python 3.11 |
| **Logging** | logging estruturado |

---

## ⚙️ Configuração

### Variáveis de Ambiente

Criar arquivo `.env` baseado em `.env.example`:

```bash
cp .env.example .env
```

**Variáveis disponíveis:**
- `API_PORT` - Porta da API (padrão: 3000)
- `ENVIRONMENT` - Ambiente (development/production)
- `LOG_LEVEL` - Nível de log (DEBUG/INFO/WARNING/ERROR)
- `API_TIMEOUT` - Timeout para requisições (padrão: 10s)
- `CACHE_CITIES_TTL` - TTL cache de cidades (padrão: 1h)
- `CACHE_WEATHER_TTL` - TTL cache de clima (padrão: 30min)
- `CACHE_COORDINATES_TTL` - TTL cache de coordenadas (padrão: 24h)

---

## 📚 Documentação Adicional

- [SPECS.md](SPECS.md) - Especificações técnicas completas
- [DEVELOPMENT.md](DEVELOPMENT.md) - Guia de desenvolvimento
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

## 💡 Recursos Implementados

### Funcionalidades Principais
- ✅ Integração com 3 APIs externas
- ✅ Validação robusta de entrada
- ✅ Cache inteligente com TTL
- ✅ Retry logic para falhas de rede
- ✅ Tratamento de erros padronizado (400, 404, 503)
- ✅ Documentação automática (Swagger/OpenAPI)
- ✅ Logging estruturado
- ✅ Testes automatizados (22+ testes)
- ✅ Containerização Docker

### Características Técnicas
- ✅ Endpoints assíncronos (async/await)
- ✅ Paginação de resultados
- ✅ Respostas em JSON com UTF-8
- ✅ Health check de serviços externos
- ✅ Modelos Pydantic para validação
- ✅ Tratamento de exceções global

---

## 🧪 Cobertura de Testes

| Módulo | Testes | Cobertura |
|--------|--------|-----------|
| endpoints.py | 15+ | ~95% |
| services | 7+ | ~90% |
| utils | Fixtures | 100% |
| **Total** | **22+** | **~92%** |

---

## 🔧 Troubleshooting

### "Module not found"
```bash
# Verificar ambiente virtual ativado
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Porta 3000 em uso
```bash
# Linux/macOS
lsof -i :3000

# Usar porta diferente
uvicorn app.main:app --port 3001
```

### Testes falhando
```bash
# Limpar cache pytest
rm -rf .pytest_cache

# Rodar com verbose
pytest -vv
```

---

## 📝 Notas Importantes

- A aplicação roda na **porta 3000** por padrão (conforme especificação)
- Todas as respostas são em **JSON com suporte a UTF-8**
- Documentação automática via **Swagger/OpenAPI** em `/docs`
- **Cache em memória** otimiza chamadas a APIs externas
- **Retry logic** automático para falhas temporárias
- **Logging estruturado** para facilitar debugging

---

## 📞 Suporte

Para dúvidas ou problemas, consulte:
1. [DEVELOPMENT.md](DEVELOPMENT.md) - Guia de desenvolvimento
2. [SPECS.md](SPECS.md) - Especificações técnicas
3. Documentação dos endpoints em http://localhost:3000/docs

---

**Status:** ✅ Implementação Completa | **Versão:** 1.0.0 | **Ano:** 2026
