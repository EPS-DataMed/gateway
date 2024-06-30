
# API Gateway
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_gateway&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_gateway) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_gateway&metric=coverage)](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_gateway) [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_gateway&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_gateway)

Este projeto é um API Gateway construído utilizando FastAPI. Ele redireciona requisições para diferentes serviços internos com autenticação baseada em tokens JWT.

## Estrutura do Projeto

- `main.py`: Contém a aplicação FastAPI e a lógica para redirecionamento de requisições.
- `tests/`: Contém testes unitários para as funcionalidades do API Gateway.
- `requirements.txt`: Lista de dependências do projeto.
- `Dockerfile`: Dockerfile para criação da imagem Docker do projeto.
- `docker-compose.yml`: Arquivo para orquestração dos serviços Docker.
- `.env`: Arquivo contendo variáveis de ambiente necessárias para o projeto.

## Dependências

- Python 3.10
- FastAPI
- httpx
- PyJWT
- pytest
- pytest-asyncio
- pytest-cov
- python-dotenv

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` no diretório raiz do projeto com o seguinte conteúdo:

```
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
AUTH_SERVICE_NAME=authentication-kw8k
USER_SERVICE_NAME=user-service-evf6
FILE_SERVICE_NAME=file-manager-iuhn
DATA_SERVICE_NAME=data-processing-otv0
TERM_SERVICE_NAME=term-service
SERVICE_DOMAIN=onrender.com
```

### Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    ```

2. Navegue até o diretório do projeto:
    ```bash
    cd seu-repositorio
    ```

3. Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venvScriptsactivate`
    ```

4. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Executando a Aplicação

1. Execute a aplicação:
    ```bash
    uvicorn main:app --reload
    ```

A aplicação estará disponível em `http://127.0.0.1:8000`.

### Testes

1. Para rodar os testes:
    ```bash
    pytest --asyncio-mode=auto --cov=main --cov-report=term-missing
    ```

## Docker

### Construir e Executar com Docker

1. Construir a imagem Docker:
    ```bash
    docker-compose build
    ```

2. Executar o container:
    ```bash
    docker-compose up
    ```

A aplicação estará disponível em `http://127.0.0.1:8000`.

### Executar Testes em Docker

1. Para executar os testes:
    ```bash
    docker-compose run test
    ```
