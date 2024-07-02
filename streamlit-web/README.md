# AI Help Desk 웹앱 with Streamlit

## 준비 
[Streamlit 설치](https://docs.streamlit.io/get-started/installation)

Create an environment using venv

MAC / Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 로컬 실행 

```bash
streamlit run 검색.py
```

## Deploy to Cloud Run

```bash
export GCP_PROJECT='<Your GCP Project Id>'
export GCP_REGION='asia-northeast3'
export AR_REPO='<REPLACE_WITH_YOUR_AR_REPO_NAME>' 
export SERVICE_NAME='sharp-ai-web'

gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$GCP_REGION \
  --platform=managed  \
  --project=$GCP_PROJECT \
  --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION
```

```bash
export GCP_PROJECT='<project-id>'
export GCP_REGION='asia-northeast3'
export AR_REPO='<artificial-repo>' 
export SERVICE_NAME='ai-help-desk'

gcloud init
gcloud config set project <project_id>
gcloud run deploy sharp-ai-chatbot-manual-search --service-account=<service_account_id>@<project_id>.iam.gserviceaccount.com --platform=managed --ingress=all --port=8080 --region=asia-northeast3 --set-env-vars "PROJECT_ID=<project_id>" --set-env-vars "ENGINE_ID=<datasource_id>" --source . 

gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$GCP_REGION \
  --platform=managed  \
  --project=$GCP_PROJECT \
  --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION
```