import streamlit as st
import data_loader
import budget_page
from datetime import date

def label_month_from_date(chosen_date):
    month_name = budget_page.MONTHS[chosen_date.month - 1]
    return budget_page.label_month(month_name, chosen_date.year)

def get_month_categories(budget, month):
    categories = []
    for entry in budget:
        if entry["month"] == month:
            categories.append(entry["category"])
    if categories:
        return categories
    return st.session_state["default_categories"]

def get_planned_amount(budget, month, category):
    for entry in budget:
        if entry["month"] == month and entry["category"] == category:
            return entry["planned_amount"]
    return None

def calculate_category_spent(expenses, month, category):
    total = 0.0
    for expense in expenses:
        if expense["month"] == month and expense["category"] == category:
            total += expense["amount"]
    return round(total, 2)

def validate_expense(category, description, amount):
    if category is None:
        return "Pick a category."
    if description.strip() == "":
        return "Description is required."
    if amount is None or amount <= 0:
        return "Amount must be greater than 0."
    return None

def build_confirmation_message(budget, expenses, month, category, amount):
    message = f"Saved {budget_page.format_pesos(amount)} under {category}."
    planned = get_planned_amount(budget, month, category)
    if planned is None:
        return message + f" There is no planned amount for {category} in {month}."
    left = round(planned - calculate_category_spent(expenses, month, category) - amount, 2)
    if left >= 0:
        return message + f" {category} has {budget_page.format_pesos(left)} left in {month}."
    return message + f" You are over budget on {category} by {budget_page.format_pesos(-left)}."

def build_expense_entry(chosen_date, month, category, description, amount):
    return {
        "date": chosen_date.isoformat(),
        "month": month,
        "category": category,
        "description": description.strip(),
        "amount": round(amount, 2)
    }

def submit_expense(budget, expenses, chosen_date, month, category, description, amount):
    entry = build_expense_entry(chosen_date, month, category, description, amount)
    data_loader.add_expense(entry)
    st.session_state["expense_message"] = build_confirmation_message(budget, expenses, month, category, amount)
    st.session_state["expense_form_version"] = st.session_state.get("expense_form_version", 0) + 1
    st.rerun()

def draw_saved_message():
    message = st.session_state.pop("expense_message", None)
    if message:
        st.success(message)

def draw_expense_inputs(budget):
    version = st.session_state.get("expense_form_version", 0)

    col_date, col_category = st.columns(2)
    chosen_date = col_date.date_input("Date", value=date.today(), key="expense_date")
    month = label_month_from_date(chosen_date)
    category = col_category.selectbox("Category", get_month_categories(budget, month), index=None, placeholder="Pick a category", key=f"expense_category_{version}")
    description = st.text_input("Description", key=f"expense_description_{version}")
    amount = st.number_input("Amount", min_value=0.0, value=None, step=50.0, placeholder="e.g. 150.00", key=f"expense_amount_{version}")
    return chosen_date, month, category, description, amount

def show_expense_page():
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()
    st.title("Expenses")

    st.subheader("Add expense")
    draw_saved_message()
    chosen_date, month, category, description, amount = draw_expense_inputs(budget)
    st.caption(f"This will be recorded under {month}.")

    error = validate_expense(category, description, amount)
    if error:
        st.caption(f":gray[{error}]")
    if st.button("Save expense", type="primary", disabled=error is not None):
        submit_expense(budget, expenses, chosen_date, month, category, description, amount)