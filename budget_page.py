import streamlit as st
import data_loader

def calculate_total_planned(rows):
    total = 0.0
    for row in rows:
        total += row["planned_amount"]
    return total

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Current Budget")
    
    months = []
    for entry in budget:
        if entry["month"] not in months:
            months.append(entry["month"])
    month = st.selectbox("Select Month:", months)
    monthly_budget = [entry for entry in budget if entry["month"] == month]
 
    if monthly_budget:
        income = monthly_budget[0]['income']
    else:
        income = 0.0

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
        st.success(f"Unallocated Income: {unallocated_income}")
    elif unallocated_income == 0:
        st.info("All budgets are spent!")
    else:
        st.error(f"You have overspent your budget by: {-unallocated_income}")
""" 
    if st.button("Save Budget"):
        budget = [entry for entry in budget if entry["month"] != month]
        budget.extend(edited_budget)

        data_loader.save_budget_data(budget)
        st.success("Budget Saved!") """