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

#budget get_starting_rows but returns names
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

#same widget drawing from draw_income_inputs for the dialog
def draw_expense_inputs(budget):
    version = st.session_state.get("expense_form_version", 0)

    col_date, col_category = st.columns(2)
    chosen_date = col_date.date_input("Date", value=date.today(), key="expense_date")
    month = label_month_from_date(chosen_date)
    category = col_category.selectbox("Category", get_month_categories(budget, month), index=None, placeholder="Pick a category", key=f"expense_category_{version}")
    description = st.text_input("Description", key=f"expense_description_{version}")
    amount = st.number_input("Amount", min_value=0.0, value=None, step=50.0, placeholder="e.g. 150.00", key=f"expense_amount_{version}")
    return chosen_date, month, category, description, amount

#keeps expenses from the selected month
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

#build_budget_entries but for displaying entries and not saving to the CSV
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

#dataframe for display instead of drawing the table with individual edit/delete button.
#Returns the selected expense (only possible in edit mode) or None
def draw_history(month, month_expenses):
    st.subheader(f"Expenses for {month}:")
    selected = None
    if len(month_expenses):
        st.metric("Total spent", format_pesos(calculate_total_spent(month_expenses)))
        edit_mode = st.toggle("Edit mode", key="history_edit_mode")
        rows = build_history_rows(month_expenses)
        if edit_mode:
            version = st.session_state.get("history_version", 0)
            event = st.dataframe(rows, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key=f"history_table_{month}_{version}")
            if event.selection.rows:
                selected = month_expenses[event.selection.rows[0]]
        else:
            st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info("No expenses recorded for this month yet.")
    return selected

#shows which expense is selected 
def draw_selected_expense(selected):
    st.caption(f"Selected: {selected['date']}, {selected['category']}, {selected['description']}, {format_pesos(selected['amount'])}")
    
def draw_history_month_picker():
    today = date.today()
    col_month, col_year = st.columns(2)
    month_name = col_month.selectbox("Month", MONTHS, index=today.month - 1, key="history_month_name")
    year = col_year.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1, key="history_year")
    return label_month(month_name, year)

def find_expense_index(expenses, selected):
    for i in range(len(expenses)):
        if expenses[i] is selected:
            return i
    return None

def delete_expense(index):
    expenses = data_loader.load_expense_data()
    expenses.pop(index)
    data_loader.save_expense_data(expenses)
    st.session_state["history_version"] = st.session_state.get("history_version", 0) + 1

#same dialog from budget page
@st.dialog("Notice")
def notice_dialog(kind, message):
    if kind == "success":
        st.success(message)
    else:
        st.error(message)
    if st.button("Okay", type="primary"):
        st.rerun()

@st.dialog("Edit expense")
def edit_expense_dialog(index):
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()
    old = expenses[index]

    chosen_date = st.date_input("Date", value=date.fromisoformat(old["date"]))
    month = label_month_from_date(chosen_date)

    options = get_month_categories(budget, month)
    if month == old["month"] and old["category"] not in options:
        options = options + [old["category"]]
    if old["category"] in options:
        start = options.index(old["category"])
    else:
        start = None

    category = st.selectbox("Category", options, index=start, placeholder="Pick a category")
    description = st.text_input("Description", value=old["description"])
    amount = st.number_input("Amount", min_value=0.0, value=old["amount"], step=50.0)

    error = validate_expense(category, description, amount)
    if error:
        st.caption(f":red[{error}]")

    col_cancel, col_save = st.columns(2)
    if col_cancel.button("Cancel", width="stretch"):
        st.rerun()
    if col_save.button("Save changes", type="primary", disabled=error is not None, width="stretch"):
        expenses[index] = build_expense_entry(chosen_date, month, category, description, amount)
        data_loader.save_expense_data(expenses)
        st.session_state["history_version"] = st.session_state.get("history_version", 0) + 1
        st.rerun()

@st.dialog("Delete expense")
def confirm_delete_dialog(index):
    st.warning("Delete this expense? This can't be undone.")

    col_cancel, col_delete = st.columns(2)
    if col_cancel.button("Cancel", width="stretch"):
        st.rerun()
    if col_delete.button("Delete", type="primary", width="stretch"):
        delete_expense(index)
        st.rerun()

def show_expense_page():
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()

    #column ratio for the expense history and the add expense, best one is 2.5:1
    col_history, col_addexpense = st.columns([2.5, 1], gap="large")
    with col_history:
        st.subheader("Expense History")

        expense_history = draw_history_month_picker()
        month_expenses = get_month_expenses(expenses, expense_history)
        selected = draw_history(expense_history, month_expenses)

        if selected is not None:
            draw_selected_expense(selected)
            col_edit, col_delete, _ = st.columns([1, 1, 4])
            if col_edit.button("Edit", icon=":material/edit:", key="edit_expense"):
                edit_expense_dialog(find_expense_index(expenses, selected))
            if col_delete.button("Delete", icon=":material/delete:", key="delete_expense"):
                confirm_delete_dialog(find_expense_index(expenses, selected))
    with col_addexpense:
        st.subheader("Add Expense")
        
        chosen_date, month, category, description, amount = draw_expense_inputs(budget)
        st.caption(f"This will be recorded under {month}.")
        error = validate_expense(category, description, amount)
        if error:
            st.caption(f":gray[{error}]")
        if st.button("Save expense", type="primary", disabled=error is not None):
            submit_expense(budget, expenses, chosen_date, month, category, description, amount)



