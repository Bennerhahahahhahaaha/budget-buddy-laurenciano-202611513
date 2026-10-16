import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
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

def getrows(month_budget, month_expense):
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
    
    colors = ["#81C784", "#A5D6A7", "#C8E6C9", "#F2C14E", "#E08E45", "#4DB6AC", "#9CCC65", "#BCAAA4"]
    plt.figure(figsize=(5,4), facecolor="#E8F5E9")
    plt.pie(values, labels=labels, colors=colors, autopct="%1.1f%%")

    st.pyplot(plt.gcf())
    plt.close()

def draw_bar_chart(rows):
    st.subheader("Planned vs actual")

    if len(rows) == 0:
        st.info("No categories to compare.")
        return

    labels = []
    planned = []
    spent = []
    for row in rows:
        labels.append(row["category"])
        planned.append(row["planned"])
        spent.append(row["spent"])
    
    colors = ["#A5D6A7", "#1B5E20"]

    x = np.arange(len(labels))
    width = 0.4

    plt.figure(figsize=(5, 4), facecolor="#E8F5E9")
    ax = plt.gca()
    ax.set_facecolor("#E8F5E9")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.bar(x - width / 2, planned, width, label="Planned", color=colors[0])
    plt.bar(x + width / 2, spent, width, label="Actual", color=colors[1])

    plt.xticks(x, labels, rotation=45, ha="right")
    plt.ylabel("Pesos")
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close()



def breakdown_table(rows):
    st.subheader("Budget Breakdown")
    if len(rows) == 0:
        st.info("No categories yet. Setup your budget first here!") #hyperlink there later
        return
    
    display_rows = []

    for row in rows:
        display_rows.append({
            "Category": row["category"],
            "Planned": budget_page.format_pesos(row["planned"]),
            "Spent": budget_page.format_pesos(row["spent"]),
            "Remaining": budget_page.format_pesos(row["remaining"]),
            "Status": "Over budget" if row["remaining"] < 0 else "On track",
        })
    st.dataframe(
        display_rows,
        hide_index=True,
        width="stretch",
        column_config={
            "Category": st.column_config.TextColumn("Category"),
            "Planned": st.column_config.TextColumn("Planned"),
            "Spent": st.column_config.TextColumn("Spent"),
            "Remaining": st.column_config.TextColumn("Remaining"),
            "Status": st.column_config.TextColumn("Status"),
        }
    )

def draw_dashboard_summary(income, planned, spent, remaining):
    col_income, col_planned, col_spent, col_remaining = st.columns(4)
    col_income.metric("Income", budget_page.format_pesos(income))
    col_planned.metric("Planned expenses", budget_page.format_pesos(planned))
    col_spent.metric("Actual expenses", budget_page.format_pesos(spent))
    col_remaining.metric("Money remaining", budget_page.format_pesos(remaining))

    if remaining < 0:
        st.error(f"You have spent {budget_page.format_pesos(-remaining)} more than your income, see here") #Add hyperlink later

def show_dashboard_page():
    budget = data_loader.load_budget_data()
    expenses = data_loader.load_expense_data()

    st.title("Dashboard")
    month = budget_page.draw_month_picker()

    month_budget = get_month_budget(budget, month)
    month_expenses = expense_page.get_month_expenses(expenses, month)

    if len(month_budget) == 0:
        st.info(f"No budget saved for {month} yet. Set it up first here!.") #Set up hyperlink here soon

    income = get_month_income(month_budget)
    planned = budget_page.calculate_total_planned(month_budget)
    spent = expense_page.calculate_total_spent(month_expenses)
    remaining = calculate_remaining(income, spent)
    rows = getrows(month_budget, month_expenses)

    st.subheader(f"What's up on {month}")
    draw_dashboard_summary(income, planned, spent, remaining)

    col_pie, col_bar = st.columns(2)
    with col_pie:
        draw_pie_chart(rows)
    with col_bar:
        draw_bar_chart(rows)
    breakdown_table(rows)