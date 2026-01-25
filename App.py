import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop", page_icon="📱", layout="wide")

# --- Google Sheet Setup ---
# Aapki provide ki hui link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl=0 for real-time updates
        data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        if data is None or data.empty:
            return pd.DataFrame(columns=['ID', 'Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])
        return data
    except Exception:
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
                entry_id = datetime.now().strftime('%Y%m%d%H%M%S')
                
                # Nayi entry ka dataframe
                new_entry = pd.DataFrame([[entry_id, date, cat, item, cost, sale, profit, pay]], 
                                       columns=['ID', 'Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])
                
                # Data combine karein
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                
                try:
                    conn.update(spreadsheet=SHEET_URL, data=updated_df)
                    st.success(f"✅ Save ho gaya! Profit: {profit}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Save nahi ho saka. Error: {e}")
                    st.info("Tip: Streamlit Secrets mein Google Credentials lazmi add karein.")
            else:
                st.warning("Item name aur Sale Price likhna zaroori hai.")

# --- 2. REPORTS ---
elif menu == "Reports & Graphs":
    st.header("📊 Karobaar ki Report")
    if not df.empty:
        # Convert columns to numeric for calculation
        df['Sale Price'] = pd.to_numeric(df['Sale Price'], errors='coerce').fillna(0)
        df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
        
        m1, m2 = st.columns(2)
        m1.metric("Kul Sale (Total)", f"Rs. {df['Sale Price'].sum():,.0f}")
        m2.metric("Kul Bachat (Profit)", f"Rs. {df['Profit'].sum():,.0f}")
        
        # Charts
        st.subheader("Sales Trend")
        fig_line = px.bar(df.groupby('Date')['Sale Price'].sum().reset_index(), x='Date', y='Sale Price', color='Sale Price')
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.subheader("Payment Distribution")
        fig_pie = px.pie(df, values='Sale Price', names='Payment')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Abhi koi record mojood nahi hai.")

# --- 3. DELETE RECORD ---
elif menu == "Record Manager (Delete)":
    st.header("🗑️ Record Delete Karein")
    if not df.empty:
        st.write("Niche table se ghalat entry dhoondein:")
        st.dataframe(df, use_container_width=True)
        
        delete_id = st.selectbox("Delete karne ke liye ID select karein:", df['ID'].tolist())
        
        if st.button("❌ Confirm Delete"):
            updated_df = df[df['ID'].astype(str) != str(delete_id)]
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.warning("Entry delete kar di gayi hai.")
            st.rerun()
    else:
        st.info("Delete karne ke liye koi data nahi hai.")
