# Kubernetes Deployment Guide

This guide details how to deploy CreatorOS AI to a local Kubernetes cluster (e.g., Docker Desktop Kubernetes or Minikube).

## Prerequisites
- A running Kubernetes cluster (Docker Desktop Kubernetes recommended).
- `kubectl` configured to interact with your cluster.
- NGINX Ingress Controller installed in the cluster.
  *(For Docker Desktop, install it via:*
  `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.2/deploy/static/provider/cloud/deploy.yaml`
  *Then, to fix `ERR_CONNECTION_REFUSED` on Windows `localhost:80`, patch it to use hostNetwork:)*
  `kubectl patch deployment -n ingress-nginx ingress-nginx-controller --type='json' -p='[{"op": "add", "path": "/spec/template/spec/hostNetwork", "value": true}]'`

## 1. Local Image Building
Before deploying to Kubernetes locally, build the images using the Docker Compose configuration:
```bash
$env:DOCKER_BUILDKIT=0  # Required for some Windows environments
docker compose build
```
This ensures `creatoros-ai-backend:latest` and `creatoros-ai-frontend:latest` exist in your local Docker daemon registry.

## 2. Secrets Configuration
Copy the example secrets file and encode your actual secrets in Base64:
```bash
cp k8s/secrets.example.yaml k8s/secrets.yaml
```
*(Remember not to commit `k8s/secrets.yaml` to version control).*

Modify `k8s/secrets.yaml` to contain your Base64 encoded secrets under `data` (or keep using `stringData` for plain text during local development). 
For local development, `stringData` in `secrets.example.yaml` can be deployed directly for testing if you populate the placeholder keys.

## 3. Deployment Sequence

### 3.1. Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 3.2. Config and Secrets
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml  # Or secrets.example.yaml if testing
```

### 3.3. Infrastructure (PostgreSQL & Redis)
```bash
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/redis/
```
Wait until the pods are running:
```bash
kubectl get pods -n creatoros
```

### 3.4. Database Migration Job
```bash
kubectl apply -f k8s/jobs/alembic-migration.yaml
```
Verify the job completed successfully:
```bash
kubectl get jobs -n creatoros
kubectl logs job/alembic-migration -n creatoros
```

### 3.5. Application and Workers
```bash
kubectl apply -f k8s/backend/
kubectl apply -f k8s/scheduler/
kubectl apply -f k8s/analytics/
kubectl apply -f k8s/frontend/
```

### 3.6. Ingress
```bash
kubectl apply -f k8s/ingress/
```

## 4. Verification (Local Access)

For LOCAL development, you must route the `creatoros.local` domain to your local machine.

Add the ingress host to your local hosts file (`C:\Windows\System32\drivers\etc\hosts` on Windows, or `/etc/hosts` on Linux/Mac):
```text
127.0.0.1 creatoros.local
```

> [!NOTE]
> **LOCAL vs PRODUCTION:**
> - **LOCAL:** Always use `http://creatoros.local` and `http://creatoros.local/api/v1/docs`. This runs through your local Kubernetes Ingress (exposed on localhost:80 via `hostNetwork: true`).
> - **PRODUCTION:** Production deployments will use a real domain (e.g. `https://creatoros.com`) and will not require host file modifications.

Access the application in your browser:
- Frontend: `http://creatoros.local`
- API Docs: `http://creatoros.local/api/v1/docs`

## 5. Teardown
To cleanly remove all resources:
```bash
kubectl delete namespace creatoros
```
