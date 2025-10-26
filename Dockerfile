# Dockerfile Simples - Integra Maker
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 5000

# Comando para executar
CMD ["python", "app.py"]