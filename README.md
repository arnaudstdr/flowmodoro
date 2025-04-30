# 🚀 FlowModoro - Gestion optimisée du temps avec méthode Pomodoro améliorée

FlowModoro est une application de bureau Python conçue pour optimiser ta productivité grâce à une gestion intelligente des sessions de travail et de pauses inspirée de la méthode Pomodoro. Avec un design intuitif, des statistiques détaillées et une intégration complète avec des notifications push, FlowModoro est l’outil idéal pour travailler efficacement tout en gardant un esprit léger et motivé.


## 🎯 Objectifs de FlowModoro
- Maximiser ta productivité avec des sessions de travail structurées.
- Faciliter le suivi du temps passé par tâches et catégories.
- Améliorer l’équilibre travail-pause pour rester concentré.
- Rendre agréable et ludique la gestion quotidienne du temps.


## 🌟 Fonctionnalités clés

### ⏰ Gestion intelligente des sessions
- Sessions de travail automatisées : Timer intégré, démarrage/arrêt clair.
- Calcul automatique des pauses : Pause dynamique basée sur la durée du travail (pause = travail/5).
- Notifications sonores et Push (via Pushover) : Rappels doux mais efficaces à la fin des sessions.

### 📂 Gestion des catégories et des tâches
- Catégories personnalisées avec icônes pour une meilleure visualisation :
  - Formation 📚
  - Pro 💼
  - Perso 🏠
- Gestion intuitive des tâches :
  - Ajout rapide avec option « Billable 💰 ».
  - Suppression facile des tâches.

### 📈 Analyse détaillée de ta productivité
- Historique quotidien et hebdomadaire clair.
- Analyse détaillée du temps passé par tâche et catégorie.
- Export facile au format CSV pour un suivi précis et réutilisable.
- Graphiques interactifs pour visualiser ton activité efficacement.

### 🎨 Interface utilisateur ergonomique
- Interface moderne utilisant ttkbootstrap avec thèmes personnalisables :
  - Superhero, Darkly, Flatly, Minty, Cyborg, Journal, Solar.
- Intégration d’emojis et d’icônes pour une expérience visuelle ludique et agréable.


## 🛠️ Stack technique
- **Python 3** pour le cœur de l’application.
- Interface graphique basée sur **Tkinter** avec la librairie **ttkbootstrap**.
- Gestion de fichiers de données en **JSON**JSON et export CSV intégré
- Intégration de notifications via **API Pushover**.
- Module audio via **pygame** pour les notifications sonores.


## 🧑‍💻 Installation et lancement
1. Clone le dépôt :
```bash
git clone https://github.com/ton-username/FlowModoro.git
cd FlowModoro
```

2. Installe les dépendances :
```bash
pip install -r requirements.txt
```

3. Configure tes clés API (pour Pushover) dans un fichier api.py :
```python
KEY = "ta clé utilisateur Pushover"
TOKEN = "ton token API Pushover"
```

4. Lance l’application :
```bash
python flow.py
```


## ⚙️ Paramètres et configuration

Tu peux ajuster les paramètres suivants dans la fenêtre dédiée accessible depuis le menu “Settings” :
- Activation/Désactivation du son 🎶
- Activation/Désactivation des notifications Push 📲
- Choix du thème 🎨
- Activation du rappel automatique en cas d’inactivité ⏳


## 🚧 Évolutions futures

Voici quelques idées prévues pour améliorer encore FlowModoro :
- Intégration d’un système de badges ou récompenses 🎖️
- Mode sombre automatique selon l’heure 🌙
- Sauvegarde cloud automatique pour l’accès depuis plusieurs machines ☁️

## 📝 Licence

Ce projet est distribué sous licence MIT. Voir LICENSE pour plus d’informations.


Bonne productivité avec FlowModoro ! 🚀