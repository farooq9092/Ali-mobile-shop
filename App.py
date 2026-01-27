import streamlit as st
import pandas as pd
import plotly.express as px
from github import Github
import io
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Ali Mobile Shop - Pro Manager", page_icon="📱", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    h1 { color: #00cc66; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- GitHub Auth ---
try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["REPO_NAME"]
    g = Github(token)
    repo = g.get_repo(repo_name)
except Exception:
    st.error("Secrets Missing! Check GITHUB_TOKEN and REPO_NAME.")
    st.stop()

CSV_FILE = "sales_record.csv"

def load_data():
    try:
        contents = repo.get_contents(CSV_FILE)
        data = contents.decoded_content.decode('utf-8')
        df = pd.read_csv(io.StringIO(data))
        df['Date'] = pd.to_datetime(df['Date'])
        return df, contents.sha
    except:
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

# --- Header ---
st.markdown("<h1>📱 Ali Mobile Shop - Management System</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Navigation ---
st.sidebar.title("Ali Mobile Pro")
menu = st.sidebar.radio("Main Menu", ["Nayi Entry (New Sale)", "Dashboard (Reports)", "History & Records"])

# --- 1. NEW ENTRY ---
if menu == "Nayi Entry (New Sale)":
    st.header("📝 Nayi Entry Karein")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Tareekh", datetime.now())
            cat = st.selectbox("Category", ["Accessories", "Repairing"])
            item = st.text_input("Item Name / Kaam")
        with col2:
            cost = st.number_input("Khareed (Cost)", min_value=0.0)
            sale = st.number_input("Becha (Sale)", min_value=0.0)
            pay = st.selectbox("Payment", ["Cash", "EasyPaisa", "JazzCash"])
        
        if st.form_submit_button("💾 Save to Cloud"):
            if item and sale > 0:
                profit = sale - cost
                new_row = pd.DataFrame([[date.strftime('%Y-%m-%d'), cat, item, cost, sale, profit, pay]], columns=df.columns)
                # Convert back to string for consistency
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                updated_df = pd.concat([df, new_row], ignore_index=True)
                save_data(updated_df, current_sha)
                st.success(f"✅ Record Sync Ho Gaya! Munafa: {profit}")
                st.rerun()

# --- 2. DASHBOARD (Detailed Reports) ---
elif menu == "Dashboard (Reports)":
    st.header("📊 Business Analytics")
    
    if not df.empty:
        # Filtering Options
        st.subheader("Filters")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            view_type = st.radio("View Type", ["Overall (Sab Saath)", "Accessories Only", "Repairing Only"], horizontal=True)
        with col_f2:
            time_frame = st.radio("Time Frame", ["Daily", "Monthly"], horizontal=True)

        # Apply Filters
        df_filtered = df.copy()
        if "Accessories" in view_type:
            df_filtered = df[df['Category'] == "Accessories"]
        elif "Repairing" in view_type:
            df_filtered = df[df['Category'] == "Repairing"]

        # Metrics
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Total Sale ({view_type})", f"Rs. {df_filtered['Sale'].sum():,.0f}")
        m2.metric(f"Total Profit ({view_type})", f"Rs. {df_filtered['Profit'].sum():,.0f}")
        m3.metric("Total Bills", len(df_filtered))

        # Charts
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📈 Sale Graph")
            if time_frame == "Daily":
                daily_data = df_filtered.groupby('Date')['Sale'].sum().reset_index()
                fig = px.bar(daily_data, x='Date', y='Sale', title="Rozana ki Sale", color='Sale')
            else:
                df_filtered['Month'] = pd.to_datetime(df_filtered['Date']).dt.to_period('M').astype(str)
                monthly_data = df_filtered.groupby('Month')['Sale'].sum().reset_index()
                fig = px.bar(monthly_data, x='Month', y='Sale', title="Mahana Sale")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("💰 Profit vs Cost")
            fig_pie = px.pie(df_filtered, values='Sale', names='Category', hole=0.4, title="Revenue Source")
            if view_type == "Overall (Sab Saath)":
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(f"Aap abhi sirf {view_type} dekh rahe hain.")
    else:
        st.info("Abhi data khali hai. Entry karein!")

# --- 3. HISTORY ---
elif menu == "History & Records":
    st.header("📋 Database Record")
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Backup (CSV)", csv, "ali_mobile_record.csv", "text/csv")
