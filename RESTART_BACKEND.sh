#!/bin/bash

echo "🔄 Reiniciando backend com logs bonitos..."
echo ""

# Matar processos antigos
pkill -f "python.*run.py" 2>/dev/null
sleep 1

# Iniciar novo
cd /Users/tidos/Desktop/scripts
python3 run.py

