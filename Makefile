# Payment Gateway - Makefile
# ========================
# Uso: make [target]
# Lista todos os targets: make help

.PHONY: help install install-backend install-frontend \
        dev dev-backend dev-frontend run \
        test test-cov test-fast test-watch \
        db-init db-migrate db-upgrade db-seed db-reset db-shell \
        build up down restart logs \
        prod prod-stop \
        lint lint-frontend clean fclean

# Variáveis
PYTHON ?= python3
PIP ?= pip
FLASK_APP ?= run:app
PORT ?= 5001
VENV ?= venv
DOCKER_COMPOSE ?= docker-compose

# =============================================================================
# HELP
# =============================================================================

help:
	@echo "💳 Payment Gateway - Comandos disponíveis"
	@echo ""
	@echo "  🚀 INÍCIO RÁPIDO"
	@echo "    setup            Setup completo (install + db-init + db-seed)"
	@echo "    check            Verifica ambiente (Python, Node, Redis)"
	@echo "    dev              Inicia backend + frontend em paralelo"
	@echo "    dev-full         Setup + Dev (primeira vez)"
	@echo ""
	@echo "  📦 INSTALAÇÃO"
	@echo "    install          Instala backend + frontend"
	@echo "    install-backend  Instala dependências Python"
	@echo "    install-frontend Instala dependências Node"
	@echo ""
	@echo "  💻 DESENVOLVIMENTO"
	@echo "    dev-backend      Apenas backend (porta $(PORT))"
	@echo "    dev-frontend     Apenas frontend (porta 5173)"
	@echo "    run              Backend com python run.py"
	@echo "    celery           Inicia Celery worker"
	@echo "    redis-local      Inicia Redis local"
	@echo ""
	@echo "  🧪 TESTES"
	@echo "    test             Testes completos com cobertura"
	@echo "    test-fast        Testes sem cobertura"
	@echo "    test-cov         Testes + report HTML"
	@echo ""
	@echo "  💾 BANCO DE DADOS"
	@echo "    db-init          Cria tabelas"
	@echo "    db-seed          Popula dados iniciais"
	@echo "    db-migrate       Cria nova migration"
	@echo "    db-upgrade       Aplica migrations"
	@echo "    db-reset         Reset completo (APAGA TUDO)"
	@echo "    db-backup        Backup do banco SQLite"
	@echo "    db-shell         Shell interativo"
	@echo ""
	@echo "  🐳 DOCKER"
	@echo "    build            Build da imagem"
	@echo "    up               Sobe todos os containers"
	@echo "    down             Para containers"
	@echo "    restart          Reinicia containers"
	@echo "    logs             Mostra logs"
	@echo ""
	@echo "  🚀 PRODUÇÃO"
	@echo "    prod             Inicia com Gunicorn"
	@echo "    prod-stop        Para Gunicorn"
	@echo "    frontend-build   Build do frontend"
	@echo ""
	@echo "  🛠️  UTILITÁRIOS"
	@echo "    lint             Lint backend + frontend"
	@echo "    clean            Remove cache (mantém DB)"
	@echo "    fclean           Limpeza completa"

# =============================================================================
# SETUP
# =============================================================================

install: install-backend install-frontend
	@echo "✓ Instalação concluída"

install-backend:
	@echo "Instalando dependências Python..."
	$(PIP) install -r requirements.txt
	@echo "✓ Backend instalado"

install-frontend:
	@echo "Instalando dependências Node..."
	cd frontend && npm install
	@echo "✓ Frontend instalado"

# =============================================================================
# DESENVOLVIMENTO
# =============================================================================

dev:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	@echo "  Backend: http://localhost:$(PORT)"
	@echo "  Frontend: http://localhost:5173"
	@echo ""
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Iniciando backend em http://localhost:$(PORT)"
	$(PYTHON) run.py

dev-frontend:
	@echo "Iniciando frontend em http://localhost:5173"
	cd frontend && npm run dev

dev-full: db-init db-seed
	@echo "🚀 Setup completo + Dev"
	@make dev

run:
	@echo "Backend: http://localhost:$(PORT)"
	FLASK_APP=$(FLASK_APP) PORT=$(PORT) $(PYTHON) run.py

celery:
	@echo "Iniciando Celery worker..."
	celery -A celery_worker.celery worker --loglevel=info

redis-local:
	@echo "Iniciando Redis local..."
	redis-server

# =============================================================================
# TESTES
# =============================================================================

test:
	@echo "Executando testes com cobertura..."
	$(PYTHON) -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html
	@echo "✓ Relatório HTML: htmlcov/index.html"

test-fast:
	@echo "Executando testes (rápido, sem cobertura)..."
	$(PYTHON) -m pytest tests/ -v --tb=short -q --no-cov
	@echo "✓ Testes concluídos"

test-cov:
	@echo "Executando testes + cobertura..."
	$(PYTHON) -m pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term
	@echo "✓ Abra htmlcov/index.html"

# =============================================================================
# BANCO DE DADOS
# =============================================================================

db-init:
	@echo "Criando tabelas..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask init-db
	@echo "✓ Banco inicializado"

db-migrate:
	@echo "Criando migration..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db migrate -m "$(msg)"
	@echo "✓ Migration criada (msg='descrição')"

db-upgrade:
	@echo "Aplicando migrations..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db upgrade
	@echo "✓ Migrations aplicadas"

db-seed:
	@echo "Populando banco..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask seed-db
	@echo "✓ Seed concluído"

db-reset:
	@echo "⚠️  ATENÇÃO: Isso vai apagar TODOS os dados!"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ]
	@rm -f gateway.db
	@make db-init db-seed
	@echo "✓ Banco resetado completamente"

db-shell:
	@echo "Abrindo shell do banco..."
	$(PYTHON) -c "from run import app, db; from app.models import *; app.app_context().push(); import code; code.interact(local=locals())"

db-backup:
	@echo "Fazendo backup do banco..."
	@mkdir -p backups
	@cp gateway.db backups/gateway_$(shell date +%Y%m%d_%H%M%S).db
	@echo "✓ Backup salvo em backups/"

# =============================================================================
# PRODUÇÃO - DOCKER
# =============================================================================

build:
	@echo "Build da imagem Docker..."
	$(DOCKER_COMPOSE) build
	@echo "✓ Imagem construída"

up:
	@echo "Subindo serviços (PostgreSQL + Redis + App + Celery)..."
	$(DOCKER_COMPOSE) up -d
	@echo "✓ API: http://localhost:5000"
	@echo "  Execute 'make db-upgrade db-seed' após primeiro up"

down:
	@echo "Parando containers..."
	$(DOCKER_COMPOSE) down
	@echo "✓ Containers parados"

restart: down up

logs:
	$(DOCKER_COMPOSE) logs -f

# =============================================================================
# PRODUÇÃO - LOCAL (Gunicorn)
# =============================================================================

prod:
	@echo "Iniciando com Gunicorn (4 workers)..."
	gunicorn --bind 0.0.0.0:$(PORT) --workers 4 --timeout 120 run:app

prod-stop:
	@pkill -f "gunicorn.*run:app" || true
	@echo "✓ Gunicorn parado"

# =============================================================================
# FRONTEND - BUILD
# =============================================================================

frontend-build:
	@echo "Build do frontend para produção..."
	cd frontend && npm run build
	@echo "✓ Arquivos em frontend/dist/"

frontend-preview:
	cd frontend && npm run preview

# =============================================================================
# UTILITÁRIOS
# =============================================================================

lint:
	@echo "Lint backend..."
	$(PYTHON) -m pyflakes app/ 2>/dev/null || true
	@echo "Lint frontend..."
	cd frontend && npm run lint 2>/dev/null || true
	@echo "✓ Lint concluído"

lint-frontend:
	cd frontend && npm run lint

clean:
	@echo "Limpando cache e arquivos gerados (mantém banco de dados)..."
	rm -rf htmlcov/ .pytest_cache/ .coverage
	rm -rf __pycache__/ app/__pycache__/ app/*/__pycache__/ tests/__pycache__/
	rm -rf frontend/dist/ frontend/node_modules/.vite/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Limpeza concluída"

fclean: clean
	@echo "Removendo banco de dados local e arquivos de teste..."
	rm -f gateway.db *.sqlite *.sqlite3
	rm -rf .tox/ backups/
	@echo "✓ Limpeza completa. Execute 'make db-init db-seed' para recriar o banco."

setup: install db-init db-seed
	@echo ""
	@echo "✅ Setup completo!"
	@echo ""
	@echo "Para iniciar o desenvolvimento:"
	@echo "  make dev"
	@echo ""
	@echo "Credenciais de login:"
	@echo "  Admin: admin@gateway.com / admin123"
	@echo "  Tenant: user@samplestore.com / user123"

check:
	@echo "🔍 Verificando ambiente..."
	@$(PYTHON) --version
	@echo "Flask: $(shell pip show flask 2>/dev/null | grep Version || echo 'não instalado')"
	@echo "Node: $(shell node --version 2>/dev/null || echo 'não instalado')"
	@echo "Redis: $(shell redis-cli --version 2>/dev/null || echo 'não instalado')"
	@echo "✓ Verificação concluída"
