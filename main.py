import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="VisWalis", page_icon="🧹", layout="centered")

st.sidebar.image("VisWalis-logo.png", width=220)
st.sidebar.write("### Upload a CSV file")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type="csv", help="Limit 200MB per file • CSV")

def clean_data(df):
    """Applies basic data cleaning techniques."""
    df = df.copy()
    # 1. Remove Duplicates
    df.drop_duplicates(inplace=True)

    # 2. Handle missing values
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            # Fill numeric columns with the mean
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # Fill categorical columns with the mode
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)

    # 3. Remove outliers using IQR
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    # 4. Trim whitespace from strings
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        df[col] = df[col].str.strip()

    # 5. Checkng for correct data types
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(0, inplace=True)  # Replace any coerced NaN with 0
    
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
