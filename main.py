import streamlit as st
from dashboard_page import show_dashboard_page
from budget_page import show_budget_page
from expense_page import show_expense_page

DEFAULT_CATEGORIES = ["Food", "Transportation", "School Supplies", "Contribution", "Rent", "Bills"]

st.set_page_config(page_title="Budget Buddy!", layout="wide", page_icon="green_apple.png")
st.logo("green_apple.png")
st.session_state["default_categories"] = DEFAULT_CATEGORIES

def shared_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

        h1, h2, h3, p, label, li,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            font-family: 'Nunito', sans-serif;
        }

        .block-container {
            max-width: 1400px;
            padding: 2rem 2.5rem;
        }

        h1, h2, h3 {
            color: #1B5E20;
            font-weight: 700;
        }

        [data-testid="stMetricLabel"] {
            color: #4C6B50;
        }

        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #A5D6A7;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 6px rgba(27, 94, 32, 0.08);
        }

        [data-testid="stMetricValue"] {
            color: #1B5E20;
            font-weight: 700;
        }

        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] a span {
            font-size: 1.15rem;
        }

        [data-testid="stSidebarNav"] li {
            margin-bottom: 0.25rem;
        }
        .st-key-remaining_card [data-testid="stMetricValue"] {
            color: #C62828;
        }
        [data-testid="stSidebarHeader"] img,
        [data-testid="stLogo"] {
            height: 3.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
shared_design()

dashboard = st.Page(show_dashboard_page, title="Home", icon=":material/home:", default=True)
budgets = st.Page(show_budget_page, title="Budgets", icon=":material/account_balance_wallet:")
expenses = st.Page(show_expense_page, title="Expenses", icon=":material/receipt_long:")

st.session_state["page_budgets"] = budgets
st.session_state["page_expenses"] = expenses

page = st.navigation([dashboard, budgets, expenses])
page.run()