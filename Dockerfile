# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o ChromaDB/Compilação
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte para dentro do container
COPY . .

# Comando para rodar a aplicação
CMD ["python", "main.py"]