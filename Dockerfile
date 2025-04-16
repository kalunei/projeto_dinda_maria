# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o diretório de trabalho do container
COPY . /app

# Instalar as dependências do projeto (remover a criação do ambiente virtual)
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta que o app vai usar
EXPOSE 8080

# Comando para rodar a aplicação (substitua pelo seu comando, se for diferente)
CMD ["python", "app.py"]
