# Subscription Management System — Team Starter Pack

This is a Python + Flask + MySQL starter project for a 4-member team.
It is a starter implementation, not a finished production system.

## Requirements
- Python 3.10+
- MySQL Server (Workbench is only the database client)
- VS Code

## Setup
1. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\\Scripts\\activate`
2. Install packages: `pip install -r requirements.txt`
3. Create the database by running `schema.sql` in MySQL Workbench.
4. Copy `.env.example` to `.env` and fill in your MySQL settings.
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000`

## Team split
- Member 1: Authentication (`modules/auth.py`)
- Member 2: Products and plans (`modules/catalog.py`)
- Member 3: Subscriptions (`modules/subscriptions.py`)
- Member 4: Billing and reports (`modules/billing.py`, `modules/reports.py`)

Agree on database fields and function names before everyone starts coding.
Do not use real payment credentials or store plain-text passwords.
