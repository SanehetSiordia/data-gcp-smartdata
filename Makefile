-include .env
export

COMPOSE_FILE ?= compose.yml
ENV ?= .env

SERVICE_PYTHON ?= python_service
SERVICE_GCP ?= gcp_service
CONTAINER_GCP ?= $(DOCKER_GCP_NAME)
GCP_PROJECT_ID ?= $(GCP_PROJECT_ID)
GCP_SA_NAME ?= $(GCP_SA_NAME)
GCP_SA_EMAIL ?= $(GCP_SA_EMAIL)
GCP_KEY_FILE ?= $(GCP_KEY_FILE)

.PHONY: make-all create-gcp-docker create-python-docker setup-sa create-firewall-gcp

make-all: create-gcp-docker create-python-docker setup-sa create-firewall-gcp

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
		echo "=== Iniciando sesion de usuario para aprovisionamiento inicial ==="; \
		docker exec -it $(CONTAINER_GCP) gcloud auth login --no-launch-browser; \
		docker exec $(CONTAINER_GCP) gcloud config set project $(GCP_PROJECT_ID); \
		echo "=== Creando Service Account en GCP ==="; \
		-docker exec $(CONTAINER_GCP) gcloud iam service-accounts create $(GCP_SA_NAME) \
			--project=$(GCP_PROJECT_ID) \
			--display-name="Compute and Firewall Provisioner"; \
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
		docker exec $(CONTAINER_GCP) gcloud iam service-accounts keys create $(GCP_KEY_FILE) \
			--iam-account=$(GCP_SA_EMAIL) \
			--project=$(GCP_PROJECT_ID); \
		echo "Llave generada exitosamente en $(GCP_KEY_FILE)"; \
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