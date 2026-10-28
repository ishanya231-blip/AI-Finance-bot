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
