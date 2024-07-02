# AI Help Desk Sample App

## 준비 

Create an environment using venv

MAC / Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 로컬 실행 

```bash
flask run 
```

## Deploy to Cloud Run

- GCP Project ID: <project-id>
- Search Widget ID: <search widget id>
- Service Account: <sa-name>@<project-id>.iam.gserviceaccount.com
- Agent ID (Dialogflow Messanger): <agent-id>
- OAuth Client ID: <oauth-client-id>


배포전 프로젝트 확인 
```bash
gcloud config get project
gcloud config set project sharp-ai-helpdesk-common
```
배포
```bash
gcloud run deploy <cloud-run-name> --service-account=<sa-name>@<project-id>.iam.gserviceaccount.com --platform=managed --ingress=all --port=8080 --region=asia-northeast3 --allow-unauthenticated --cpu=2 --memory=1Gi --session-affinity  --set-env-vars "WIDGET_ID=<search widget id>" --set-env-vars "AGENT_ID=<agent-id>" --set-env-vars "CLIENT_ID=<oauth-client-id>" --source . 
```



```bash
```