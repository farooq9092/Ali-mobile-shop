import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop Manager", page_icon="📱", layout="wide")

st.title("📱 Ali Mobile Shop - Management System")

# --- Google Sheet Connection ---
# Apni sheet ka URL yahan lazmi dalein
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Sheet read karne ki koshish
        data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        # Agar sheet khali ho ya columns na hon to khud banaye
        if data is None or data.empty:
            return pd.DataFrame(columns=['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment Method'])
        return data
    except Exception:
        # Agar error aaye to empty record show kare
        return pd.DataFrame(columns=['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment Method'])

# Load current record
df = load_data()

# --- Sidebar Menu ---
menu = st.sidebar.radio("Main Menu", ["Nayi Entry (Sale/Repair)", "Dashboard (Munafa/Graphs)", "Pura Record (View/Delete)"])

# --- 1. NEW ENTRY ---
if menu == "Nayi Entry (Sale/Repair)":
    st.header("📝 Nayi Entry Shamil Karein")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Tareekh", datetime.now()).strftime('%Y-%m-%d')
            cat = st.selectbox("Category", ["Accessories", "Repairing"])
            item = st.text_input("Item ya Kaam ka Naam")
            pay = st.selectbox("Payment Method", ["Cash", "EasyPaisa", "JazzCash"])
        with col2:
            cost = st.number_input("Khareed Rate (Cost)", min_value=0)
            sale = st.number_input("Becha (Sale Price)", min_value=0)
        
        if st.form_submit_button("💾 Record Save Karein"):
            if item and sale > 0:
                profit = sale - cost
                new_row = pd.DataFrame([[date, cat, item, cost, sale, profit, pay]], 
                                       columns=['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment Method'])
                
                # Combine and Update
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"✅ Save Ho Gaya! Munafa: {profit} PKR")
                st.rerun()
            else:
                st.warning("Item name aur Sale Price likhna zaroori hai!")

# --- 2. DASHBOARD ---
elif menu == "Dashboard (Munafa/Graphs)":
    st.header("📊 Karobaar ki Report")
    if not df.empty:
        # Data types sahi karna
        df['Sale Price'] = pd.to_numeric(df['Sale Price'], errors='coerce').fillna(0)
        df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Kul Sale (Revenue)", f"Rs. {df['Sale Price'].sum():,.0f}")
        m2.metric("Kul Munafa (Total Profit)", f"Rs. {df['Profit'].sum():,.0f}")
        m3.metric("Total Entries", len(df))

        # Visualizations
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Daily Sales Trend")
            fig_bar = px.bar(df.groupby('Date')['Sale Price'].sum().reset_index(), x='Date', y='Sale Price', color='Sale Price')
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.subheader("Category Wise Sale")
            fig_pie = px.pie(df, values='Sale Price', names='Category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Abhi koi data mojood nahi hai.")

# --- 3. VIEW/DELETE ---
elif menu == "Pura Record (View/Delete)":
    st.header("📋 Sab Records")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Delete ka option
        st.markdown("---")
        st.subheader("Ghalat Entry Delete Karein")
        row_to_delete = st.number_input("Row Number select karein (Pehli row 0 hai)", min_value=0, max_value=len(df)-1, step=1)
        if st.button("❌ Row Delete Karein"):
            updated_df = df.drop(df.index[row_to_delete])
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.error(f"Row {row_to_delete} delete kar di gayi hai.")
            st.rerun()
    else:
        st.info("Record khali hai.")
