# 📚 SmartReader Chat – Résumeur d'Articles Scientifiques

💬 **SmartReader** est une application web basée sur Streamlit, qui permet de **poser des questions à un PDF scientifique**, et d'en **obtenir un résumé des points clés** grâce à l'IA.

---

## 🎯 Objectif du projet

> Extraire et résumer automatiquement des articles scientifiques en mettant en avant les points clés.

---

## ⚙️ Fonctionnalités

- 📤 Upload de fichier PDF scientifique
- ✂️ Découpage intelligent du texte en chunks (LangChain)
- 🧠 Embedding rapide avec `MiniLM`
- 🔍 Recherche de passages pertinents avec **FAISS** (RAG)
- 🤖 Résumé généré avec Ollama (`mistral`, `phi`, `tinyllama`, etc.)
- 🧾 Historique de conversation exportable en `.txt`
- ⚡ Optimisé pour la rapidité (streaming, chunks courts)

---

## 🧪 Technologies utilisées

```bash
- Streamlit
- LangChain (TextSplitter)
- ChromaDB
- sentence-transformers (MiniLM)
- Ollama (mistral, phi, tinyllama...)
- Python 3.9+
```

---

## 🚀 Installation & Lancement

### 1. Cloner le repo

```bash
git clone https://github.com/tonrepo/smartreader-chat.git
cd smartreader-chat
```

### 2. Créer un environnement

```bash
conda create -n smartreader python=3.9
conda activate smartreader
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer un ou plusieurs modèles Ollama

```bash
ollama pull tinyllama
ollama pull mistral
ollama pull phi
```

### 5. Lancer le serveur Ollama dans un terminal

```bash
ollama serve
```

### 6. Lancer l'application

```bash
streamlit run app.py
```

---

## 🖥️ Utilisation

1. Uploade ton fichier PDF
2. Pose une question (ex : *What is the main conclusion?*)
3. Reçois une réponse contextualisée résumée
4. Exporte le chat si besoin 📥

---


