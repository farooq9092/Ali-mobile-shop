import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import requests

# --- Page Config ---
st.set_page_config(page_title="Ali Mobile Shop", page_icon="📱", layout="wide")

st.title("📱 Ali Mobile Shop Manager")

# --- Google Sheet URL (Public CSV Link) ---
# Is link ke aakhir mein /export?format=csv lazmi hona chahiye
SHEET_ID = "1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss"
CSV_URL = f"https://docs.google.com/spreadsheets/d/1UjU0Zri8NKdxXjePGK-mTTMRFUluVs93aanUblqS3ss/edit?usp=drivesdk"

def load_data():
    try:
        # Direct CSV link se data read karna
        df = pd.read_csv(CSV_URL)
        return df
    except:
        # Agar sheet khali ho
        return pd.DataFrame(columns=['Date', 'Category', 'Item Name', 'Cost Price', 'Sale Price', 'Profit', 'Payment'])

df = load_data()

# --- Sidebar Menu ---
menu = st.sidebar.radio("Menu", ["Nayi Entry", "Dashboard", "Record Dekhein"])

if menu == "Nayi Entry":
    st.header("📝 Nayi Sale/Repairing")
    # Note: Link se direct "Update" karna mushkil hai, isliye hum yahan download link dein ge
    st.info("Note: Google Policy ki wajah se Direct Save band hai. Aap entries niche dekh kar Excel mein update kar sakte hain.")
    
    with st.form("my_form"):
        date = st.date_input("Date", datetime.now())
        cat = st.selectbox("Category", ["Accessories", "Repairing"])
        item = st.text_input("Item Name")
        cost = st.number_input("Cost Price", min_value=0)
        sale = st.number_input("Sale Price", min_value=0)
        
        if st.form_submit_button("Calculated Profit Dekhein"):
            profit = sale - cost
            st.success(f"Profit: {profit} PKR. Isay apni Google Sheet mein manually add kar lein.")

elif menu == "Dashboard":
    st.header("📊 Business Report")
    if not df.empty:
        total_sale = df['Sale Price'].sum()
        st.metric("Total Sale", f"Rs. {total_sale}")
        fig = px.bar(df, x='Date', y='Sale Price', color='Category')
        st.plotly_chart(fig)

elif menu == "Record Dekhein":
    st.header("📋 Google Sheet Data")
    st.dataframe(df)
