import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# FOOD DELIVERY STORYTELLING DASHBOARD
# Adapted from the original Food Delivery project and the
# visual storytelling layout in storytelling-dashboard.pdf
# ---------------------------------------------------------

st.set_page_config(
    page_title="Food Delivery Story Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Theme ----------
st.markdown("""
<style>
    .stApp { background-color: #f4f7fb; }
    [data-testid="stSidebar"] {
        background: #142b4d;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .main-title {
        color: #183b68;
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .sub-title { color: #6b7890; font-size: 13px; margin-bottom: 20px; }
    .story {
        background: #e8f0fb;
        border-left: 5px solid #2e65a5;
        padding: 13px 16px;
        border-radius: 7px;
        color: #183b68;
        margin: 12px 0 8px 0;
    }
    .story-title { font-weight: 800; color: #214f87; }
    .small-note { color: #66758b; font-size: 12px; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e1e8f0;
        padding: 14px 16px;
        border-radius: 9px;
    }
    h2, h3 { color: #183b68; }
</style>
""", unsafe_allow_html=True)

BLUE = ["#214f87", "#4f83c2", "#80a9d8", "#a9c5e5", "#d0e0f2"]

# ---------- Load and clean data ----------
@st.cache_data
def load_data():
    data = pd.read_csv("delivery_data.csv")
    numeric_columns = [
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "Restaurant_latitude",
        "Restaurant_longitude",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
        "Time_taken(min)"
    ]

    for col in numeric_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    required = [
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "Type_of_order",
        "Type_of_vehicle",
        "Time_taken(min)"
    ]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            "The CSV file is missing these required columns: "
            + ", ".join(missing)
        )

    data = data.dropna(subset=required).copy()
    data["Type_of_order"] = data["Type_of_order"].astype(str)
    data["Type_of_vehicle"] = data["Type_of_vehicle"].astype(str)
    return data

try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load delivery_data.csv: {error}")
    st.info("Keep app.py and delivery_data.csv in the same project folder.")
    st.stop()

if df.empty:
    st.error("The dataset has no complete records to display.")
    st.stop()

# ---------- Sidebar navigation and filters ----------
st.sidebar.markdown("## 🍔 DELIVERY STORY")
st.sidebar.caption("FOOD DELIVERY ANALYTICS")
page = st.sidebar.radio(
    "DASHBOARD",
    [
        "Delivery Overview",
        "Delivery Time Trends",
        "Delivery Performance Insights",
        "Vehicle & Order Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### FILTERS")
st.sidebar.caption("Selections update the dashboard charts and KPIs.")

order_options = sorted(df["Type_of_order"].dropna().unique().tolist())
vehicle_options = sorted(df["Type_of_vehicle"].dropna().unique().tolist())

selected_orders = st.sidebar.multiselect(
    "Order type", order_options, default=order_options
)
selected_vehicles = st.sidebar.multiselect(
    "Vehicle type", vehicle_options, default=vehicle_options
)

age_min, age_max = int(df["Delivery_person_Age"].min()), int(df["Delivery_person_Age"].max())
rating_min, rating_max = float(df["Delivery_person_Ratings"].min()), float(df["Delivery_person_Ratings"].max())
time_min, time_max = int(df["Time_taken(min)"].min()), int(df["Time_taken(min)"].max())

age_range = st.sidebar.slider(
    "Delivery person age", age_min, age_max, (age_min, age_max)
)
rating_range = st.sidebar.slider(
    "Delivery person rating",
    float(rating_min), float(rating_max),
    (float(rating_min), float(rating_max)), step=0.1
)
time_range = st.sidebar.slider(
    "Delivery time (minutes)", time_min, time_max, (time_min, time_max)
)

if st.sidebar.button("Reset all filters", use_container_width=True):
    st.rerun()

# Apply all filters once
filtered_df = df[
    df["Type_of_order"].isin(selected_orders)
    & df["Type_of_vehicle"].isin(selected_vehicles)
    & df["Delivery_person_Age"].between(age_range[0], age_range[1])
    & df["Delivery_person_Ratings"].between(rating_range[0], rating_range[1])
    & df["Time_taken(min)"].between(time_range[0], time_range[1])
].copy()

# ---------- Common page heading and KPIs ----------
page_titles = {
    "Delivery Overview": "Delivery Performance | Executive Overview",
    "Delivery Time Trends": "Delivery Time Trends | When Do Deliveries Take Longer?",
    "Delivery Performance Insights": "Delivery Insights | What Affects Delivery Performance?",
    "Vehicle & Order Analysis": "Vehicle & Order Analysis | Which Categories Perform Better?"
}
page_subtitles = {
    "Delivery Overview": "A guided story from delivery performance to useful observations",
    "Delivery Time Trends": "Understand the distribution of delivery duration and age patterns",
    "Delivery Performance Insights": "Explore how delivery-person ratings relate to delivery duration",
    "Vehicle & Order Analysis": "Compare delivery duration across vehicle and order categories"
}

st.markdown(f'<div class="main-title">{page_titles[page]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{page_subtitles[page]}</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No records match the selected filters. Please widen or reset the filters.")
    st.stop()

avg_time = filtered_df["Time_taken(min)"].mean()
median_time = filtered_df["Time_taken(min)"].median()
avg_rating = filtered_df["Delivery_person_Ratings"].mean()
total_deliveries = len(filtered_df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("TOTAL DELIVERIES", f"{total_deliveries:,}")
k2.metric("AVERAGE DELIVERY TIME", f"{avg_time:.1f} min")
k3.metric("MEDIAN DELIVERY TIME", f"{median_time:.1f} min")
k4.metric("AVERAGE DELIVERY-PERSON RATING", f"{avg_rating:.2f} / 5")

st.markdown("---")

# ---------- 1. Delivery Overview ----------
if page == "Delivery Overview":
    left, right = st.columns([1.6, 1])

    with left:
        st.subheader("1. How are delivery times distributed?")
        fig = px.histogram(
            filtered_df,
            x="Time_taken(min)",
            nbins=25,
            labels={"Time_taken(min)": "Delivery time (minutes)", "count": "Number of deliveries"},
            color_discrete_sequence=[BLUE[0]]
        )
        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            bargap=0.08,
            margin=dict(l=15, r=15, t=25, b=15)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("2. Deliveries by order type")
        order_counts = (
            filtered_df["Type_of_order"]
            .value_counts()
            .rename_axis("Order type")
            .reset_index(name="Deliveries")
        )
        fig = px.pie(
            order_counts, names="Order type", values="Deliveries",
            hole=0.48, color_discrete_sequence=BLUE
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=5, r=5, t=25, b=5),
            legend_title_text=""
        )
        st.plotly_chart(fig, use_container_width=True)

    story = (
        f"The selected data contains {total_deliveries:,} deliveries. "
        f"Average delivery time is {avg_time:.1f} minutes and the median is "
        f"{median_time:.1f} minutes."
    )
    st.markdown(
        f'<div class="story"><div class="story-title">STORY 01 | Overall delivery performance</div>{story}</div>',
        unsafe_allow_html=True
    )
    st.markdown("**NEXT STEP:** Check the delivery-time distribution, then explore which vehicle and order categories have longer average delivery times.")
    st.caption("HOW TO READ THIS: KPI cards summarize the filtered records. Charts below them show how delivery times and order categories are distributed.")

# ---------- 2. Delivery Time Trends ----------
elif page == "Delivery Time Trends":
    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("1. Delivery time distribution")
        fig = px.histogram(
            filtered_df, x="Time_taken(min)", nbins=30,
            marginal="box",
            labels={"Time_taken(min)": "Delivery time (minutes)"},
            color_discrete_sequence=[BLUE[0]]
        )
        fig.update_layout(template="plotly_white", margin=dict(l=15, r=15, t=25, b=15))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("2. Average time by age group")
        age_data = filtered_df.copy()
        age_data["Age group"] = pd.cut(
            age_data["Delivery_person_Age"],
            bins=[0, 20, 30, 40, 50, 100],
            labels=["Below 20", "21–30", "31–40", "41–50", "Above 50"],
            include_lowest=True
        )
        age_summary = (
            age_data.groupby("Age group", observed=False)["Time_taken(min)"]
            .mean().reset_index()
        )
        age_summary = age_summary.dropna()
        fig = px.bar(
            age_summary, x="Age group", y="Time_taken(min)",
            text_auto=".1f",
            labels={"Time_taken(min)": "Average delivery time (minutes)"},
            color="Age group", color_discrete_sequence=BLUE
        )
        fig.update_layout(
            template="plotly_white", showlegend=False,
            margin=dict(l=10, r=10, t=25, b=15)
        )
        st.plotly_chart(fig, use_container_width=True)

    slowest = filtered_df["Time_taken(min)"].max()
    fastest = filtered_df["Time_taken(min)"].min()
    st.markdown(
        f'<div class="story"><div class="story-title">STORY 02 | Delivery duration varies across orders</div>'
        f'In the selected records, delivery times range from {fastest:.0f} to {slowest:.0f} minutes. '
        f'The histogram helps identify common delivery-time ranges, while the age-group chart compares average duration.</div>',
        unsafe_allow_html=True
    )
    st.markdown("**DECISION PROMPT:** Which delivery-time ranges occur most often? Do age groups show noticeable differences?")
    st.caption("This dataset does not provide a confirmed monthly order-date field, so this view uses delivery-time distribution rather than inventing a monthly trend.")

# ---------- 3. Delivery Performance Insights ----------
elif page == "Delivery Performance Insights":
    left, right = st.columns(2)

    with left:
        st.subheader("1. Delivery-person rating vs delivery time")
        fig = px.scatter(
            filtered_df,
            x="Delivery_person_Ratings",
            y="Time_taken(min)",
            color="Type_of_order",
            opacity=0.65,
            labels={
                "Delivery_person_Ratings": "Delivery-person rating",
                "Time_taken(min)": "Delivery time (minutes)",
                "Type_of_order": "Order type"
            },
            color_discrete_sequence=BLUE
        )
        fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=25, b=15))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("2. Delivery time and rating correlation")
        corr = filtered_df[[
            "Delivery_person_Age",
            "Delivery_person_Ratings",
            "Time_taken(min)"
        ]].corr()
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="Blues", zmin=-1, zmax=1
        )
        fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=25, b=15))
        st.plotly_chart(fig, use_container_width=True)

    correlation = filtered_df["Delivery_person_Ratings"].corr(filtered_df["Time_taken(min)"])
    if pd.isna(correlation):
        relationship = "There is not enough variation in the selected data to calculate this correlation."
    elif correlation > 0.2:
        relationship = "The selected data shows a positive association between rating and delivery time."
    elif correlation < -0.2:
        relationship = "The selected data shows a negative association between rating and delivery time."
    else:
        relationship = "The selected data shows a weak linear association between rating and delivery time."

    st.markdown(
        f'<div class="story"><div class="story-title">STORY 03 | Ratings and delivery duration</div>'
        f'{relationship} The calculated correlation is {correlation:.2f} when available. '
        f'This is an association, not proof that one factor causes the other.</div>',
        unsafe_allow_html=True
    )
    st.markdown("**DECISION PROMPT:** Are ratings changing with delivery duration? Investigate other factors before drawing conclusions.")

# ---------- 4. Vehicle & Order Analysis ----------
else:
    left, right = st.columns(2)

    vehicle_summary = (
        filtered_df.groupby("Type_of_vehicle", as_index=False)["Time_taken(min)"]
        .mean().sort_values("Time_taken(min)", ascending=False)
    )
    order_summary = (
        filtered_df.groupby("Type_of_order", as_index=False)["Time_taken(min)"]
        .mean().sort_values("Time_taken(min)", ascending=False)
    )

    with left:
        st.subheader("1. Average delivery time by vehicle")
        fig = px.bar(
            vehicle_summary, x="Time_taken(min)", y="Type_of_vehicle",
            orientation="h", text_auto=".1f",
            labels={
                "Time_taken(min)": "Average delivery time (minutes)",
                "Type_of_vehicle": "Vehicle type"
            },
            color="Type_of_vehicle", color_discrete_sequence=BLUE
        )
        fig.update_layout(
            template="plotly_white", showlegend=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=10, r=10, t=25, b=15)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("2. Average delivery time by order type")
        fig = px.bar(
            order_summary, x="Time_taken(min)", y="Type_of_order",
            orientation="h", text_auto=".1f",
            labels={
                "Time_taken(min)": "Average delivery time (minutes)",
                "Type_of_order": "Order type"
            },
            color="Type_of_order", color_discrete_sequence=BLUE
        )
        fig.update_layout(
            template="plotly_white", showlegend=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=10, r=10, t=25, b=15)
        )
        st.plotly_chart(fig, use_container_width=True)

    longest_vehicle = vehicle_summary.iloc[0]
    longest_order = order_summary.iloc[0]
    st.markdown(
        f'<div class="story"><div class="story-title">STORY 04 | Vehicle and order categories show different delivery times</div>'
        f'{longest_vehicle["Type_of_vehicle"]} has the highest average delivery time among the selected vehicle categories '
        f'({longest_vehicle["Time_taken(min)"]:.1f} minutes). '
        f'{longest_order["Type_of_order"]} has the highest average delivery time among the selected order categories '
        f'({longest_order["Time_taken(min)"]:.1f} minutes).</div>',
        unsafe_allow_html=True
    )
    st.markdown("**NEXT STEP:** Review categories with longer average delivery times and investigate the reasons using additional operational information.")

# ---------- Filtered data preview and download ----------
st.markdown("---")
with st.expander("View filtered delivery records"):
    st.dataframe(filtered_df, use_container_width=True, height=300)

csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data as CSV",
    data=csv_data,
    file_name="filtered_delivery_data.csv",
    mime="text/csv"
)

st.markdown(
    '<div class="small-note">Food Delivery Time Analysis Dashboard | '
    'Built with Python, Streamlit, Pandas and Plotly. '
    'The dataset contains delivery-person ratings; these should not be described as direct customer ratings.</div>',
    unsafe_allow_html=True
)
