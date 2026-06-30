# Adaptive Insider Threat Detection Using Isolation Forest

Final Year Engineering Project — Secure Banking Web App with AI-based adaptive security.

## Features

### Banking Module
- User registration & login
- Deposit, withdraw, transfer
- Transaction history with search/filter/pagination
- Printable & downloadable PDF receipts
- Profile management

### Security AI Module
- Real-time behavior logging (8 features)
- Pre-trained Isolation Forest anomaly detection
- Dynamic trust score (0–100)
- Decision engine with adaptive responses:
  - Mask account data
  - Show decoy balance
  - Restrict transfers/withdrawals
  - Generate security alerts

### Admin Module
- Separate admin login
- Dashboard KPIs + Chart.js analytics
- User management & online users
- Alerts, behavior logs, trust score monitoring

## Tech Stack

Python Flask | SQLite | Bootstrap 5 | Chart.js | scikit-learn | Isolation Forest

## Setup

```bash
cd Adaptive_Insider_Threat_Detection
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Place your Colab-exported model at:

`ml_model/trained_model.pkl`

The application only loads this pre-trained model with Joblib. It does not
retrain the model. If the file is missing during development, the app uses a
simple fallback predictor so the banking demo can still run, and the Admin
Dashboard displays the model integration status.

Initialize DB:

```bash
python database/create_tables.py
```

Run:

```bash
python app.py
```

Open: http://127.0.0.1:5000

## Default Admin

- URL: `/admin/login`
- Email: `admin@bank.local`
- Password: `Admin@123`

## Project Structure

See repository folders: `routes/`, `models/`, `security_ai/`, `templates/`, `static/`, `ml_model/`

## ML Feature Vector Order

```
[login_hour, session_duration, transaction_count, amount_transferred,
 download_count, ip_change, new_payee_added, failed_attempts]
```

## Testing

```bash
pytest tests/ -v
```

On OneDrive, if Windows reports pytest cache or `__pycache__` file errors, run:

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"
pytest tests/ -q -p no:cacheprovider
```

## Authors

Final Year Project — Adaptive Insider Threat Detection
