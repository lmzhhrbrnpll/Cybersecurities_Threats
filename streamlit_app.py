import streamlit as st
import pandas as pd


# --- PAGE CONFIGURATION ---
st.set_page_config(
   page_title="Cybersecurities Threats Data Analysis",
   layout="wide",
   initial_sidebar_state="expanded",
)

# --- DATA LOADING ---
# Using st.cache_data to avoid reloading data on every interaction
@st.cache_data
def load_data():
   """Loads the dataset"""
   df = pd.read_csv('/workspaces/Cybersecurities_Threats/data/cybersecurity_threats.csv')
   # Drop rows with missing values for simplicity in this demo
   df.dropna(inplace=True)
   return df


df = load_data()


st.title("🌏 Global Cybersecurity Threats")
def justified_text(text):
    st.markdown(
        f"""
        <div style='text-align: justify; text-justify: inter-word; line-height: 1.6;'>
        {text}
        </div>
        """,
        unsafe_allow_html=True
    )

justified_text(
    "In an increasingly interconnected world, understanding the dynamic landscape of cyber threats is not just an option—it's a necessity. This live dashboard provides a data-driven snapshot of the most pressing cybersecurity threats facing organizations and individuals globally. Explore the data, understand the trends, and fortify your digital defenses."
)

# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Filter Data")

# Filter for country
countries = st.sidebar.multiselect(
    "Select Countries",
    options=df["Country"].unique(),
    default=df["Country"].unique()[:3]  # Default to first 3 countries
)

# Filter for attack type
attack_types = st.sidebar.multiselect(
    "Select Attack Types",
    options=df["Attack Type"].unique(),
    default=df["Attack Type"].unique()
)

# Filter for target industry
industries = st.sidebar.multiselect(
    "Select Target Industries",
    options=df["Target Industry"].unique(),
    default=df["Target Industry"].unique()[:3]
)

# Filter for attack source
attack_sources = st.sidebar.multiselect(
    "Select Attack Sources",
    options=df["Attack Source"].unique(),
    default=df["Attack Source"].unique()
)

# Filter for year range
df['Year'] = pd.to_datetime(df['Year']).dt.year
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter for financial loss
min_loss, max_loss = float(df["Financial Loss (in Million $)"].min()), float(df["Financial Loss (in Million $)"].max())
loss_range = st.sidebar.slider(
    "Select Financial Loss Range (Million $)",
    min_value=min_loss,
    max_value=max_loss,
    value=(min_loss, max_loss)
)

# --- FILTERING THE DATAFRAME ---
df_selection = df.copy()

# Apply filters
if countries:
    df_selection = df_selection[df_selection["Country"].isin(countries)]
if attack_types:
    df_selection = df_selection[df_selection["Attack Type"].isin(attack_types)]
if industries:
    df_selection = df_selection[df_selection["Target Industry"].isin(industries)]
if attack_sources:
    df_selection = df_selection[df_selection["Attack Source"].isin(attack_sources)]

# Apply range filters
df_selection = df_selection[
    (df_selection["Year"] >= year_range[0]) & 
    (df_selection["Year"] <= year_range[1]) &
    (df_selection["Financial Loss (in Million $)"] >= loss_range[0]) & 
    (df_selection["Financial Loss (in Million $)"] <= loss_range[1])
]

# Display error message if no data is selected
if df_selection.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# --- MAIN PAGE CONTENT ---
st.subheader("📊 Key Metrics")

# --- DISPLAY KEY METRICS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_incidents = df_selection.shape[0]
    st.metric(label="Total Incidents", value=total_incidents)
with col2:
    total_loss = round(df_selection["Financial Loss (in Million $)"].sum(), 2)
    st.metric(label="Total Financial Loss (Million $)", value=total_loss)
with col3:
    avg_loss = round(df_selection["Financial Loss (in Million $)"].mean(), 2)
    st.metric(label="Average Loss per Incident (Million $)", value=avg_loss)
with col4:
    total_users = df_selection["Number of Affected Users"].sum()
    st.metric(label="Total Affected Users", value=f"{total_users:,}")

st.markdown("---")

# --- VISUALIZATIONS ---
st.subheader("📈 Visualizations")

# Arrange charts in columns
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    # Attack types distribution
    st.subheader("Attack Types Distribution")
    attack_type_counts = df_selection['Attack Type'].value_counts()
    st.bar_chart(attack_type_counts)

with viz_col2:
    # Financial loss by country
    st.subheader("Total Financial Loss by Country")
    loss_by_country = df_selection.groupby('Country')['Financial Loss (in Million $)'].sum().sort_values(ascending=False)
    st.bar_chart(loss_by_country)

# Second row of visualizations
viz_col3, viz_col4 = st.columns(2)

with viz_col3:
    # Target industries most affected
    st.subheader("Most Affected Industries")
    industry_counts = df_selection['Target Industry'].value_counts().head(10)
    st.bar_chart(industry_counts)

with viz_col4:
    # Attack sources distribution
    st.subheader("Attack Sources Distribution")
    source_counts = df_selection['Attack Source'].value_counts()
    
    # Display as table since pie chart is not available in native Streamlit
    st.dataframe(source_counts, use_container_width=True)

# Time series analysis
st.subheader("Cyber Attacks Over Time")
yearly_attacks = df_selection.groupby('Year').size()
st.line_chart(yearly_attacks)

# Vulnerability analysis
st.subheader("Security Vulnerabilities")
vuln_counts = df_selection['Security Vulnerability Type'].value_counts()
st.bar_chart(vuln_counts)

# Defense mechanisms effectiveness
st.subheader("Defense Mechanisms Used")
defense_counts = df_selection['Defense Mechanism Used'].value_counts()
st.bar_chart(defense_counts)

# Resolution time analysis
st.subheader("Incident Resolution Time Analysis")
resolution_stats = df_selection['Incident Resolution Time (in Hours)'].describe()

col5, col6, col7 = st.columns(3)
with col5:
    st.metric("Average Resolution Time", f"{resolution_stats['mean']:.2f} hours")
with col6:
    st.metric("Median Resolution Time", f"{resolution_stats['50%']:.2f} hours")
with col7:
    st.metric("Longest Resolution Time", f"{resolution_stats['max']:.2f} hours")


# Additional insights
st.subheader("🔍 Additional Insights")

# Top 5 most costly incidents
st.write("**Top 5 Most Costly Incidents:**")
top_costly = df_selection.nlargest(5, 'Financial Loss (in Million $)')[['Country', 'Attack Type', 'Target Industry', 'Financial Loss (in Million $)']]
st.dataframe(top_costly, use_container_width=True)

# Attack type vs financial loss
st.write("**Average Financial Loss by Attack Type:**")
avg_loss_by_attack = df_selection.groupby('Attack Type')['Financial Loss (in Million $)'].mean().sort_values(ascending=False)
st.dataframe(avg_loss_by_attack.round(2), use_container_width=True)

# Country analysis
st.write("**Incidents by Country:**")
country_analysis = df_selection['Country'].value_counts()
st.dataframe(country_analysis, use_container_width=True)

# --- DISPLAY RAW DATA ---
with st.expander("View Filtered Data"):
    st.dataframe(df_selection)
    st.markdown(f"**Data Dimensions:** {df_selection.shape[0]} rows, {df_selection.shape[1]} columns")
