import streamlit as st
import data_loader
from datetime import date

MONTHS = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]


def label_month(month_name, year):
    return f"{month_name} {year}"

def calculate_total_planned(rows):
    total = 0.0
    for row in rows:
        total += row["planned_amount"]
    return total

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Current Budget")
    
    today = date.today()
    col_month, col_year = st.columns(2)
    month_name = col_month.selectbox("Month:", MONTHS, index=today.month - 1)
    year = col_year.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1)
    month = label_month(month_name, int(year)) 
    monthly_budget = [entry for entry in budget if entry["month"] == month]
 
    if monthly_budget:
        default_source = monthly_budget[0]["income_source"]
        default_income = monthly_budget[0]["income"]
    else:
        default_source = ""
        default_income = 0.0

    col_source, col_income = st.columns(2)
    income_source = col_source.text_input("Income source", value=default_source, key=f"source_{month}")
    income = col_income.number_input("Expected Income", value=float(default_income), key=f"income_{month}")

    st.subheader(f"{month}'s Budget")
    if monthly_budget:
        st.dataframe(monthly_budget, width="stretch", column_order=["category", "planned_amount"])
    else:
        st.info("No Entries")
    total_planned = calculate_total_planned(monthly_budget)
    unallocated_income = income - total_planned

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", f"{income:,.2f}")
    col2.metric("Planned Expenses", f"{total_planned:,.2f}")
    col3.metric("Unallocated", f"{unallocated_income:,.2f}")
    
    if unallocated_income > 0:
        st.success(f"Remaining unallocated income: ₱{unallocated_income:,.2f}")
    elif unallocated_income == 0:
        st.info("All income has been allocated")
    else:
        st.error(f"Your planned expenses exceed your income by ₱{-unallocated_income:,.2f}")