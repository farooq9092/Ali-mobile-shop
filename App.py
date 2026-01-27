import streamlit as st
import pandas as pd
import plotly.express as px
from github import Github
import io
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop Pro", page_icon="📱", layout="wide")

# --- CSS for Professional Look ---
st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GitHub Auth ---
try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["REPO_NAME"]
    g = Github(token)
    repo = g.get_repo(repo_name)
except Exception:
    st.error("GitHub Secrets missing! Check GITHUB_TOKEN and REPO_NAME.")
    st.stop()

CSV_FILE = "sales_record.csv"

def load_data():
    try:
        contents = repo.get_contents(CSV_FILE)
        data = contents.decoded_content.decode('utf-8')
        df = pd.read_csv(io.StringIO(data))
        return df, contents.sha
    except:
        # Agar file nahi hai to naye columns banayein
        cols = ['Date', 'Category', 'Item', 'Cost', 'Sale', 'Profit', 'Payment']
        return pd.DataFrame(columns=cols), None

def save_data(df, sha):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(CSV_FILE, "Update Record", csv_buffer.getvalue(), sha)
    else:
        repo.create_file(CSV_FILE, "Initial Record", csv_buffer.getvalue())

# Load Data
df, current_sha = load_data()

# --- Sidebar ---
st.sidebar.title("Ali Mobile Pro")
menu = st.sidebar.radio("Navigation", ["Daily Entry", "Business Report", "History"])

# --- 1. DAILY ENTRY ---
if menu == "Daily Entry":
    st.header("📝 Nayi Sale/Repairing Shamil Karein")
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Date", datetime.now()).strftime('%Y-%m-%d')
            cat = st.selectbox("Category", ["Accessories", "Repairing", "LCD/Panel", "Software"])
            item = st.text_input("Item Name")
        with c2:
            cost = st.number_input("Cost Price", min_value=0.0)
            sale = st.number_input("Sale Price", min_value=0.0)
            pay = st.selectbox("Payment", ["Cash", "EasyPaisa", "JazzCash", "Bank"])
        
        if st.form_submit_button("Submit & Cloud Sync"):
            if item and sale > 0:
                profit = sale - cost
                new_row = pd.DataFrame([[date, cat, item, cost, sale, profit, pay]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df, current_sha)
                st.success(f"✅ Record Cloud par save ho gaya! Profit: {profit}")
                st.balloons()
                st.rerun()

# --- 2. REPORT ---
elif menu == "Business Report":
    st.header("📊 Business Analytics")
    if not df.empty:
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Revenue", f"Rs. {df['Sale'].sum():,.0f}")
        m2.metric("Net Profit", f"Rs. {df['Profit'].sum():,.0f}")
        m3.metric("Margin %", f"{(df['Profit'].sum()/df['Sale'].sum()*100):.1f}%")
        
        # Charts
        st.subheader("Sales Trend")
        fig = px.area(df.groupby('Date')['Sale'].sum().reset_index(), x='Date', y='Sale', title="Daily Revenue Growth")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Record khali hai.")

# --- 3. HISTORY ---
elif menu == "History":
    st.header("📋 All Transactions")
    st.dataframe(df, use_container_width=True)
    if st.button("Download CSV Backup"):
        st.download_button("Click here", df.to_csv(index=False), "backup.csv", "text/csv")
