import streamlit as st
import data_loader

def show_budget_page():
    st.title("Current Budget")
    budget = data_loader.load_budget_data()
    st.dataframe(budget, use_container_width=True)