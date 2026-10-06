import streamlit as st
import data_loader

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Budget Overview")
    total_budget = 0
    
    months = []
    for entry in budget:
        if entry["month"] not in months:
            months.append(entry["month"])
    income_source = ""
    month = st.selectbox("Select Month:", months)

    monthly_budget = [entry for entry in budget if entry["month"] == month]

    if monthly_budget:
        income = monthly_bodget[0]['income]']
    else:
        income = 0
   

    