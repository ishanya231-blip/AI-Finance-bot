"""
Personal Finance Advisor Bot - Full Stack Application Entry Point
Built with Flask, SQLAlchemy, and AI Financial Analysis Engine.
Run directly with: python app.py
"""

import os
from datetime import datetime, date
from flask import Flask, render_template, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-personal-finance-bot'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///personal_finance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== DATABASE MODELS ====================

"""
SQLAlchemy Database Models for Personal Finance Advisor Bot
Supports Users, Profiles (Scenario personas), Categories, Income, Expenses,
Budget Plans, Financial Goals, and Monthly Reports.
"""

from datetime import datetime, date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    incomes = db.relationship('Income', backref='user', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship('BudgetPlan', backref='user', lazy=True, cascade="all, delete-orphan")
    goals = db.relationship('FinancialGoal', backref='user', lazy=True, cascade="all, delete-orphan")
    reports = db.relationship('MonthlyReport', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile': self.profile.to_dict() if self.profile else None
        }

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Scenarios: 'salaried', 'student', 'freelancer', 'household'
    persona_type = db.Column(db.String(50), nullable=False, default='salaried')
    display_title = db.Column(db.String(100), nullable=False)
    monthly_target_savings = db.Column(db.Float, default=0.0)
    emergency_fund_target = db.Column(db.Float, default=0.0)
    current_emergency_fund = db.Column(db.Float, default=0.0)
    monthly_allowance = db.Column(db.Float, default=0.0) # Student specific
    income_variability_risk = db.Column(db.String(20), default='low') # 'low', 'medium', 'high'
    dependents_count = db.Column(db.Integer, default=0) # Household specific

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'persona_type': self.persona_type,
            'display_title': self.display_title,
            'monthly_target_savings': self.monthly_target_savings,
            'emergency_fund_target': self.emergency_fund_target,
            'current_emergency_fund': self.current_emergency_fund,
            'monthly_allowance': self.monthly_allowance,
            'income_variability_risk': self.income_variability_risk,
            'dependents_count': self.dependents_count
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    category_type = db.Column(db.String(30), nullable=False, default='need') # 'need', 'want', 'saving', 'debt'
    icon = db.Column(db.String(30), default='tag')
    color_code = db.Column(db.String(20), default='#3B82F6')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'icon': self.icon,
            'color_code': self.color_code
        }

class Income(db.Model):
    __tablename__ = 'incomes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(30), default='monthly') # 'monthly', 'weekly', 'project_based'
    date = db.Column(db.Date, nullable=False, default=date.today)
    is_recurring = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'source_name': self.source_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'date': self.date.isoformat() if hasattr(self.date, 'isoformat') else str(self.date),
            'is_recurring': self.is_recurring
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    frequency = db.Column(db.String(30), default='daily') # 'daily', 'weekly', 'monthly'

    category = db.relationship('Category', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'General',
            'category_type': self.category.category_type if self.category else 'need',
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat() if hasattr(self.date, 'isoformat') else str(self.date),
            'frequency': self.frequency
        }

class BudgetPlan(db.Model):
    __tablename__ = 'budget_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month_year = db.Column(db.String(7), nullable=False) # YYYY-MM
    total_projected_income = db.Column(db.Float, nullable=False)
    allocated_needs = db.Column(db.Float, nullable=False)
    allocated_wants = db.Column(db.Float, nullable=False)
    allocated_savings = db.Column(db.Float, nullable=False)
    allocated_debt = db.Column(db.Float, default=0.0)
    ai_strategy_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allocations = db.relationship('BudgetCategoryAllocation', backref='budget_plan', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'month_year': self.month_year,
            'total_projected_income': self.total_projected_income,
            'allocated_needs': self.allocated_needs,
            'allocated_wants': self.allocated_wants,
            'allocated_savings': self.allocated_savings,
            'allocated_debt': self.allocated_debt,
            'ai_strategy_summary': self.ai_strategy_summary,
            'allocations': [a.to_dict() for a in self.allocations]
        }

class BudgetCategoryAllocation(db.Model):
    __tablename__ = 'budget_category_allocations'
    id = db.Column(db.Integer, primary_key=True)
    budget_plan_id = db.Column(db.Integer, db.ForeignKey('budget_plans.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    allocated_cap = db.Column(db.Float, nullable=False)

    category = db.relationship('Category', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'General',
            'allocated_cap': self.allocated_cap
        }

class FinancialGoal(db.Model):
    __tablename__ = 'financial_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    goal_category = db.Column(db.String(50), default='emergency_fund')
    status = db.Column(db.String(20), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_pct': round((self.current_amount / self.target_amount * 100), 1) if self.target_amount > 0 else 0,
            'target_date': self.target_date.isoformat() if self.target_date and hasattr(self.target_date, 'isoformat') else str(self.target_date),
            'goal_category': self.goal_category,
            'status': self.status
        }

class MonthlyReport(db.Model):
    __tablename__ = 'monthly_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month_year = db.Column(db.String(7), nullable=False)
    total_income = db.Column(db.Float, nullable=False)
    total_expense = db.Column(db.Float, nullable=False)
    net_savings = db.Column(db.Float, nullable=False)
    savings_rate_pct = db.Column(db.Float, nullable=False)
    health_score = db.Column(db.Integer, nullable=False)
    ai_insights = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'month_year': self.month_year,
            'total_income': self.total_income,
            'total_expense': self.total_expense,
            'net_savings': self.net_savings,
            'savings_rate_pct': self.savings_rate_pct,
            'health_score': self.health_score,
            'ai_insights': self.ai_insights,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
        }

# ==================== AI FINANCIAL ENGINE ====================

"""
AI Financial Analysis Engine
Core computational and heuristic intelligence for:
- Categorization and spending breakdown
- Anomaly and overspending detection
- Persona-tailored budget generation (Salaried, Student, Freelancer, Household)
- Actionable saving recommendations
- Monthly financial health scoring and structured executive reporting
"""

from typing import List, Dict, Any
from datetime import datetime, date

class AIFinancialEngine:
    def __init__(self):
        # Default baseline budgeting benchmarks per scenario persona
        self.benchmarks = {
            'salaried': {'needs_pct': 50.0, 'wants_pct': 30.0, 'savings_pct': 20.0},
            'student': {'needs_pct': 65.0, 'wants_pct': 20.0, 'savings_pct': 15.0},
            'freelancer': {'needs_pct': 45.0, 'wants_pct': 25.0, 'savings_pct': 30.0},
            'household': {'needs_pct': 60.0, 'wants_pct': 20.0, 'savings_pct': 20.0}
        }

    def aggregate_financials(self, incomes: List[Dict[str, Any]], expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates total income, total expense, category sums, and bucket breakdowns (needs, wants, savings)."""
        total_income = sum(float(i['amount']) for i in incomes)
        total_expense = sum(float(e['amount']) for e in expenses)
        net_savings = max(0.0, total_income - total_expense)
        deficit = max(0.0, total_expense - total_income)
        savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

        by_category = {}
        by_type = {'need': 0.0, 'want': 0.0, 'saving': 0.0, 'debt': 0.0}

        for exp in expenses:
            cat_name = exp.get('category_name', 'General')
            cat_type = exp.get('category_type', 'need')
            amt = float(exp['amount'])
            
            by_category[cat_name] = by_category.get(cat_name, 0.0) + amt
            if cat_type in by_type:
                by_type[cat_type] += amt
            else:
                by_type['need'] += amt

        type_percentages = {}
        if total_income > 0:
            for k, v in by_type.items():
                type_percentages[k] = round((v / total_income) * 100, 1)
        else:
            type_percentages = {k: 0.0 for k in by_type}

        return {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'net_savings': round(net_savings, 2),
            'deficit': round(deficit, 2),
            'savings_rate': savings_rate,
            'by_category': {k: round(v, 2) for k, v in by_category.items()},
            'by_type': {k: round(v, 2) for k, v in by_type.items()},
            'type_percentages': type_percentages
        }

    def detect_overspending(self, profile: Dict[str, Any], aggregated: Dict[str, Any], budget_plan: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Identifies categories and expense buckets that violate targets or healthy ratios."""
        alerts = []
        persona = profile.get('persona_type', 'salaried')
        income = aggregated['total_income']
        by_type = aggregated['by_type']
        by_cat = aggregated['by_category']
        type_pcts = aggregated['type_percentages']

        # 1. Deficit alert
        if aggregated['deficit'] > 0:
            alerts.append({
                'severity': 'critical',
                'category': 'Overall Budget',
                'title': 'Operating Cashflow Deficit',
                'message': f"Monthly spending exceeds total income by ${aggregated['deficit']:,.2f}. Immediate expense trimming required."
            })

        # 2. Wants / Discretionary overspending
        max_wants_pct = self.benchmarks.get(persona, self.benchmarks['salaried'])['wants_pct']
        if type_pcts.get('want', 0) > (max_wants_pct + 5):
            alerts.append({
                'severity': 'warning',
                'category': 'Discretionary Wants',
                'title': 'Discretionary Overspending Detected',
                'message': f"Discretionary spending is {type_pcts['want']}% of income (ideal ceiling is {max_wants_pct}% for {persona.capitalize()})."
            })

        # 3. Persona-specific checks
        if persona == 'salaried':
            dining_ent = by_cat.get('Entertainment', 0) + by_cat.get('Dining Out', 0)
            if income > 0 and (dining_ent / income) > 0.15:
                alerts.append({
                    'severity': 'warning',
                    'category': 'Entertainment & Dining',
                    'title': 'Lifestyle Creep in Leisure',
                    'message': f"Dining and entertainment represent {round(dining_ent / income * 100, 1)}% of your income. Trimming weekend spend could save ${round(dining_ent * 0.25, 2)} monthly."
                })

        elif persona == 'student':
            allowance = profile.get('monthly_allowance', income)
            wants_total = by_type.get('want', 0)
            if allowance > 0 and (wants_total / allowance) > 0.30:
                alerts.append({
                    'severity': 'warning',
                    'category': 'Student Discretionary',
                    'title': 'Allowance Exhaustion Risk',
                    'message': f"Non-essential purchases consumed {round(wants_total / allowance * 100, 1)}% of your monthly allowance, risking mid-month cash depletion."
                })

        elif persona == 'freelancer':
            ef_current = profile.get('current_emergency_fund', 0)
            ef_target = profile.get('emergency_fund_target', income * 6)
            if ef_target > 0 and ef_current < (ef_target * 0.5):
                alerts.append({
                    'severity': 'warning',
                    'category': 'Emergency Reserve',
                    'title': 'Low Cash Buffer for Variable Income',
                    'message': f"Your emergency fund is only {round(ef_current / ef_target * 100, 1)}% funded. Variable income earners require at least 3-6 months of baseline runway."
                })

        elif persona == 'household':
            groceries = by_cat.get('Family Groceries', by_cat.get('Groceries', 0))
            if income > 0 and (groceries / income) > 0.14:
                alerts.append({
                    'severity': 'info',
                    'category': 'Groceries',
                    'title': 'High Grocery Outlay',
                    'message': f"Household grocery expenditure accounts for {round(groceries / income * 100, 1)}% of joint income. Meal batching and wholesale purchasing recommended."
                })

        return alerts

    def generate_personalized_budget(self, profile: Dict[str, Any], incomes: List[Dict[str, Any]], expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates an intelligent, scenario-tailored budget plan based on persona dynamics."""
        persona = profile.get('persona_type', 'salaried')
        total_income = sum(float(i['amount']) for i in incomes)
        target_ratios = self.benchmarks.get(persona, self.benchmarks['salaried']).copy()

        if persona == 'student':
            allocated_needs = round(total_income * (target_ratios['needs_pct'] / 100.0), 2)
            allocated_wants = round(total_income * (target_ratios['wants_pct'] / 100.0), 2)
            allocated_savings = round(total_income * (target_ratios['savings_pct'] / 100.0), 2)
            strategy = (
                f"Student Envelope Allocation: 65% for essentials (shared room, books, campus dining, transit), "
                f"20% flexible allowance for social/discretionary, and 15% dedicated to establishing a graduate transition fund."
            )

        elif persona == 'freelancer':
            base_burn_rate = sum(float(e['amount']) for e in expenses if e.get('category_type') == 'need')
            if total_income > (base_burn_rate * 1.5):
                target_ratios['savings_pct'] = 35.0
                target_ratios['wants_pct'] = 20.0
                target_ratios['needs_pct'] = 45.0
            allocated_needs = round(total_income * (target_ratios['needs_pct'] / 100.0), 2)
            allocated_wants = round(total_income * (target_ratios['wants_pct'] / 100.0), 2)
            allocated_savings = round(total_income * (target_ratios['savings_pct'] / 100.0), 2)
            strategy = (
                f"Variable Income Buffer Strategy: Fixed baseline needs locked at ${allocated_needs:,.2f}. "
                f"Aggressive {target_ratios['savings_pct']}% allocation (${allocated_savings:,.2f}) funneled into 6-month emergency reserve and tax buffer."
            )

        elif persona == 'household':
            allocated_needs = round(total_income * (target_ratios['needs_pct'] / 100.0), 2)
            allocated_wants = round(total_income * (target_ratios['wants_pct'] / 100.0), 2)
            allocated_savings = round(total_income * (target_ratios['savings_pct'] / 100.0), 2)
            strategy = (
                f"Consolidated Household Protocol: 60% prioritized for joint essentials (mortgage, groceries, utilities, tuition/healthcare), "
                f"20% for family recreation and personal allowances, and 20% toward collective savings milestones (education fund & family reserve)."
            )

        else: # Salaried Professional
            allocated_needs = round(total_income * (target_ratios['needs_pct'] / 100.0), 2)
            allocated_wants = round(total_income * (target_ratios['wants_pct'] / 100.0), 2)
            allocated_savings = round(total_income * (target_ratios['savings_pct'] / 100.0), 2)
            strategy = (
                f"Classic 50/30/20 Wealth Builder: 50% for core fixed commitments (rent, transport, groceries), "
                f"30% for flexible lifestyle choices, and 20% automated sweep to retirement/wealth generation vehicles."
            )

        unique_cats = {}
        for exp in expenses:
            c_name = exp.get('category_name', 'General')
            c_type = exp.get('category_type', 'need')
            unique_cats[c_name] = c_type

        allocations = []
        needs_cats = [k for k, v in unique_cats.items() if v == 'need']
        wants_cats = [k for k, v in unique_cats.items() if v == 'want']

        if needs_cats:
            per_need_cap = round(allocated_needs / len(needs_cats), 2)
            for c in needs_cats:
                allocations.append({'category_name': c, 'category_type': 'need', 'allocated_cap': per_need_cap})

        if wants_cats:
            per_want_cap = round(allocated_wants / len(wants_cats), 2)
            for c in wants_cats:
                allocations.append({'category_name': c, 'category_type': 'want', 'allocated_cap': per_want_cap})

        return {
            'total_projected_income': total_income,
            'allocated_needs': allocated_needs,
            'allocated_wants': allocated_wants,
            'allocated_savings': allocated_savings,
            'allocated_debt': 0.0,
            'ai_strategy_summary': strategy,
            'target_ratios': target_ratios,
            'allocations': allocations
        }

    def generate_saving_recommendations(self, profile: Dict[str, Any], aggregated: Dict[str, Any], alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Produces concrete, prioritized, actionable suggestions for saving optimization."""
        recs = []
        persona = profile.get('persona_type', 'salaried')
        by_cat = aggregated['by_category']
        net_savings = aggregated['net_savings']
        total_income = aggregated['total_income']

        if persona == 'salaried':
            recs.append({
                'priority': 'High',
                'action': 'Automate Payday Sweep',
                'impact': f'Saves approx. ${round(total_income * 0.20, 2):,.2f}/mo',
                'description': 'Configure an automatic bank transfer of 20% of net salary directly to high-yield savings on salary day before discretionary spending begins.'
            })
            if 'Dining Out' in by_cat or 'Entertainment' in by_cat:
                combined = by_cat.get('Dining Out', 0) + by_cat.get('Entertainment', 0)
                recs.append({
                    'priority': 'Medium',
                    'action': 'Implement 2-Day Dining Rule',
                    'impact': f'Estimated monthly reduction: ${round(combined * 0.3, 2):,.2f}',
                    'description': 'Cap mid-week food delivery and dine out strictly on weekends or prep office lunches 3 days a week.'
                })

        elif persona == 'student':
            recs.append({
                'priority': 'High',
                'action': 'Campus Subscription Audit & Meal Card Maximization',
                'impact': 'Estimated monthly reduction: $40 - $80',
                'description': 'Switch recurring digital services (Spotify, Prime) to student discount tiers and utilize prepaid campus dining hall credits to curb takeout.'
            })
            recs.append({
                'priority': 'Medium',
                'action': 'Transit & Course Material Optimization',
                'impact': 'Estimated semester savings: $150 - $300',
                'description': 'Utilize university subsidized transit passes and digital library reserves rather than buying retail textbooks.'
            })

        elif persona == 'freelancer':
            recs.append({
                'priority': 'High',
                'action': 'Dedicated Tax & Income Smoothing Vault',
                'impact': 'Protects 25-30% of each client invoice',
                'description': 'Segregate 30% of every received invoice immediately into an escrow savings account for quarterly taxes and seasonal downtime reserves.'
            })
            recs.append({
                'priority': 'High',
                'action': 'Accelerate 6-Month Emergency Runway',
                'impact': f'Target monthly contribution: ${round(max(200.0, net_savings * 0.5), 2):,.2f}',
                'description': 'Allocate 50% of monthly surplus directly to a high-yield liquid emergency fund until 6 months of minimum living expenses are secured.'
            })

        elif persona == 'household':
            recs.append({
                'priority': 'High',
                'action': 'Smart Utility Peak-Hours & Bulk Grocery Batching',
                'impact': 'Estimated monthly reduction: $80 - $160',
                'description': 'Schedule heavy appliances during off-peak power hours and consolidate weekly grocery runs with a structured menu to cut perishable waste.'
            })
            recs.append({
                'priority': 'Medium',
                'action': 'Annual Family Goal Sinking Fund',
                'impact': f'Builds ${round(net_savings * 0.4 * 12, 2):,.2f} annual reserve',
                'description': 'Direct 40% of household monthly savings into specific sub-accounts for annual insurance premiums, education fees, and vehicle maintenance.'
            })

        if len(recs) < 3:
            recs.append({
                'priority': 'Low',
                'action': 'Recurring Subscription Health Check',
                'impact': 'Estimated annual savings: $120 - $300',
                'description': 'Review recurring app subscriptions, gym memberships, and streaming plans; cancel unused services.'
            })

        return recs

    def calculate_financial_health_score(self, aggregated: Dict[str, Any], profile: Dict[str, Any]) -> int:
        score = 0
        savings_rate = aggregated['savings_rate']
        deficit = aggregated['deficit']
        type_pcts = aggregated['type_percentages']

        if savings_rate >= 25.0:
            score += 40
        elif savings_rate >= 20.0:
            score += 35
        elif savings_rate >= 10.0:
            score += 25
        elif savings_rate > 0.0:
            score += 15

        if deficit == 0:
            score += 30
        else:
            loss_penalty = min(25, int((deficit / max(1.0, aggregated['total_income'])) * 50))
            score += max(0, 30 - loss_penalty)

        ef_curr = profile.get('current_emergency_fund', 0)
        ef_target = profile.get('emergency_fund_target', 0)
        if ef_target > 0:
            ef_ratio = min(1.0, ef_curr / ef_target)
            score += int(ef_ratio * 20)
        else:
            score += 10

        wants_pct = type_pcts.get('want', 0)
        if wants_pct <= 25.0:
            score += 10
        elif wants_pct <= 35.0:
            score += 6
        else:
            score += 2

        return max(5, min(100, score))

    def generate_monthly_report(self, profile: Dict[str, Any], month_year: str, incomes: List[Dict[str, Any]], expenses: List[Dict[str, Any]], goals: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        aggregated = self.aggregate_financials(incomes, expenses)
        alerts = self.detect_overspending(profile, aggregated)
        budget = self.generate_personalized_budget(profile, incomes, expenses)
        recommendations = self.generate_saving_recommendations(profile, aggregated, alerts)
        health_score = self.calculate_financial_health_score(aggregated, profile)

        persona_titles = {
            'salaried': 'Salaried Professional Monthly Statement',
            'student': 'College Student Allowance & Expense Summary',
            'freelancer': 'Freelance Earnings & Volatility Ledger',
            'household': 'Consolidated Household Financial Statement'
        }

        return {
            'report_title': persona_titles.get(profile.get('persona_type', 'salaried'), 'Monthly Financial Statement'),
            'month_year': month_year,
            'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'financials': aggregated,
            'health_score': health_score,
            'health_grade': 'Excellent' if health_score >= 80 else 'Healthy' if health_score >= 65 else 'Attention Needed' if health_score >= 45 else 'Critical',
            'active_budget_plan': budget,
            'overspending_alerts': alerts,
            'actionable_recommendations': recommendations,
            'goals_summary': goals or []
        }


ai_engine = AIFinancialEngine()


# ==================== SCENARIO SEED DATA ====================

"""
Seed Data Generator for Personal Finance Advisor Bot
Provides rich, realistic datasets for all 4 core user scenarios:
1. Salaried Professional
2. College Student
3. Freelancer with Variable Income
4. Household Manager
"""

from datetime import date

SCENARIO_DATA = {
    'salaried': {
        'profile': {
            'username': 'alex_corporate',
            'email': 'alex.salaried@example.com',
            'persona_type': 'salaried',
            'display_title': 'Salaried Software Engineer',
            'monthly_target_savings': 1200.0,
            'emergency_fund_target': 18000.0,
            'current_emergency_fund': 12500.0,
            'income_variability_risk': 'low',
            'dependents_count': 0
        },
        'incomes': [
            {'source_name': 'Tech Corp Monthly Salary', 'amount': 5500.0, 'frequency': 'monthly', 'date': '2026-10-01', 'is_recurring': True}
        ],
        'expenses': [
            {'category_name': 'Rent & Housing', 'category_type': 'need', 'description': 'Monthly Apartment Rent', 'amount': 1600.0, 'date': '2026-10-02', 'frequency': 'monthly'},
            {'category_name': 'Groceries', 'category_type': 'need', 'description': 'Supermarket Groceries', 'amount': 550.0, 'date': '2026-10-05', 'frequency': 'weekly'},
            {'category_name': 'Utilities', 'category_type': 'need', 'description': 'Electric & Fiber Internet', 'amount': 180.0, 'date': '2026-10-07', 'frequency': 'monthly'},
            {'category_name': 'Transportation', 'category_type': 'need', 'description': 'Metro Pass & Fuel', 'amount': 220.0, 'date': '2026-10-10', 'frequency': 'monthly'},
            {'category_name': 'Dining Out', 'category_type': 'want', 'description': 'Weekend Dinners & Food Delivery', 'amount': 480.0, 'date': '2026-10-15', 'frequency': 'weekly'},
            {'category_name': 'Entertainment', 'category_type': 'want', 'description': 'Concert Tickets & Gaming', 'amount': 380.0, 'date': '2026-10-18', 'frequency': 'monthly'},
            {'category_name': 'Health & Fitness', 'category_type': 'need', 'description': 'Gym Membership', 'amount': 85.0, 'date': '2026-10-03', 'frequency': 'monthly'}
        ],
        'goals': [
            {'title': 'Emergency Fund (6 Months)', 'target_amount': 18000.0, 'current_amount': 12500.0, 'target_date': '2027-04-30', 'goal_category': 'emergency_fund'},
            {'title': 'Index Fund Investment Portfolio', 'target_amount': 25000.0, 'current_amount': 8400.0, 'target_date': '2027-12-31', 'goal_category': 'investment'}
        ]
    },
    'student': {
        'profile': {
            'username': 'maya_student',
            'email': 'maya.student@university.edu',
            'persona_type': 'student',
            'display_title': 'Undergraduate College Student',
            'monthly_target_savings': 150.0,
            'emergency_fund_target': 2500.0,
            'current_emergency_fund': 450.0,
            'monthly_allowance': 850.0,
            'income_variability_risk': 'medium',
            'dependents_count': 0
        },
        'incomes': [
            {'source_name': 'Parental Monthly Allowance', 'amount': 850.0, 'frequency': 'monthly', 'date': '2026-10-01', 'is_recurring': True},
            {'source_name': 'Campus Lab Assistant Stipend', 'amount': 320.0, 'frequency': 'monthly', 'date': '2026-10-15', 'is_recurring': True}
        ],
        'expenses': [
            {'category_name': 'Shared Dorm Rent', 'category_type': 'need', 'description': 'Student Housing Co-op Fee', 'amount': 450.0, 'date': '2026-10-01', 'frequency': 'monthly'},
            {'category_name': 'Campus Dining', 'category_type': 'need', 'description': 'Dining Hall Meal Plan & Groceries', 'amount': 260.0, 'date': '2026-10-04', 'frequency': 'weekly'},
            {'category_name': 'Textbooks & Supplies', 'category_type': 'need', 'description': 'Midterm Lab Manuals', 'amount': 75.0, 'date': '2026-10-08', 'frequency': 'monthly'},
            {'category_name': 'Coffee & Cafe Hangouts', 'category_type': 'want', 'description': 'Campus Cafe Study Sessions', 'amount': 110.0, 'date': '2026-10-12', 'frequency': 'weekly'},
            {'category_name': 'Social Outings', 'category_type': 'want', 'description': 'Weekend Movies & Group Dinners', 'amount': 140.0, 'date': '2026-10-20', 'frequency': 'weekly'},
            {'category_name': 'Digital Subscriptions', 'category_type': 'want', 'description': 'Music & Streaming', 'amount': 30.0, 'date': '2026-10-05', 'frequency': 'monthly'}
        ],
        'goals': [
            {'title': 'Post-Graduation Security Buffer', 'target_amount': 2500.0, 'current_amount': 450.0, 'target_date': '2027-06-15', 'goal_category': 'emergency_fund'},
            {'title': 'Laptop Upgrade Fund', 'target_amount': 1200.0, 'current_amount': 380.0, 'target_date': '2027-02-28', 'goal_category': 'purchase'}
        ]
    },
    'freelancer': {
        'profile': {
            'username': 'sam_freelance',
            'email': 'sam.creative@freelance.io',
            'persona_type': 'freelancer',
            'display_title': 'Independent UI/UX Consultant',
            'monthly_target_savings': 1800.0,
            'emergency_fund_target': 24000.0,
            'current_emergency_fund': 9800.0,
            'income_variability_risk': 'high',
            'dependents_count': 0
        },
        'incomes': [
            {'source_name': 'Fintech Design Sprint (Client A)', 'amount': 3200.0, 'frequency': 'project_based', 'date': '2026-10-04', 'is_recurring': False},
            {'source_name': 'Brand Retainer (Client B)', 'amount': 1500.0, 'frequency': 'monthly', 'date': '2026-10-12', 'is_recurring': True},
            {'source_name': 'Advisory Hourly Billing', 'amount': 950.0, 'frequency': 'project_based', 'date': '2026-10-24', 'is_recurring': False}
        ],
        'expenses': [
            {'category_name': 'Studio Apartment Rent', 'category_type': 'need', 'description': 'Monthly Living Quarters', 'amount': 1650.0, 'date': '2026-10-01', 'frequency': 'monthly'},
            {'category_name': 'Co-working Desk & Fiber', 'category_type': 'need', 'description': 'Shared Workspace Membership', 'amount': 350.0, 'date': '2026-10-03', 'frequency': 'monthly'},
            {'category_name': 'Design Software SaaS', 'category_type': 'need', 'description': 'Figma, Adobe CC, Notion', 'amount': 140.0, 'date': '2026-10-06', 'frequency': 'monthly'},
            {'category_name': 'Private Health Insurance', 'category_type': 'need', 'description': 'Freelancer Health & Dental Plan', 'amount': 420.0, 'date': '2026-10-10', 'frequency': 'monthly'},
            {'category_name': 'Groceries & Nutrition', 'category_type': 'need', 'description': 'Home Cooked Meal Supplies', 'amount': 520.0, 'date': '2026-10-14', 'frequency': 'weekly'},
            {'category_name': 'Client Business Meals', 'category_type': 'want', 'description': 'Pitch Lunches & Coffee Meetings', 'amount': 280.0, 'date': '2026-10-18', 'frequency': 'monthly'},
            {'category_name': 'Travel & Recreation', 'category_type': 'want', 'description': 'Weekend Road Trip', 'amount': 310.0, 'date': '2026-10-22', 'frequency': 'monthly'}
        ],
        'goals': [
            {'title': '6-Month Runway Emergency Fund', 'target_amount': 24000.0, 'current_amount': 9800.0, 'target_date': '2027-08-31', 'goal_category': 'emergency_fund'},
            {'title': 'Annual Quarterly Tax Reserve', 'target_amount': 14000.0, 'current_amount': 6500.0, 'target_date': '2027-03-31', 'goal_category': 'debt_payoff'}
        ]
    },
    'household': {
        'profile': {
            'username': 'jordan_family',
            'email': 'jordan.family@home.org',
            'persona_type': 'household',
            'display_title': 'Family Household Manager',
            'monthly_target_savings': 1800.0,
            'emergency_fund_target': 35000.0,
            'current_emergency_fund': 18500.0,
            'income_variability_risk': 'low',
            'dependents_count': 3
        },
        'incomes': [
            {'source_name': 'Primary Earner Salary', 'amount': 5200.0, 'frequency': 'monthly', 'date': '2026-10-01', 'is_recurring': True},
            {'source_name': 'Secondary Earner Salary', 'amount': 4100.0, 'frequency': 'monthly', 'date': '2026-10-01', 'is_recurring': True}
        ],
        'expenses': [
            {'category_name': 'Mortgage Payment', 'category_type': 'need', 'description': 'Home Mortgage & Property Tax', 'amount': 2750.0, 'date': '2026-10-01', 'frequency': 'monthly'},
            {'category_name': 'Family Groceries', 'category_type': 'need', 'description': 'Wholesale Market & Supermarket Groceries', 'amount': 1350.0, 'date': '2026-10-05', 'frequency': 'weekly'},
            {'category_name': 'Household Utilities', 'category_type': 'need', 'description': 'Power, Water, Gas, Fiber, Trash', 'amount': 480.0, 'date': '2026-10-08', 'frequency': 'monthly'},
            {'category_name': 'Childcare & Tuition', 'category_type': 'need', 'description': 'School Fees & After-school Care', 'amount': 1650.0, 'date': '2026-10-10', 'frequency': 'monthly'},
            {'category_name': 'Family Healthcare & Rx', 'category_type': 'need', 'description': 'Pediatrician & Dental Copays', 'amount': 380.0, 'date': '2026-10-12', 'frequency': 'monthly'},
            {'category_name': 'Vehicles & Insurance', 'category_type': 'need', 'description': 'Auto Loan, Gas & Joint Auto Insurance', 'amount': 720.0, 'date': '2026-10-15', 'frequency': 'monthly'},
            {'category_name': 'Family Outings & Activities', 'category_type': 'want', 'description': 'Zoo Passes, Weekend Dinners & Sports', 'amount': 480.0, 'date': '2026-10-21', 'frequency': 'weekly'}
        ],
        'goals': [
            {'title': 'College Education Sinking Fund', 'target_amount': 50000.0, 'current_amount': 18500.0, 'target_date': '2030-08-01', 'goal_category': 'investment'},
            {'title': 'Home Maintenance & Repair Reserve', 'target_amount': 15000.0, 'current_amount': 7200.0, 'target_date': '2027-10-31', 'goal_category': 'emergency_fund'}
        ]
    }
}


# ==================== RESTFUL API & WEB ROUTES ====================

"""
Flask RESTful API and Web Routes for Personal Finance Advisor Bot
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date

ai_engine = AIFinancialEngine()

def get_current_user():
    user = User.query.first()
    if not user:
        user = seed_scenario_user('salaried')
    return user

def seed_scenario_user(persona_key):
    data = SCENARIO_DATA.get(persona_key, SCENARIO_DATA['salaried'])
    prof_data = data['profile']

    user = User.query.filter_by(username=prof_data['username']).first()
    if not user:
        user = User(username=prof_data['username'], email=prof_data['email'])
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            persona_type=prof_data['persona_type'],
            display_title=prof_data['display_title'],
            monthly_target_savings=prof_data['monthly_target_savings'],
            emergency_fund_target=prof_data['emergency_fund_target'],
            current_emergency_fund=prof_data['current_emergency_fund'],
            monthly_allowance=prof_data.get('monthly_allowance', 0.0),
            income_variability_risk=prof_data.get('income_variability_risk', 'low'),
            dependents_count=prof_data.get('dependents_count', 0)
        )
        db.session.add(profile)
    else:
        Income.query.filter_by(user_id=user.id).delete()
        Expense.query.filter_by(user_id=user.id).delete()
        FinancialGoal.query.filter_by(user_id=user.id).delete()
        BudgetPlan.query.filter_by(user_id=user.id).delete()

    for inc in data['incomes']:
        inc_date = datetime.strptime(inc['date'], '%Y-%m-%d').date() if isinstance(inc['date'], str) else inc['date']
        i_rec = Income(
            user_id=user.id,
            source_name=inc['source_name'],
            amount=inc['amount'],
            frequency=inc['frequency'],
            date=inc_date,
            is_recurring=inc.get('is_recurring', True)
        )
        db.session.add(i_rec)

    for exp in data['expenses']:
        cat = Category.query.filter_by(name=exp['category_name']).first()
        if not cat:
            cat = Category(name=exp['category_name'], category_type=exp.get('category_type', 'need'))
            db.session.add(cat)
            db.session.flush()
        
        exp_date = datetime.strptime(exp['date'], '%Y-%m-%d').date() if isinstance(exp['date'], str) else exp['date']
        e_rec = Expense(
            user_id=user.id,
            category_id=cat.id,
            description=exp['description'],
            amount=exp['amount'],
            date=exp_date,
            frequency=exp.get('frequency', 'daily')
        )
        db.session.add(e_rec)

    for g in data.get('goals', []):
        t_date = datetime.strptime(g['target_date'], '%Y-%m-%d').date() if isinstance(g['target_date'], str) else g['target_date']
        goal_rec = FinancialGoal(
            user_id=user.id,
            title=g['title'],
            target_amount=g['target_amount'],
            current_amount=g['current_amount'],
            target_date=t_date,
            goal_category=g.get('goal_category', 'emergency_fund')
        )
        db.session.add(goal_rec)

    db.session.commit()
    return user

# ==================== EMBEDDED DASHBOARD TEMPLATE ====================

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal Finance Advisor Bot | AI Financial Planning Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #0b1120; color: #f8fafc; }
    .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-input { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.12); color: #f8fafc; }
  </style>
</head>
<body class="min-h-screen">
  <header class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-40 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-slate-950 font-bold text-xl">
          ₹
        </div>
        <div>
          <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-200">
            Personal Finance Advisor Bot
          </h1>
          <p class="text-xs text-slate-400">AI-Powered Financial Planning Assistant (Flask • SQLAlchemy • AI Engine)</p>
        </div>
      </div>

      <div class="flex items-center space-x-2 bg-slate-950/60 p-1.5 rounded-xl border border-slate-800 text-xs font-medium">
        <span class="text-slate-400 px-2">Scenario:</span>
        <button onclick="switchScenario('salaried')" id="btn-salaried" class="scenario-btn px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-semibold transition">1. Salaried</button>
        <button onclick="switchScenario('student')" id="btn-student" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">2. Student</button>
        <button onclick="switchScenario('freelancer')" id="btn-freelancer" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">3. Freelancer</button>
        <button onclick="switchScenario('household')" id="btn-household" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">4. Household</button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
    <div class="glass-card rounded-2xl p-4 sm:p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-l-4 border-l-emerald-500">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase font-bold tracking-wider text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/30">Active Persona</span>
          <h2 id="persona-title" class="text-lg font-bold text-white">Salaried Software Engineer</h2>
        </div>
        <p id="persona-summary" class="text-xs text-slate-300 mt-1 max-w-2xl">
          Logs monthly salary and daily expenses across rent, food, transport, and leisure. AI detects overspending in discretionary categories and provides 50/30/20 budget sweeps.
        </p>
      </div>
      <div class="flex items-center gap-3 w-full md:w-auto">
        <button onclick="generateAIBudget()" class="flex-1 md:flex-none px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20 hover:opacity-95 transition flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          Regenerate AI Budget
        </button>
        <button onclick="openReportModal()" class="flex-1 md:flex-none px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          Monthly Statement
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Total Monthly Income</p>
          <span class="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"/></svg>
          </span>
        </div>
        <h3 id="stat-income" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p class="text-xs text-emerald-400 mt-1 flex items-center gap-1">100% Inflow Tracked</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Total Expenses Logged</p>
          <span class="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6"/></svg>
          </span>
        </div>
        <h3 id="stat-expense" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p id="stat-expense-burn" class="text-xs text-slate-400 mt-1">Burn rate calculation...</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Net Monthly Savings</p>
          <span class="p-1.5 rounded-lg bg-teal-500/10 text-teal-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </span>
        </div>
        <h3 id="stat-savings" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p id="stat-savings-rate" class="text-xs text-teal-400 mt-1">0% Savings Rate</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">AI Financial Health Score</p>
          <span id="health-grade-pill" class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400">Optimal</span>
        </div>
        <div class="flex items-baseline gap-2 mt-2">
          <h3 id="stat-health-score" class="text-2xl font-bold text-white">0</h3>
          <span class="text-xs text-slate-400">/ 100</span>
        </div>
        <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
          <div id="health-bar" class="bg-gradient-to-r from-teal-400 to-emerald-400 h-full rounded-full" style="width: 0%"></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="glass-card rounded-2xl p-6">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h3 class="font-bold text-base text-white">AI Budget Plan & Spending Distribution</h3>
              <p id="ai-strategy-text" class="text-xs text-slate-400 mt-0.5">Custom algorithm tailored to your lifestyle profile.</p>
            </div>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">October 2026</span>
          </div>

          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Needs (Essential Living)</span>
                <span id="bucket-needs-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-needs-bar" class="bg-blue-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Wants (Discretionary & Leisure)</span>
                <span id="bucket-wants-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-wants-bar" class="bg-amber-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Savings & Debt Reserve</span>
                <span id="bucket-savings-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-savings-bar" class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>
          </div>

          <div class="mt-6 border-t border-slate-800 pt-4">
            <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Itemized Category Outlays</h4>
            <div id="category-chips" class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
            </div>
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-base text-white">Recent Transactions</h3>
            <div class="flex gap-2">
              <button onclick="toggleTransactionModal('income')" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition">+ Log Income</button>
              <button onclick="toggleTransactionModal('expense')" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20 transition">+ Log Expense</button>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead>
                <tr class="text-slate-400 border-b border-slate-800">
                  <th class="pb-2 font-medium">Date</th>
                  <th class="pb-2 font-medium">Description</th>
                  <th class="pb-2 font-medium">Category</th>
                  <th class="pb-2 font-medium text-right">Amount</th>
                </tr>
              </thead>
              <tbody id="transactions-tbody" class="divide-y divide-slate-800/60">
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="glass-card rounded-2xl p-6 border-t-2 border-t-amber-500">
          <div class="flex items-center space-x-2 mb-3">
            <div class="p-1 rounded-md bg-amber-500/20 text-amber-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            <h3 class="font-bold text-sm text-white">AI Anomaly & Overspend Alerts</h3>
          </div>
          <div id="alerts-container" class="space-y-2.5">
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6 border-t-2 border-t-teal-500">
          <div class="flex items-center space-x-2 mb-3">
            <div class="p-1 rounded-md bg-teal-500/20 text-teal-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            </div>
            <h3 class="font-bold text-sm text-white">Actionable Saving Recommendations</h3>
          </div>
          <div id="recommendations-container" class="space-y-3">
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6">
          <h3 class="font-bold text-sm text-white mb-3">Milestone Saving Goals</h3>
          <div id="goals-container" class="space-y-3">
          </div>
        </div>
      </div>
    </div>
  </main>

  <div id="report-modal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-2xl w-full rounded-2xl p-6 max-h-[90vh] overflow-y-auto space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 id="modal-report-title" class="font-bold text-lg text-white">Monthly Financial Statement</h3>
        <button onclick="closeReportModal()" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <div id="modal-report-body" class="text-xs space-y-3 text-slate-300">
      </div>
      <div class="text-right pt-2 border-t border-slate-800">
        <button onclick="closeReportModal()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200">Close</button>
      </div>
    </div>
  </div>

  <div id="tx-modal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-md w-full rounded-2xl p-6 space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 id="tx-modal-title" class="font-bold text-base text-white">Log Transaction</h3>
        <button onclick="closeTxModal()" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <form id="tx-form" onsubmit="submitTransaction(event)" class="space-y-3 text-xs">
        <input type="hidden" id="tx-type" value="expense">
        <div>
          <label class="block text-slate-400 mb-1">Title / Description</label>
          <input type="text" id="tx-desc" required placeholder="e.g. Client Payment or Grocery Run" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div id="tx-cat-wrapper">
          <label class="block text-slate-400 mb-1">Category</label>
          <input type="text" id="tx-cat" placeholder="e.g. Groceries, Entertainment, Rent" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Amount ($)</label>
          <input type="number" step="0.01" id="tx-amount" required placeholder="0.00" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Date</label>
          <input type="date" id="tx-date" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="closeTxModal()" class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300">Cancel</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400">Save</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let currentScenario = 'salaried';

    async function loadDashboard() {
      try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      }
    }

    function renderDashboard(data) {
      const { profile, financials, budget_plan, alerts, recommendations, health_score, goals, recent_expenses } = data;

      document.getElementById('persona-title').textContent = profile.display_title || 'Financial Profile';
      
      const summaries = {
        'salaried': 'Logs monthly salary and daily expenses across rent, food, transport, and leisure. AI detects overspending in discretionary categories and provides 50/30/20 budget sweeps.',
        'student': 'Tracks constrained monthly allowance across essentials (dorm, campus food, textbooks) and discretionary leisure, providing micro-budget guardrails.',
        'freelancer': 'Handles variable project billings and multiple clients, establishing lean baseline living budgets and emergency fund escrow reserves.',
        'household': 'Aggregates multi-earner family income streams to manage high-cost shared groceries, utilities, childcare, and sinking funds.'
      };
      document.getElementById('persona-summary').textContent = summaries[profile.persona_type] || '';

      document.getElementById('stat-income').textContent = `$${financials.total_income.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-expense').textContent = `$${financials.total_expense.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-savings').textContent = `$${financials.net_savings.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-savings-rate').textContent = `${financials.savings_rate}% Monthly Savings Rate`;
      document.getElementById('stat-expense-burn').textContent = `${(100 - financials.savings_rate).toFixed(1)}% Income Utilized`;
      document.getElementById('stat-health-score').textContent = health_score;
      document.getElementById('health-bar').style.width = `${health_score}%`;

      const healthGradePill = document.getElementById('health-grade-pill');
      if (health_score >= 80) {
        healthGradePill.textContent = 'Excellent';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400';
      } else if (health_score >= 65) {
        healthGradePill.textContent = 'Healthy';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-teal-500/20 text-teal-400';
      } else {
        healthGradePill.textContent = 'Action Needed';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-400';
      }

      document.getElementById('ai-strategy-text').textContent = budget_plan.ai_strategy_summary || 'Custom AI Strategy Active';
      
      const needsSpent = financials.by_type.need || 0;
      const needsCap = budget_plan.allocated_needs || (financials.total_income * 0.5);
      const needsPct = needsCap > 0 ? Math.min(100, (needsSpent / needsCap) * 100) : 0;
      document.getElementById('bucket-needs-label').textContent = `$${needsSpent.toLocaleString()} / $${needsCap.toLocaleString()} (${needsPct.toFixed(0)}%)`;
      document.getElementById('bucket-needs-bar').style.width = `${needsPct}%`;
      document.getElementById('bucket-needs-bar').className = needsPct > 100 ? 'bg-rose-500 h-full rounded-full' : 'bg-blue-500 h-full rounded-full';

      const wantsSpent = financials.by_type.want || 0;
      const wantsCap = budget_plan.allocated_wants || (financials.total_income * 0.3);
      const wantsPct = wantsCap > 0 ? Math.min(100, (wantsSpent / wantsCap) * 100) : 0;
      document.getElementById('bucket-wants-label').textContent = `$${wantsSpent.toLocaleString()} / $${wantsCap.toLocaleString()} (${wantsPct.toFixed(0)}%)`;
      document.getElementById('bucket-wants-bar').style.width = `${wantsPct}%`;
      document.getElementById('bucket-wants-bar').className = wantsPct > 100 ? 'bg-rose-500 h-full rounded-full' : 'bg-amber-500 h-full rounded-full';

      const savingsTarget = budget_plan.allocated_savings || (financials.total_income * 0.2);
      const savingsPct = savingsTarget > 0 ? Math.min(100, (financials.net_savings / savingsTarget) * 100) : 0;
      document.getElementById('bucket-savings-label').textContent = `$${financials.net_savings.toLocaleString()} / $${savingsTarget.toLocaleString()} (${savingsPct.toFixed(0)}%)`;
      document.getElementById('bucket-savings-bar').style.width = `${savingsPct}%`;

      const chipsEl = document.getElementById('category-chips');
      chipsEl.innerHTML = '';
      for (const [cat, amt] of Object.entries(financials.by_category)) {
        const div = document.createElement('div');
        div.className = 'p-2 rounded-xl bg-slate-900/90 border border-slate-800 flex justify-between items-center';
        div.innerHTML = `<span class="text-slate-300 truncate">${cat}</span><span class="font-bold text-white">$${amt.toLocaleString()}</span>`;
        chipsEl.appendChild(div);
      }

      const tbody = document.getElementById('transactions-tbody');
      tbody.innerHTML = '';
      recent_expenses.slice(-6).reverse().forEach(t => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40';
        tr.innerHTML = `
          <td class="py-2.5 text-slate-400">${t.date}</td>
          <td class="py-2.5 font-medium text-slate-200">${t.description}</td>
          <td class="py-2.5"><span class="px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-slate-300">${t.category_name}</span></td>
          <td class="py-2.5 text-right font-semibold text-rose-400">-$${t.amount.toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });

      const alertsEl = document.getElementById('alerts-container');
      alertsEl.innerHTML = '';
      if (!alerts || alerts.length === 0) {
        alertsEl.innerHTML = '<p class="text-xs text-slate-400 italic">No budget overspending detected. Keep up the disciplined spending!</p>';
      } else {
        alerts.forEach(a => {
          const div = document.createElement('div');
          const borderCol = a.severity === 'critical' ? 'border-rose-500/50 bg-rose-950/20' : 'border-amber-500/40 bg-amber-950/20';
          div.className = `p-3 rounded-xl border ${borderCol} text-xs`;
          div.innerHTML = `<p class="font-semibold text-white">${a.title}</p><p class="text-slate-300 mt-0.5 leading-relaxed">${a.message}</p>`;
          alertsEl.appendChild(div);
        });
      }

      const recsEl = document.getElementById('recommendations-container');
      recsEl.innerHTML = '';
      recommendations.forEach(r => {
        const div = document.createElement('div');
        div.className = 'p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs';
        div.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-teal-300">${r.action}</span>
            <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-400">${r.priority}</span>
          </div>
          <p class="text-slate-300 mt-1 leading-relaxed">${r.description}</p>
          <p class="text-[11px] text-emerald-400 font-medium mt-1">Impact: ${r.impact}</p>
        `;
        recsEl.appendChild(div);
      });

      const goalsEl = document.getElementById('goals-container');
      goalsEl.innerHTML = '';
      goals.forEach(g => {
        const div = document.createElement('div');
        div.className = 'p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1';
        div.innerHTML = `
          <div class="flex justify-between font-medium">
            <span class="text-slate-200">${g.title}</span>
            <span class="text-slate-400">$${g.current_amount.toLocaleString()} / $${g.target_amount.toLocaleString()}</span>
          </div>
          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div class="bg-gradient-to-r from-teal-500 to-emerald-400 h-full rounded-full" style="width: ${g.progress_pct}%"></div>
          </div>
          <p class="text-[10px] text-slate-400 text-right">${g.progress_pct}% achieved • Target: ${g.target_date}</p>
        `;
        goalsEl.appendChild(div);
      });
    }

    async function switchScenario(key) {
      currentScenario = key;
      document.querySelectorAll('.scenario-btn').forEach(b => {
        b.className = 'scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition';
      });
      const activeBtn = document.getElementById(`btn-${key}`);
      if (activeBtn) activeBtn.className = 'scenario-btn px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-semibold transition';

      try {
        await fetch('/api/scenarios/switch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ persona: key })
        });
        await loadDashboard();
      } catch (err) {
        console.error('Failed to switch scenario:', err);
      }
    }

    async function generateAIBudget() {
      try {
        await fetch('/api/budget/generate', { method: 'POST' });
        await loadDashboard();
      } catch (err) {
        console.error('Error generating AI budget:', err);
      }
    }

    async function openReportModal() {
      try {
        const res = await fetch('/api/report');
        const r = await res.json();
        document.getElementById('modal-report-title').textContent = r.report_title;
        document.getElementById('modal-report-body').innerHTML = `
          <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            <div><p class="text-slate-400 text-[10px]">Income</p><p class="text-sm font-bold text-emerald-400">$${r.financials.total_income.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Expenses</p><p class="text-sm font-bold text-rose-400">$${r.financials.total_expense.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Net Savings</p><p class="text-sm font-bold text-white">$${r.financials.net_savings.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Health Grade</p><p class="text-sm font-bold text-teal-400">${r.health_grade} (${r.health_score}/100)</p></div>
          </div>
          <div class="mt-3">
            <h5 class="font-bold text-slate-200 mb-1">Executive AI Strategy Assessment</h5>
            <p class="leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">${r.active_budget_plan.ai_strategy_summary}</p>
          </div>
          <div class="mt-3">
            <h5 class="font-bold text-slate-200 mb-1">Top Saving Directives</h5>
            <ul class="list-disc list-inside space-y-1 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
              ${r.actionable_recommendations.map(a => `<li><strong class="text-teal-300">${a.action}:</strong> ${a.description} <em class="text-emerald-400">(${a.impact})</em></li>`).join('')}
            </ul>
          </div>
        `;
        document.getElementById('report-modal').classList.remove('hidden');
      } catch (err) {
        console.error('Failed to open statement:', err);
      }
    }

    function closeReportModal() {
      document.getElementById('report-modal').classList.add('hidden');
    }

    function toggleTransactionModal(type) {
      document.getElementById('tx-type').value = type;
      document.getElementById('tx-modal-title').textContent = type === 'income' ? 'Log Income Stream' : 'Log Daily/Weekly Expense';
      document.getElementById('tx-cat-wrapper').style.display = type === 'income' ? 'none' : 'block';
      document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
      document.getElementById('tx-modal').classList.remove('hidden');
    }

    function closeTxModal() {
      document.getElementById('tx-modal').classList.add('hidden');
    }

    async function submitTransaction(e) {
      e.preventDefault();
      const type = document.getElementById('tx-type').value;
      const desc = document.getElementById('tx-desc').value;
      const cat = document.getElementById('tx-cat').value || 'General';
      const amount = parseFloat(document.getElementById('tx-amount').value);
      const date = document.getElementById('tx-date').value;

      const endpoint = type === 'income' ? '/api/income' : '/api/expense';
      const payload = type === 'income' ? { source_name: desc, amount, date } : { description: desc, category_name: cat, amount, date };

      try {
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        closeTxModal();
        await loadDashboard();
      } catch (err) {
        console.error('Error logging transaction:', err);
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
      loadDashboard();
    });
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML_TEMPLATE)


# ==================== APPLICATION RUNNER ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed default salaried scenario if empty
        if not User.query.first():
            seed_scenario_user('salaried')
    print("=" * 70)
    print("  Personal Finance Advisor Bot is running!")
    print("  Local Dashboard:  http://127.0.0.1:5000")
    print("  Default Scenario: Salaried Professional (Switchable via UI)")
    print("=" * 70)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    scenarios = []
    for k, v in SCENARIO_DATA.items():
        p = v['profile']
        scenarios.append({
            'key': k,
            'title': p['display_title'],
            'persona_type': p['persona_type'],
            'description': f"{p['persona_type'].capitalize()} financial scenario with tailored budget strategy."
        })
    return jsonify({'scenarios': scenarios})

@app.route('/api/scenarios/switch', methods=['POST'])
def switch_scenario():
    data = request.get_json() or {}
    persona_key = data.get('persona', 'salaried')
    if persona_key not in SCENARIO_DATA:
        return jsonify({'error': 'Invalid scenario persona'}), 400
    
    user = seed_scenario_user(persona_key)
    return jsonify({
        'status': 'success',
        'message': f'Switched to {SCENARIO_DATA[persona_key]["profile"]["display_title"]}',
        'user_id': user.id
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    user = get_current_user()
    profile = user.profile.to_dict() if user.profile else {}
    incomes = [i.to_dict() for i in user.incomes]
    expenses = [e.to_dict() for e in user.expenses]
    goals = [g.to_dict() for g in user.goals]

    aggregated = ai_engine.aggregate_financials(incomes, expenses)
    latest_budget = BudgetPlan.query.filter_by(user_id=user.id).order_by(BudgetPlan.created_at.desc()).first()
    budget_dict = latest_budget.to_dict() if latest_budget else ai_engine.generate_personalized_budget(profile, incomes, expenses)
    alerts = ai_engine.detect_overspending(profile, aggregated, budget_dict)
    recs = ai_engine.generate_saving_recommendations(profile, aggregated, alerts)
    health_score = ai_engine.calculate_financial_health_score(aggregated, profile)

    return jsonify({
        'user': user.to_dict(),
        'profile': profile,
        'financials': aggregated,
        'budget_plan': budget_dict,
        'alerts': alerts,
        'recommendations': recs,
        'health_score': health_score,
        'goals': goals,
        'recent_expenses': expenses[-8:],
        'recent_incomes': incomes
    })

@app.route('/api/income', methods=['POST'])
def add_income():
    user = get_current_user()
    data = request.get_json() or {}
    try:
        amount = float(data.get('amount', 0))
        source_name = data.get('source_name', 'Other Income')
        frequency = data.get('frequency', 'monthly')
        date_val = datetime.strptime(data.get('date', date.today().isoformat()), '%Y-%m-%d').date()

        inc = Income(user_id=user.id, source_name=source_name, amount=amount, frequency=frequency, date=date_val)
        db.session.add(inc)
        db.session.commit()
        return jsonify({'status': 'success', 'income': inc.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/expense', methods=['POST'])
def add_expense():
    user = get_current_user()
    data = request.get_json() or {}
    try:
        amount = float(data.get('amount', 0))
        cat_name = data.get('category_name', 'General')
        cat_type = data.get('category_type', 'need')
        desc = data.get('description', '')
        freq = data.get('frequency', 'daily')
        date_val = datetime.strptime(data.get('date', date.today().isoformat()), '%Y-%m-%d').date()

        cat = Category.query.filter_by(name=cat_name).first()
        if not cat:
            cat = Category(name=cat_name, category_type=cat_type)
            db.session.add(cat)
            db.session.flush()

        exp = Expense(user_id=user.id, category_id=cat.id, description=desc, amount=amount, date=date_val, frequency=freq)
        db.session.add(exp)
        db.session.commit()
        return jsonify({'status': 'success', 'expense': exp.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/budget/generate', methods=['POST'])
def generate_budget_plan():
    user = get_current_user()
    profile = user.profile.to_dict() if user.profile else {}
    incomes = [i.to_dict() for i in user.incomes]
    expenses = [e.to_dict() for e in user.expenses]

    plan_data = ai_engine.generate_personalized_budget(profile, incomes, expenses)
    month_str = date.today().strftime('%Y-%m')

    b_plan = BudgetPlan(
        user_id=user.id,
        month_year=month_str,
        total_projected_income=plan_data['total_projected_income'],
        allocated_needs=plan_data['allocated_needs'],
        allocated_wants=plan_data['allocated_wants'],
        allocated_savings=plan_data['allocated_savings'],
        allocated_debt=plan_data['allocated_debt'],
        ai_strategy_summary=plan_data['ai_strategy_summary']
    )
    db.session.add(b_plan)
    db.session.flush()

    for alloc in plan_data.get('allocations', []):
        cat = Category.query.filter_by(name=alloc['category_name']).first()
        if cat:
            b_alloc = BudgetCategoryAllocation(
                budget_plan_id=b_plan.id,
                category_id=cat.id,
                allocated_cap=alloc['allocated_cap']
            )
            db.session.add(b_alloc)

    db.session.commit()
    return jsonify({'status': 'success', 'budget_plan': b_plan.to_dict()})

@app.route('/api/report', methods=['GET'])
def get_monthly_report():
    user = get_current_user()
    profile = user.profile.to_dict() if user.profile else {}
    incomes = [i.to_dict() for i in user.incomes]
    expenses = [e.to_dict() for e in user.expenses]
    goals = [g.to_dict() for g in user.goals]
    month_str = request.args.get('month', date.today().strftime('%Y-%m'))

    report_dict = ai_engine.generate_monthly_report(profile, month_str, incomes, expenses, goals)
    return jsonify(report_dict)

# ==================== EMBEDDED DASHBOARD TEMPLATE ====================

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal Finance Advisor Bot | AI Financial Planning Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #0b1120; color: #f8fafc; }
    .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-input { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.12); color: #f8fafc; }
  </style>
</head>
<body class="min-h-screen">
  <header class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-40 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-slate-950 font-bold text-xl">
          ₹
        </div>
        <div>
          <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-200">
            Personal Finance Advisor Bot
          </h1>
          <p class="text-xs text-slate-400">AI-Powered Financial Planning Assistant (Flask • SQLAlchemy • AI Engine)</p>
        </div>
      </div>

      <div class="flex items-center space-x-2 bg-slate-950/60 p-1.5 rounded-xl border border-slate-800 text-xs font-medium">
        <span class="text-slate-400 px-2">Scenario:</span>
        <button onclick="switchScenario('salaried')" id="btn-salaried" class="scenario-btn px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-semibold transition">1. Salaried</button>
        <button onclick="switchScenario('student')" id="btn-student" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">2. Student</button>
        <button onclick="switchScenario('freelancer')" id="btn-freelancer" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">3. Freelancer</button>
        <button onclick="switchScenario('household')" id="btn-household" class="scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition">4. Household</button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
    <div class="glass-card rounded-2xl p-4 sm:p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-l-4 border-l-emerald-500">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase font-bold tracking-wider text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/30">Active Persona</span>
          <h2 id="persona-title" class="text-lg font-bold text-white">Salaried Software Engineer</h2>
        </div>
        <p id="persona-summary" class="text-xs text-slate-300 mt-1 max-w-2xl">
          Logs monthly salary and daily expenses across rent, food, transport, and leisure. AI detects overspending in discretionary categories and provides 50/30/20 budget sweeps.
        </p>
      </div>
      <div class="flex items-center gap-3 w-full md:w-auto">
        <button onclick="generateAIBudget()" class="flex-1 md:flex-none px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20 hover:opacity-95 transition flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          Regenerate AI Budget
        </button>
        <button onclick="openReportModal()" class="flex-1 md:flex-none px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          Monthly Statement
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Total Monthly Income</p>
          <span class="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"/></svg>
          </span>
        </div>
        <h3 id="stat-income" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p class="text-xs text-emerald-400 mt-1 flex items-center gap-1">100% Inflow Tracked</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Total Expenses Logged</p>
          <span class="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6"/></svg>
          </span>
        </div>
        <h3 id="stat-expense" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p id="stat-expense-burn" class="text-xs text-slate-400 mt-1">Burn rate calculation...</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">Net Monthly Savings</p>
          <span class="p-1.5 rounded-lg bg-teal-500/10 text-teal-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </span>
        </div>
        <h3 id="stat-savings" class="text-2xl font-bold text-white mt-2">$0.00</h3>
        <p id="stat-savings-rate" class="text-xs text-teal-400 mt-1">0% Savings Rate</p>
      </div>

      <div class="glass-card rounded-2xl p-5">
        <div class="flex justify-between items-start">
          <p class="text-xs font-medium text-slate-400">AI Financial Health Score</p>
          <span id="health-grade-pill" class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400">Optimal</span>
        </div>
        <div class="flex items-baseline gap-2 mt-2">
          <h3 id="stat-health-score" class="text-2xl font-bold text-white">0</h3>
          <span class="text-xs text-slate-400">/ 100</span>
        </div>
        <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
          <div id="health-bar" class="bg-gradient-to-r from-teal-400 to-emerald-400 h-full rounded-full" style="width: 0%"></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="glass-card rounded-2xl p-6">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h3 class="font-bold text-base text-white">AI Budget Plan & Spending Distribution</h3>
              <p id="ai-strategy-text" class="text-xs text-slate-400 mt-0.5">Custom algorithm tailored to your lifestyle profile.</p>
            </div>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">October 2026</span>
          </div>

          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Needs (Essential Living)</span>
                <span id="bucket-needs-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-needs-bar" class="bg-blue-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Wants (Discretionary & Leisure)</span>
                <span id="bucket-wants-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-wants-bar" class="bg-amber-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-medium mb-1.5">
                <span class="text-slate-300">Savings & Debt Reserve</span>
                <span id="bucket-savings-label" class="text-slate-400">$0 / $0</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div id="bucket-savings-bar" class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>
          </div>

          <div class="mt-6 border-t border-slate-800 pt-4">
            <h4 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Itemized Category Outlays</h4>
            <div id="category-chips" class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
            </div>
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-base text-white">Recent Transactions</h3>
            <div class="flex gap-2">
              <button onclick="toggleTransactionModal('income')" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition">+ Log Income</button>
              <button onclick="toggleTransactionModal('expense')" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20 transition">+ Log Expense</button>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead>
                <tr class="text-slate-400 border-b border-slate-800">
                  <th class="pb-2 font-medium">Date</th>
                  <th class="pb-2 font-medium">Description</th>
                  <th class="pb-2 font-medium">Category</th>
                  <th class="pb-2 font-medium text-right">Amount</th>
                </tr>
              </thead>
              <tbody id="transactions-tbody" class="divide-y divide-slate-800/60">
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="glass-card rounded-2xl p-6 border-t-2 border-t-amber-500">
          <div class="flex items-center space-x-2 mb-3">
            <div class="p-1 rounded-md bg-amber-500/20 text-amber-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            </div>
            <h3 class="font-bold text-sm text-white">AI Anomaly & Overspend Alerts</h3>
          </div>
          <div id="alerts-container" class="space-y-2.5">
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6 border-t-2 border-t-teal-500">
          <div class="flex items-center space-x-2 mb-3">
            <div class="p-1 rounded-md bg-teal-500/20 text-teal-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            </div>
            <h3 class="font-bold text-sm text-white">Actionable Saving Recommendations</h3>
          </div>
          <div id="recommendations-container" class="space-y-3">
          </div>
        </div>

        <div class="glass-card rounded-2xl p-6">
          <h3 class="font-bold text-sm text-white mb-3">Milestone Saving Goals</h3>
          <div id="goals-container" class="space-y-3">
          </div>
        </div>
      </div>
    </div>
  </main>

  <div id="report-modal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-2xl w-full rounded-2xl p-6 max-h-[90vh] overflow-y-auto space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 id="modal-report-title" class="font-bold text-lg text-white">Monthly Financial Statement</h3>
        <button onclick="closeReportModal()" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <div id="modal-report-body" class="text-xs space-y-3 text-slate-300">
      </div>
      <div class="text-right pt-2 border-t border-slate-800">
        <button onclick="closeReportModal()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200">Close</button>
      </div>
    </div>
  </div>

  <div id="tx-modal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-md w-full rounded-2xl p-6 space-y-4 border border-slate-700">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 id="tx-modal-title" class="font-bold text-base text-white">Log Transaction</h3>
        <button onclick="closeTxModal()" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <form id="tx-form" onsubmit="submitTransaction(event)" class="space-y-3 text-xs">
        <input type="hidden" id="tx-type" value="expense">
        <div>
          <label class="block text-slate-400 mb-1">Title / Description</label>
          <input type="text" id="tx-desc" required placeholder="e.g. Client Payment or Grocery Run" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div id="tx-cat-wrapper">
          <label class="block text-slate-400 mb-1">Category</label>
          <input type="text" id="tx-cat" placeholder="e.g. Groceries, Entertainment, Rent" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Amount ($)</label>
          <input type="number" step="0.01" id="tx-amount" required placeholder="0.00" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div>
          <label class="block text-slate-400 mb-1">Date</label>
          <input type="date" id="tx-date" class="w-full p-2.5 rounded-lg glass-input focus:outline-none focus:border-emerald-500">
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="closeTxModal()" class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300">Cancel</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400">Save</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let currentScenario = 'salaried';

    async function loadDashboard() {
      try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      }
    }

    function renderDashboard(data) {
      const { profile, financials, budget_plan, alerts, recommendations, health_score, goals, recent_expenses } = data;

      document.getElementById('persona-title').textContent = profile.display_title || 'Financial Profile';
      
      const summaries = {
        'salaried': 'Logs monthly salary and daily expenses across rent, food, transport, and leisure. AI detects overspending in discretionary categories and provides 50/30/20 budget sweeps.',
        'student': 'Tracks constrained monthly allowance across essentials (dorm, campus food, textbooks) and discretionary leisure, providing micro-budget guardrails.',
        'freelancer': 'Handles variable project billings and multiple clients, establishing lean baseline living budgets and emergency fund escrow reserves.',
        'household': 'Aggregates multi-earner family income streams to manage high-cost shared groceries, utilities, childcare, and sinking funds.'
      };
      document.getElementById('persona-summary').textContent = summaries[profile.persona_type] || '';

      document.getElementById('stat-income').textContent = `$${financials.total_income.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-expense').textContent = `$${financials.total_expense.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-savings').textContent = `$${financials.net_savings.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
      document.getElementById('stat-savings-rate').textContent = `${financials.savings_rate}% Monthly Savings Rate`;
      document.getElementById('stat-expense-burn').textContent = `${(100 - financials.savings_rate).toFixed(1)}% Income Utilized`;
      document.getElementById('stat-health-score').textContent = health_score;
      document.getElementById('health-bar').style.width = `${health_score}%`;

      const healthGradePill = document.getElementById('health-grade-pill');
      if (health_score >= 80) {
        healthGradePill.textContent = 'Excellent';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400';
      } else if (health_score >= 65) {
        healthGradePill.textContent = 'Healthy';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-teal-500/20 text-teal-400';
      } else {
        healthGradePill.textContent = 'Action Needed';
        healthGradePill.className = 'text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-400';
      }

      document.getElementById('ai-strategy-text').textContent = budget_plan.ai_strategy_summary || 'Custom AI Strategy Active';
      
      const needsSpent = financials.by_type.need || 0;
      const needsCap = budget_plan.allocated_needs || (financials.total_income * 0.5);
      const needsPct = needsCap > 0 ? Math.min(100, (needsSpent / needsCap) * 100) : 0;
      document.getElementById('bucket-needs-label').textContent = `$${needsSpent.toLocaleString()} / $${needsCap.toLocaleString()} (${needsPct.toFixed(0)}%)`;
      document.getElementById('bucket-needs-bar').style.width = `${needsPct}%`;
      document.getElementById('bucket-needs-bar').className = needsPct > 100 ? 'bg-rose-500 h-full rounded-full' : 'bg-blue-500 h-full rounded-full';

      const wantsSpent = financials.by_type.want || 0;
      const wantsCap = budget_plan.allocated_wants || (financials.total_income * 0.3);
      const wantsPct = wantsCap > 0 ? Math.min(100, (wantsSpent / wantsCap) * 100) : 0;
      document.getElementById('bucket-wants-label').textContent = `$${wantsSpent.toLocaleString()} / $${wantsCap.toLocaleString()} (${wantsPct.toFixed(0)}%)`;
      document.getElementById('bucket-wants-bar').style.width = `${wantsPct}%`;
      document.getElementById('bucket-wants-bar').className = wantsPct > 100 ? 'bg-rose-500 h-full rounded-full' : 'bg-amber-500 h-full rounded-full';

      const savingsTarget = budget_plan.allocated_savings || (financials.total_income * 0.2);
      const savingsPct = savingsTarget > 0 ? Math.min(100, (financials.net_savings / savingsTarget) * 100) : 0;
      document.getElementById('bucket-savings-label').textContent = `$${financials.net_savings.toLocaleString()} / $${savingsTarget.toLocaleString()} (${savingsPct.toFixed(0)}%)`;
      document.getElementById('bucket-savings-bar').style.width = `${savingsPct}%`;

      const chipsEl = document.getElementById('category-chips');
      chipsEl.innerHTML = '';
      for (const [cat, amt] of Object.entries(financials.by_category)) {
        const div = document.createElement('div');
        div.className = 'p-2 rounded-xl bg-slate-900/90 border border-slate-800 flex justify-between items-center';
        div.innerHTML = `<span class="text-slate-300 truncate">${cat}</span><span class="font-bold text-white">$${amt.toLocaleString()}</span>`;
        chipsEl.appendChild(div);
      }

      const tbody = document.getElementById('transactions-tbody');
      tbody.innerHTML = '';
      recent_expenses.slice(-6).reverse().forEach(t => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40';
        tr.innerHTML = `
          <td class="py-2.5 text-slate-400">${t.date}</td>
          <td class="py-2.5 font-medium text-slate-200">${t.description}</td>
          <td class="py-2.5"><span class="px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-slate-300">${t.category_name}</span></td>
          <td class="py-2.5 text-right font-semibold text-rose-400">-$${t.amount.toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });

      const alertsEl = document.getElementById('alerts-container');
      alertsEl.innerHTML = '';
      if (!alerts || alerts.length === 0) {
        alertsEl.innerHTML = '<p class="text-xs text-slate-400 italic">No budget overspending detected. Keep up the disciplined spending!</p>';
      } else {
        alerts.forEach(a => {
          const div = document.createElement('div');
          const borderCol = a.severity === 'critical' ? 'border-rose-500/50 bg-rose-950/20' : 'border-amber-500/40 bg-amber-950/20';
          div.className = `p-3 rounded-xl border ${borderCol} text-xs`;
          div.innerHTML = `<p class="font-semibold text-white">${a.title}</p><p class="text-slate-300 mt-0.5 leading-relaxed">${a.message}</p>`;
          alertsEl.appendChild(div);
        });
      }

      const recsEl = document.getElementById('recommendations-container');
      recsEl.innerHTML = '';
      recommendations.forEach(r => {
        const div = document.createElement('div');
        div.className = 'p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs';
        div.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-teal-300">${r.action}</span>
            <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-400">${r.priority}</span>
          </div>
          <p class="text-slate-300 mt-1 leading-relaxed">${r.description}</p>
          <p class="text-[11px] text-emerald-400 font-medium mt-1">Impact: ${r.impact}</p>
        `;
        recsEl.appendChild(div);
      });

      const goalsEl = document.getElementById('goals-container');
      goalsEl.innerHTML = '';
      goals.forEach(g => {
        const div = document.createElement('div');
        div.className = 'p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1';
        div.innerHTML = `
          <div class="flex justify-between font-medium">
            <span class="text-slate-200">${g.title}</span>
            <span class="text-slate-400">$${g.current_amount.toLocaleString()} / $${g.target_amount.toLocaleString()}</span>
          </div>
          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div class="bg-gradient-to-r from-teal-500 to-emerald-400 h-full rounded-full" style="width: ${g.progress_pct}%"></div>
          </div>
          <p class="text-[10px] text-slate-400 text-right">${g.progress_pct}% achieved • Target: ${g.target_date}</p>
        `;
        goalsEl.appendChild(div);
      });
    }

    async function switchScenario(key) {
      currentScenario = key;
      document.querySelectorAll('.scenario-btn').forEach(b => {
        b.className = 'scenario-btn px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition';
      });
      const activeBtn = document.getElementById(`btn-${key}`);
      if (activeBtn) activeBtn.className = 'scenario-btn px-3 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-semibold transition';

      try {
        await fetch('/api/scenarios/switch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ persona: key })
        });
        await loadDashboard();
      } catch (err) {
        console.error('Failed to switch scenario:', err);
      }
    }

    async function generateAIBudget() {
      try {
        await fetch('/api/budget/generate', { method: 'POST' });
        await loadDashboard();
      } catch (err) {
        console.error('Error generating AI budget:', err);
      }
    }

    async function openReportModal() {
      try {
        const res = await fetch('/api/report');
        const r = await res.json();
        document.getElementById('modal-report-title').textContent = r.report_title;
        document.getElementById('modal-report-body').innerHTML = `
          <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            <div><p class="text-slate-400 text-[10px]">Income</p><p class="text-sm font-bold text-emerald-400">$${r.financials.total_income.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Expenses</p><p class="text-sm font-bold text-rose-400">$${r.financials.total_expense.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Net Savings</p><p class="text-sm font-bold text-white">$${r.financials.net_savings.toLocaleString()}</p></div>
            <div><p class="text-slate-400 text-[10px]">Health Grade</p><p class="text-sm font-bold text-teal-400">${r.health_grade} (${r.health_score}/100)</p></div>
          </div>
          <div class="mt-3">
            <h5 class="font-bold text-slate-200 mb-1">Executive AI Strategy Assessment</h5>
            <p class="leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">${r.active_budget_plan.ai_strategy_summary}</p>
          </div>
          <div class="mt-3">
            <h5 class="font-bold text-slate-200 mb-1">Top Saving Directives</h5>
            <ul class="list-disc list-inside space-y-1 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
              ${r.actionable_recommendations.map(a => `<li><strong class="text-teal-300">${a.action}:</strong> ${a.description} <em class="text-emerald-400">(${a.impact})</em></li>`).join('')}
            </ul>
          </div>
        `;
        document.getElementById('report-modal').classList.remove('hidden');
      } catch (err) {
        console.error('Failed to open statement:', err);
      }
    }

    function closeReportModal() {
      document.getElementById('report-modal').classList.add('hidden');
    }

    function toggleTransactionModal(type) {
      document.getElementById('tx-type').value = type;
      document.getElementById('tx-modal-title').textContent = type === 'income' ? 'Log Income Stream' : 'Log Daily/Weekly Expense';
      document.getElementById('tx-cat-wrapper').style.display = type === 'income' ? 'none' : 'block';
      document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
      document.getElementById('tx-modal').classList.remove('hidden');
    }

    function closeTxModal() {
      document.getElementById('tx-modal').classList.add('hidden');
    }

    async function submitTransaction(e) {
      e.preventDefault();
      const type = document.getElementById('tx-type').value;
      const desc = document.getElementById('tx-desc').value;
      const cat = document.getElementById('tx-cat').value || 'General';
      const amount = parseFloat(document.getElementById('tx-amount').value);
      const date = document.getElementById('tx-date').value;

      const endpoint = type === 'income' ? '/api/income' : '/api/expense';
      const payload = type === 'income' ? { source_name: desc, amount, date } : { description: desc, category_name: cat, amount, date };

      try {
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        closeTxModal();
        await loadDashboard();
      } catch (err) {
        console.error('Error logging transaction:', err);
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      document.getElementById('tx-date').value = new Date().toISOString().split('T')[0];
      loadDashboard();
    });
  </script>
</body>
</html>
"""


# ==================== APPLICATION RUNNER ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed default salaried scenario if empty
        if not User.query.first():
            seed_scenario_user('salaried')
    print("=" * 70)
    print("  Personal Finance Advisor Bot is running!")
    print("  Local Dashboard:  http://127.0.0.1:5000")
    print("  Default Scenario: Salaried Professional (Switchable via UI)")
    print("=" * 70)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
