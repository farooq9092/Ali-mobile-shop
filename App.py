import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop", page_icon="📱", layout="wide")

st.title("📱 Ali Mobile Shop - Professional Manager")

# --- Google Sheets Connection ---
# Yahan apni Google Sheet ka URL dalein
SHEET_URL = "APNI_GOOGLE_SHEET_KA_URL_YAHAN_PASTE_KAREIN"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3,4,5,6], ttl=0)

# --- Sidebar Menu ---
menu = st.sidebar.selectbox("Menu", ["Nayi Entry", "Reports", "Data Dekhein"])

df = load_data()

if menu == "Nayi Entry":
    st.header("📝 New Sale/Repair Entry")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now()).strftime('%Y-%m-%d')
            category = st.selectbox("Category", ["Accessories", "Repairing"])
            item = st.text_input("Item/Work Name")
            pay = st.selectbox("Payment", ["Cash", "EasyPaisa", "JazzCash"])
        with col2:
            cost = st.number_input("Cost Price", min_value=0)
            sale = st.number_input("Sale Price", min_value=0)
        
        if st.form_submit_button("Save Record"):
            profit = sale - cost
            new_row = pd.DataFrame([[date, category, item, cost, sale, profit, pay]])
            # Update Google Sheet
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success("✅ Data Google Sheet mein save ho gaya!")
            st.rerun()

elif menu == "Reports":
    st.header("📊 Sales Dashboard")
    if not df.empty:
        df['Sale Price'] = pd.to_numeric(df['Sale Price'])
        df['Profit'] = pd.to_numeric(df['Profit'])
        
        m1, m2 = st.columns(2)
        m1.metric("Total Sale", f"Rs. {df['Sale Price'].sum()}")
        m2.metric("Total Profit", f"Rs. {df['Profit'].sum()}")
        
        # Graph
        fig = px.bar(df, x='Date', y='Sale Price', color='Category', title="Daily Sales Growth")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Data Dekhein":
    st.header("📋 All Records")
    st.dataframe(df)
