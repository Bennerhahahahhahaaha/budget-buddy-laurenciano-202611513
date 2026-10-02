import streamlit as st
import data_loader

def show_budget_page():
    st.title("Current Budget")
    st.subheader("Monthly Budget Setup")
    budget = data_loader.load_budget_data()

    months = []
    for entry in budget:
        if entry["month"] not in months:
            months.append(entry["month"])
    month = st.selectbox("Select a month:", months)

    income_source = ""
    income = 0.0

    for entry in budget:
        if entry["month"] == month:
            income_source = entry["income_source"]
            income = entry["income"]
            break
    
    st.text_input("Income Source:", value=income_source)
    st.number_input("Income:", value=income, min_value=0.0)


