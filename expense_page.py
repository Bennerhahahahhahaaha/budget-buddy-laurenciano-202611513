import streamlit as st
import data_loader
from datetime import date


MONTHS = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]

def format_pesos(amount):
    return f"₱{amount:,.2f}"

def label_month(month_name, year):
    return f"{month_name} {year}"

def label_month_from_date(chosen_date):
    month_name = MONTHS[chosen_date.month - 1]
    return label_month(month_name, chosen_date.year)

#format_pesos, label_month copy pasted from budget_page instead of importing

def get_expense_date(expense):
    return expense["date"]

#budget get_starting_rows butreturns names
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

#same loop at total_planned
def calculate_category_spent(expenses, month, category):
    total = 0.0
    for expense in expenses:
        if expense["month"] == month and expense["category"] == category:
            total += expense["amount"]
    return round(total, 2)

#same input validation for budget page
def validate_expense(category, description, amount):
    if category is None:
        return "Pick a category."
    if description.strip() == "":
        return "Description is required."
    if amount is None or amount <= 0:
        return "Amount must be greater than 0."
    return None

#notice message same logic as budget page
def build_confirmation_message(budget, expenses, month, category, amount):
    message = f"Saved {format_pesos(amount)} under {category}."
    planned = get_planned_amount(budget, month, category)
    if planned is None:
        return message + f" There is no planned amount for {category} in {month}."
    left = round(planned - calculate_category_spent(expenses, month, category) - amount, 2)
    if left >= 0:
        return message + f" {category} has {format_pesos(left)} left in {month}."
    return message + f" You are over budget on {category} by {format_pesos(-left)}."

#only 1 entry per date same logic
def build_expense_entry(chosen_date, month, category, description, amount):
    return {
        "date": chosen_date.isoformat(),
        "month": month,
        "category": category,
        "description": description.strip(),
        "amount": round(amount, 2)
    }

#submit_budget 
def submit_expense(budget, expenses, chosen_date, month, category, description, amount):
    entry = build_expense_entry(chosen_date, month, category, description, amount)
    data_loader.add_expense(entry)
    st.session_state["expense_form_version"] = st.session_state.get("expense_form_version", 0) + 1
    notice_dialog("success", build_confirmation_message(budget, expenses, month, category, amount))

def draw_expense_inputs(budget):
    version = st.session_state.get("expense_form_version", 0)

    col_date, col_category = st.columns(2)
    chosen_date = col_date.date_input("Date", value=date.today(), key="expense_date")
    month = label_month_from_date(chosen_date)
    category = col_category.selectbox("Category", get_month_categories(budget, month), index=None, placeholder="Pick a category", key=f"expense_category_{version}")
    description = st.text_input("Description", key=f"expense_description_{version}")
    amount = st.number_input("Amount", min_value=0.0, value=None, step=50.0, placeholder="e.g. 150.00", key=f"expense_amount_{version}")
    return chosen_date, month, category, description, amount

def get_month_expenses(expenses, month):
    month_expenses = []
    for expense in expenses:
        if expense["month"] == month:
            month_expenses.append(expense)
    return sorted(month_expenses, key=get_expense_date, reverse=True)
    
def calculate_total_spent(month_expenses):
    total = 0.0
    for expense in month_expenses:
        total += expense["amount"]
    return round(total, 2)

def build_history_rows(month_expenses):
    rows = []
    for expense in month_expenses:
        rows.append({
            "Date": expense["date"],
            "Category": expense["category"],
            "Description": expense["description"],
            "Amount": format_pesos(expense["amount"])
        })
    return rows

def draw_history(month, month_expenses):
    st.subheader(f"Expenses for {month}:")
    if len(month_expenses):
        st.metric("Total spent", format_pesos(calculate_total_spent(month_expenses)))
        st.dataframe(build_history_rows(month_expenses), hide_index=True, width="stretch")
    else:
        st.info("No expenses recorded for this month yet.")

def draw_history_month_picker():
    today = date.today()
    col_month, col_year = st.columns(2)
    month_name = col_month.selectbox("Month", MONTHS, index=today.month - 1, key="history_month_name")
    year = col_year.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1, key="history_year")
    return label_month(month_name, year)

@st.dialog("Notice")
def notice_dialog(kind, message):
    if kind == "success":
        st.success(message)
    else:
        st.error(message)
    if st.button("Okay", type="primary"):
        st.rerun()

def show_expense_page():
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()
    st.title("Expenses")

    st.subheader("Add expense")
    chosen_date, month, category, description, amount = draw_expense_inputs(budget)
    st.caption(f"This will be recorded under {month}.")

    error = validate_expense(category, description, amount)
    if error:
        st.caption(f":gray[{error}]")
    if st.button("Save expense", type="primary", disabled=error is not None):
        submit_expense(budget, expenses, chosen_date, month, category, description, amount)
    st.divider()
    st.subheader("Expense History")
    expense_history = draw_history_month_picker()
    month_expenses = get_month_expenses(expenses, expense_history)
    draw_history(expense_history, month_expenses)