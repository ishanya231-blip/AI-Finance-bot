"""
Unit Test Suite for AI Financial Advisory Engine
Tests all 4 user scenarios, budget generation, overspending alerts, and reports.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from app.ai_engine import AIFinancialEngine
from app.seed_data import SCENARIO_DATA

class TestAIFinancialEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AIFinancialEngine()

    def test_scenario_1_salaried_professional(self):
        data = SCENARIO_DATA['salaried']
        profile = data['profile']
        incomes = data['incomes']
        expenses = data['expenses']

        aggregated = self.engine.aggregate_financials(incomes, expenses)
        self.assertEqual(aggregated['total_income'], 5500.0)
        self.assertEqual(aggregated['total_expense'], 3495.0)
        self.assertAlmostEqual(aggregated['net_savings'], 2005.0)
        self.assertAlmostEqual(aggregated['savings_rate'], 36.5, places=1)

        budget = self.engine.generate_personalized_budget(profile, incomes, expenses)
        self.assertEqual(budget['allocated_needs'], 2750.0) # 50%
        self.assertEqual(budget['allocated_wants'], 1650.0) # 30%
        self.assertEqual(budget['allocated_savings'], 1100.0) # 20%
        self.assertIn("50/30/20 Wealth Builder", budget['ai_strategy_summary'])

        alerts = self.engine.detect_overspending(profile, aggregated, budget)
        recs = self.engine.generate_saving_recommendations(profile, aggregated, alerts)

        alert_categories = [a['category'] for a in alerts]
        self.assertIn('Entertainment & Dining', alert_categories)

        rec_actions = [r['action'] for r in recs]
        self.assertIn('Automate Payday Sweep', rec_actions)

        score = self.engine.calculate_financial_health_score(aggregated, profile)
        self.assertGreaterEqual(score, 75)

    def test_scenario_2_college_student(self):
        data = SCENARIO_DATA['student']
        profile = data['profile']
        incomes = data['incomes']
        expenses = data['expenses']

        aggregated = self.engine.aggregate_financials(incomes, expenses)
        self.assertEqual(aggregated['total_income'], 1170.0)
        self.assertEqual(aggregated['total_expense'], 1065.0)
        self.assertEqual(aggregated['net_savings'], 105.0)

        budget = self.engine.generate_personalized_budget(profile, incomes, expenses)
        self.assertEqual(budget['target_ratios']['needs_pct'], 65.0)
        self.assertIn("Student Envelope Allocation", budget['ai_strategy_summary'])

        alerts = self.engine.detect_overspending(profile, aggregated, budget)
        recs = self.engine.generate_saving_recommendations(profile, aggregated, alerts)

        rec_actions = [r['action'] for r in recs]
        self.assertTrue(any('Campus' in act for act in rec_actions))

    def test_scenario_3_freelancer_variable_income(self):
        data = SCENARIO_DATA['freelancer']
        profile = data['profile']
        incomes = data['incomes']
        expenses = data['expenses']

        aggregated = self.engine.aggregate_financials(incomes, expenses)
        self.assertEqual(aggregated['total_income'], 5650.0)
        self.assertEqual(aggregated['total_expense'], 3670.0)

        budget = self.engine.generate_personalized_budget(profile, incomes, expenses)
        self.assertIn("Variable Income Buffer Strategy", budget['ai_strategy_summary'])
        self.assertGreaterEqual(budget['allocated_savings'], 1400.0)

        alerts = self.engine.detect_overspending(profile, aggregated, budget)
        recs = self.engine.generate_saving_recommendations(profile, aggregated, alerts)

        rec_actions = [r['action'] for r in recs]
        self.assertIn('Dedicated Tax & Income Smoothing Vault', rec_actions)
        self.assertIn('Accelerate 6-Month Emergency Runway', rec_actions)

    def test_scenario_4_household_manager(self):
        data = SCENARIO_DATA['household']
        profile = data['profile']
        incomes = data['incomes']
        expenses = data['expenses']

        aggregated = self.engine.aggregate_financials(incomes, expenses)
        self.assertEqual(aggregated['total_income'], 9300.0)
        self.assertEqual(aggregated['total_expense'], 7810.0)
        self.assertEqual(aggregated['net_savings'], 1490.0)

        budget = self.engine.generate_personalized_budget(profile, incomes, expenses)
        self.assertEqual(budget['target_ratios']['needs_pct'], 60.0)
        self.assertIn("Consolidated Household Protocol", budget['ai_strategy_summary'])

        alerts = self.engine.detect_overspending(profile, aggregated, budget)
        recs = self.engine.generate_saving_recommendations(profile, aggregated, alerts)

        rec_actions = [r['action'] for r in recs]
        self.assertTrue(any('Utility' in act or 'Grocery' in act for act in rec_actions))

    def test_monthly_report_generation(self):
        data = SCENARIO_DATA['salaried']
        report = self.engine.generate_monthly_report(
            profile=data['profile'],
            month_year='2026-10',
            incomes=data['incomes'],
            expenses=data['expenses'],
            goals=data['goals']
        )

        self.assertIn('report_title', report)
        self.assertIn('health_score', report)
        self.assertIn('health_grade', report)
        self.assertIn('financials', report)
        self.assertIn('active_budget_plan', report)
        self.assertIn('actionable_recommendations', report)
        self.assertEqual(len(report['goals_summary']), 2)

    def test_homepage_renders_without_runtime_error(self):
        client = flask_app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Personal Finance Advisor Bot', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
