# StreamEvents
Plataforma per gestionar i visualitzar esdeveniments en temps real.

## ✨ Objectius
- Gestionar esdeveniments i notificacions.  
- Permetre visualització en temps real.  
- Integració amb diferents fonts de dades.

## 🧱 Stack Principal
- **Backend:** Django, Django REST Framework  
- **Frontend:** React / Vue (si n’hi ha)  
- **Base de dades:** PostgreSQL / MongoDB  
- **Altres:** Celery, Redis, Docker, etc.

## 📂 Estructura Simplificada
projecte/
├── backend/
│ ├── manage.py
│ ├── apps/
├── frontend/
├── requirements.txt
├── README.md

## ✅ Requisits previs
- Python 3.12+  
- Node.js 20+ (si hi ha frontend)  
- pip i virtualenv

## 🚀 Instal·lació ràpida
```bash
git clone https://github.com/usuari/streamevents.git
cd streamevents
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
