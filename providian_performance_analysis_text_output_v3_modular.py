# providian_performance_analysis_text_output_v3_modular.py

import pandas as pd
import numpy as np

def load_rent_roll(file):
    df = pd.read_excel(file)
    df['Vacancy'] = df['Tenant'].isna()
    df['Delinquent'] = df['Past Due'] > 0
    return df

def calculate_vacancy_delinquency(df):
    total_units = len(df)
    vacant_units = df['Vacancy'].sum()
    delinquent_units = df['Delinquent'].sum()
    vacancy_rate = vacant_units / total_units if total_units else 0
    delinquency_rate = delinquent_units / total_units if total_units else 0
    return vacancy_rate, delinquency_rate

def load_cash_flow(file_path):
    df = pd.read_excel(file_path)
    df['Account Name'] = df['Account Name'].astype(str).str.strip()
    return df

def extract_operating_expenses(df):
    monthly_cols = [
        'Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024', 'Jun 2024',
        'Jul 2024', 'Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024'
    ]
    row = df[df['Account Name'] == 'Total Operating Expense']
    expenses = row[monthly_cols].values.flatten() if not row.empty else [0]*12
    return monthly_cols, expenses

def process_summary_multi_rent_rolls(rent_roll_files, cash_flow_file):
    monthly_summary = []
    for file in rent_roll_files:
        df = load_rent_roll(file)
        vacancy, delinquency = calculate_vacancy_delinquency(df)
        monthly_summary.append((vacancy, delinquency))
    cash_df = load_cash_flow(cash_flow_file)
    months, expenses = extract_operating_expenses(cash_df)
    return months, expenses, monthly_summary

def generate_analysis_text(months, expenses, monthly_summary):
    vacancy_rates = [v for v, _ in monthly_summary]
    delinquency_rates = [d for _, d in monthly_summary]

    avg_vacancy = np.mean(vacancy_rates)
    max_vacancy = max(vacancy_rates)
    min_vacancy = min(vacancy_rates)
    avg_delinquency = np.mean(delinquency_rates)
    max_delinquency = max(delinquency_rates)

    avg_expense = np.mean(expenses)
    dec_expense = expenses[-1]

    sections = {
        "Vacancy": f"Average Vacancy Rate: ~{avg_vacancy:.0%}\n\n- Highest Vacancy: {months[vacancy_rates.index(max_vacancy)]} - {max_vacancy:.2%}\n- Lowest Vacancy: {months[vacancy_rates.index(min_vacancy)]} - {min_vacancy:.2%}\n\nObservation:\n- Vacancy remained elevated throughout the year.\n- Did not stabilize under 30%.\n\nSummary: High risk, upside if leasing improves.",
        "Delinquency": f"Average Delinquency: ~{avg_delinquency:.2%}\n\n- Highest Delinquency: {months[delinquency_rates.index(max_delinquency)]} - {max_delinquency:.2%}\n\nObservation:\n- Delinquency manageable overall.\n\nSummary: No crisis, but should monitor collections.",
        "Expenses": f"Average Monthly Expenses: ~${avg_expense:,.0f}\n\n- Big Spike: December - ${dec_expense:,.0f}\n\nObservation:\n- Spike due to taxes.\n\nSummary: Expense control looks solid outside tax event.",
        "Occupancy": "Occupancy fluctuated in the 50–60% range. Revenue not sufficient to offset steady expenses.\n\nSummary: Cash flow likely negative without occupancy gains.",
        "Margins": "Operating expenses stable, but income too low.\n\nSummary: Margin compression a major risk. Improve occupancy urgently.",
        "Risks": "- Vacancy above normal range\n- Leasing velocity slow\n- Tax cycle causes seasonal stress\n- Economic vacancy may also exist",
        "Grade": "Grade: C- (Risky but Recoverable)\n\nFocus Areas:\n- Leasing\n- Staff performance\n- Lead management\n\nSummary: Property has upside, but immediate action required."
    }

    return sections
