import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# DEBUG: Confirm which credentials are being loaded
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("🔍 DEBUG - URL loaded:", SUPABASE_URL)
print("🔍 DEBUG - KEY loaded (first 20 chars):", SUPABASE_KEY[:20] if SUPABASE_KEY else "NOT FOUND")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ .env file not found or variables missing! Make sure .env is in the SAME folder as this script.")

print("🚀 Mock Data Generate Ho Raha Hai...")
np.random.seed(42)
n_records = 10500

# Generating Data Fields
order_ids = [f"CA-2025-{100000 + i}" for i in range(n_records)]
order_dates = [datetime(2024, 1, 1) + timedelta(days=int(np.random.randint(0, 800))) for i in range(n_records)]
customer_ids = [f"CS-{np.random.randint(1001, 1500)}" for i in range(n_records)]
segments = np.random.choice(['Consumer', 'Corporate', 'Home Office'], size=n_records, p=[0.5, 0.3, 0.2])
regions = np.random.choice(['North', 'South', 'East', 'West'], size=n_records)

states_map = {
    'North': ['Delhi', 'Punjab', 'Haryana', 'UP'],
    'South': ['Karnataka', 'Tamil Nadu', 'Telangana', 'Kerala'],
    'East': ['West Bengal', 'Odisha', 'Bihar', 'Jharkhand'],
    'West': ['Maharashtra', 'Gujarat', 'Rajasthan', 'Goa']
}
states = [np.random.choice(states_map[r]) for r in regions]
categories = np.random.choice(['Furniture', 'Office Supplies', 'Technology'], size=n_records, p=[0.3, 0.4, 0.3])

sub_cats_map = {
    'Furniture': ['Chairs', 'Tables', 'Furnishings'],
    'Office Supplies': ['Paper', 'Binders', 'Art', 'Fasteners'],
    'Technology': ['Phones', 'Accessories', 'Copiers']
}
sub_cats = [np.random.choice(sub_cats_map[c]) for c in categories]

quantities = np.random.randint(1, 10, size=n_records)
base_prices = np.random.uniform(10, 500, size=n_records)
sales = base_prices * quantities
discounts = np.random.choice([0.0, 0.1, 0.2, 0.5], size=n_records, p=[0.6, 0.2, 0.1, 0.1])
sales = sales * (1 - discounts)

profits = []
for i in range(n_records):
    if sub_cats[i] == 'Tables' and regions[i] == 'South':
        p = -float(sales[i] * np.random.uniform(0.1, 0.4))
    else:
        p = float(sales[i] * np.random.uniform(0.05, 0.25))
    profits.append(p)

df = pd.DataFrame({
    'order_id': order_ids, 'order_date': order_dates, 'customer_id': customer_ids,
    'segment': segments, 'region': regions, 'state': states,
    'category': categories, 'sub_category': sub_cats,
    'sales': np.round(sales, 2), 'quantity': quantities, 'discount': discounts, 'profit': np.round(profits, 2)
})

df.loc[df.sample(frac=0.01).index, 'discount'] = np.nan

print("🧹 Data Preprocessing Aur Cleaning Shuru...")
df.dropna(subset=['order_id', 'sales'], inplace=True)

df['discount'] = df['discount'].fillna(0.0)
df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime('%Y-%m-%d')

df['profit_margin'] = np.round((df['profit'] / df['sales']) * 100, 2)
df['calculated_cost_basis'] = np.round(df['sales'] - df['profit'], 2)

df['profit_margin'] = df['profit_margin'].replace([np.inf, -np.inf], np.nan).fillna(0.0)
df['calculated_cost_basis'] = df['calculated_cost_basis'].fillna(0.0)

df.to_csv('cleaned_sales_data.csv', index=False)
print("✨ Cleaned data local save ho gaya: cleaned_sales_data.csv")

try:
    print("🔌 Supabase Se Connection Set Ho Raha Hai...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    records = df.to_dict(orient='records')

    batch_size = 500
    total_batches = (len(records) + batch_size - 1) // batch_size
    print(f"📤 Transmitting {len(records)} records in {total_batches} batches...")

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        supabase.table('corporate_sales_records').upsert(batch).execute()
        print(f"  ✅ Batch {i // batch_size + 1}/{total_batches} done")

    print("⚡ Success! Saara data Supabase me chala gaya.")
except Exception as e:
    print(f"❌ Error: {e}")