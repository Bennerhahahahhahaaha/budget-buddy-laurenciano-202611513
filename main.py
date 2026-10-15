import streamlit as st
import dashboard_page
import budget_page
import expense_page

DEFAULT_CATEGORIES = ["Food", "Transportation", "School Supplies", "Contribution", "Rent", "Bills"]

st.set_page_config(page_title="Budget Tracker", layout="wide")
st.session_state["default_categories"] = DEFAULT_CATEGORIES

dashboard = st.Page(dashboard_page.show_dashboard_page, title="Dashboard", default=True)
budgets = st.Page(budget_page.show_budget_page, title="Budgets")
expenses = st.Page(expense_page.show_expense_page, title="Expenses")

 
page = st.navigation([dashboard, budgets, expenses])
page.run()