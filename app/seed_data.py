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
