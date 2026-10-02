# Kubernetes Deployment Guide

This directory contains production-ready manifests for deploying
ResumeFilter on Kubernetes.

---

## Prerequisites

| Component | Purpose | Install |
|---|---|---|
| **kubectl** | CLI | https://kubernetes.io/docs/tasks/tools/ |
| **Ingress-NGINX** | HTTP routing | `helm install ingress-nginx ingress-nginx/ingress-nginx` |
| **cert-manager** | TLS certificates | https://cert-manager.io/docs/installation/ |
| **KEDA** | Autoscaling workers | `helm install keda kedacore/keda` |
| **Metrics Server** | HPA | Usually pre-installed on managed clusters |

---

## Directory Structure
k8s/
├── namespace.yaml # Namespace definition
├── configmap.yaml # Non-sensitive config
├── secrets.yaml.example # Template for secrets
├── ingress.yaml # Ingress + TLS
├── postgres/
│ ├── statefulset.yaml
│ └── service.yaml
├── redis/
│ ├── deployment.yaml
│ └── service.yaml
├── minio/
│ ├── statefulset.yaml
│ └── service.yaml
├── api/
│ ├── deployment.yaml
│ ├── service.yaml
│ └── hpa.yaml
├── worker/
│ ├── deployment.yaml
│ └── keda-scaledobject.yaml
└── flower/
└── deployment.yaml

text

---

## Deployment Steps

### 1. Create the namespace

```bash
kubectl apply -f k8s/namespace.yaml
2. Create secrets
Option A — via kubectl (recommended):

bash
kubectl create secret generic resume-filter-secrets \
  --namespace resume-filter \
  --from-literal=SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" \
  --from-literal=MASTER_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -hex 32)" \
  --from-literal=MINIO_ROOT_USER="minioadmin" \
  --from-literal=MINIO_ROOT_PASSWORD="$(openssl rand -hex 32)" \
  --from-literal=MINIO_ACCESS_KEY="minioadmin" \
  --from-literal=MINIO_SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=PLATFORM_LLM_API_KEY="gsk_xxxxx" \
  --from-literal=UI_STORAGE_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
Option B — via YAML:

Copy secrets.yaml.example to secrets.yaml, fill in the values,
then apply it:

bash
kubectl apply -f k8s/secrets.yaml
3. Update the ConfigMap
Edit k8s/configmap.yaml and replace:

DATABASE_URL — use the actual PostgreSQL password

CORS_ORIGINS — your production domain

Then apply:

bash
kubectl apply -f k8s/configmap.yaml
4. Build and push Docker images
bash
# Replace `your-username` with your GitHub username.
docker build -t ghcr.io/your-username/resume-filter-api:latest -f docker/Dockerfile.api .
docker build -t ghcr.io/your-username/resume-filter-worker:latest -f docker/Dockerfile.worker .
docker push ghcr.io/your-username/resume-filter-api:latest
docker push ghcr.io/your-username/resume-filter-worker:latest
5. Deploy infrastructure
bash
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/redis/
kubectl apply -f k8s/minio/
Wait for readiness:

bash
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/component=postgres \
  -n resume-filter --timeout=120s

kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/component=redis \
  -n resume-filter --timeout=60s

kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/component=minio \
  -n resume-filter --timeout=120s
6. Run database migrations
bash
kubectl run resume-filter-migrate \
  --namespace resume-filter \
  --rm -it --restart=Never \
  --image=ghcr.io/your-username/resume-filter-api:latest \
  --env-from=configmap/resume-filter-config \
  --env-from=secret/resume-filter-secrets \
  -- alembic upgrade head
7. Deploy the application
bash
kubectl apply -f k8s/api/
kubectl apply -f k8s/worker/
kubectl apply -f k8s/flower/
8. Deploy ingress
Edit k8s/ingress.yaml and replace resume-filter.example.com
with your real domain, then:

bash
kubectl apply -f k8s/ingress.yaml
Verification
Check pods
bash
kubectl get pods -n resume-filter
Expected:

text
NAME                                        READY   STATUS    RESTARTS
resume-filter-api-xxxxx                     1/1     Running   0
resume-filter-api-yyyyy                     1/1     Running   0
resume-filter-worker-xxxxx                  1/1     Running   0
resume-filter-worker-yyyyy                  1/1     Running   0
resume-filter-postgres-0                    1/1     Running   0
resume-filter-redis-xxxxx                   1/1     Running   0
resume-filter-minio-0                       1/1     Running   0
resume-filter-flower-xxxxx                  1/1     Running   0
Check health endpoint
bash
kubectl port-forward -n resume-filter svc/resume-filter-api 8080:80
curl http://localhost:8080/health
Check the UI
Open in a browser: https://resume-filter.example.com/ui

Scaling
API (HPA)
Scale on CPU > 70% or memory > 80%. Min: 2, Max: 10.

bash
kubectl get hpa -n resume-filter
Workers (KEDA)
Scale on Celery queue length. Min: 1, Max: 20.

bash
kubectl get scaledobject -n resume-filter
kubectl get pods -n resume-filter -l app.kubernetes.io/component=worker -w
Updating
Roll out a new image
bash
docker build -t ghcr.io/your-username/resume-filter-api:v0.2.0 -f docker/Dockerfile.api .
docker push ghcr.io/your-username/resume-filter-api:v0.2.0

kubectl set image deployment/resume-filter-api \
  api=ghcr.io/your-username/resume-filter-api:v0.2.0 \
  -n resume-filter

kubectl rollout status deployment/resume-filter-api -n resume-filter
Roll back
bash
kubectl rollout undo deployment/resume-filter-api -n resume-filter
Cleanup
bash
kubectl delete namespace resume-filter
This deletes everything including PVCs. Back up first!

Troubleshooting
Pod stuck in Pending
bash
kubectl describe pod <pod-name> -n resume-filter
Usually caused by:

Insufficient cluster resources.

Missing StorageClass (check with kubectl get sc).

Pod in CrashLoopBackOff
bash
kubectl logs <pod-name> -n resume-filter --previous
Usually caused by:

Wrong secrets.

Database not reachable.

Missing migrations.

Ingress returns 502
Check that the API pods are Ready:

bash
kubectl get endpoints -n resume-filter
The resume-filter-api endpoint should have at least one IP.

Workers not scaling
bash
kubectl describe scaledobject resume-filter-worker-scaler -n resume-filter
kubectl logs -n keda deploy/keda-operator
Ensure KEDA is installed and the Redis address is correct.

Production Hardening Checklist
□ Replace all CHANGE_ME / replace-with placeholders.
□ Use strong random passwords (32+ hex chars).
□ Set APP_ENV=production and DEBUG=false.
□ Configure TLS via cert-manager.
□ Restrict CORS_ORIGINS to your real domain.
□ Enable network policies (restrict pod-to-pod traffic).
□ Configure PostgreSQL backups (e.g., via pg_dump CronJob).
□ Configure MinIO backups.
□ Set up log aggregation (Loki, ELK, ...).
□ Set up metrics (Prometheus + Grafana).
□ Configure alerts (health check failures, pod restarts).
□ Scan Docker images for vulnerabilities (Trivy).
□ Review RBAC and use least-privilege service accounts.
text

**احفظ وأغلق.**

---

## ✅ التحقق النهائي

```powershell
cd C:\Eban_projects\resume-filter
tree k8s /F
يجب أن ترى:

text
k8s/
├── README.md                 ← جديد
├── configmap.yaml
├── ingress.yaml
├── namespace.yaml
├── secrets.yaml.example
├── api/
│   ├── deployment.yaml
│   ├── hpa.yaml
│   └── service.yaml
├── flower/
│   └── deployment.yaml
├── minio/
│   ├── service.yaml
│   └── statefulset.yaml
├── postgres/
│   ├── service.yaml
│   └── statefulset.yaml
├── redis/
│   ├── deployment.yaml
│   └── service.yaml
└── worker/
    ├── deployment.yaml
    └── keda-scaledobject.yaml