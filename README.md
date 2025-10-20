# 🎯 Système de Pointage Intelligent par Reconnaissance Faciale



Ce projet est une application de bureau complète et autonome pour la gestion des présences, utilisant la reconnaissance faciale en temps réel pour remplacer les systèmes de pointage traditionnels.
![Uploading Screenshot 2025-10-09 164345.jpg…]()
---

## ✨ Fonctionnalités

- **Pointage en Temps Réel** : Identification automatique des employés via un flux caméra.  
- **Logique de Pointage Intelligente** : Un système de timer et de période de grâce pour fiabiliser les enregistrements.  
- **Interface Graphique Professionnelle** : Une application facile à utiliser avec un thème moderne, construite avec Tkinter et ttkbootstrap.  
- **Gestion Complète des Employés** : Un onglet dédié pour ajouter (par caméra ou dossier), lister et supprimer des employés.  
- **Tableau de Bord d'Analyse** : Un onglet pour visualiser et filtrer l'historique des pointages par employé et par période.  
- **Base de Données Persistante** : Toutes les données sont stockées de manière fiable dans une base de données SQLite.  

---

## 🛠️ Stack Technique

- **Langage** : Python  
- **IA & Vision par Ordinateur** : TensorFlow, DeepFace (avec le modèle ArcFace), OpenCV  
- **Base de Données** : SQLite  
- **Interface Graphique (GUI)** : Tkinter, ttkbootstrap, Pillow  
- **Manipulation de Données** : NumPy, Pickle  

---

## 🚀 Guide d'Installation et de Lancement

Ce projet a été développé et testé avec **Python 3.10**.  
Suivez ces étapes pour l’installer et le lancer sur votre machine.

### Étape 1 : Prérequis

Assurez-vous d’avoir installé :

- Python 3.10  
- Git  

### Étape 2 : Cloner le Projet

Ouvrez un terminal et exécutez :

```bash
git clone https://github.com/mohamedazizaouioua-web/Intelligent-Attendance-System-Using-Facial-Recognition.git
cd Intelligent-Attendance-System-Using-Facial-Recognition
```

### Étape 3 : Configurer l’Environnement et Installer les Dépendances

```bash
# 1. Créez un environnement virtuel :
py -3.10 -m venv .venv

# 2. Activez l’environnement virtuel :
.venv\Scripts\activate

# 3. Installez les dépendances :
pip install -r requirements.txt
```

### Étape 4 : Initialiser la Base de Données 

Avant le premier lancement, exécutez ce script une seule fois :

```bash
python setup_database.py
```

## 📖 Guide d’Utilisation de l’Application 

### 1. Lancer l’Application

-Assurez-vous que votre environnement virtuel est activé.
-Exécutez :

```bash
python gui_app.py
```

### 2. Ajouter des Employés 

-Allez dans l’onglet Gestion des Employés.

-Entrez le nom de l’employé.

-Cliquez sur Ajouter via Dossier ou Ajouter via Caméra.

### 3. Mettre à Jour la Base de Reconnaissance (Étape Cruciale)

-Après avoir ajouté ou supprimé des employés, cliquez sur le bouton **METTRE À JOUR MAINTENANT**.

-Attendez le message de succès.

### 4. Lancer le Pointage 

-Allez dans l’onglet Système de Pointage.

-Cliquez sur Démarrer la Caméra.

### 5. Analyser les Données

-Allez dans l’onglet Tableau de Bord pour filtrer et consulter l’historique.

✍️ Auteur

Mohamed Aziz Aouioua
