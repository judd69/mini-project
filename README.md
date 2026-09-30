# 🗳️ SecureVote — Cloud-Native Online Voting Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Deployment](https://img.shields.io/badge/Azure-App%20Service-0078D4.svg?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![Security](https://img.shields.io/badge/Security-SHA--256%20Cryptographic%20Receipts-success.svg)](#security-architecture)

> **SecureVote** is a secure, cloud-optimized online voting web application engineered for student elections, organizational ballots, and institutional governance. Designed from the ground up for high integrity, privacy protection, and deployment on **Azure App Service (Free/Student Tier)**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Security & Cryptographic Architecture](#-security--cryptographic-architecture)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quickstart & Local Setup](#-quickstart--local-setup)
- [Azure Deployment Guide](#-azure-deployment-guide)
- [Interactive Features](#-interactive-features)
- [Screenshots & UI Showcase](#-screenshots--ui-showcase)
- [License & Contributing](#-license--contributing)

---

## ✨ Key Features

- 🔒 **Cryptographic Vote Receipts**: Every cast ballot generates an immutable SHA-256 verification hash and receipt token, enabling voters to independently verify their ballot's inclusion.
- 🛡️ **Zero Voter-Ballot Traceability**: Strict separation between voter registration records and cast ballots guarantees complete ballot secrecy while strictly preventing double-voting.
- 🎨 **Modern, Sleek User Interface**: Built with modern aesthetics, custom gradients, micro-interactions, responsive candidate selection cards, and real-time result visualizations.
- 🤖 **Integrated AI Support Assistant**: Floating conversational chatbot widget providing instant voter assistance, election rules explanation, and troubleshooting.
- 🚦 **Brute-Force & Rate-Limiting Protection**: Integrated with `django-axes` to protect authentication endpoints from credential-stuffing and automated attacks.
- ☁️ **Azure Ready**: Pre-configured with dual environments (`development` with SQLite and `production` with Azure SQL / PostgreSQL, WhiteNoise static asset pipeline, and Gunicorn).

---

## 🔐 Security & Cryptographic Architecture

```
                    ┌─────────────────────────┐
                    │ Voter Authenticates     │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌──────────────────┐            ┌───────────────────┐
       │   Voter Profile  │            │ Anonymous Ballot  │
       │ (has_voted=True) │            │  (Candidate Pick) │
       └──────────────────┘            └─────────┬─────────┘
                                                 │
                                                 ▼
                                       ┌───────────────────┐
                                       │ SHA-256 Hash Gen  │
                                       │ Verification Code │
                                       └───────────────────┘
```

1. **Ballot Anonymization**: When a ballot is submitted, the voter's `has_voted` flag is toggled atomically. The cast ballot does not store foreign keys linking back to the user identity.
2. **Cryptographic Verification**: A unique SHA-256 hash receipt is computed from election metadata, timestamp, candidate identifier, and a secure salt.
3. **Double-Click & Double-Submit Protection**: JavaScript client-side debounce combined with database-level atomic transaction locks prevents duplicate submissions.
4. **CSRF & Security Headers**: Strict CSRF protection, secure cookie flags (`HttpOnly`, `SameSite=Lax`), and Content Security Policy headers.

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, Django 4.2 LTS | MVC framework, ORM, Auth, Admin |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JS | Micro-interactions, Glassmorphism, Responsive UI |
| **Security** | SHA-256, Django-Axes | Brute-force prevention, cryptographic receipts |
| **Database** | SQLite (Dev) / Azure SQL / Postgres (Prod) | Configured via `dj-database-url` |
| **WSGI / Static**| Gunicorn, WhiteNoise | Production asset compression & serving |
| **Cloud** | Microsoft Azure | Azure App Service (B1 / F1 Tier) |

---

## 📂 Project Structure

```bash
secure-voting-app/
├── chatbot/                   # AI Helpdesk & Voter Assistant app
│   ├── models.py              # Chat session & query logs
│   ├── urls.py                # Chat API endpoints
│   └── views.py               # AI response engine
├── voting/                    # Core Election & Ballot engine
│   ├── models.py              # Election, Candidate, Ballot, Voter models
│   ├── urls.py                # Election routes, vote submission, results
│   ├── views.py               # Ballot submission, verification views
│   └── admin.py               # Admin election management dashboard
├── securevote/                # Project Configuration
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Local SQLite settings
│   │   └── production.py      # Azure App Service & Azure SQL settings
│   ├── asgi.py
│   ├── wsgi.py
│   └── urls.py
├── static/                    # Custom CSS, JS, and Assets
│   ├── css/style.css          # Design system & animations
│   └── js/
│       ├── vote.js            # Interactive vote submissions & ripples
│       └── chatbot.js         # Floating chat assistant logic
├── templates/                 # Modular Django HTML Templates
│   ├── base.html              # Base layout with navbar & footer
│   ├── chatbot/               # Chat widget partials
│   └── voting/                # Election list, ballot, receipt, results
├── requirements.txt           # Pinned production dependencies
├── seed_data.py               # Demo election seed script
├── startup.sh                 # Azure Linux App Service entrypoint
└── manage.py                  # Django CLI entrypoint
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/judd69/mini-project.git
cd mini-project
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py shell < seed_data.py
# Or run: python -c "exec(open('seed_data.py', encoding='utf-8').read())"
```

### 5. Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## ☁️ Azure Deployment Guide

This repository is pre-configured for **Azure App Service (Linux B1/F1 Free Tier)**.

### Environment Variables for Azure
Set the following Application Settings in the Azure Portal or via Azure CLI:

```env
DJANGO_SETTINGS_MODULE=securevote.settings.production
SECRET_KEY=<your-secure-random-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.azurewebsites.net
DATABASE_URL=postgres://<user>:<password>@<host>:5432/<dbname>
```

### Azure App Service Startup Command
In Azure App Service > **Configuration** > **General settings** > **Startup Command**:
```bash
bash startup.sh
```

---

## 💡 Interactive Features

- **Dynamic Vote Confirmation**: Multi-step interactive ballot with confirmation modal to eliminate misclicks.
- **Instant Receipt Lookup**: Voters can input their transaction hash to verify timestamped ballot inclusion without exposing candidate selection.
- **Real-Time Visual Tally**: Live SVG/CSS percentage bars showcasing candidate vote shares upon election close.
- **Admin Management**: Full CRUD interface for creating elections, managing voter eligibility lists, and scheduling start/end time windows.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
