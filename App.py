import streamlit as st
import pandas as pd
import plotly.express as px
from github import Github
import io
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Ali Mobiles & Communication", page_icon="📱", layout="wide")

# --- GitHub Auth ---
try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["REPO_NAME"]
    g = Github(token)
    repo = g.get_repo(repo_name)
except Exception:
    st.error("Secrets Missing! Check GITHUB_TOKEN and REPO_NAME.")
    st.stop()

# --- Load Logo from GitHub ---
def get_logo():
    try:
        file_content = repo.get_contents("1000041294.jpg") # Ya jo bhi aapne GitHub pe naam rakha ho
        return file_content.download_url
    except:
        return None

logo_url = get_logo()

# --- Header with Logo ---
st.markdown("<br>", unsafe_allow_html=True)
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if logo_url:
        st.image(logo_url, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #00cc66;'>Ali Mobiles & Communication</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- Load Data Logic ---
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

def save_data(df, sha, message="Update Record"):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(CSV_FILE, message, csv_buffer.getvalue(), sha)
    else:
        repo.create_file(CSV_FILE, "Initial Record", csv_buffer.getvalue())

df, current_sha = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("Shop Manager")
menu = st.sidebar.radio("Main Menu", ["Nayi Entry", "Dashboard (Reports)", "History & Delete"])

# --- 1. NEW ENTRY ---
if menu == "Nayi Entry":
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
                if not df.empty:
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                new_row = pd.DataFrame([[date.strftime('%Y-%m-%d'), cat, item, cost, sale, profit, pay]], columns=df.columns)
                updated_df = pd.concat([df, new_row], ignore_index=True)
                save_data(updated_df, current_sha, f"Added: {item}")
                st.success(f"✅ Record Sync Ho Gaya!")
                st.rerun()

# --- 2. DASHBOARD ---
elif menu == "Dashboard (Reports)":
    st.header("📊 Business Analytics")
    if not df.empty:
        # Target Tracker
        target_profit = 60000
        current_profit = df['Profit'].sum()
        progress = min(current_profit / target_profit, 1.0)
        
        st.markdown(f"""
            <div style="background-color: #1e2130; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #00cc66;">
                <h3 style='margin:0; color:#00cc66;'>🎯 Monthly Profit Target: Rs. {target_profit:,}</h3>
                <h1 style='margin:10px 0;'>Rs. {current_profit:,.0f}</h1>
                <p style='color:#aaa;'>Progress: {progress*100:.1f}% | Remaining: Rs. {max(target_profit-current_profit, 0):,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        st.progress(progress)
        st.markdown("<br>", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Sale", f"Rs. {df['Sale'].sum():,.0f}")
        m2.metric("Total Profit", f"Rs. {df['Profit'].sum():,.0f}")
        m3.metric("Total Entries", len(df))

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💳 Payment Methods")
            fig_pay = px.pie(df, values='Sale', names='Payment', hole=0.4, 
                             color='Payment', color_discrete_map={'Cash':'#00cc66', 'EasyPaisa':'#00bfff', 'JazzCash':'#ffcc00'})
            st.plotly_chart(fig_pay, use_container_width=True)
        with c2:
            st.subheader("📈 Profit by Category")
            fig_cat = px.bar(df.groupby('Category')['Profit'].sum().reset_index(), x='Category', y='Profit', color='Category')
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No data available.")

# --- 3. HISTORY & DELETE ---
elif menu == "History & Delete":
    st.header("📋 Records Management")
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        st.markdown("---")
        delete_idx = st.number_input("Delete Index:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("❌ Confirm Delete"):
            updated_df = df.drop(df.index[delete_idx])
            save_data(updated_df, current_sha, f"Deleted index {delete_idx}")
            st.warning("Entry delete ho gayi!")
            st.rerun()
