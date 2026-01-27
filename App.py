import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Ali Mobile Shop Manager", page_icon="📱", layout="wide")

# --- Connection Setup ---
# Hum Google Sheet use karein ge taake reboot par data delete na ho
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Sheet se data uthana
        data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        return data
    except:
        # Agar sheet khali hai ya link mein masla hai
        return pd.DataFrame(columns=['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment Method'])

# Load current data
df = load_data()

# --- App Header ---
st.title("📱 Ali Mobile Shop - Management System")
st.markdown("---")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Nayi Entry (Add Sale)", "Dashboard (Munafa/Report)", "Mukammal Record"])

# --- 1. NEW ENTRY SECTION ---
if menu == "Nayi Entry (Add Sale)":
    st.header("📝 Nayi Entry Karein")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Tareekh", datetime.now())
            category = st.selectbox("Category", ["Accessories", "Repairing"])
            item_name = st.text_input("Item Name / Kaam")
            payment_method = st.selectbox("Payment Method", ["Cash", "EasyPaisa", "JazzCash"])
            
        with col2:
            cost_price = st.number_input("Khareed Rate (Cost)", min_value=0)
            sale_price = st.number_input("Becha (Sale Price)", min_value=0)
        
        submitted = st.form_submit_button("💾 Data Save Karein")
        
        if submitted:
            if item_name and sale_price > 0:
                profit = sale_price - cost_price
                new_data = pd.DataFrame([{
                    'Date': date.strftime('%Y-%m-%d'), 
                    'Category': category, 
                    'Item Name': item_name, 
                    'Cost Price': cost_price, 
                    'Sale Price': sale_price, 
                    'Profit': profit,
                    'Payment Method': payment_method
                }])
                
                # Naye data ko purane ke saath milana
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
                # Google Sheet mein save karna
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"✅ Record Save Ho Gaya! Profit: {profit} PKR")
                st.rerun()
            else:
                st.error("Ghalti! Item name aur Sale Price likhna zaroori hai.")

# --- 2. DASHBOARD SECTION ---
elif menu == "Dashboard (Munafa/Report)":
    st.header("📊 Business Report")
    
    if not df.empty:
        # Calculations
        total_sale = df['Sale Price'].astype(float).sum()
        total_profit = df['Profit'].astype(float).sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Kul Sale (Total Revenue)", f"Rs. {total_sale:,.0f}")
        col2.metric("Kul Bachat (Total Profit)", f"Rs. {total_profit:,.0f}")
        
        # Graphs
        st.subheader("Sales Graph")
        fig = px.bar(df, x='Date', y='Sale Price', color='Category', title="Daily Sales")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Payment Methods (Cash vs Online)")
        fig_pie = px.pie(df, values='Sale Price', names='Payment Method')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Abhi koi record nahi mila.")

# --- 3. VIEW RECORD ---
elif menu == "Mukammal Record":
    st.header("📋 Sheet Record")
    st.dataframe(df, use_container_width=True)
