import streamlit as st
import data_loader
import budget_page
from datetime import date

def month_of(chosen_date):
    selected_month = budget_page.MONTHS[chosen_date.month - 1]
    return budget_page.label_month(selected_month, chosen_date.year)

def get_month_categories(month):
    budget = data_loader.load_budget_data()
    categories = []
    for entry in budget:
        if entry["month"] == month:
            categories.append(entry["category"])
    if categories:
        return categories
    return st.session_state["default_categories"]

def draw_expense_inputs():
    col_date, col_category = st.columns(2)
    chosen_date = col_date.date_input("Date", value=date.today())
    month = month_of(chosen_date)
    category = col_category.selectbox("Category", get_month_categories(month), index=None, placeholder="Pick a category")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, value=None, step=50.0, placeholder="e.g. 150.00")
    return chosen_date, month, category, description, amount
    
def show_expense_page():
    st.title("Expenses")
    st.subheader("Add Expense")

    chosen_date, month, category, description, amount = draw_expense_inputs()

