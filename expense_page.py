import streamlit as st
import data_loader

def show_expense_page():
    st.title("What's my Expenses?")
    expenses = data_loader.load_expense_data()
    st.dataframe(expenses, use_container_width=True)