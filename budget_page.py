import streamlit as st
import data_loader

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Budget Overview")
    
    months = []
    for entry in budget:
        if entry["month"] not in months:
            months.append(entry["month"])
    month = st.selectbox("Select Month:", months)

    monthly_budget = [entry for entry in budget if entry["month"] == month]
 
    if monthly_budget:
        income = monthly_budget[0]['income']
    else:
        income = 0
 
    total_planned = 0
    for entry in monthly_budget:
        total_planned += entry['planned_amount']

   
    unallocated_income = income - total_planned
 
    st.write("Income:", income)
    st.write("Planned Budget:", total_planned)
    if unallocated_income > 0:
        st.write("Unallocated Income:", unallocated_income)
        st.success(f"Unallocated Income: {unallocated_income}")
    else:
        st.write("Unallocated Income:", unallocated_income)
        st.error(f"You have overspent your budget by: {-unallocated_income}")
    
    st.write("Budget Entries for", month)
    for entry in monthly_budget:
        st.write(f"{entry['category']}: {entry['planned_amount']}")