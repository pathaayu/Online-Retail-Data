import pandas as pd
from datetime import timedelta

# ----------------------------------------
# 1. Load & Prepare Dataset
# ----------------------------------------

df = pd.read_csv("online_retail_data.csv")

df["order_date"] = pd.to_datetime(df["order_date"])
df["year_month"] = df["order_date"].dt.to_period("M")

# ----------------------------------------
# 2. Monthly Retention Rate
# ----------------------------------------

# Unique customers per month
customers_by_month = df.groupby("year_month")["customer_id"].apply(lambda x: set(x))

months = sorted(customers_by_month.index)
retention_data = []

for i in range(1, len(months)):
    prev_month = months[i - 1]
    curr_month = months[i]

    prev_customers = customers_by_month[prev_month]
    curr_customers = customers_by_month[curr_month]

    retained = len(prev_customers.intersection(curr_customers))
    retention_rate = retained / len(prev_customers) if prev_customers else 0

    retention_data.append({
        "month": str(curr_month),
        "retention_rate": round(retention_rate, 4)
    })

retention_df = pd.DataFrame(retention_data)
retention_df.to_csv("monthly_retention_rate.csv", index=False)
print("📈 Monthly retention saved → monthly_retention_rate.csv")

# ----------------------------------------
# 3. Churned Customers (No Activity in 60 Days)
# ----------------------------------------

last_purchase = df.groupby("customer_id")["order_date"].max()
latest_date = df["order_date"].max()
cutoff_date = latest_date - timedelta(days=60)

churned = last_purchase[last_purchase < cutoff_date].index.tolist()

churn_df = pd.DataFrame({"customer_id": churned})
churn_df.to_csv("churned_customers.csv", index=False)
print(f"⚠️ Churned customers saved → churned_customers.csv")
print(f"Total churned customers: {len(churn_df)}")