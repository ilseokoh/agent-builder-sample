FROM python:3.11

EXPOSE 8080
WORKDIR /app

COPY . ./
COPY ./pages ./pages/

RUN pip install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "검색.py", "--server.port=8080", "--server.address=0.0.0.0"]