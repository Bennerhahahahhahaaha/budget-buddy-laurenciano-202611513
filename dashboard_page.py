import streamlit as st
import matplotlib.pyplot as plt
import data_loader
import budget_page
import expense_page


def get_month_budget(budget, month):
    budget_entries = []
    for entry in budget:
        if entry["month"] == month:
            budget_entries.append(entry)
    return budget_entries

def get_month_income(month_budget):
    if month_budget:
        return month_budget[0]["income"]
    else:
        return 0.0

def calculate_remaining(income, total_spent):
    return round(income - total_spent, 2) + 0.0

def breakdown(month_budget, month_expense):
    rows = []
    for entry in month_budget:
        planned = entry["planned_amount"]
        spent = expense_page.calculate_category_spent(month_expense, entry["month"], entry["category"])
        remaining = round(planned - spent, 2) + 0.0
        rows.append({
            "category": entry["category"],
            "planned": planned,
            "spent": spent,
            "remaining": remaining, 
        })
    return rows

def draw_pie_chart(rows):
    st.subheader("Planned budget")
    labels = []
    values = []
    for row in rows:
        if row["planned"] > 0:
            labels.append(row["category"])
            values.append(row["planned"])

    if len(values) == 0:
        st.info("Nothing planned yet, so there is no chart to show.")
        return

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
    plt.close(fig)

def draw_dashboard_summary(income, planned, spent, remaining):
    col_income, col_planned, col_spent, col_remaining = st.columns(4)
    col_income.metric("Income", budget_page.format_pesos(income))
    col_planned.metric("Planned expenses", budget_page.format_pesos(planned))
    col_spent.metric("Actual expenses", budget_page.format_pesos(spent))
    col_remaining.metric("Money remaining", budget_page.format_pesos(remaining))

    if remaining < 0:
        st.error(f"You have spent {budget_page.format_pesos(-remaining)} more than your income.")

def show_dashboard_page():
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()

    st.title("Dashboard")
    month = budget_page.draw_month_picker()

    month_budget = get_month_budget(budget, month)
    month_expenses = expense_page.get_month_expenses(expenses, month)

    if len(month_budget) == 0:
        st.info(f"No budget saved for {month} yet. Set it up first!.") #Set up hyperlink here soon

    income = get_month_income(month_budget)
    planned = budget_page.calculate_total_planned(month_budget)
    spent = expense_page.calculate_total_spent(month_expenses)
    remaining = calculate_remaining(income, spent)
    rows = breakdown(month_budget, month_expenses)

    st.subheader(f"What's up on {month}")
    draw_dashboard_summary(income, planned, spent, remaining)

    col_pie, col_bar = st.columns(2)
    with col_pie:
        draw_pie_chart(rows)
    #with col_bar: mamaya 