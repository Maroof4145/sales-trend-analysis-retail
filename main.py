import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/superstore.csv", encoding='latin1')

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])
    cat_cols = ["Category", "Sub-Category", "Segment", "Region", "Ship Mode"]
    for col in cat_cols:
        df[col] = df[col].str.strip().str.title()
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%B")
    return df

df = load_data()

st.title("📊 Superstore Sales Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Select Year(s):", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Select Region(s):", df["Region"].unique(), default=df["Region"].unique())
categories = st.sidebar.multiselect("Select Category(ies):", df["Category"].unique(), default=df["Category"].unique())

# Filtered dataframe
filtered_df = df[df["Year"].isin(years) & df["Region"].isin(regions) & df["Category"].isin(categories)]

# KPIs
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()

st.metric("Total Sales", f"${total_sales:,.2f}")
st.metric("Total Profit", f"${total_profit:,.2f}")
st.metric("Unique Orders", total_orders)

# Monthly Trend
st.subheader("📅 Monthly Sales Trend")
monthly = filtered_df.groupby(["Year", "Month Name"])["Sales"].sum().reset_index()
monthly["Month"] = pd.to_datetime(monthly["Month Name"], format="%B").dt.month
monthly = monthly.sort_values(["Year", "Month"])

fig, ax = plt.subplots(figsize=(10, 4))
for y in monthly["Year"].unique():
    data = monthly[monthly["Year"] == y]
    ax.plot(data["Month"], data["Sales"], marker='o', label=str(y))
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.set_title("Monthly Sales Trend")
ax.set_xlabel("Month")
ax.set_ylabel("Sales")
ax.legend()
st.pyplot(fig)

# Top Products
st.subheader("🔥 Top 5 Best-Selling Products")
top_products = filtered_df.groupby("Product Name")["Quantity"].sum().sort_values(ascending=False).head(5)
fig2, ax2 = plt.subplots()
top_products.plot(kind='barh', ax=ax2)
ax2.set_title("Top 5 Best-Selling Products")
ax2.set_xlabel("Quantity Sold")
st.pyplot(fig2)

# Profit Heatmap by Region and Category
st.subheader("🌍 Regional Demand Heatmap")
heatmap_data = filtered_df.groupby(["Region", "Category"])["Quantity"].sum().unstack().fillna(0)
fig3, ax3 = plt.subplots()
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax3)
ax3.set_title("Quantity Sold by Region and Category")
st.pyplot(fig3)

st.caption("Created with ❤️ using Streamlit")
