-include .env
export

# Evita que MSYS2 / Git Bash en Windows altere las rutas absolutas de Linux (/workspace)
export MSYS_NO_PATHCONV=1

COMPOSE_FILE ?= compose.yml
ENV ?= .env

SERVICE_PYTHON ?= python_service
SERVICE_GCP ?= gcp_service
CONTAINER_GCP ?= $(DOCKER_GCP_NAME)
GCP_PROJECT_ID ?= $(GCP_PROJECT_ID)
GCP_SA_NAME ?= $(GCP_SA_NAME)
GCP_SA_EMAIL ?= $(GCP_SA_EMAIL)
GCP_KEY_FILE ?= $(GCP_KEY_FILE)

MY_IP ?= $(shell curl -4 -s https://ifconfig.me)

.PHONY: up create-gcp-docker create-python-docker setup-sa create-firewall-gcp restrict-firewall-gcp down purge

up: create-gcp-docker create-python-docker setup-sa create-firewall-gcp

create-gcp-docker:
	@echo "=== Verificando estado del servicio $(SERVICE_GCP) ==="
	@if [ -z "$$(docker compose -f $(COMPOSE_FILE) ps -q $(SERVICE_GCP) 2>/dev/null)" ]; then \
		echo "=== Levantando servicio $(SERVICE_GCP) ==="; \
		docker compose -f $(COMPOSE_FILE) up -d $(SERVICE_GCP); \
	else \
		echo "El servicio $(SERVICE_GCP) ya esta activo."; \
	fi

create-python-docker:
	@echo "=== Verificando estado del servicio $(SERVICE_PYTHON) ==="
	@if [ -z "$$(docker compose -f $(COMPOSE_FILE) ps -q $(SERVICE_PYTHON) 2>/dev/null)" ]; then \
		echo "=== Levantando servicio $(SERVICE_PYTHON) ==="; \
		docker compose -f $(COMPOSE_FILE) up -d $(SERVICE_PYTHON); \
	else \
		echo "El servicio $(SERVICE_PYTHON) ya esta activo."; \
	fi

setup-sa: create-gcp-docker
	@mkdir -p credentials
	@if [ -f "./credentials/service_account_key.json" ]; then \
		echo "=== La llave de Service Account ya existe en ./credentials/. Omitiendo login inicial. ==="; \
	else \
		echo "=== Verificando sesion en gcloud CLI ==="; \
		if ! docker exec $(CONTAINER_GCP) gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then \
			docker exec -it $(CONTAINER_GCP) gcloud auth login --no-launch-browser; \
		fi; \
		docker exec $(CONTAINER_GCP) gcloud config set project $(GCP_PROJECT_ID); \
		echo "=== Habilitando APIs requeridas del proyecto ==="; \
		docker exec $(CONTAINER_GCP) gcloud services enable cloudresourcemanager.googleapis.com compute.googleapis.com; \
		echo "=== Creando Service Account en GCP ==="; \
		docker exec $(CONTAINER_GCP) gcloud iam service-accounts create $(GCP_SA_NAME) \
			--project=$(GCP_PROJECT_ID) \
			--display-name="Compute and Firewall Provisioner" || true; \
		echo "=== Asignando roles IAM necesarios ==="; \
		docker exec $(CONTAINER_GCP) gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
			--member="serviceAccount:$(GCP_SA_EMAIL)" \
			--role="roles/compute.instanceAdmin.v1"; \
		docker exec $(CONTAINER_GCP) gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
			--member="serviceAccount:$(GCP_SA_EMAIL)" \
			--role="roles/compute.securityAdmin"; \
		docker exec $(CONTAINER_GCP) gcloud projects add-iam-policy-binding $(GCP_PROJECT_ID) \
			--member="serviceAccount:$(GCP_SA_EMAIL)" \
			--role="roles/iam.serviceAccountUser"; \
		echo "=== Exportando llave JSON ==="; \
		MSYS_NO_PATHCONV=1 docker exec $(CONTAINER_GCP) gcloud iam service-accounts keys create credentials/service_account_key.json \
			--iam-account=$(GCP_SA_EMAIL) \
			--project=$(GCP_PROJECT_ID); \
		echo "Esperando 10 segundos a que la llave se propague en Google IAM..."; \
		sleep 10; \
		echo "Llave generada exitosamente en credentials/service_account_key.json"; \
	fi

create-firewall-gcp: create-gcp-docker
	@echo "=== Autenticando con Service Account en $(CONTAINER_GCP) ==="
	docker exec $(CONTAINER_GCP) gcloud auth activate-service-account --key-file=$(GCP_KEY_FILE)
	@echo "=== Fijando proyecto $(GCP_PROJECT_ID) ==="
	docker exec $(CONTAINER_GCP) gcloud config set project $(GCP_PROJECT_ID)
	@echo "=== Comprobando/Creando regla de firewall para PostgreSQL ==="
	@docker exec $(CONTAINER_GCP) gcloud compute firewall-rules describe allow-postgres-ingress --project=$(GCP_PROJECT_ID) >/dev/null 2>&1 || \
		docker exec $(CONTAINER_GCP) gcloud compute firewall-rules create allow-postgres-ingress \
			--project=$(GCP_PROJECT_ID) \
			--direction=INGRESS \
			--priority=1000 \
			--network=default \
			--action=ALLOW \
			--rules=tcp:5432 \
			--source-ranges=0.0.0.0/0 \
			--target-tags=postgres-server
			
restrict-firewall-gcp: create-firewall-gcp
	@if [ -z "$(MY_IP)" ]; then echo "No se pudo obtener la IP publica"; exit 1; fi
	@echo "=== Restringiendo tcp:5432 a $(MY_IP)/32 ==="
	docker exec $(CONTAINER_GCP) gcloud compute firewall-rules update allow-postgres-ingress \
		--project=$(GCP_PROJECT_ID) \
		--source-ranges=$(MY_IP)/32
	@docker exec $(CONTAINER_GCP) gcloud compute firewall-rules describe allow-postgres-ingress \
		--project=$(GCP_PROJECT_ID) --format="value(sourceRanges)"

down:
	docker compose -f $(COMPOSE_FILE) down
	@echo "=== Entorno detenido ==="

purge:
	docker compose -f $(COMPOSE_FILE) down -v
	docker builder prune -f
	@echo "=== Entorno detenido, volumenes y caches purgados ==="