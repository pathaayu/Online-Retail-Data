import pandas as pd
import streamlit as st

# Try importing plotly and fail gracefully if it's missing
try:
    import plotly.express as px
except ModuleNotFoundError:
    st.set_page_config(page_title="Online Retail Dashboard", layout="wide")
    st.error(
        "❌ The 'plotly' library is not installed.\n\n"
        "To fix this:\n"
        "• If running locally: run `pip install plotly`\n"
        "• If using Streamlit Cloud: create `requirements.txt` with:\n"
        "    streamlit\n    pandas\n    plotly"
    )
    st.stop()

# ======================================================
# 1. Page config & basic styling
# ======================================================

st.set_page_config(
    page_title="Online Retail Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .main {
            background-color: #f4f6fb;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }
        .kpi-card {
            padding: 0.9rem 1.1rem;
            border-radius: 0.8rem;
            background-color: #ffffff;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
            border: 1px solid rgba(148, 163, 184, 0.15);
            margin-bottom: 0.8rem;
        }
        .kpi-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #6b7280;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 600;
            color: #111827;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# 2. Load & prepare data
# ======================================================

@st.cache_data
def load_data():
    df = pd.read_csv("online_retail_data.csv")

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["quantity"] * df["price"]
    df["profit"] = df["revenue"] * 0.30  # 30% margin, cost = 70%

    # Age groups for segmentation
    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 30, 45, 60, 80],
        labels=["18-30", "31-45", "46-60", "60+"]
    )

    # Month-Year for trends
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    return df


df = load_data()

# ======================================================
# 3. Header
# ======================================================

st.title("📊 Sales Opportunities Dashboard")
st.caption("Online retail analytics – built with Python, Streamlit & Plotly")
st.markdown("---")

# ======================================================
# 4. Sidebar filters
# ======================================================

st.sidebar.header("🔍 Filters")

min_date = df["order_date"].min()
max_date = df["order_date"].max()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

categories = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["category_name"].unique()),
    default=sorted(df["category_name"].unique()),
)

genders = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["gender"].dropna().unique()),
    default=sorted(df["gender"].dropna().unique()),
)

age_groups = st.sidebar.multiselect(
    "Age Group",
    options=df["age_group"].cat.categories.tolist(),
    default=df["age_group"].cat.categories.tolist(),
)

all_cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect(
    "City (optional – leave empty for all)",
    options=all_cities,
    default=[],
)

# Apply filters
filtered_df = df[
    (df["order_date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date)))
    & (df["category_name"].isin(categories))
    & (df["gender"].isin(genders))
    & (df["age_group"].isin(age_groups))
]

if selected_cities:
    filtered_df = filtered_df[filtered_df["city"].isin(selected_cities)]

# ======================================================
# 5. Layout: left KPIs & right charts
# ======================================================

left_col, right_col = st.columns([1, 3])

# ---------- 5A. KPIs ----------
with left_col:
    st.subheader("📌 KPIs")

    if filtered_df.empty:
        st.info("No data for selected filters.")
    else:
        total_revenue = filtered_df["revenue"].sum()
        total_profit = filtered_df["profit"].sum()
        avg_order_value = filtered_df["revenue"].mean()
        num_orders = len(filtered_df)
        num_customers = filtered_df["customer_id"].nunique()

        def kpi_html(label, value):
            return f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """

        st.markdown(
            kpi_html("Total Revenue", f"${total_revenue:,.1f}"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_html("Total Profit", f"${total_profit:,.1f}"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_html("Avg Order Value", f"${avg_order_value:,.1f}"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_html("Total Orders", f"{num_orders:,}"),
            unsafe_allow_html=True,
        )
        st.markdown(
            kpi_html("Active Customers", f"{num_customers:,}"),
            unsafe_allow_html=True,
        )

# ---------- 5B. Right side charts ----------
with right_col:
    st.subheader("📈 KPIs & Trends")

    if filtered_df.empty:
        st.info("No data available for selected filters.")
    else:
        # Monthly revenue trend
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
            title="Sales Over Time",
            markers=True,
        )
        fig_monthly.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue",
            template="simple_white",
            height=260,
            margin=dict(t=40, l=40, r=20, b=40),
        )

        top_left, top_right = st.columns(2)

        with top_left:
            st.plotly_chart(fig_monthly, use_container_width=True)

        with top_right:
            cat_avg = (
                filtered_df.groupby("category_name")["revenue"]
                .mean()
                .reset_index()
                .sort_values("revenue", ascending=False)
            )
            fig_cat = px.bar(
                cat_avg,
                x="category_name",
                y="revenue",
                title="Avg Sales Value by Category",
            )
            fig_cat.update_layout(
                xaxis_title="Category",
                yaxis_title="Avg Revenue per Order",
                template="simple_white",
                height=260,
                margin=dict(t=40, l=40, r=20, b=80),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        # Bottom wide chart: Age × Gender
        seg = (
            filtered_df.groupby(["age_group", "gender"])["revenue"]
            .sum()
            .reset_index()
        )
        fig_seg = px.bar(
            seg,
            x="age_group",
            y="revenue",
            color="gender",
            barmode="group",
            title="Revenue by Age Group & Gender",
        )
        fig_seg.update_layout(
            xaxis_title="Age Group",
            yaxis_title="Revenue",
            template="simple_white",
            height=260,
            margin=dict(t=40, l=40, r=20, b=40),
        )
        st.plotly_chart(fig_seg, use_container_width=True)

# ======================================================
# 6. Extra comparisons
# ======================================================

st.markdown("---")
st.subheader("🧩 Additional Comparisons")

bottom_left, bottom_right = st.columns(2)

if filtered_df.empty:
    bottom_left.info("No data for bottom charts with current filters.")
else:
    with bottom_left:
        st.markdown("#### 🏷 Total Revenue by Category")
        cat_rev = (
            filtered_df.groupby("category_name")["revenue"]
            .sum()
            .reset_index()
            .sort_values("revenue", ascending=False)
        )
        fig_cat_sum = px.bar(
            cat_rev,
            x="category_name",
            y="revenue",
            title="Total Revenue by Category",
        )
        fig_cat_sum.update_layout(
            xaxis_title="Category",
            yaxis_title="Revenue",
            template="simple_white",
            height=260,
            margin=dict(t=40, l=40, r=20, b=80),
        )
        st.plotly_chart(fig_cat_sum, use_container_width=True)

    with bottom_right:
        st.markdown("#### 🏙 Top 10 Cities by Revenue")
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
            title="Top 10 Cities by Revenue",
        )
        fig_city.update_layout(
            xaxis_title="City",
            yaxis_title="Revenue",
            template="simple_white",
            height=260,
            margin=dict(t=40, l=40, r=20, b=80),
        )
        st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")
st.caption("Designed as a portfolio-style dashboard. Add your name/logo in the title bar for extra polish ✨")