#!/bin/bash

echo "📦 Instalando dependências de desenvolvimento..."
pip install -r requirements.txt

echo ""
echo "🎨 Formatando código com Black..."
black app/

echo ""
echo "📋 Organizando imports com isort..."
isort app/

echo ""
echo "✅ Verificando código com flake8..."
flake8 app/

echo ""
echo "✨ Configuração concluída!"
echo ""
echo "💡 Dicas:"
echo "  - Para formatar um arquivo específico: black app/main.py"
echo "  - Para formatar todo o projeto: black ."
echo "  - Para verificar sem modificar: black --check ."
echo "  - Para ver diferenças: black --diff ."

