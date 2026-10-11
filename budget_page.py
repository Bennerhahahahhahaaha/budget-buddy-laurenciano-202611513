import streamlit as st
import data_loader
from datetime import date

MONTHS = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
CATEGORIES = ["Food", "Transportation", "School Supplies", "Contribution", "Rent", "Bills"]


def label_month(month_name, year):
    return f"{month_name} {year}"

def get_years(budget):
    #get years with saved value for the year selectbox
    years = []
    for entry in budget:
        year = int(entry["month"].split()[-1])
        if year not in years:
            years.append(year)
    years.sort()
    return years
def parse_year(choice, default):
    if choice is None:
        return default
    try: year = int(choice)
    except ValueError:
        return None
    if 2000 <= year <= 2100:
        return year
    return None

def get_starting_rows(month_entries):
    if len(month_entries) == 0:
        return [{"category": c, "planned_amount": 0.0} for c in CATEGORIES]
    rows = []
    for entry in month_entries:
        rows.append({"category": entry["category"], "planned_amount": entry["planned_amount"]})
    return rows

def load_list(month, month_entries):
    if st.session_state.get("working_month") != month:
        st.session_state["working_month"] = month
        st.session_state["working_rows"] = get_starting_rows(month_entries)

def calculate_total_planned(rows):
    total = 0.0
    for row in rows:
        total += row["planned_amount"]
    return total

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Current Budget")
    
    today = date.today()
    saved_years = get_years(budget)
    col_month, col_year = st.columns(2)
    month_name = col_month.selectbox("Month", MONTHS, index=today.month - 1)
    year_choice = col_year.selectbox("Year", [str(y) for y in saved_years], index=None, placeholder=str(today.year), accept_new_options=True, key="year_pick")

    year = parse_year(year_choice, today.year)
    if year is None:
        st.error("Enter a year between 2000 and 2100.")
        return
    
    month = label_month(month_name, int(year)) 
    monthly_budget = [entry for entry in budget if entry["month"] == month]

    load_list(month, monthly_budget)
    rows = st.session_state["working_rows"]
 
    if monthly_budget:
        default_source = monthly_budget[0]["income_source"]
        default_income = monthly_budget[0]["income"]
    else:
        default_source = ""
        default_income = 0.0

    col_source, col_income = st.columns(2)
    income_source = col_source.text_input("Income source", value=default_source, key=f"source_{month}")
    income = col_income.number_input("Expected Income", min_value=0.0, value=float(default_income), step=500.0, key=f"income_{month}")

    st.subheader(f"{month}'s Budget")
    if len(rows):
        st.dataframe(rows, width="stretch", hide_index=True, column_order=["category", "planned_amount"])
    total_planned = calculate_total_planned(rows)
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