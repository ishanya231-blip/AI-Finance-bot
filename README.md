# Personal Finance Advisor Bot 🚀

An AI-powered financial planning assistant built with a scalable full-stack architecture using **Flask**, **SQLAlchemy**, and an **AI Financial Analysis Engine**.

Designed to help individuals, freelancers, students, and households take control of their personal finances through automated budget generation, anomaly detection, actionable saving strategies, and structured monthly reporting.

---

## 🌟 Supported Personas & Scenarios

1. **Scenario 1: Salaried Professional**
   - Logs monthly salary and daily expenses across rent, food, transport, and leisure.
   - Detects overspending in entertainment & dining out (lifestyle creep).
   - Generates personalized 50/30/20 budget allocations with automated payday savings sweeps.
   - Generates monthly summary statements tracking income vs. expenses, net savings, and financial goals.

2. **Scenario 2: College Student**
   - Manages a constrained monthly allowance across essential (dorm, meal card, books) and discretionary spending.
   - Enforces realistic budget limits to prevent mid-month cash depletion.
   - Delivers AI recommendations for student discounts, campus transit passes, and digital subscription audits.

3. **Scenario 3: Freelancer with Variable Income**
   - Logs earnings from multiple clients and tracks project-related expenses.
   - Smooths fluctuating monthly income by locking a lean baseline living budget.
   - Automatically allocates surplus earnings to build a 6-month liquid emergency runway and a dedicated quarterly tax reserve.

4. **Scenario 4: Household Manager**
   - Consolidates shared multi-earner family income streams.
   - Monitors essential high-cost categories (mortgage, groceries, utilities, education, healthcare).
   - Flags budget overruns and utility spikes, providing bulk purchasing strategies and family sinking funds.

---

## 📂 Project Architecture

```
personal_finance_bot/
├── app/
│   ├── __init__.py           # Application initialization
│   ├── models.py             # SQLAlchemy ORM models (User, Profile, Income, Expense, BudgetPlan, Goal, Report)
│   ├── ai_engine.py          # AI Financial Analysis Engine (anomaly detection, persona budget algorithms)
│   ├── routes.py             # RESTful API endpoints and dashboard routes
│   ├── seed_data.py          # Pre-built realistic datasets for all 4 scenarios
│   └── templates/
│       └── index.html        # Interactive responsive frontend with live scenario switcher
├── tests/
│   └── test_ai_engine.py     # Unit test suite with 100% test coverage
├── app.py                    # Standalone runnable full-stack application
├── requirements.txt          # Python dependencies
└── README.md                 # Complete system documentation
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Stack Application
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

### 3. Run Unit Tests
```bash
python -m unittest tests/test_ai_engine.py
```

---

## 📡 RESTful API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/scenarios` | Lists all 4 persona scenarios |
| `POST` | `/api/scenarios/switch` | Switches active persona (`{"persona": "salaried"\|"student"\|"freelancer"\|"household"}`) |
| `GET` | `/api/dashboard` | Returns financial totals, active budget plan, AI alerts, and goals |
| `POST` | `/api/income` | Logs an income entry |
| `POST` | `/api/expense` | Logs a daily/weekly expense entry |
| `POST` | `/api/budget/generate` | Runs AI engine to generate personalized budget |
| `GET` | `/api/report` | Generates structured monthly financial statement |
