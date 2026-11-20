
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Analytics Studio",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# 2. GREEN AND WHITE THEME
# ==================================================

st.markdown("""
<style>
/* Main page */
.stApp {
    background-color: #F4F9F5;
    color: #1F2937;
}

/* Make regular text readable throughout the main page */
.stApp, .stApp p, .stApp label, .stApp li,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stCaptionContainer"] {
    color: #374151;
}

.stApp [data-testid="stCaptionContainer"] {
    color: #596579 !important;
    opacity: 1 !important;
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #14532D;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #14532D;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* Titles */
.main-title {
    color: #14532D;
    font-size: 36px;
    font-weight: 800;
}

.section-title {
    color: #14532D;
    font-size: 23px;
    font-weight: 750;
    padding: 10px 0;
    border-bottom: 2px solid #BBF7D0;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #BBF7D0;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: #4B5563 !important;
    opacity: 1 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #14532D !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    background-color: #15803D;
    color: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #15803D;
}

.stButton button:hover, .stDownloadButton button:hover {
    background-color: #166534;
    color: #FFFFFF;
    border-color: #166534;
}

/* Alerts and info panels */
[data-testid="stAlert"] p {
    color: #1F2937 !important;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. HELPER FUNCTIONS
# ==================================================

def section(title):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )


def format_number(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


def find_date_columns(data):
    date_columns = []

    for col in data.columns:

        if pd.api.types.is_datetime64_any_dtype(data[col]):
            date_columns.append(col)

        elif any(word in str(col).lower() for word in
                 ["date", "time", "timestamp"]):

            converted = pd.to_datetime(
                data[col], errors="coerce"
            )

            if converted.notna().sum() > 0:
                date_columns.append(col)

    return date_columns


def calculate_growth(data, metric):
    data = data.copy()

    previous = data[metric].shift(1)

    data["Growth %"] = np.where(
        previous != 0,
        ((data[metric] - previous) / previous.abs()) * 100,
        np.nan
    )

    return data


# ==================================================
# 4. HEADER
# ==================================================

st.markdown(
    '<div class="main-title">📊 Analytics Studio</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="main-subtitle">Upload your dataset and discover patterns, trends, '
    'performance metrics and business insights.</p>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 5. SIDEBAR
# ==================================================

st.sidebar.title("📊 Analytics Studio")
st.sidebar.write("Your Data Analysis Workspace")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

st.sidebar.divider()
st.sidebar.caption("Supported formats: CSV and XLSX")


# ==================================================
# 6. FILE UPLOAD
# ==================================================

if uploaded_file is None:

    st.info("👈 Upload a CSV or Excel file from the sidebar.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("📈 **Performance Analysis**")
        st.caption("Identify top-performing categories and items.")

    with col2:
        st.write("🔍 **Data Quality**")
        st.caption("Find missing values and duplicates.")

    with col3:
        st.write("💡 **Business Insights**")
        st.caption("Discover trends and patterns.")

    st.stop()


# ==================================================
# 7. READ DATA
# ==================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        try:
            df = pd.read_csv(uploaded_file)

        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                encoding="latin1"
            )

    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"Unable to read file: {e}")
    st.stop()


if df.empty:
    st.error("The uploaded file contains no data.")
    st.stop()


df = df.copy()
df.columns = df.columns.astype(str).str.strip()


# ==================================================
# 8. AUTOMATIC DATE DETECTION
# ==================================================

for col in df.columns:

    if any(word in col.lower() for word in
           ["date", "datetime", "timestamp"]):

        converted = pd.to_datetime(
            df[col], errors="coerce"
        )

        if converted.notna().sum() > 0:
            df[col] = converted


# ==================================================
# 9. DATASET OVERVIEW
# ==================================================

section("1. Dataset Overview")

total_rows = len(df)
total_columns = len(df.columns)
missing_total = int(df.isnull().sum().sum())
duplicate_total = int(df.duplicated().sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", f"{total_rows:,}")
col2.metric("Total Columns", f"{total_columns:,}")
col3.metric("Missing Values", f"{missing_total:,}")
col4.metric("Duplicate Rows", f"{duplicate_total:,}")

st.write("**Uploaded File:**", uploaded_file.name)

with st.expander("View Dataset Preview"):
    st.dataframe(
        df.head(100),
        use_container_width=True
    )


# ==================================================
# 10. DATA QUALITY ANALYSIS
# ==================================================

section("2. Data Quality Analysis")

complete_cells = df.size - missing_total

completeness = (
    complete_cells / df.size * 100
    if df.size else 0
)

duplicate_percentage = (
    duplicate_total / total_rows * 100
    if total_rows else 0
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Data Completeness",
        f"{completeness:.2f}%"
    )
    st.progress(int(completeness))

with col2:
    st.metric(
        "Duplicate Percentage",
        f"{duplicate_percentage:.2f}%"
    )


# Missing values

missing_df = df.isnull().sum().reset_index()
missing_df.columns = ["Column", "Missing Values"]

missing_df = missing_df[
    missing_df["Missing Values"] > 0
].sort_values(
    "Missing Values",
    ascending=False
)

if not missing_df.empty:

    st.write("**Missing Values by Column**")

    fig = px.bar(
        missing_df,
        x="Column",
        y="Missing Values",
        color_discrete_sequence=["#16A34A"],
        title="Missing Values Analysis"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        missing_df,
        use_container_width=True
    )

else:
    st.success("No missing values found.")


# Duplicate analysis

duplicate_data = pd.DataFrame({
    "Type": ["Unique Records", "Duplicate Records"],
    "Records": [
        total_rows - duplicate_total,
        duplicate_total
    ]
})

fig = px.pie(
    duplicate_data,
    names="Type",
    values="Records",
    hole=0.5,
    title="Unique vs Duplicate Records",
    color_discrete_sequence=["#16A34A", "#BBF7D0"]
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 11. COLUMN INFORMATION
# ==================================================

section("3. Column Information")

column_info = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [str(df[col].dtype) for col in df.columns],
    "Unique Values": [df[col].nunique() for col in df.columns],
    "Missing Values": [df[col].isnull().sum() for col in df.columns]
})

st.dataframe(
    column_info,
    use_container_width=True
)


# ==================================================
# 12. COLUMN CLASSIFICATION
# ==================================================

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

categorical_columns = df.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

date_columns = find_date_columns(df)

col1, col2, col3 = st.columns(3)

col1.metric("Numerical Columns", len(numeric_columns))
col2.metric("Categorical Columns", len(categorical_columns))
col3.metric("Date Columns", len(date_columns))


# ==================================================
# 13. CATEGORY ANALYSIS
# ==================================================

section("4. Category Analysis")

if categorical_columns:

    selected_category = st.selectbox(
        "Choose a category column",
        categorical_columns
    )

    category_counts = (
        df[selected_category]
        .dropna()
        .astype(str)
        .value_counts()
        .head(10)
    )

    if not category_counts.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Most Frequent Value",
            str(category_counts.index[0])
        )

        col2.metric(
            "Number of Records",
            f"{int(category_counts.iloc[0]):,}"
        )

        top_counts = category_counts.rename(
            "Records"
        ).reset_index()

        top_counts.columns = [
            selected_category,
            "Records"
        ]

        fig = px.bar(
            top_counts,
            x=selected_category,
            y="Records",
            color="Records",
            color_continuous_scale="Greens",
            title=f"Top 10 Values - {selected_category}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            top_counts,
            use_container_width=True
        )

    else:
        st.info("No category values available.")

else:
    st.info("No categorical columns detected.")


# ==================================================
# 14. DEMOGRAPHIC ANALYSIS
# ==================================================

section("5. Demographic Analysis")

person_keywords = [
    "person", "offender", "victim", "customer",
    "employee", "user", "gender", "age",
    "race", "name", "client"
]

person_columns = [
    col for col in df.columns
    if any(word in col.lower() for word in person_keywords)
]

if person_columns:

    selected_person = st.selectbox(
        "Select a demographic column",
        person_columns
    )

    person_counts = (
        df[selected_person]
        .dropna()
        .astype(str)
        .value_counts()
        .head(10)
    )

    if not person_counts.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Most Frequent Value",
            str(person_counts.index[0])
        )

        col2.metric(
            "Record Count",
            f"{int(person_counts.iloc[0]):,}"
        )

        person_data = person_counts.rename(
            "Records"
        ).reset_index()

        person_data.columns = [
            selected_person,
            "Records"
        ]

        fig = px.bar(
            person_data,
            x=selected_person,
            y="Records",
            color_discrete_sequence=["#15803D"],
            title=f"Demographic Distribution - {selected_person}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No available values in this column.")

else:
    st.info("No demographic columns detected.")

st.caption(
    "This section describes patterns in the uploaded data. "
    "It does not establish individual behaviour or causation."
)


# ==================================================
# 15. METRICS & PERFORMANCE ANALYSIS
# ==================================================

section("6. Metrics & Performance Analysis")

if numeric_columns:

    selected_numeric = st.selectbox(
        "Choose a numerical metric",
        numeric_columns
    )

    numeric_data = pd.to_numeric(
        df[selected_numeric],
        errors="coerce"
    ).dropna()

    if not numeric_data.empty:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total",
            format_number(numeric_data.sum())
        )

        col2.metric(
            "Average",
            format_number(numeric_data.mean())
        )

        col3.metric(
            "Median",
            format_number(numeric_data.median())
        )

        col4.metric(
            "Maximum",
            format_number(numeric_data.max())
        )

        fig = px.histogram(
            numeric_data,
            x=selected_numeric,
            title=f"Distribution of {selected_numeric}",
            color_discrete_sequence=["#16A34A"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No valid numerical values found.")

else:
    st.info("No numerical columns detected.")


# ==================================================
# 16. PERFORMANCE COMPARISON
# ==================================================

section("7. Performance Comparison")

if categorical_columns and numeric_columns:

    col1, col2 = st.columns(2)

    with col1:

        performance_category = st.selectbox(
            "Select category or item",
            categorical_columns,
            key="performance_category"
        )

    with col2:

        performance_metric = st.selectbox(
            "Select numerical metric",
            numeric_columns,
            key="performance_metric"
        )

    aggregation = st.radio(
        "Choose calculation",
        ["Sum", "Average", "Count"],
        horizontal=True
    )

    if aggregation == "Sum":

        performance_data = df.groupby(
            performance_category,
            dropna=True
        )[performance_metric].sum()

        metric_name = "Total"

    elif aggregation == "Average":

        performance_data = df.groupby(
            performance_category,
            dropna=True
        )[performance_metric].mean()

        metric_name = "Average"

    else:

        performance_data = df.groupby(
            performance_category,
            dropna=True
        )[performance_metric].count()

        metric_name = "Count"

    performance_data = performance_data.sort_values(
        ascending=False
    ).head(10)

    if not performance_data.empty:

        performance_df = performance_data.rename(
            metric_name
        ).reset_index()

        best_item = performance_df.iloc[0][
            performance_category
        ]

        best_value = performance_df.iloc[0][metric_name]

        col1, col2 = st.columns(2)

        col1.metric(
            "Top Performing Category",
            str(best_item)
        )

        col2.metric(
            "Performance",
            format_number(best_value)
        )

        fig = px.bar(
            performance_df,
            x=performance_category,
            y=metric_name,
            color=metric_name,
            color_continuous_scale="Greens",
            title=f"Performance by {performance_category}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            performance_df,
            use_container_width=True
        )

    else:
        st.info("No comparison data available.")

else:
    st.info(
        "This analysis needs categorical and numerical columns."
    )


# ==================================================
# 17. CONTRIBUTION ANALYSIS
# ==================================================

section("8. Contribution Analysis")

if categorical_columns and numeric_columns:

    contribution_category = st.selectbox(
        "Choose category",
        categorical_columns,
        key="contribution_category"
    )

    contribution_metric = st.selectbox(
        "Choose metric",
        numeric_columns,
        key="contribution_metric"
    )

    contribution = df.groupby(
        contribution_category,
        dropna=True
    )[contribution_metric].sum().sort_values(
        ascending=False
    )

    if not contribution.empty:

        contribution_total = contribution.sum()

        contribution_df = contribution.rename(
            "Value"
        ).reset_index()

        if contribution_total != 0:

            contribution_df["Contribution %"] = (
                contribution_df["Value"] /
                contribution_total * 100
            )

            if (contribution_df["Value"] >= 0).all():

                fig = px.pie(
                    contribution_df.head(10),
                    names=contribution_category,
                    values="Value",
                    hole=0.45,
                    title="Category Contribution",
                    color_discrete_sequence=px.colors.sequential.Greens
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                fig = px.bar(
                    contribution_df.head(10),
                    x=contribution_category,
                    y="Value",
                    title="Category Contribution",
                    color="Value",
                    color_continuous_scale="Greens"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.dataframe(
                contribution_df,
                use_container_width=True
            )

        else:
            st.info("Total value is zero.")

else:
    st.info(
        "Categorical and numerical columns are required."
    )


# ==================================================
# 18. TREND ANALYSIS - DAILY, WEEKLY AND MONTHLY
# ==================================================

section("9. Trend Analysis")

if date_columns and numeric_columns:

    col1, col2 = st.columns(2)

    with col1:

        trend_date = st.selectbox(
            "Select Date Column",
            date_columns,
            key="trend_date"
        )

    with col2:

        trend_metric = st.selectbox(
            "Select Metric",
            numeric_columns,
            key="trend_metric"
        )

    trend_df = df[[trend_date, trend_metric]].copy()

    trend_df[trend_date] = pd.to_datetime(
        trend_df[trend_date],
        errors="coerce"
    )

    trend_df[trend_metric] = pd.to_numeric(
        trend_df[trend_metric],
        errors="coerce"
    )

    trend_df = trend_df.dropna()

    if not trend_df.empty:

        # DAILY AGGREGATION

        daily_data = (
            trend_df
            .set_index(trend_date)[trend_metric]
            .resample("D")
            .sum()
            .reset_index()
        )

        # WEEKLY AGGREGATION

        weekly_data = (
            trend_df
            .set_index(trend_date)[trend_metric]
            .resample("W")
            .sum()
            .reset_index()
        )

        # MONTHLY AGGREGATION
        # "M" supports older Pandas versions too.

        monthly_data = (
            trend_df
            .set_index(trend_date)[trend_metric]
            .resample("M")
            .sum()
            .reset_index()
        )

        daily_data = calculate_growth(
            daily_data, trend_metric
        )

        weekly_data = calculate_growth(
            weekly_data, trend_metric
        )

        monthly_data = calculate_growth(
            monthly_data, trend_metric
        )

        # TREND OVERVIEW

        st.subheader("Trend Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Daily Records",
            f"{len(daily_data):,}"
        )

        col2.metric(
            "Weekly Records",
            f"{len(weekly_data):,}"
        )

        col3.metric(
            "Monthly Records",
            f"{len(monthly_data):,}"
        )

        st.divider()

        # DAILY TREND

        st.subheader("Daily Trend")

        fig_daily = px.line(
            daily_data,
            x=trend_date,
            y=trend_metric,
            markers=True,
            title=f"Daily {trend_metric} Trend",
            color_discrete_sequence=["#16A34A"],
            template="plotly_white"
        )

        fig_daily.update_layout(
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title=trend_metric
        )

        st.plotly_chart(
            fig_daily,
            use_container_width=True
        )

        if len(daily_data) >= 2:

            latest = daily_data.iloc[-1][trend_metric]
            previous = daily_data.iloc[-2][trend_metric]

            if previous != 0:

                growth = (
                    (latest - previous) /
                    abs(previous)
                ) * 100

                st.metric(
                    "Latest Day vs Previous Day",
                    format_number(latest),
                    delta=f"{growth:+.2f}%"
                )

        with st.expander("View Daily Trend Data"):

            st.dataframe(
                daily_data,
                use_container_width=True
            )

        st.divider()

        # WEEKLY TREND

        st.subheader("Weekly Trend")

        fig_weekly = px.line(
            weekly_data,
            x=trend_date,
            y=trend_metric,
            markers=True,
            title=f"Weekly {trend_metric} Trend",
            color_discrete_sequence=["#15803D"],
            template="plotly_white"
        )

        fig_weekly.update_layout(
            hovermode="x unified",
            xaxis_title="Week Ending",
            yaxis_title=trend_metric
        )

        st.plotly_chart(
            fig_weekly,
            use_container_width=True
        )

        if len(weekly_data) >= 2:

            latest = weekly_data.iloc[-1][trend_metric]
            previous = weekly_data.iloc[-2][trend_metric]

            if previous != 0:

                growth = (
                    (latest - previous) /
                    abs(previous)
                ) * 100

                st.metric(
                    "Latest Week vs Previous Week",
                    format_number(latest),
                    delta=f"{growth:+.2f}%"
                )

        with st.expander("View Weekly Trend Data"):

            st.dataframe(
                weekly_data,
                use_container_width=True
            )

        st.divider()

        # MONTHLY TREND

        st.subheader("Monthly Trend")

        fig_monthly = px.line(
            monthly_data,
            x=trend_date,
            y=trend_metric,
            markers=True,
            title=f"Monthly {trend_metric} Trend",
            color_discrete_sequence=["#166534"],
            template="plotly_white"
        )

        fig_monthly.update_layout(
            hovermode="x unified",
            xaxis_title="Month",
            yaxis_title=trend_metric
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )

        if len(monthly_data) >= 2:

            latest = monthly_data.iloc[-1][trend_metric]
            previous = monthly_data.iloc[-2][trend_metric]

            if previous != 0:

                growth = (
                    (latest - previous) /
                    abs(previous)
                ) * 100

                st.metric(
                    "Latest Month vs Previous Month",
                    format_number(latest),
                    delta=f"{growth:+.2f}%"
                )

        with st.expander("View Monthly Trend Data"):

            st.dataframe(
                monthly_data,
                use_container_width=True
            )

        # AUTOMATIC TREND INSIGHTS

        st.divider()

        st.subheader("Trend Insights")

        for period_name, period_data in [
            ("Daily", daily_data),
            ("Weekly", weekly_data),
            ("Monthly", monthly_data)
        ]:

            if len(period_data) >= 2:

                first_value = period_data.iloc[0][trend_metric]
                last_value = period_data.iloc[-1][trend_metric]

                if first_value != 0:

                    total_change = (
                        (last_value - first_value) /
                        abs(first_value)
                    ) * 100

                    if total_change > 0:

                        st.success(
                            f"{period_name}: {trend_metric} increased "
                            f"by {total_change:.2f}% from the first "
                            f"to the last available period."
                        )

                    elif total_change < 0:

                        st.warning(
                            f"{period_name}: {trend_metric} decreased "
                            f"by {abs(total_change):.2f}% from the first "
                            f"to the last available period."
                        )

                    else:

                        st.info(
                            f"{period_name}: No overall change "
                            f"between the first and last period."
                        )

    else:

        st.warning(
            "No valid date and numerical values available."
        )

else:

    st.info(
        "Trend Analysis requires at least one date column "
        "and one numerical column."
    )


# ==================================================
# 19. OUTLIER DETECTION
# ==================================================

section("10. Outlier Detection")

if numeric_columns:

    outlier_col = st.selectbox(
        "Choose column for outlier detection",
        numeric_columns,
        key="outlier_col"
    )

    outlier_values = pd.to_numeric(
        df[outlier_col],
        errors="coerce"
    ).dropna()

    if len(outlier_values) >= 4:

        q1 = outlier_values.quantile(0.25)
        q3 = outlier_values.quantile(0.75)

        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = outlier_values[
            (outlier_values < lower_limit) |
            (outlier_values > upper_limit)
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric("Outliers", f"{len(outliers):,}")
        col2.metric("Lower Limit", format_number(lower_limit))
        col3.metric("Upper Limit", format_number(upper_limit))

        fig = px.box(
            outlier_values,
            y=outlier_col,
            title=f"Outlier Analysis - {outlier_col}",
            color_discrete_sequence=["#16A34A"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        if not outliers.empty:

            st.write("**Outlier Values**")

            st.dataframe(
                outliers.to_frame(name=outlier_col),
                use_container_width=True
            )

        else:
            st.success("No outliers detected using the IQR method.")

    else:
        st.info("At least four numerical values are required.")

else:
    st.info("No numerical columns available.")


# ==================================================
# 20. AUTOMATIC BUSINESS INSIGHTS
# ==================================================

section("11. Automatic Business Insights")

insights = []

insights.append(
    f"The dataset contains {total_rows:,} records "
    f"and {total_columns:,} columns."
)

insights.append(
    f"Data completeness is {completeness:.2f}%."
)

if duplicate_total > 0:

    insights.append(
        f"{duplicate_total:,} duplicate rows were detected. "
        "Review them before analysis."
    )

else:

    insights.append("No duplicate rows were detected.")

if not missing_df.empty:

    highest_missing = missing_df.iloc[0]["Column"]

    highest_missing_count = missing_df.iloc[0]["Missing Values"]

    insights.append(
        f"'{highest_missing}' has the highest number of missing "
        f"values ({highest_missing_count:,})."
    )

if categorical_columns:

    for col in categorical_columns[:5]:

        values = (
            df[col]
            .dropna()
            .astype(str)
            .value_counts()
        )

        if not values.empty:

            insights.append(
                f"In '{col}', the most frequent value is "
                f"'{values.index[0]}' with {values.iloc[0]:,} records."
            )

if numeric_columns:

    for col in numeric_columns[:5]:

        values = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        if not values.empty:

            insights.append(
                f"'{col}' has an average of {values.mean():,.2f} "
                f"and a total of {values.sum():,.2f}."
            )

for i, insight in enumerate(insights, start=1):

    st.markdown(f"**{i}.** {insight}")


# ==================================================
# 21. DOWNLOAD CLEANED DATASET
# ==================================================

section("12. Download Cleaned Dataset")

st.write(
    "This download removes exact duplicate rows. "
    "Missing values are not automatically changed."
)

cleaned_df = df.drop_duplicates()

st.metric(
    "Records After Removing Duplicates",
    f"{len(cleaned_df):,}"
)

csv_data = cleaned_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Cleaned CSV",
    data=csv_data,
    file_name="cleaned_dataset.csv",
    mime="text/csv"
)


# ==================================================
# 22. FINAL SUMMARY
# ==================================================

section("13. Final Dataset Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric(
    "Original Records",
    f"{total_rows:,}"
)

summary_col2.metric(
    "Cleaned Records",
    f"{len(cleaned_df):,}"
)

summary_col3.metric(
    "Removed Duplicates",
    f"{total_rows - len(cleaned_df):,}"
)

st.success(
    "Your dataset analysis is complete. "
    "Explore the sections above to identify patterns and insights."
)

st.caption("Analytics Studio | Data Analysis Workspace")
