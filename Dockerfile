# Utilise une image officielle Python
FROM python:3.13-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt ./
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande de lancement (à adapter si besoin)
CMD ["python", "main.py"]
