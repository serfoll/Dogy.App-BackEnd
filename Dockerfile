FROM python:3.11.4-slim

WORKDIR /assistant

COPY requirements.txt /assistant

RUN pip install -r --no-cache-dir requirements.txt

RUN uvicorn --version

COPY . /assistant

EXPOSE 8000

CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0"]
