import streamlit as st
import numpy as np
import pandas as pd
import dashboard_page
import budget_page
import expense_page

st.set_page_config(page_title="Budget Tracker", page_icon="$$$", layout="wide")

st.sidebar.title("Budget Buddy")
page = st.sidebar.radio("Select a page:", ["Dashboard", "Budget", "Expenses"])

if page == "Dashboard":
    dashboard_page.show_dashboard_page()
elif page == "Budget":
    budget_page.show_budget_page()
elif page == "Expenses":
    expense_page.show_expense_page()


