"""
Flask RESTful API and Web Routes for Personal Finance Advisor Bot
"""

from flask import Blueprint, render_template, request, jsonify
from app.models import db, User, UserProfile, Income, Expense, Category, BudgetPlan, BudgetCategoryAllocation, FinancialGoal, MonthlyReport
from app.ai_engine import AIFinancialEngine
from app.seed_data import SCENARIO_DATA
from datetime import datetime, date

api_bp = Blueprint('api', __name__)
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

@api_bp.route('/')
def index():
    return render_template('index.html')

@api_bp.route('/api/scenarios', methods=['GET'])
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

@api_bp.route('/api/scenarios/switch', methods=['POST'])
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

@api_bp.route('/api/dashboard', methods=['GET'])
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

@api_bp.route('/api/income', methods=['POST'])
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

@api_bp.route('/api/expense', methods=['POST'])
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

@api_bp.route('/api/budget/generate', methods=['POST'])
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

@api_bp.route('/api/report', methods=['GET'])
def get_monthly_report():
    user = get_current_user()
    profile = user.profile.to_dict() if user.profile else {}
    incomes = [i.to_dict() for i in user.incomes]
    expenses = [e.to_dict() for e in user.expenses]
    goals = [g.to_dict() for g in user.goals]
    month_str = request.args.get('month', date.today().strftime('%Y-%m'))

    report_dict = ai_engine.generate_monthly_report(profile, month_str, incomes, expenses, goals)
    return jsonify(report_dict)
