import pandas as pd
import streamlit as st
import plotly.express as px

# ----------------------------
# 1. Load & Prepare Data
# ----------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("online_retail_data.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["quantity"] * df["price"]
    df["profit"] = df["revenue"] * 0.30  # 30% margin, cost = 70% of price

    # Age groups
    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 30, 45, 60, 80],
        labels=["18-30", "31-45", "46-60", "60+"]
    )

    # Month-Year for trends
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    return df

df = load_data()

# ----------------------------
# 2. Page Layout & Title
# ----------------------------

st.set_page_config(
    page_title="Online Retail Dashboard",
    layout="wide"
)

st.title("📊 Online Retail Analytics Dashboard")
st.caption("Interactive dashboard built with Python, Streamlit & Plotly")

# ----------------------------
# 3. Sidebar Filters
# ----------------------------

st.sidebar.header("🔍 Filters")

# Date range
min_date = df["order_date"].min()
max_date = df["order_date"].max()
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Category filter
categories = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["category_name"].unique()),
    default=sorted(df["category_name"].unique())
)

# Gender filter
genders = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["gender"].dropna().unique()),
    default=sorted(df["gender"].dropna().unique())
)

# Age group filter
age_groups = st.sidebar.multiselect(
    "Age Group",
    options=df["age_group"].cat.categories.tolist(),
    default=df["age_group"].cat.categories.tolist()
)

# City filter (top n)
all_cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect(
    "City (optional, leave empty for all)",
    options=all_cities,
    default=[]
)

# Apply filters
filtered_df = df[
    (df["order_date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (df["category_name"].isin(categories)) &
    (df["gender"].isin(genders)) &
    (df["age_group"].isin(age_groups))
]

if selected_cities:
    filtered_df = filtered_df[filtered_df["city"].isin(selected_cities)]

# ----------------------------
# 4. KPIs
# ----------------------------

st.subheader("📌 Key Performance Indicators")

total_revenue = filtered_df["revenue"].sum()
total_profit = filtered_df["profit"].sum()
avg_order_value = filtered_df["revenue"].mean() if not filtered_df.empty else 0
num_orders = len(filtered_df)
num_customers = filtered_df["customer_id"].nunique()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("# Orders", f"{num_orders:,}")
col5.metric("# Unique Customers", f"{num_customers:,}")

st.markdown("---")

# ----------------------------
# 5. Trends Section
# ----------------------------

st.subheader("📈 KPIs & Trends")

# Monthly revenue trend
if not filtered_df.empty:
    monthly = (
        filtered_df.groupby("year_month")["revenue"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )
    fig_monthly = px.line(
        monthly,
        x="year_month",
        y="revenue",
        title="Monthly Revenue Trend",
        markers=True
    )
    fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Revenue")
    st.plotly_chart(fig_monthly, use_container_width=True)
else:
    st.info("No data available for selected filters.")

# ----------------------------
# 6. Category & City Comparisons
# ----------------------------

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("### 🏷 Revenue by Category")
    if not filtered_df.empty:
        cat_rev = (
            filtered_df.groupby("category_name")["revenue"]
            .sum()
            .reset_index()
            .sort_values("revenue", ascending=False)
        )
        fig_cat = px.bar(
            cat_rev,
            x="category_name",
            y="revenue",
            title="Revenue by Category"
        )
        fig_cat.update_layout(xaxis_title="Category", yaxis_title="Revenue")
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data for selected filters.")

with right_col:
    st.markdown("### 🏙 Top 10 Cities by Revenue")
    if not filtered_df.empty:
        city_rev = (
            filtered_df.groupby("city")["revenue"]
            .sum()
            .reset_index()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        fig_city = px.bar(
            city_rev,
            x="city",
            y="revenue",
            title="Top 10 Cities by Revenue"
        )
        fig_city.update_layout(xaxis_title="City", yaxis_title="Revenue")
        st.plotly_chart(fig_city, use_container_width=True)
    else:
        st.info("No city data for selected filters.")

st.markdown("---")

# ----------------------------
# 7. Customer Segmentation
# ----------------------------

st.subheader("👥 Customer Segmentation & Comparison")

seg_col1, seg_col2 = st.columns(2)

with seg_col1:
    st.markdown("#### Revenue by Age Group")
    if not filtered_df.empty:
        age_seg = (
            filtered_df.groupby("age_group")["revenue"]
            .sum()
            .reset_index()
            .sort_values("age_group")
        )
        fig_age = px.bar(
            age_seg,
            x="age_group",
            y="revenue",
            title="Revenue by Age Group"
        )
        fig_age.update_layout(xaxis_title="Age Group", yaxis_title="Revenue")
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("No age data for selected filters.")

with seg_col2:
    st.markdown("#### Revenue by Gender")
    if not filtered_df.empty:
        gender_seg = (
            filtered_df.groupby("gender")["revenue"]
            .sum()
            .reset_index()
        )
        fig_gender = px.bar(
            gender_seg,
            x="gender",
            y="revenue",
            title="Revenue by Gender"
        )
        fig_gender.update_layout(xaxis_title="Gender", yaxis_title="Revenue")
        st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.info("No gender data for selected filters.")

# Age x Gender comparison (heatmap-style bar)
st.markdown("#### Age Group vs Gender — Revenue Matrix")
if not filtered_df.empty:
    pivot = (
        filtered_df
        .groupby(["age_group", "gender"])["revenue"]
        .sum()
        .reset_index()
    )
    fig_pivot = px.bar(
        pivot,
        x="age_group",
        y="revenue",
        color="gender",
        barmode="group",
        title="Revenue by Age Group & Gender"
    )
    fig_pivot.update_layout(xaxis_title="Age Group", yaxis_title="Revenue")
    st.plotly_chart(fig_pivot, use_container_width=True)
else:
    st.info("No segmentation data for selected filters.")

st.markdown("---")
st.caption("Built with ❤️ using Python, Pandas, Streamlit & Plotly")