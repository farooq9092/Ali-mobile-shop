import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Ali Mobile Shop Manager", page_icon="📱", layout="wide")

# --- File Handling (Excel Sheet) ---
FILE_NAME = 'ali_mobile_data.csv'

def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        # Agar file nahi hai to nayi banayein
        columns = ['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment Method']
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# --- App Header ---
st.title("📱 Ali Mobile Shop Management System")
st.markdown("---")

# --- Sidebar (Menu) ---
menu = st.sidebar.selectbox("Menu", ["Nayi Entry Karein (New Sale)", "Dashboard (Reports)", "Pura Record Dekhein"])

# Load current data
df = load_data()

# --- 1. NEW ENTRY SECTION ---
if menu == "Nayi Entry Karein (New Sale)":
    st.header("📝 New Sale / Repair Entry")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date (Tareekh)", datetime.now())
            category = st.selectbox("Category (Qisam)", ["Accessories (Saman)", "Repairing (Marammat)"])
            item_name = st.text_input("Item Name (Cheez ka naam/Kaam)", placeholder="e.g. Glass Protector, LCD Change")
            payment_method = st.selectbox("Payment Method", ["Cash", "EasyPaisa", "JazzCash", "Bank Transfer"])
            
        with col2:
            cost_price = st.number_input("Khareed Rate (Cost Price)", min_value=0, value=0, help="Ye item apko kitne ka mila?")
            sale_price = st.number_input("Farokht Rate (Sale Price)", min_value=0, value=0, help="Apne kitne ka becha?")
        
        submitted = st.form_submit_button("💾 Record Save Karein")
        
        if submitted:
            if item_name and sale_price > 0:
                profit = sale_price - cost_price
                new_data = {
                    'Date': date, 
                    'Category': category, 
                    'Item Name': item_name, 
                    'Cost Price': cost_price, 
                    'Sale Price': sale_price, 
                    'Profit': profit,
                    'Payment Method': payment_method
                }
                # Add to dataframe
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                st.success(f"✅ Entry Saved! Profit: {profit} PKR")
            else:
                st.error("⚠️ Please Item ka naam aur Price zaroor likhein.")

# --- 2. DASHBOARD SECTION ---
elif menu == "Dashboard (Reports)":
    st.header("📊 Business Reports & Analysis")
    
    if not df.empty:
        # Convert Date column to datetime for filtering
        df['Date'] = pd.to_datetime(df['Date'])
        
        # --- Filters ---
        col1, col2 = st.columns(2)
        with col1:
            view_mode = st.radio("View Mode:", ["Daily (Rozana)", "Monthly (Mahana)"], horizontal=True)
        with col2:
            cat_filter = st.selectbox("Category Filter:", ["All", "Accessories (Saman)", "Repairing (Marammat)"])

        # Filter Logic
        df_display = df.copy()
        if cat_filter != "All":
            if "Accessories" in cat_filter:
                df_display = df[df['Category'] == "Accessories (Saman)"]
            else:
                df_display = df[df['Category'] == "Repairing (Marammat)"]

        # --- Metrics (Top Cards) ---
        total_sale = df_display['Sale Price'].sum()
        total_profit = df_display['Profit'].sum()
        total_repair_income = df[df['Category'] == "Repairing (Marammat)"]['Sale Price'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Sale (Revenue)", f"Rs. {total_sale:,}")
        m2.metric("📈 Total Profit (Bachat)", f"Rs. {total_profit:,}", delta_color="normal")
        m3.metric("🔧 Only Repairing Income", f"Rs. {total_repair_income:,}")

        st.markdown("---")

        # --- Charts ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📈 Sale Trend (Graph)")
            # Grouping by Date
            if view_mode == "Daily (Rozana)":
                sales_over_time = df_display.groupby('Date')['Sale Price'].sum().reset_index()
                fig_line = px.bar(sales_over_time, x='Date', y='Sale Price', title="Daily Sales Bar Chart", color='Sale Price')
            else:
                # Monthly grouping
                df_display['Month'] = df_display['Date'].dt.to_period('M').astype(str)
                sales_over_time = df_display.groupby('Month')['Sale Price'].sum().reset_index()
                fig_line = px.bar(sales_over_time, x='Month', y='Sale Price', title="Monthly Sales Trend")
                
            st.plotly_chart(fig_line, use_container_width=True)

        with c2:
            st.subheader("💳 Payment Methods (Cash/Online)")
            payment_counts = df_display.groupby('Payment Method')['Sale Price'].sum().reset_index()
            fig_pie = px.pie(payment_counts, values='Sale Price', names='Payment Method', title="Payment Distribution", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("Abhi tak koi data nahi hai. Pehle 'Nayi Entry' mein jakar data dalein.")

# --- 3. DATA SHEET VIEW ---
elif menu == "Pura Record Dekhein":
    st.header("📋 Pura Excel Record")
    
    st.dataframe(df, use_container_width=True)
    
    # Download Button
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        label="📥 Download Sheet (CSV)",
        data=csv,
        file_name='ali_mobile_full_record.csv',
        mime='text/csv',
    )
