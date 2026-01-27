import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop Pro", page_icon="📱", layout="wide")

# --- Database Setup (SQLite) ---
DB_FILE = "ali_mobile_shop_db.sqlite"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  category TEXT,
                  item_name TEXT,
                  cost_price REAL,
                  sale_price REAL,
                  profit REAL,
                  payment_method TEXT)''')
    conn.commit()
    conn.close()

def add_data(date, category, item, cost, sale, profit, payment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO sales (date, category, item_name, cost_price, sale_price, profit, payment_method) VALUES (?,?,?,?,?,?,?)",
              (date, category, item, cost, sale, profit, payment))
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

def delete_record(record_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sales WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# --- Professional UI ---
st.markdown("<h1 style='text-align: center;'>📱 Professional Shop Manager v2.0</h1>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Dashboard Navigation", ["Sales Entry", "Business Analytics", "Database Manager"])

df = get_all_data()

# --- 1. SALES ENTRY ---
if menu == "Sales Entry":
    st.subheader("📝 New Transaction")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now()).strftime('%Y-%m-%d')
            cat = st.selectbox("Category", ["Accessories", "Repairing", "LCD/Panel", "Software"])
            item = st.text_input("Item Description")
        with col2:
            cost = st.number_input("Cost Price", min_value=0.0)
            sale = st.number_input("Sale Price", min_value=0.0)
            pay = st.selectbox("Payment", ["Cash", "EasyPaisa", "JazzCash", "Bank"])
        
        if st.form_submit_button("Submit Transaction"):
            if item and sale > 0:
                profit = sale - cost
                add_data(date, cat, item, cost, sale, profit, pay)
                st.success(f"Entry Saved! Profit: {profit}")
                st.rerun()

# --- 2. BUSINESS ANALYTICS ---
elif menu == "Business Analytics":
    st.subheader("📊 Performance Overview")
    if not df.empty:
        total_sale = df['sale_price'].sum()
        total_profit = df['profit'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Revenue", f"Rs. {total_sale:,.0f}")
        m2.metric("Net Profit", f"Rs. {total_profit:,.0f}")
        m3.metric("Total Bills", len(df))
        
        c1, c2 = st.columns(2)
        with c1:
            fig_daily = px.area(df.groupby('date')['sale_price'].sum().reset_index(), 
                                x='date', y='sale_price', title="Daily Revenue Trend")
            st.plotly_chart(fig_daily, use_container_width=True)
        with c2:
            fig_pie = px.pie(df, values='profit', names='category', title="Profit Distribution", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available yet.")

# --- 3. DATABASE MANAGER ---
elif menu == "Database Manager":
    st.subheader("📋 Administrative Controls")
    st.dataframe(df, use_container_width=True)
    
    if not df.empty:
        record_to_del = st.selectbox("Select ID to Delete", df['id'].tolist())
        if st.button("Delete Record Permanently"):
            delete_record(record_to_del)
            st.warning(f"Record {record_to_del} Deleted.")
            st.rerun()
        
        # CSV Export for backup
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Database Backup (CSV)", csv, "ali_mobile_backup.csv", "text/csv")
