# Subscription Management System — Team Starter

Separate ownership: Member 1 auth; Member 2 catalog; Member 3 subscriptions; Member 4 billing/reports. Shared files: `app.py`, `db.py`, `schema.sql`.

## Run (VS Code terminal)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Initial modules are foundations, not a finished secure production system. There is no seeded administrator yet; team must provision one securely during development.

## Git
Use branches `feature/auth`, `feature/catalog`, `feature/subscriptions`, `feature/billing-reports`. Each teammate edits assigned module only; submit PRs for integration. Agree on currency, tax treatment, rounding, and invoice cycle key before billing work.
