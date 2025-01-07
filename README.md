# Flowmodoro

Flowmodoro est une application de gestion de temps inspirée de la technique Pomodoro. Elle aide les utilisateurs à améliorer leur productivité en suivant leurs sessions de travail, en catégorisant leurs tâches, et en analysant leur temps passé grâce à des rapports et des graphiques.

## Fonctionnalités

### Gestion de sessions
- Démarrez et arrêtez des sessions de travail avec un minuteur intégré.
- Enregistrez automatiquement la durée, la catégorie, et la tâche associée à chaque session.
- Recevez des notifications pour indiquer la fin d’une session ou d’une pause.

### Gestion des tâches
- Ajoutez et gérez vos tâches directement dans l’application.
- Associez des tâches à des catégories spécifiques.
- Marquez les tâches comme “facturables” pour un suivi des heures travaillées rémunérées.

### Analyse de productivité
- Analysez votre temps par tâche et catégorie.
- Visualisez les sessions journalières, hebdomadaires, et globales.
- Exportez les analyses au format CSV pour une consultation ou un partage facile.
- Affichez un graphique des temps passés par catégorie.

### Notifications
- Recevez des notifications push via Pushover pour rester informé de vos sessions de travail.

## Prérequis
Avant de lancer le projet, assurez-vous d’avoir les éléments suivants installés sur votre machine :
- **Python 3.8+**
- **Bibliothèques Python**:
  - `tkinter`
  - `pygame`
  - `matplotlib`
  - `requests`
  - `json`
  - `csv`
- **API Pushover** : Créer un compte [Pushover](https://pushover.net/) et obtenez un `user_key` et un `token`.

## Installation
1. Clonez le projet depuis ce dépôt :
```bash
git clone https://github.com/arnaudstdr/flowmodoro.git
cd flowmodoro
```
2. Installez lezs dépendances nécessaires :
```bash
pip install -r requirements.txt
```
3. Configurez vos clés API dans un fichier nommé `api.py` :
```python
# api.py
KEY = "votre_user_key"
TOKEN = "votre_api_token"
```

## Utilisation
1. Lancez l'application :
```bash
python flow.py
```
2. Naviguez dans l'interface pour :
   - **Démarrer une session de travail** en sélectionnant une catégorie et une tâche.
   - **Ajouter une tâche** ou la marquer comme facturable.
   - **Analyser votre productivité** grâce aux différents outils intégrés.
3. Exporter vos anlyses au format CSV ou viasulisez vos données sous forme de graphique.

## Capture d'écran
![Aperçu de Flowmodoro](/screenshot.png)

## Structure du projet
```plaintext
flowmodoro/
├── flow.py            # Script principal de l'application
├── tasks.json         # Fichier de stockage des tâches
├── sessions.json      # Fichier de stockage des sessions
├── api.py             # Clés API pour les notifications
├── notification.mp3   # Clés API pour les notifications
├── screenshot.png     # Clés API pour les notifications
├── README.md          # Documentation du projet
└── LICENCE            # Licence MIT
```

## Licence
Ce projet est sous licence MIT. Consultez le fichier [LICENSE](/LICENCE) pour plus de détails.