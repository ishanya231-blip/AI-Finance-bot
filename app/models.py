"""
SQLAlchemy Database Models for Personal Finance Advisor Bot
Supports Users, Profiles (Scenario personas), Categories, Income, Expenses,
Budget Plans, Financial Goals, and Monthly Reports.
"""

from datetime import datetime, date

try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
except ImportError:
    # Graceful fallback to pure SQLAlchemy if flask_sqlalchemy is not installed
    from sqlalchemy.orm import declarative_base, relationship
    from sqlalchemy import Column, Integer, Float, String, Text, Date, DateTime, ForeignKey, Boolean
    db = type('DB', (), {
        'Model': declarative_base(),
        'Column': Column, 'Integer': Integer, 'Float': Float, 'String': String,
        'Text': Text, 'Date': Date, 'DateTime': DateTime, 'ForeignKey': ForeignKey,
        'Boolean': Boolean, 'relationship': relationship
    })()

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
