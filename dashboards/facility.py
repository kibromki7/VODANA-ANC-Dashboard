import streamlit as st
from api_handler import fetch_data
import pandas as pd
from datetime import date
import plotly.express as px
import numpy as np



def apply_custom_checkbox_styles():
    """Apply custom CSS for sidebar checkbox visibility and styling."""
    st.markdown(
        """
        <style>
            /* Change color of checkbox labels in the sidebar */
            .stSidebar .stCheckbox > label {
                color: #ffffff;  /* White color for better visibility */
                font-size: 16px;  /* Font size for readability */
            }

            /* Change checkbox itself color */
            .stSidebar .stCheckbox input[type="checkbox"] {
                background-color: #264653;  /* Dark background color for checkboxes */
                border-color: #ffffff;  /* White border color */
            }

            /* Change checkbox color on hover */
            .stSidebar .stCheckbox input[type="checkbox"]:hover {
                background-color: #2a9d8f;  /* Teal color on hover */
            }
        </style>
        """,
        unsafe_allow_html=True
    )



# Helper function to extract facility name columns dynamically
def get_facility_columns(df):
    return [col for col in df.columns if col.startswith("health_facility_name")]

# Helper function to extract date columns dynamically
def get_date_columns(df):
    return [col for col in df.columns if col.startswith("date_of_visit")]

# Helper function to filter data by date range
def filter_data_by_date(df, date_columns, start_date, end_date):
    filtered_data = pd.DataFrame()
    for col in date_columns:
        if col in df.columns:
            temp_data = df[(df[col] >= start_date) & (df[col] <= end_date)]
            filtered_data = pd.concat([filtered_data, temp_data])
    return filtered_data

# Helper function to create pie chart
def create_pie_chart(data, condition_columns, condition_name):
    # Flatten the data from the multiple columns (e.g., vodan_syphilis_v1, vodan_syphilis_v2, ...)
    combined_data = pd.concat([data[col] for col in condition_columns if col in data.columns], axis=0, ignore_index=True)
    combined_data.replace("", np.nan, inplace=True)
    # Drop NaN values (not relevant for analysis)
    combined_data = combined_data.dropna()
    
    # Count occurrences of each value (e.g., Positive, Negative, etc.)
    condition_counts = combined_data.value_counts()

    # Plot pie chart
    fig = px.pie(
        names=condition_counts.index, 
        values=condition_counts.values, 
        title=f"Distribution of {condition_name} Visits",
        labels={str(val): str(val) for val in condition_counts.index}
    )
    return fig

# Helper function to filter and categorize visits by mother's age
def visits_by_age_group(data):
    st.markdown(
    f"""
    <h3 style="text-align: center;">Total Visits by Age Group</h3>
    """, 
    unsafe_allow_html=True
    )


    # Define age groups
    age_bins = [10, 15, 20, 100]  # 10-14, 15-19, 20+
    age_labels = ["10-14", "15-19", "20+"]
    
    # Identify age columns dynamically
    age_columns = [col for col in data.columns if col.startswith("vodan_motherage_v")]

    if age_columns:
        # Combine all age columns into one for analysis
        combined_ages = pd.concat([data[col] for col in age_columns], axis=0, ignore_index=True)

        # Convert combined ages to numeric, coercing invalid values to NaN
        combined_ages = pd.to_numeric(combined_ages, errors="coerce")
        
        # Drop rows where age is NaN
        combined_ages = combined_ages.dropna()

        # Create a DataFrame for analysis
        age_data = pd.DataFrame({"age": combined_ages})

        # Create age groups
        age_data["age_group"] = pd.cut(age_data["age"], bins=age_bins, labels=age_labels, right=False)

        # Count visits by age group
        age_counts = age_data["age_group"].value_counts().sort_index()
        col11, col12, col13 = st.columns(3)
        
        with col11:
            st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Age Group 10-14</div>
                <div class="value">{age_counts.get("10-14", 0)}</div>
                </div>
                <div class="icon">🤰🏾</div>
                </div>
                """,
                unsafe_allow_html=True
                )

        with col12:
            st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Age Group 15-19</div>
                <div class="value">{age_counts.get("15-19", 0)}</div>
                </div>
                <div class="icon">🫄🏾</div>
                </div>
                """,
                unsafe_allow_html=True
                )
          
        with col13:
            st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Age Group 20+</div>
                <div class="value">{age_counts.get("20+", 0)}</div>
                </div>
                <div class="icon">🫃🏾</div>
                </div>
                """,
                unsafe_allow_html=True
                )

        # Display pie chart
        st.markdown(
        f"""
        <h3 style="text-align: center;">Age Group Distribution (Pie Chart)</h3>
        """, 
        unsafe_allow_html=True
        )
        fig = px.pie(names=age_counts.index, values=age_counts.values, title="Visits by Age Group")
        st.plotly_chart(fig)

    else:
        st.warning("No age columns found in the dataset.")
def is_risky_mother(data, visit_suffix):
    try:
        # Convert age column to numeric, forcing errors to NaN
        age_column = pd.to_numeric(data[f"vodan_motherage_{visit_suffix}"], errors="coerce")

        return (
            (data[f"vodan_tuberculosistbscreening_{visit_suffix}"] == "Positive for TB1") |
            (data[f"vodan_hivstatus_{visit_suffix}"] == "1HIVpositive") |
            (age_column < 16) |
            (age_column > 40)
        )
    except KeyError:
        # Handles cases where the column might not exist
        return pd.Series(False, index=data.index)# Facility-level dashboard
def render_facility_dashboard(user, api_token):
    #apply_custom_checkbox_styles()
    #st.header(f"Dashboard for: {user['facility']}")
    df = fetch_data(api_token)


    facility_name = user['facility'] 
    st.markdown(
        f"""
        <div class="header-container">
            <h1 class="header-title">Dashboard for <span style="color:yellow;"> {facility_name} </span></h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Extract facility columns
    facility_columns = get_facility_columns(df)

    # Filter data for the user's facility dynamically
    facility_data = pd.DataFrame()
    for col in facility_columns:
        if col in df.columns:
            temp_data = df[df[col] == user["facility"]]
            facility_data = pd.concat([facility_data, temp_data])

    if not facility_data.empty:
        # Extract relevant date columns
        date_columns = get_date_columns(facility_data)

        # Define date ranges for today, this month, and this year
        today = date.today()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        # Filter data for different time periods
        today_data = filter_data_by_date(facility_data, date_columns, today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        month_data = filter_data_by_date(facility_data, date_columns, start_of_month.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        year_data = filter_data_by_date(facility_data, date_columns, start_of_year.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        
        homepage=st.sidebar.button("Home")
        selected_day = st.sidebar.date_input("Select a Day", value=pd.Timestamp.today())

        # Sidebar option to show total visits by age group
        age_group_dashboard = st.sidebar.button("Total Visits by Age Group")
        show_health_conditions_pie = st.sidebar.button("Infectious Diseases")


        if age_group_dashboard:
            # If the checkbox is checked, only show the total visits by age group
            visits_by_age_group(facility_data)
        # Render pie charts for health conditions (syphilis, hepatitis B, hepatitis C
        # Render pie charts for health conditions (syphilis, hepatitis B, hepatitis C)
        elif show_health_conditions_pie:
            # Filter the data for the user's facility (no date range filtering)
            #facility_data = filter_data_by_date(facility_data, date_columns, "2020-01-01", "2024-12-31")  # You can remove this line for no date filtering
            # Extract the relevant columns for the health conditions
            syphilis_columns = [f"vodan_syphilis_v{i}" for i in range(1, 9)]  # Adjusted to check all syphilis columns
            hepatitis_b_columns = [f"vodan_hepatitisb_v{i}" for i in range(1, 9)]  # Adjusted to check all hepatitis B columns
            hepatitis_c_columns = [f"vodan_hepatitisc_v{i}" for i in range(1, 9)]  # Adjusted to check all hepatitis C columns
            HIV_columns = [f"vodan_hivstatus_v{i}" for i in range(1, 9)]  # Adjusted to check all hepatitis C columns
            TB_columns = [f"vodan_tuberculosistbscreening_v{i}" for i in range(1, 9)]  # Adjusted to check all hepatitis C columns
            # Create pie charts for each condition
            col31, col32, col33 = st.columns(3)
            with col31:
                st.subheader("Syphilis")
                syphilis_pie_chart = create_pie_chart(facility_data, syphilis_columns, "Syphilis")
                st.plotly_chart(syphilis_pie_chart)
            with col32:
                st.subheader("Hepatitis B")
                hepatitis_b_pie_chart = create_pie_chart(facility_data, hepatitis_b_columns, "Hepatitis B")
                st.plotly_chart(hepatitis_b_pie_chart)
            with col33:
                st.subheader("Hepatitis C")
                hepatitis_c_pie_chart = create_pie_chart(facility_data, hepatitis_c_columns, "Hepatitis C")
                st.plotly_chart(hepatitis_c_pie_chart)
            col34, col35 = st.columns(2)
            with col34:
                st.subheader("HIV")
                HIV_pie_chart = create_pie_chart(facility_data, HIV_columns, "HIV")
                st.plotly_chart(HIV_pie_chart)
            with col35:
                st.subheader("HIV")
                TB_pie_chart = create_pie_chart(facility_data, TB_columns, "TB")
                st.plotly_chart(TB_pie_chart)
        else:
            # If the checkbox is not checked, show the default visualizations
            # Display metrics for total visits
            date_columns = [col for col in facility_data.columns if col.startswith("date_of_visit_")]
            # Ensure all date columns are in datetime format
            for col in date_columns:
                facility_data[col] = pd.to_datetime(facility_data[col], errors='coerce')
                    # Count the total visits for the selected day across all date columns
            selected_day_visits = facility_data[date_columns].apply(lambda row: row.isin([pd.Timestamp(selected_day)]).sum(), axis=1).sum()

            
            visit_suffixes = [f"v{i}" for i in range(1, 9)]
            risky_mothers = set()  # Use a set to avoid double-counting mothers across visits
            for suffix in visit_suffixes:
                risky_mothers.update(facility_data[is_risky_mother(facility_data, suffix)].index)
                # Total number of unique risky mothers
            total_risky_mothers = len(risky_mothers)

            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Today's Total Visits</div>
                <div class="value">{len(today_data)}</div>
                </div>
                <div class="icon">&#128339;</div>
                </div>
                """,
                unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">This Month's Total Visits</div>
                <div class="value">{len(month_data)}</div>
                </div>
                <div class="icon">🫄🏾</div>
                </div>
                """,
                unsafe_allow_html=True
                )
            with col3:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">This Year's Total Visits</div>
                <div class="value">{len(year_data)}</div>
                </div>
                <div class="icon">🗓️</div>
                </div>
                """,
                unsafe_allow_html=True
                )
            
            col111, col112, col113 = st.columns(3)
            with col111:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Visits on Selected Day</div>
                <div class="value">{selected_day_visits}</div>
                </div>
                <div class="icon">&#128198;</div>
                </div>
                """,
                unsafe_allow_html=True
                )
                
            with col112:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Total Visits</div>
                <div class="value">{len(facility_data)}</div>
                </div>
                <div class="icon">&#128197;</div>
                </div>
                """,
                unsafe_allow_html=True
                )
            with col113:
                st.markdown(
                f"""
                <div class="metrics-box">
                <div class="text-container">
                <div class="title">Mothers Needing Follow-Up</div>
                <div class="value">{total_risky_mothers}</div>
                </div>
                <div class="icon">&#129658;</div>
                </div>
                """,
                unsafe_allow_html=True
                )

            # Visualization: Visits by visit number for today, this month, and this year
            #st.subheader("Visits by Visit Number")

            def visits_by_visit_number(data, title):
                visit_counts = data["redcap_event_name"].value_counts().sort_index().reset_index()
                #st.write(title)
                
                visit_counts.columns = ['Visit Number', 'Count']  # Rename columns for clarity

                fig_bar = px.bar(
                    visit_counts,
                    x='Visit Number',
                    y='Count',
                    color='Visit Number',  # Assign color based on the Visit Number
                    color_discrete_sequence=px.colors.qualitative.Set1,  # Choose a color palette
                    title=title,
                    labels={'Count': 'Count', 'Visit Number': 'Visit Number'},
                    width=800  # Increase width for bar chart
                )
                st.plotly_chart(fig_bar)

            col4, col5 = st.columns(2)
            with col4:
                visits_by_visit_number(today_data, "Today's Visits by Number")
            with col5:
                visits_by_visit_number(month_data, "This Month's Visits by Number")
            col6, col7 =st.columns(2)
            with col6:
                visits_by_visit_number(year_data, "This Year's Visits by Number")
            with col7:
                visits_by_visit_number(facility_data, "Total Visits by Number")

            # Visualization: Line chart for total visits day by day
            st.subheader("Total Visits Day by Day")
            def daily_visits(data):
                daily_counts = pd.DataFrame()
                for col in date_columns:
                    if col in data.columns:
                        temp = data[col].value_counts().reset_index()
                        temp.columns = ["date", "count"]
                        daily_counts = pd.concat([daily_counts, temp])

                daily_counts = daily_counts.groupby("date")["count"].sum().sort_index().reset_index()
                daily_counts["date"] = pd.to_datetime(daily_counts["date"])
                return daily_counts

            daily_data = daily_visits(facility_data)
            st.line_chart(daily_data.set_index("date"))

    else:
        st.warning("No data available for this facility.")