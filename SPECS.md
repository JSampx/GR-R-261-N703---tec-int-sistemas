

# Especificações Técnicas: API de Agregação de Dados Climáticos e Geográficos

## Objetivo
Desenvolver uma API REST que integre APIs públicas para fornecer informações combinadas sobre cidades brasileiras, incluindo dados geográficos e climáticos. O processamento para identificar a cidade, buscar informações geográficas, obter coordenadas e consultar dados climáticos deve ser feito internamente pela aplicação.

## Requisitos de Implementação
* **Linguagem:** Python com FastAPI.
* **Porta Padrão:** A API deve rodar na porta 3000.
* **Implantação:** Docker para subir o serviço.
* **Formato de Resposta:** Todas as respostas devem ser estritamente em JSON.
* **Encoding:** Suporte a caracteres especiais (UTF-8).
* **Documentação** Swagger (OpenAPI).
* **Liguagem Padrão** Utilizar português brasileiro em todos os comentários e documentações.

## Endpoints 

### 1. Informações da Cidade com Clima
* **Rota:** `GET /api/v1/clima/{nome_cidade}` 
* **Regra:** O usuário informa apenas o nome da cidade (obrigatório, string). Não é permitido utilizar coordenadas fixas no código.
* **Códigos de Retorno:** 200 (Sucesso) , 404 (Cidade não encontrada) 400 (Nome inválido), 503 (Serviço externo indisponível).

### 2. Listagem de Cidades por Estado
* **Rota:** `GET /api/v1/cidades/{sigla_uf}` 
* **Parâmetros:** `sigla_uf` (Obrigatório, string 2 caracteres). 
* **Query Parameters:** `limite` (Opcional, integer, default: 10, range: 1-100).
* **Códigos de Retorno:** 200 (Sucesso) , 404 (UF não encontrada) , 400 (Sigla UF inválida).

### 3. Health Check
* **Rota:** `GET /api/v1/health`
* **Códigos de Retorno:** 200 (healthy ou degraded).

## Testes Automatizados
* Implementar no mínimo 2 testes automatizados na pasta `/tests`.
* Cenários obrigatórios: Resposta correta para nome de cidade válido e tratamento de erro para cidade não encontrada.

## APIs Externas Sugeridas
* **Brasil API - IBGE:** Informações sobre estados e municípios (https://brasilapi.com.br/docs#tag/IBGE).
* **Brasil API - CPTEC:** Dados meteorológicos (https://brasilapi.com.br/docs#tag/CPTEC).

