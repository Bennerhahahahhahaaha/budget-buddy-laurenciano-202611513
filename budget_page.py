import streamlit as st
import data_loader
from datetime import date

MONTHS = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]

def format_pesos(amount):
    return f"₱{amount:,.2f}"

def label_month(month_name, year):
    return f"{month_name} {year}"

def get_starting_rows(month_entries):
    rows = []
    if month_entries:
        for entry in month_entries:
            rows.append({"category": entry["category"], "planned_amount": entry["planned_amount"]})
    else:
        for name in st.session_state["default_categories"]:
            rows.append({"category": name, "planned_amount": 0.0})
    return rows

def budget_rows(month, income_source, income, rows):
    search = []
    for row in rows:
        search.append({
            "month": month,
            "income_source": income_source,
            "income": income,
            "category": row["category"],
            "planned_amount": row["planned_amount"]
        })
    return search

def load_list(month, month_entries):
    if st.session_state.get("working_month") != month:
        st.session_state["working_month"] = month
        st.session_state["working_rows"] = get_starting_rows(month_entries)

@st.dialog("Category")
def category_dialog(index=None):
    rows = st.session_state["working_rows"]

    if index is None:
        name_default = ""
        amount_default = None
    else:
        name_default = rows[index]["category"]
        amount_default = rows[index]["planned_amount"]

    name = st.text_input("Category name", value=name_default)
    amount = st.number_input("Planned amount", min_value=0.0, value=amount_default, step=100.0, placeholder="e.g. 100.00")

    name_error = validate_categoryname(rows, name, index)
    if name_error and name != "":
        st.caption(f":red[{name_error}]")
    error = name_error is not None or amount is None

    col_cancel, col_save = st.columns(2)
    if col_cancel.button("Cancel", width="stretch"):
        st.rerun()
    if col_save.button("Save", type="primary", disabled=error, width="stretch"):
        new_row = {"category": name.strip(), "planned_amount": amount}
        if index is None:
            rows.append(new_row)
        else:
            rows[index] = new_row
        st.rerun()

def draw_category_rows(rows):
    head_name, head_amount, _, _ = st.columns([4, 3, 1, 1])
    head_name.caption("Category")
    head_amount.caption("Planned amount")

    for i in range(len(rows)):
        col_name, col_amount, col_edit, col_remove = st.columns([4, 3, 1, 1])
        col_name.write(rows[i]["category"])
        col_amount.write(format_pesos(rows[i]['planned_amount']))
        if col_edit.button("Edit", icon=":material/edit:", key=f"edit_{i}"):
            category_dialog(i)
        if col_remove.button("Delete", icon=":material/delete:", key=f"remove_{i}"): 
            rows.pop(i)
            st.rerun()

def validate_categoryname(rows, name, skip_index=None):
    if name.strip() == "":
        return "Category name is required."
    for i in range(len(rows)):
        if i != skip_index and rows[i]["category"].lower() == name.strip().lower():
            return "That category already exists."
    return None
    
def calculate_total_planned(rows):
    total = 0.0
    for row in rows:
        total += row["planned_amount"]
    return total

@st.dialog("Notice")
def message_dialog(type, message):
    if type == "success":
        st.success(message)
    else:
        st.error(message)
    if st.button("Okay", type="primary"):
        st.rerun()

def show_budget_page():
    budget = data_loader.load_budget_data()
    st.title("Current Budget")

    today = date.today()
    col_month, col_year = st.columns(2)
    month_name = col_month.selectbox("Month", MONTHS, index=today.month - 1)
    year = col_year.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1)

    month = label_month(month_name, year)
    monthly_budget = [entry for entry in budget if entry["month"] == month]

    load_list(month, monthly_budget)
    rows = st.session_state["working_rows"]
 
    if monthly_budget:
        default_source = monthly_budget[0]["income_source"]
        default_income = monthly_budget[0]["income"]
    else:
        default_source = ""
        default_income = 0.0

    col_source, col_income = st.columns(2)
    income_source = col_source.text_input("Income source", value=default_source, key=f"source_{month}")
    income = col_income.number_input("Expected Income", min_value=0.0, value=float(default_income), step=500.0, key=f"income_{month}")

    st.subheader(f"{month}'s Budget")
    if len(rows):
        draw_category_rows(rows)
    else:
        st.info("No categories yet, add some!")
    if st.button("+ Add Category"):
        category_dialog()
    

    total_planned = calculate_total_planned(rows)
    unallocated_income = income - total_planned

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", format_pesos(income))
    col2.metric("Planned Expenses", format_pesos(total_planned))
    col3.metric("Unallocated", format_pesos(unallocated_income))

    if unallocated_income > 0:
        st.success(f"Remaining unallocated income: {format_pesos(unallocated_income)}")
    elif unallocated_income == 0:
        st.info("All income has been allocated")
    else:
        st.error(f"Your planned expenses exceed your income by {format_pesos(-unallocated_income)}")

    if st.button("Save Budget", type="primary"):
        if income_source.strip() == "":
            message_dialog("error", "Please enter an income source.")
        elif len(rows) == 0:
            message_dialog("error", "Add at least one category.")
        else:
            new_rows = budget_rows(month, income_source.strip(), income, rows)
            budget = [e for e in budget if e["month"] != month]
            budget.extend(new_rows)
            data_loader.save_budget_data(budget)
            message_dialog("success", f"Budget for {month} saved!")