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

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
    plt.close(fig)


def draw_bar_chart(rows):
    st.subheader("Planned vs actual")
    if len(rows) == 0:
        st.info("No categories to compare.")
        return

    labels = []
    planned_values = []
    spent_values = []
    for row in rows:
        labels.append(row["category"])
        planned_values.append(row["planned"])
        spent_values.append(row["spent"])

    positions = list(range(len(labels)))
    width = 0.4
    planned_x = []
    spent_x = []
    for p in positions:
        planned_x.append(p - width / 2)
        spent_x.append(p + width / 2)

    fig, ax = plt.subplots()
    ax.bar(planned_x, planned_values, width, label="Planned")
    ax.bar(spent_x, spent_values, width, label="Actual")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Pesos")
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

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