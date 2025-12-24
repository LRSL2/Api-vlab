# Vlab API - Gateway para Data Lake de Abastecimento

API desenvolvida para o desafio técnico V-Lab, focada em ingestão e consulta de dados de abastecimento da frota nacional.

## 🚀 Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web assíncrono
- **SQLAlchemy** - ORM com suporte async
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache
- **Alembic** - Migrations de banco de dados
- **Docker** - Containerização
- **Pytest** - Testes automatizados

## 🏗️ Arquitetura

```
app/
├── api/v1/           # Endpoints da API
├── core/             # Configurações (database, security, logging)
├── models/           # Models do SQLAlchemy
├── schemas/          # Schemas Pydantic
├── services/         # Lógica de negócio
├── routers/          # Routers adicionais
├── utils/            # Utilitários (validators, enums)
└── test/             # Testes automatizados
```

## 🔧 Instalação
### Setup Local

```bash
# Clonar repositório
git clone https://github.com/LRSL2/Api-vlab.git
cd Api-vlab

# Criar ambiente virtual
python3 -m venv venv

# Configurar variáveis de ambiente
adicione:
"DATABASE_URL=postgresql+asyncpg://vlab:vlab@localhost:5432/vlab_db
API_KEY=vlab-secret-key
LOG_LEVEL=INFO"
ao final do arquivo activate do venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento

# Rodar migrations
alembic upgrade head

# Iniciar aplicação
docker-compose up --build

# API disponível em http://localhost:8000/docs
```

## 📚 Documentação da API

Acesse a documentação interativa:
- Swagger UI: http://localhost:8000/docs

### Endpoints Principais

#### POST /api/v1/
Cria um novo registro de abastecimento (requer autenticação).

```bash
curl -X POST http://localhost:8000/api/v1/ \
  -H "X-API-Key: vlab-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": 1,
    "timestamp": "2024-12-20T12:00:00Z",
    "fuel_type": "GASOLINA",
    "price_per_liter": "5.50",
    "volume_liters": "40",
    "driver_cpf": "11144477735"
  }'
```

#### GET /api/v1/refuelings
Lista abastecimentos com paginação e filtros.

```bash
# Com filtros
curl "http://localhost:8000/api/v1/refuelings?fuel_type=GASOLINA&page=1&size=10"

# Resposta:
{
  "total": 150,
  "page": 1,
  "size": 10,
  "data": [...]
}
```

#### GET /api/v1/motoristas/{cpf}/historico
Histórico de abastecimentos de um motorista.

```bash
curl "http://localhost:8000/api/v1/motoristas/11144477735/historico?page=1&size=10"
```

#### GET /health
Status da aplicação e conexão com banco.

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=app

# Testes específicos
pytest app/test/test_validators.py -v
```

## 🎨 Linters e Formatação

```bash
# Formatar código automaticamente
make format

# Verificar código
make lint

# Ver documentação completa
cat docs/LINTERS.md
```

## 📊 Script de Carga

Para testar a API com dados aleatórios:

```bash
# Configurar variáveis
export API_URL="http://localhost:8000/api/v1/"
export API_KEY="vlab-secret-key"

# Rodar script
python load_data.py
```

## 🔐 Autenticação

A API usa autenticação via API Key no header:

```
X-API-Key: vlab-secret-key
```

Configure a chave no arquivo `.env`:
```
API_KEY=sua-chave-secreta
```

## 🗄️ Migrations

```bash
# Criar nova migration
alembic revision --autogenerate -m "Descrição"

# Aplicar migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Ver histórico
alembic history
```

## 📝 Variáveis de Ambiente

```bash
DATABASE_URL=postgresql+asyncpg://vlab:vlab@localhost:5432/vlab_db
API_KEY=vlab-secret-key
LOG_LEVEL=INFO
```

## 🛠️ Comandos Make

```bash
make help          # Ver todos os comandos
make format        # Formatar código
make lint          # Verificar código
make test          # Rodar testes
make run           # Iniciar aplicação
make docker-up     # Subir Docker
make docker-down   # Parar Docker
make clean         # Limpar cache
```
# Cobertura dos testes:
<img src="https://github.com/LRSL2/Api-vlab/blob/36baca43496c645c2bb7045786d709a05f510880/coverage_Api-vlab.png" alt="" width="300px" />
