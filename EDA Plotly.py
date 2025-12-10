import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# =======================
# Load & prepare data
# =======================
df = pd.read_csv("online_retail_data.csv")

df["order_date"] = pd.to_datetime(df["order_date"])
df["revenue"] = df["quantity"] * df["price"]
df["profit"] = df["revenue"] * 0.30  # 30% margin, cost = 70%
df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

# Age groups for segmentation
df["age_group"] = pd.cut(
    df["age"],
    bins=[18, 30, 45, 60, 80],
    labels=["18-30", "31-45", "46-60", "60+"]
)

min_date = df["order_date"].min()
max_date = df["order_date"].max()

all_categories = sorted(df["category_name"].unique())
all_cities = sorted(df["city"].unique())
all_genders = sorted(df["gender"].dropna().unique())
all_age_groups = list(df["age_group"].cat.categories)

PLOT_TEMPLATE = "simple_white"

# =======================
# Dash app
# =======================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Retail Analytics Dashboard"
)
server = app.server


def kpi_card(id_, label, value_placeholder="$0"):
    """Small helper to create KPI cards."""
    return dbc.Card(
        id=id_,
        body=True,
        style={
            "borderRadius": "14px",
            "boxShadow": "0 6px 18px rgba(15, 23, 42, 0.08)",
            "border": "none",
            "backgroundColor": "#ffffff",
            "minHeight": "90px",
        },
        children=[
            html.Div(label, className="text-muted", style={"fontSize": "0.8rem", "textTransform": "uppercase"}),
            html.Div(value_placeholder, className="fw-bold", style={"fontSize": "1.6rem"}),
        ],
    )


app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f4f6fb", "minHeight": "100vh", "padding": "20px 30px"},
    children=[
        # ---------- HEADER ----------
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Sales Opportunities Dashboard", className="fw-bold mb-1"),
                        html.Div("Online Retail – Python · Dash · Plotly", className="text-muted"),
                    ],
                    md=6,
                ),
                dbc.Col(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Date Range", className="small text-muted mb-1"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        start_date=min_date,
                                        end_date=max_date,
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        display_format="YYYY-MM-DD",
                                        style={"width": "100%"},
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Category", className="small text-muted mb-1"),
                                    dcc.Dropdown(
                                        id="category-filter",
                                        options=[{"label": c, "value": c} for c in all_categories],
                                        value=all_categories,
                                        multi=True,
                                        placeholder="All categories",
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="g-2 justify-content-end",
                    ),
                    md=6,
                ),
            ],
            className="mb-3",
        ),

        # ---------- MAIN GRID ----------
        dbc.Row(
            [
                # LEFT COLUMN: KPI CARDS
                dbc.Col(
                    [
                        kpi_card("kpi-total-revenue", "Total Revenue"),
                        html.Br(),
                        kpi_card("kpi-total-profit", "Total Profit"),
                        html.Br(),
                        kpi_card("kpi-aov", "Avg Order Value"),
                        html.Br(),
                        kpi_card("kpi-orders", "Total Orders"),
                        html.Br(),
                        kpi_card("kpi-customers", "Active Customers"),
                    ],
                    md=3,
                ),

                # RIGHT COLUMN: CHARTS
                dbc.Col(
                    [
                        # TOP ROW: 2 CHARTS SIDE BY SIDE
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        body=True,
                                        style={
                                            "borderRadius": "14px",
                                            "boxShadow": "0 6px 18px rgba(15, 23, 42, 0.08)",
                                            "border": "none",
                                            "backgroundColor": "#ffffff",
                                        },
                                        children=[
                                            html.Div("Sales Over Time", className="text-muted mb-1"),
                                            dcc.Graph(
                                                    id="graph-monthly-revenue",
                                                    config={"displayModeBar": False},
                                                    style={"height": "260px"},
                                            ),
                                        ],
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        body=True,
                                        style={
                                            "borderRadius": "14px",
                                            "boxShadow": "0 6px 18px rgba(15, 23, 42, 0.08)",
                                            "border": "none",
                                            "backgroundColor": "#ffffff",
                                        },
                                        children=[
                                            html.Div("Avg Sales Value by Category", className="text-muted mb-1"),
                                            dcc.Graph(
                                                id="graph-category-revenue",
                                                config={"displayModeBar": False},
                                                style={"height": "260px"},
                                            ),
                                        ],
                                    ),
                                    md=6,
                                ),
                            ],
                            className="gy-3 mb-3",
                        ),

                        # BOTTOM WIDE CHART
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        body=True,
                                        style={
                                            "borderRadius": "14px",
                                            "boxShadow": "0 6px 18px rgba(15, 23, 42, 0.08)",
                                            "border": "none",
                                            "backgroundColor": "#ffffff",
                                        },
                                        children=[
                                            html.Div("Sales Conversion by Segment (Age × Gender)", className="text-muted mb-1"),
                                            dcc.Graph(
                                                id="graph-age-gender",
                                                config={"displayModeBar": False},
                                                style={"height": "260px"},
                                            ),
                                        ],
                                    ),
                                    md=12,
                                )
                            ]
                        ),
                    ],
                    md=9,
                ),
            ]
        ),

        html.Br(),
        html.Div("Designed for portfolio/demo use – tweak colors & texts to match your style.",
                 className="text-muted small"),
    ],
)

# =======================
# Callbacks
# =======================

@app.callback(
    [
        # KPI outputs
        Output("kpi-total-revenue", "children"),
        Output("kpi-total-profit", "children"),
        Output("kpi-aov", "children"),
        Output("kpi-orders", "children"),
        Output("kpi-customers", "children"),
        # Charts
        Output("graph-monthly-revenue", "figure"),
        Output("graph-category-revenue", "figure"),
        Output("graph-age-gender", "figure"),
    ],
    [
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("category-filter", "value"),
    ]
)
def update_dashboard(start_date, end_date, categories):
    if start_date is None:
        start_date = min_date
    if end_date is None:
        end_date = max_date

    # Filter
    filtered = df.copy()
    filtered = filtered[
        filtered["order_date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))
    ]
    if categories:
        filtered = filtered[filtered["category_name"].isin(categories)]

    if filtered.empty:
        # Empty KPIs
        def k(label):
            return [
                html.Div(label, className="text-muted", style={"fontSize": "0.8rem", "textTransform": "uppercase"}),
                html.Div("—", className="fw-bold", style={"fontSize": "1.6rem"}),
            ]

        empty_fig = px.scatter(title="No data for selected filters", template=PLOT_TEMPLATE)
        empty_fig.update_layout(margin=dict(t=40, l=20, r=10, b=40))

        return (
            k("Total Revenue"),
            k("Total Profit"),
            k("Avg Order Value"),
            k("Total Orders"),
            k("Active Customers"),
            empty_fig,
            empty_fig,
            empty_fig,
        )

    # ---- KPIs ----
    total_revenue = filtered["revenue"].sum()
    total_profit = filtered["profit"].sum()
    avg_order_value = filtered["revenue"].mean()
    total_orders = len(filtered)
    active_customers = filtered["customer_id"].nunique()

    def kpi_block(label, value):
        return [
            html.Div(label, className="text-muted", style={"fontSize": "0.8rem", "textTransform": "uppercase"}),
            html.Div(value, className="fw-bold", style={"fontSize": "1.6rem"}),
        ]

    kpi_total_revenue = kpi_block("Total Revenue", f"${total_revenue:,.1f}")
    kpi_total_profit = kpi_block("Total Profit", f"${total_profit:,.1f}")
    kpi_aov = kpi_block("Avg Order Value", f"${avg_order_value:,.1f}")
    kpi_orders = kpi_block("Total Sales", f"{total_orders:,}")
    kpi_customers = kpi_block("Active Customers", f"{active_customers:,}")

    # ---- Chart 1: Sales Over Time (line) ----
    monthly = (
        filtered.groupby("year_month")["revenue"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )
    fig_monthly = px.line(
        monthly,
        x="year_month",
        y="revenue",
        markers=True,
        template=PLOT_TEMPLATE,
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        margin=dict(t=20, l=40, r=20, b=40),
    )

    # ---- Chart 2: Avg Sales Value by Category ----
    cat_avg = (
        filtered.groupby("category_name")["revenue"]
        .mean()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    fig_cat = px.bar(
        cat_avg,
        x="category_name",
        y="revenue",
        template=PLOT_TEMPLATE,
    )
    fig_cat.update_layout(
        xaxis_title="Category",
        yaxis_title="Avg Revenue per Order",
        margin=dict(t=20, l=40, r=20, b=80),
    )

    # ---- Chart 3: Age × Gender stacked area / grouped bar ----
    seg = (
        filtered.groupby(["year_month", "age_group", "gender"])["revenue"]
        .sum()
        .reset_index()
    )

    # For simplicity & clarity, grouped bar by Age × Gender (over all time)
    seg2 = (
        filtered.groupby(["age_group", "gender"])["revenue"]
        .sum()
        .reset_index()
    )
    fig_seg = px.bar(
        seg2,
        x="age_group",
        y="revenue",
        color="gender",
        barmode="group",
        template=PLOT_TEMPLATE,
    )
    fig_seg.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Revenue",
        margin=dict(t=20, l=40, r=20, b=40),
        legend_title="Gender",
    )

    return (
        kpi_total_revenue,
        kpi_total_profit,
        kpi_aov,
        kpi_orders,
        kpi_customers,
        fig_monthly,
        fig_cat,
        fig_seg,
    )


if __name__ == "__main__":
    app.run_server(debug=True)