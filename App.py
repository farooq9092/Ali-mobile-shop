import streamlit as st
import pandas as pd
import plotly.express as px
from github import Github
import io
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Ali Mobiles & Communication", page_icon="📱", layout="wide")

# Custom Styling for Analytics
st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    .target-card { background-color: #1e2130; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #00cc66; }
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

# --- Load Logo ---
def get_logo():
    try:
        file_content = repo.get_contents("1000041294.jpg")
        return file_content.download_url
    except:
        return None

logo_url = get_logo()

# --- Header ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if logo_url:
        st.image(logo_url, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #00cc66;'>Ali Mobiles & Communication</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- Data Logic ---
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

def save_data(df, sha, message="Update"):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(CSV_FILE, message, csv_buffer.getvalue(), sha)
    else:
        repo.create_file(CSV_FILE, "Initial Record", csv_buffer.getvalue())

df, current_sha = load_data()

# --- Navigation ---
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
                st.success("✅ Saved!")
                st.rerun()

# --- 2. DASHBOARD (Detailed Reports) ---
elif menu == "Dashboard (Reports)":
    st.header("📊 Business Reports")
    if not df.empty:
        # --- FILTERS ---
        st.sidebar.markdown("### Report Filters")
        category_filter = st.sidebar.selectbox("Category Dekhein:", ["All (Combined)", "Accessories", "Repairing"])
        time_frame = st.sidebar.radio("Time View:", ["Daily", "Monthly"])

        # Filter Logic
        work_df = df.copy()
        if category_filter != "All (Combined)":
            work_df = work_df[work_df['Category'] == category_filter]

        # Target Tracker (Based on Filtered Data)
        target_profit = 60000
        current_profit = work_df['Profit'].sum()
        progress = min(current_profit / target_profit, 1.0)
        
        st.markdown(f"""
            <div class="target-card">
                <h3 style='margin:0; color:#00cc66;'>🎯 Monthly Profit Target ({category_filter})</h3>
                <h1 style='margin:10px 0;'>Rs. {current_profit:,.0f} / {target_profit:,}</h1>
                <p style='color:#aaa;'>Progress: {progress*100:.1f}% | Remaining: Rs. {max(target_profit-current_profit, 0):,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        st.progress(progress)
        st.markdown("<br>", unsafe_allow_html=True)

        # Main Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Sale", f"Rs. {work_df['Sale'].sum():,.0f}")
        m2.metric("Total Profit", f"Rs. {work_df['Profit'].sum():,.0f}")
        m3.metric("Total Entries", len(work_df))

        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader(f"📈 {time_frame} Sales Trend")
            if time_frame == "Daily":
                plot_df = work_df.groupby('Date')['Sale'].sum().reset_index()
                fig = px.bar(plot_df, x='Date', y='Sale', color='Sale', color_continuous_scale='Greens')
            else:
                work_df['Month'] = work_df['Date'].dt.to_period('M').astype(str)
                plot_df = work_df.groupby('Month')['Sale'].sum().reset_index()
                fig = px.bar(plot_df, x='Month', y='Sale', color='Sale')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("💳 Payment Types")
            fig_pay = px.pie(work_df, values='Sale', names='Payment', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pay, use_container_width=True)
            
        # Comparison Table
        st.subheader("📋 Category Summary (Comparison)")
        comp_df = df.groupby('Category').agg({'Sale':'sum', 'Profit':'sum', 'Item':'count'}).reset_index()
        comp_df.columns = ['Category', 'Total Sale', 'Total Profit', 'Total Items']
        st.table(comp_df)
    else:
        st.info("No records found.")

# --- 3. HISTORY ---
elif menu == "History & Delete":
    st.header("📋 Records Management")
    if not df.empty:
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
        st.markdown("---")
        delete_idx = st.number_input("Delete Index:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("❌ Permanent Delete"):
            updated_df = df.drop(df.index[delete_idx])
            save_data(updated_df, current_sha, "Record Deleted")
            st.warning("Entry removed!")
            st.rerun()
