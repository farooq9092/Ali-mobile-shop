import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop", page_icon="📱", layout="wide")

# --- Google Sheet Setup ---
# Apni sheet ka URL yahan lazmi dalein
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss/edit?usp=drivesdk"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        # Agar sheet bilkul khali ho to headers ke sath return karein
        if data is None or data.empty:
            return pd.DataFrame(columns=['ID', 'Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])
        return data
    except:
        return pd.DataFrame(columns=['ID', 'Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])

df = load_data()

# --- Sidebar ---
st.sidebar.title("Ali Mobile Shop")
menu = st.sidebar.radio("Main Menu", ["Nayi Entry", "Reports & Graphs", "Record Manager (Delete)"])

# --- 1. NEW ENTRY ---
if menu == "Nayi Entry":
    st.header("📝 Nayi Sale ya Repairing")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Tareekh", datetime.now()).strftime('%Y-%m-%d')
            cat = st.selectbox("Category", ["Accessories", "Repairing"])
            item = st.text_input("Item ya Kaam ka Naam")
        with col2:
            cost = st.number_input("Khareed (Cost)", min_value=0)
            sale = st.number_input("Becha (Sale)", min_value=0)
            pay = st.selectbox("Payment Mode", ["Cash", "EasyPaisa", "JazzCash"])
        
        if st.form_submit_button("Record Save Karein"):
            if item and sale > 0:
                profit = sale - cost
                # Unique ID for deletion
                entry_id = datetime.now().strftime('%Y%m%d%H%M%S')
                new_row = pd.DataFrame([[entry_id, date, cat, item, cost, sale, profit, pay]], 
                                       columns=['ID', 'Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])
                
                updated_df = pd.concat([df, new_data], ignore_index=True) if not df.empty else new_row
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"✅ Save ho gaya! Munafa: {profit}")
                st.rerun()

# --- 2. REPORTS ---
elif menu == "Reports & Graphs":
    st.header("📊 Karobaar ki Report")
    if not df.empty:
        # Metrics
        t_sale = df['Sale Price'].astype(float).sum()
        t_profit = df['Profit'].astype(float).sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Kul Sale (Total)", f"Rs. {t_sale:,.0f}")
        c2.metric("Kul Bachat (Profit)", f"Rs. {t_profit:,.0f}")
        
        # Graph
        st.subheader("Sales Graph")
        fig = px.line(df.groupby('Date')['Sale Price'].sum().reset_index(), 
                     x='Date', y='Sale Price', title="Daily Sale Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Payment Method Breakdown")
        fig2 = px.pie(df, values='Sale Price', names='Payment', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Abhi koi record nahi mila.")

# --- 3. DELETE RECORD ---
elif menu == "Record Manager (Delete)":
    st.header("🗑️ Record Delete Karein")
    if not df.empty:
        st.write("Niche diye gaye table se woh entry dhoondein jise delete karna hai:")
        
        # Displaying with a temporary index for selection
        event = st.dataframe(df, use_container_width=True)
        
        delete_id = st.selectbox("Delete karne ke liye ID select karein:", df['ID'].tolist())
        
        if st.button("❌ Confirm Delete"):
            # Filter out the selected ID
            updated_df = df[df['ID'] != delete_id]
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.warning(f"Entry {delete_id} delete kar di gayi hai.")
            st.rerun()
    else:
        st.info("Delete karne ke liye koi data nahi hai.")
