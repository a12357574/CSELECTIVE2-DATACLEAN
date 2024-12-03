import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="VisWalis", page_icon="🧹", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kaushan+Script&family=Ubuntu+Sans:ital,wght@0,100..800;1,100..800&display=swap');
        [data-testid="stAppViewContainer"], .css-1outpf7 {
            background-color: #F5F5F5;
            color: black;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
            color: black !important;
        }

        .separator-line {
            border-top: 2px solid #2C6777;
            margin: 20px 0;
        }

        .logo-text {
            display: flex;
            vertical-align: bottom;
            line-height: 2.15;
        }

        .logo {
            width: 50px;
            margin-right: 10px;
        }

        .viswalis-text {
            font-family: "Kaushan Script", cursive;
            font-weight: 400;
            font-size: 40px;
            font-style: normal;
            color: #2C6777;
        }
        .ubuntu-sans{
            font-family: "Ubuntu Sans", sans-serif;
            font-weight: bold;
            font-size: 23px;
            }
        .ubuntu-sans2{
            font-family: "Ubuntu Sans", sans-serif;
            font-weight: 400;
            font-size: 16px;
            }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:

    st.image("VisWalis-logo.png", width=220)
    st.write('<p class ="ubuntu-sans">🧹Brushing Off the Mess, 🌟Visualizing Success!</p>', unsafe_allow_html=True)
    st.write('<p class ="ubuntu-sans2">VisWalis simplifies data analysis. Upload a CSV, let us clean it, and explore interactive visualizations.</p>', unsafe_allow_html=True)
    st.markdown('<div class="separator-line"></div>', unsafe_allow_html=True)
    st.write("### Upload a CSV file")
    
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type="csv", help="Limit 200MB per file • CSV")

def clean_data(df):
    """Applies basic data cleaning techniques."""
    df = df.copy()

    # 1. Remove completely empty rows
    df.dropna(how="all", inplace=True)

    # 2. Remove duplicates
    df.drop_duplicates(inplace=True)

    # 3. Handle missing values
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            # Fill numeric columns with the mean
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # Fill categorical columns with the mode
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)

    # 4. Remove outliers using IQR
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    # 5. Trim whitespace from strings
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        df[col] = df[col].str.strip()

    # 6. Checkng for correct data types
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(0, inplace=True)  # Replace any coerced NaN with 0
    
    # 7. Reset index for consistency in display
    df.reset_index(drop=True, inplace=True)
    
    return df

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df_cleaned = clean_data(df)
        
        st.write("## Cleaned Data")
        st.dataframe(df_cleaned, use_container_width=True)

        st.download_button(
            label="Download Cleaned CSV",
            data=df_cleaned.to_csv(index=False),
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

        st.write("## Visualizations")
        chart_type = st.selectbox(
            "Choose a chart type:", 
            ["Pie Chart", "Area Chart", "Donut Chart", "Radar Chart", "Gauge Chart"]
        )

        if chart_type == "Pie Chart":
            column = st.selectbox("Select a column for the pie chart:", df_cleaned.columns)
            fig = px.pie(df_cleaned, names=column, title="Pie Chart")
            st.plotly_chart(fig)

        elif chart_type == "Area Chart":
            numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
            y_cols = st.multiselect("Select columns for the Y-axis:", numeric_cols)
            x_col = st.selectbox("Select a column for the X-axis:", df_cleaned.columns)

            if y_cols:
                fig = px.area(df_cleaned, x=x_col, y=y_cols, title="Area Chart")
                st.plotly_chart(fig)
            else:
                st.warning("Please select at least one column for the Y-axis.")

        elif chart_type == "Donut Chart":
            column = st.selectbox("Select a column for the donut chart:", df_cleaned.columns)
            fig = px.pie(df_cleaned, names=column, hole=0.4, title="Donut Chart")
            st.plotly_chart(fig)

        elif chart_type == "Radar Chart":
            numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
            selected_cols = st.multiselect("Select columns for the radar chart:", numeric_cols)

            if selected_cols:
                fig = go.Figure()
                for col in selected_cols:
                    fig.add_trace(go.Scatterpolar(r=df_cleaned[col], theta=df_cleaned.index, name=col))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    title="Radar Chart"
                )
                st.plotly_chart(fig)
            else:
                st.warning("Please select at least one column for the radar chart.")

        elif chart_type == "Gauge Chart":
            numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
            selected_cols = st.multiselect("Select columns for the gauge chart:", numeric_cols)

            if selected_cols:
                fig = go.Figure()
                for col in selected_cols:
                    value = df_cleaned[col].mean()
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=value,
                        title={"text": col},
                        domain={'x': [0.1, 0.9], 'y': [0.1, 0.9]}
                    ))
                fig.update_layout(
                    title="Gauge Chart",
                    height=400 * len(selected_cols)
                )
                st.plotly_chart(fig)
            else:
                st.warning("Please select at least one column for the gauge chart.")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a CSV file to get started.")
