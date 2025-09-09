# Use uma imagem base oficial do Python.
FROM python:3.12-slim

# Defina o diretório de trabalho no contêiner.
WORKDIR /app

# Copie o arquivo de dependências e instale-as.
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copie o restante do código da aplicação.
COPY ./app /app/app

# Comando para executar a aplicação.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
