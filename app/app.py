import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from streamlit.components.v1 import html


# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="NYC Airbnb Value Dashboard",
    layout="wide"
)

# ---------------- DATA ----------------
data = pd.read_csv(
    os.path.join(BASE_DIR, "..", "data", "neighbourhood_value_ranking.csv")
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🗺️ Controls")

borough = st.sidebar.selectbox(
    "Select Borough",
    ["All"] + sorted(data["neighbourhood_group"].unique())
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Ask the Dashboard")

question = st.sidebar.text_input("Ask about best, worst, or borough")

# ---------------- HEADER ----------------
st.title("🏙️ NYC Airbnb Neighbourhood Value Analysis")
st.caption("Value assessment using price, availability, and demand")

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Neighbourhoods", data.shape[0])
col2.metric("Boroughs", data["neighbourhood_group"].nunique())
col3.metric(
    "Undervalued Areas",
    (data["value_category"] == "Undervalued").sum()
)

st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dataset Overview",
    "🏆 Rankings",
    "🗺️ Borough Explorer",
    "🗺️ Map View",
    "💡 Insights"
])


# ================= TAB 1 =================
with tab1:
    st.subheader("Dataset Summary")

    st.markdown(
        """
        This dashboard evaluates **Airbnb value across NYC neighbourhoods**
        using a composite **Value Score**:
        """
    )

    st.latex(
        r"\text{Value Score} = \frac{\text{Availability} \times \text{Popularity}}{\text{Price}}"
    )

    st.markdown(
        """
        - Higher score → better value  
        - Lower score → overpriced or unattractive  
        - Scores are stabilized & sample-size adjusted
        """
    )

    st.dataframe(
        data.sort_values("value_rank").reset_index(drop=True),
        use_container_width=True
    )

# ================= TAB 2 =================
with tab2:
    st.subheader("Top 10 Undervalued Neighbourhoods")

    top_10 = (
        data[data["value_category"] == "Undervalued"]
        .sort_values("value_score", ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(
        data=top_10,
        x="value_score",
        y="neighbourhood",
        hue="neighbourhood_group",
        dodge=False,
        ax=ax
    )

    ax.set_xlabel("Value Score")
    ax.set_ylabel("Neighbourhood")

    st.pyplot(fig)

# ================= TAB 3 =================
with tab3:
    st.subheader("Borough-Based Analysis")

    if borough != "All":
        borough_data = data[data["neighbourhood_group"] == borough]
    else:
        borough_data = data.copy()

    with st.container():
        col1, col2 = st.columns([1.3, 2.7])

        #  Heatmap (LEFT)
        with col1:
            heatmap_data = (
                borough_data
                .sort_values("value_score", ascending=False)
                .head(15)
                .set_index("neighbourhood")[["value_score"]]
            )

            fig, ax = plt.subplots(figsize=(5,4))
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt=".2f",
                cmap="YlGnBu",
                cbar=True,
                linewidths=0.5,
                ax=ax
            )

            ax.set_title("Top Neighbourhood Value Scores")
            ax.set_xlabel("Value Score")
            ax.set_ylabel("Neighbourhood")

            st.pyplot(fig)

        # 📋 Table (RIGHT)
        with col2:
            st.dataframe(
                borough_data.sort_values("value_score", ascending=False),
                use_container_width=True
            )


# ================= TAB 4 : MAP VIEW =================
with tab4:
    st.subheader("🗺️ NYC Airbnb Value Map")

    st.markdown(
        """
        This interactive map visualizes Airbnb neighbourhood value across NYC.
        - 🟢 Undervalued areas
        - 🟡 Fairly priced areas
        - 🔴 Overpriced areas
        Marker size reflects relative value score.
        """
    )

    with open("nyc_airbnb_value_map_polished.html", "r", encoding="utf-8") as f:
        map_html = f.read()

    html(map_html, height=650, scrolling=True)


# ================= TAB 5 =================
with tab5:
    st.subheader("💡 Key Insights")

    # ---------------- BEST VALUE ----------------
    best = (
        data[data["value_category"] == "Undervalued"]
        .sort_values("value_score", ascending=False)
        .iloc[0]
    )

    # ---------------- MOST OVERPRICED ----------------
    worst = (
        data[data["value_category"] == "Overpriced"]
        .sort_values("value_score")
        .iloc[0]
    )

    # ---------------- BOROUGH SUMMARY ----------------
    borough_avg = (
        data.groupby("neighbourhood_group")["value_score"]
        .mean()
        .sort_values(ascending=False)
    )

    top_borough = borough_avg.index[0]
    bottom_borough = borough_avg.index[-1]

    # ---------------- INSIGHT CARDS ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
            🏆 **Best Value Neighbourhood**  
            📍 {best['neighbourhood']} ({best['neighbourhood_group']})  
            💲 Avg Price: ${best['avg_price']:.0f}  
            📅 Availability: {best['avg_availability']:.0f} days  
            ⭐ Value Score: {best['value_score']:.2f}
            """
        )

        st.info(
            f"""
            🗺️ **Best Value Borough**  
            **{top_borough}** has the highest average value score across NYC,
            offering better price-to-availability balance.
            """
        )

    with col2:
        st.error(
            f"""
            ⚠️ **Most Overpriced Neighbourhood**  
            📍 {worst['neighbourhood']} ({worst['neighbourhood_group']})  
            💲 Avg Price: ${worst['avg_price']:.0f}  
            ⭐ Value Score: {worst['value_score']:.2f}
            """
        )

        st.warning(
            f"""
            🏙️ **Lowest Value Borough**  
            **{bottom_borough}** shows the lowest average value score,
            driven by high prices and lower availability.
            """
        )

    # ---------------- MARKET DISTRIBUTION ----------------
    st.markdown("---")
    st.subheader("📊 Market Distribution Insight")

    value_counts = data["value_category"].value_counts()

    st.write(
        f"""
        ✔ **{value_counts.get('Fairly Priced', 0)} neighbourhoods** are fairly priced  
        ✔ **{value_counts.get('Undervalued', 0)} neighbourhoods** offer strong value  
        ✔ **{value_counts.get('Overpriced', 0)} neighbourhoods** appear overpriced  

        👉 This indicates that NYC Airbnb pricing is largely efficient,
        with **localized pockets of opportunity** rather than widespread mispricing.
        """
    )

# ---------------- CHATBOT LOGIC ----------------
if question:
    q = question.lower()

    st.sidebar.markdown("### 💬 Answer")

    # -------- PRECOMPUTED HELPERS --------
    best_neighbourhood = (
        data[data["value_category"] == "Undervalued"]
        .sort_values("value_score", ascending=False)
        .iloc[0]
    )

    worst_neighbourhood = (
        data[data["value_category"] == "Overpriced"]
        .sort_values("value_score")
        .iloc[0]
    )

    borough_avg = (
        data.groupby("neighbourhood_group")["value_score"]
        .mean()
        .sort_values(ascending=False)
    )

    # -------- BEST / WORST --------
    if "best" in q or "undervalued" in q:
        st.sidebar.write(
            f"""
            🏆 **Best Value Neighbourhood**  
            📍 {best_neighbourhood['neighbourhood']} ({best_neighbourhood['neighbourhood_group']})  
            ⭐ Value Score: {best_neighbourhood['value_score']:.2f}
            """
        )

    elif "worst" in q or "overpriced" in q:
        st.sidebar.write(
            f"""
            ⚠️ **Most Overpriced Neighbourhood**  
            📍 {worst_neighbourhood['neighbourhood']} ({worst_neighbourhood['neighbourhood_group']})  
            ⭐ Value Score: {worst_neighbourhood['value_score']:.2f}
            """
        )

    # -------- BOROUGH-SPECIFIC QUESTIONS --------
    elif "manhattan" in q:
        score = borough_avg["Manhattan"]
        st.sidebar.write(
            f"""
            🏙️ **Manhattan Insight**  
            • Highest prices in NYC  
            • Avg Value Score: {score:.2f}  
            • Often overpriced relative to availability
            """
        )

    elif "queens" in q:
        score = borough_avg["Queens"]
        st.sidebar.write(
            f"""
            🗺️ **Queens Insight**  
            • Best overall value borough  
            • Avg Value Score: {score:.2f}  
            • High availability at moderate prices
            """
        )

    elif "brooklyn" in q:
        score = borough_avg["Brooklyn"]
        st.sidebar.write(
            f"""
            🎨 **Brooklyn Insight**  
            • Mixed pricing behaviour  
            • Avg Value Score: {score:.2f}  
            • Some neighbourhoods undervalued, others overpriced
            """
        )

    elif "bronx" in q:
        score = borough_avg["Bronx"]
        st.sidebar.write(
            f"""
            🏘️ **Bronx Insight**  
            • Lower prices than Manhattan  
            • Avg Value Score: {score:.2f}  
            • Good value in several neighbourhoods
            """
        )

    elif "staten island" in q:
        score = borough_avg["Staten Island"]
        st.sidebar.write(
            f"""
            🌊 **Staten Island Insight**  
            • High availability, fewer listings  
            • Avg Value Score: {score:.2f}  
            • Niche value, limited demand
            """
        )

    # -------- HELP / FALLBACK --------
    else:
        st.sidebar.write(
            """
            🤔 I can help with:
            • Best or worst neighbourhood  
            • Borough insights (Manhattan, Queens, Brooklyn, Bronx, Staten Island)  
            • Undervalued or overpriced areas  

            👉 Try: *"best value area"* or *"Queens insight"*
            """
        )
