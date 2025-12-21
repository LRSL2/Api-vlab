# Linters e Formatação de Código

Este projeto utiliza ferramentas de linting e formatação automática para manter a qualidade e consistência do código.

## 🛠️ Ferramentas Configuradas

- **Black**: Formatação automática de código Python
- **isort**: Organização automática de imports
- **Ruff**: Linter rápido (substitui flake8, pylint, etc)
- **pre-commit**: Hooks para rodar linters antes de commits

## 📦 Instalação

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Instalar hooks do pre-commit (opcional)
pre-commit install
```

## 🚀 Uso

### Usando Make (Recomendado)

```bash
# Formatar código automaticamente
make format

# Verificar código (sem modificar)
make lint

# Ver todos os comandos disponíveis
make help
```

### Usando Scripts Diretos

```bash
# Formatar código
./scripts/format.sh

# Verificar código
./scripts/lint.sh
```

### Comandos Individuais

```bash
# Black - Formatar código
black app/ load_data.py

# Black - Apenas verificar (não modificar)
black --check app/

# isort - Organizar imports
isort app/ load_data.py

# isort - Apenas verificar
isort --check-only app/

# Ruff - Verificar problemas
ruff check app/

# Ruff - Auto-corrigir problemas
ruff check --fix app/
```

## ⚙️ Configuração

As configurações estão em `pyproject.toml`:

- **Comprimento de linha**: 100 caracteres
- **Versão Python**: 3.11
- **Black e isort**: Compatíveis entre si
- **Ruff**: Verifica erros de sintaxe, estilo, imports, etc

## 🔄 Pre-commit Hooks

Se você instalou os hooks do pre-commit, os linters rodarão automaticamente antes de cada commit:

```bash
# Instalar hooks
pre-commit install

# Rodar manualmente em todos os arquivos
pre-commit run --all-files
```

## 📋 Regras Principais

### Black
- Formatação consistente
- Strings com aspas duplas
- Linha máxima de 100 caracteres

### isort
- Imports organizados em grupos
- Compatível com Black
- Ordem: stdlib → third-party → first-party → local

### Ruff
- Detecta código morto
- Verifica nomenclatura (PEP8)
- Identifica bugs comuns
- Sugere melhorias (pyupgrade)

## 🎯 Fluxo de Trabalho

1. **Desenvolvimento**: Escreva código normalmente
2. **Antes do commit**: `make format` (formata automaticamente)
3. **Verificação**: `make lint` (verifica se está ok)
4. **Commit**: Se tudo passar, faça o commit

## 🔍 Verificação em CI/CD

Para integrar em pipelines de CI/CD:

```yaml
# Exemplo para GitHub Actions
- name: Run linters
  run: |
    pip install -r requirements-dev.txt
    make lint
```

## ❓ Troubleshooting

**"Command 'black' not found"**
```bash
pip install -r requirements-dev.txt
```

**"Imports não estão organizados"**
```bash
make format  # Isso corrigirá automaticamente
```

**"Linha muito longa"**
- Black quebra linhas automaticamente
- Se não conseguir, refatore o código em múltiplas linhas

