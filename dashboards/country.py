import streamlit as st
from api_handler import fetch_data
import pandas as pd
from datetime import date
import plotly.express as px
from PIL import Image
import numpy as np

# Helper function to extract country columns dynamically
def get_country_columns(df):
    return [col for col in df.columns if col.startswith("country")]

# Helper function to extract facility name columns dynamically
def get_facility_columns(df):
    return [col for col in df.columns if col.startswith("health_facility")]

# Helper function to extract date columns dynamically (for different versions)
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

# Function to show total visits by age group
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

        # Display as cards in three columns
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
        st.subheader("Age Group Distribution (Pie Chart)")
        fig = px.pie(names=age_counts.index, values=age_counts.values, title="Visits by Age Group")
        st.plotly_chart(fig)

    else:
        st.warning("No age columns found in the dataset.")
# Function to show syphilis distribution by country
def syphilis_distribution(data):
    #st.subheader("Syphilis Distribution by Country")

    # Identify syphilis columns dynamically
    syphilis_columns = [col for col in data.columns if col.startswith("vodan_syphilis_v")]

    if syphilis_columns:
        # Combine all syphilis columns into one for analysis
        combined_syphilis = pd.concat([data[col] for col in syphilis_columns], axis=0, ignore_index=True)
        combined_syphilis.replace("", np.nan, inplace=True)
        combined_syphilis = combined_syphilis.dropna()
        # Create a DataFrame for analysis
        syphilis_data = pd.DataFrame({"syphilis": combined_syphilis})

        # Count syphilis distribution
        syphilis_counts = syphilis_data["syphilis"].value_counts().sort_index()

        # Display pie chart
        fig = px.pie(names=syphilis_counts.index, values=syphilis_counts.values, title="Syphilis Distribution")
        st.plotly_chart(fig)

    else:
        st.warning("No syphilis columns found in the dataset.")

# Function to show Hepatitis B distribution by country
def hepatitis_b_distribution(data):
    #st.subheader("Hepatitis B Distribution by Country")

    # Identify hepatitis B columns dynamically
    hepatitis_b_columns = [col for col in data.columns if col.startswith("vodan_hepatitisb_v")]

    if hepatitis_b_columns:
        # Combine all Hepatitis B columns into one for analysis, filtering out null values
        combined_hepatitis_b = pd.concat([data[col] for col in hepatitis_b_columns], axis=0, ignore_index=True)
        combined_hepatitis_b.replace("", np.nan, inplace=True)
        # Drop NaN values to avoid them in the pie chart
        combined_hepatitis_b = combined_hepatitis_b.dropna()

        if not combined_hepatitis_b.empty:
            # Create a DataFrame for analysis
            hepatitis_b_data = pd.DataFrame({"hepatitis_b": combined_hepatitis_b})

            # Count Hepatitis B distribution
            hepatitis_b_counts = hepatitis_b_data["hepatitis_b"].value_counts().sort_index()

            # Display pie chart
            fig = px.pie(names=hepatitis_b_counts.index, values=hepatitis_b_counts.values, title="Hepatitis B Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("No valid Hepatitis B data found (all data may be NaN).")

    else:
        st.warning("No Hepatitis B columns found in the dataset.")

# Function to show Hepatitis C distribution by country
def hepatitis_c_distribution(data):
    #st.subheader("Hepatitis C Distribution by Country")

    # Identify hepatitis C columns dynamically
    hepatitis_c_columns = [col for col in data.columns if col.startswith("vodan_hepatitisc_v")]

    if hepatitis_c_columns:
        # Combine all Hepatitis C columns into one for analysis, filtering out null values
        combined_hepatitis_c = pd.concat([data[col] for col in hepatitis_c_columns], axis=0, ignore_index=True)
        combined_hepatitis_c.replace("", np.nan, inplace=True)
        # Drop NaN values to avoid them in the pie chart
        combined_hepatitis_c = combined_hepatitis_c.dropna()

        if not combined_hepatitis_c.empty:
            # Create a DataFrame for analysis
            hepatitis_c_data = pd.DataFrame({"hepatitis_c": combined_hepatitis_c})

            # Count Hepatitis C distribution
            hepatitis_c_counts = hepatitis_c_data["hepatitis_c"].value_counts().sort_index()

            # Display pie chart
            fig = px.pie(names=hepatitis_c_counts.index, values=hepatitis_c_counts.values, title="Hepatitis C Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("No valid Hepatitis C data found (all data may be NaN).")

    else:
        st.warning("No Hepatitis C columns found in the dataset.")

def HIV_distribution(data):
    #st.subheader("Hepatitis C Distribution by Country")

    # Identify hepatitis C columns dynamically
    HIV_columns = [col for col in data.columns if col.startswith("vodan_hivstatus_v")]

    if HIV_columns:
        # Combine all Hepatitis C columns into one for analysis, filtering out null values
        combined_HIV = pd.concat([data[col] for col in HIV_columns], axis=0, ignore_index=True)
        combined_HIV.replace("", np.nan, inplace=True)
        # Drop NaN values to avoid them in the pie chart
        combined_HIV = combined_HIV.dropna()

        if not combined_HIV.empty:
            # Create a DataFrame for analysis
            HIV_data = pd.DataFrame({"HIV": combined_HIV})

            # Count HIV distribution
            HIV_counts = HIV_data["HIV"].value_counts().sort_index()

            # Display pie chart
            fig = px.pie(names=HIV_counts.index, values=HIV_counts.values, title="HIV Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("No valid HIV data found (all data may be NaN).")

    else:
        st.warning("No HIV columns found in the dataset.")

def TB_distribution(data):
    #st.subheader("Hepatitis C Distribution by Country")

    # Identify hepatitis C columns dynamically
    TB_columns = [col for col in data.columns if col.startswith("vodan_tuberculosistbscreening_v")]

    if TB_columns:
        # Combine all Hepatitis C columns into one for analysis, filtering out null values
        combined_TB = pd.concat([data[col] for col in TB_columns], axis=0, ignore_index=True)
        combined_TB.replace("", np.nan, inplace=True)
        # Drop NaN values to avoid them in the pie chart
        combined_TB = combined_TB.dropna()

        if not combined_TB.empty:
            # Create a DataFrame for analysis
            TB_data = pd.DataFrame({"TB": combined_TB})

            # Count Hepatitis C distribution
            TB_counts = TB_data["TB"].value_counts().sort_index()

            # Display pie chart
            fig = px.pie(names=TB_counts.index, values=TB_counts.values, title="TB Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("No valid HIV data found (all data may be NaN).")

    else:
        st.warning("No HIV columns found in the dataset.")

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



# Function to render country-level dashboard
def render_country_dashboard(user, api_token):
    df = fetch_data(api_token)  # Fetch data using the provided API token
    country_name = user['country']  # Retrieve the user's country
    st.markdown(
        f"""
        <div class="header-container">
            <h1 class="header-title">Dashboard for <span style="color: yellow;">{country_name}</span></h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    country_columns = get_country_columns(df)

    # Filter data for the user's country dynamically
    country_data = pd.DataFrame()
    for col in country_columns:
        if col in df.columns:
            temp_data = df[df[col] == user['country']]
            country_data = pd.concat([country_data, temp_data])
    
    
    homepage=st.sidebar.button("Home")
    def country_main():
        country_columns = get_country_columns(df)
        date_columns = get_date_columns(country_data)
        today = date.today()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        today_data = filter_data_by_date(country_data, date_columns, today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        month_data = filter_data_by_date(country_data, date_columns, start_of_month.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        year_data = filter_data_by_date(country_data, date_columns, start_of_year.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        
        
        date_columns = [col for col in country_data.columns if col.startswith("date_of_visit_")]
        # Ensure all date columns are in datetime format
        for col in date_columns:
            country_data[col] = pd.to_datetime(country_data[col], errors='coerce')
                # Count the total visits for the selected day across all date columns
        selected_day_visits = country_data[date_columns].apply(lambda row: row.isin([pd.Timestamp(selected_day)]).sum(), axis=1).sum()
        
        visit_suffixes = [f"v{i}" for i in range(1, 9)]
        risky_mothers = set()  # Use a set to avoid double-counting mothers across visits
        for suffix in visit_suffixes:
            risky_mothers.update(country_data[is_risky_mother(country_data, suffix)].index)
            # Total number of unique risky mothers
        total_risky_mothers = len(risky_mothers)


        # Styling for metrics display
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
            <div class="icon">📉</div>
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
                <div class="value">{len(country_data)}</div>
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
            
        # Visualization for visits by visit number
        def visits_by_visit_number(data, title):
            visit_counts = data["redcap_event_name"].value_counts().sort_index().reset_index()
            visit_counts.columns = ['Visit Number', 'Count']
            fig = px.bar(visit_counts, x='Visit Number', y='Count', color='Visit Number', title=title, color_discrete_sequence=px.colors.qualitative.Set1, width=800)  # Increase width
            st.plotly_chart(fig)

        #st.subheader("Visits by Visit Number")
        col4, col5 = st.columns(2)
        with col4:
            visits_by_visit_number(today_data, "Today's Visits by Number")
        with col5:
            visits_by_visit_number(month_data, "This Month's Visits by Number")
            
        col6, col7 = st.columns(2)
        with col6:
            visits_by_visit_number(year_data, "This Year's Visits by Number")
        with col7:
            visits_by_visit_number(country_data, "Total Visits by Number")


        # Visualization for daily visits (handling dynamic date_of_visit_vX columns)
        def daily_visits(data):
            daily_counts = pd.DataFrame()
            for col in date_columns:
                if col in data.columns:
                    temp_counts = data[col].value_counts().reset_index()
                    temp_counts.columns = ['Date', 'Count']
                    temp_counts["Date"] = pd.to_datetime(temp_counts["Date"])
                    daily_counts = pd.concat([daily_counts, temp_counts])

            if not daily_counts.empty:
                daily_counts = daily_counts.groupby("Date")["Count"].sum().reset_index()
                return daily_counts
            return pd.DataFrame()

        st.subheader("Daily Visit Trend")
        daily_data = daily_visits(country_data)
        if not daily_data.empty:
            st.line_chart(daily_data.set_index("Date"))

    
    if not country_data.empty:
        # Extract relevant facility and date columns
        facility_columns = get_facility_columns(country_data)
        date_columns = get_date_columns(country_data)
        
        # Sidebar option for visits by age group
        selected_day = st.sidebar.date_input("Select a Day", value=pd.Timestamp.today())
        age_group_dashboard = st.sidebar.button("Total Visits by Age Group")
        health_status_dashboard = st.sidebar.button("Infectious Diseases")
        
        # Sidebar option to toggle facility-level dashboard
        facility_dashboard = st.sidebar.checkbox("Show Facility-Level Dashboard")
        
        if age_group_dashboard:
            visits_by_age_group(country_data)

        elif health_status_dashboard:
            # Create three columns for the pie charts
            col1, col2, col3 = st.columns(3)

            # Syphilis pie chart
            with col1:
                syphilis_distribution(country_data)

            # Hepatitis B pie chart
            with col2:
                hepatitis_b_distribution(country_data)

            # Hepatitis C pie chart
            with col3:
                hepatitis_c_distribution(country_data)
                
            col51, col52 = st.columns(2)
            with col51:
                HIV_distribution(country_data)
            with col52:
                TB_distribution(country_data)
        elif facility_dashboard:
            #st.subheader("Facility-Level Dashboard")
            def visits_by_facility(data, facility_columns, title):
                # Initialize an empty Series to store the count
                facility_counts = pd.Series(dtype=int)
                # Loop through the facility columns to count visits per facilit
                for col in facility_columns:
                    if col in data.columns:
                        # Filter out NaN or empty facility names
                        temp_data = data[data[col].notna() & (data[col] != '')]
                        temp_counts = temp_data[col].value_counts()
                        facility_counts = facility_counts.add(temp_counts, fill_value=0)
                        # Check if there is valid data for facility counts
                if not facility_counts.empty:
                    # Create columns for side-by-side layout
                    col1, col2 = st.columns(2)
                    # Plot bar chart for visits by facility
                    with col1:
                        fig_bar = px.bar(facility_counts.sort_index(), 
                             title=title,
                             labels={'value': 'Count', 'index': 'Facility'},
                             width=800)  # Increase width for bar chart
                        st.plotly_chart(fig_bar)
                        # Plot pie chart for visits by facility
                    with col2:
                        fig_pie = px.pie(facility_counts, 
                             names=facility_counts.index, 
                             values=facility_counts.values,
                             title="Total Visits by Facility")
                        st.plotly_chart(fig_pie)
                else:
                    st.warning("No valid data found for the selected facilities.")
                    # Example usage
            visits_by_facility(country_data, facility_columns, "Total Visits by Facility")

            #visits_by_facility(country_data, "Total Visits by Facility")

            st.subheader("Daily Visit Trends by Facility")
            st.sidebar.subheader("Select Facilities for Comparison")
            all_facilities = country_data[facility_columns].stack().unique()
            selected_facilities = st.sidebar.multiselect(
                "Choose Facilities to Compare", 
                options=all_facilities, 
                default=all_facilities[:3]
            )

            if selected_facilities:
                # Dynamically generate the line chart for selected facilities
                line_chart_data = daily_visit_trends(country_data, facility_columns, date_columns, selected_facilities)
                if line_chart_data is not None:
                    st.line_chart(line_chart_data)
                else:
                    st.warning("No valid data available for the selected facilities.")
            else:
                st.warning("Please select at least one facility to compare.")

        elif homepage:
            country_main()
        else:
            country_main()
        
            
            
    else:
        st.warning("No data available for this country.")

# Dynamically generate the line chart for daily visits by date (multiple date columns handling)
def daily_visit_trends(data, facility_columns, date_columns, selected_facilities):
    daily_counts = pd.DataFrame()

    for col in facility_columns:
        if col in data.columns:
            for facility in selected_facilities:
                temp = data[data[col] == facility]
                if not temp.empty:
                    # Process date columns to count visits per day
                    for date_col in date_columns:
                        if date_col in temp.columns:
                            melted_data = temp[[date_col]].melt(value_name="date").dropna()
                            melted_data["facility"] = facility
                            melted_data["count"] = 1
                            daily_counts = pd.concat([daily_counts, melted_data])

    if not daily_counts.empty:
        daily_counts["date"] = pd.to_datetime(daily_counts["date"])
        grouped = daily_counts.groupby(["date", "facility"])["count"].sum().reset_index()
        pivot_data = grouped.pivot(index="date", columns="facility", values="count").fillna(0)
        return pivot_data
    return None
