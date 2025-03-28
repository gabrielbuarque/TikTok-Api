FROM python:3.10

WORKDIR /app
COPY . /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && playwright install --with-deps

# Copia o código
COPY . .

# Expõe porta para EasyPanel
EXPOSE 8162

# Comando para rodar a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8162"]
