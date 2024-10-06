# Utiliser une image de base Python
FROM python:3.9-slim

# Installer les dépendances
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier les scripts Python et le fichier .env
COPY one_shot_webscrape_cass.py .
COPY api.py .
COPY .env .

# Exposer le port 5000 pour l'API Flask
EXPOSE 5000

# Commande pour collecter les données (premier script)
RUN python one_shot_webscrape_cass.py

# Commande pour lancer l'API REST
CMD ["python", "api.py"]
