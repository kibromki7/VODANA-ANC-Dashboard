import streamlit as st
from api_handler import fetch_data
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import numpy as np




# Helper function to extract country columns dynamically
def get_country_columns(df):
    # Assuming country columns start with "country" or similar prefix (update as per actual dataset)
    return [col for col in df.columns if col.startswith("country_")]

# Helper function to extract facility name columns dynamically
def get_facility_columns(df):
    # Assuming facility columns start with "health_facility" or similar prefix
    return [col for col in df.columns if col.startswith("health_facility_")]

# Helper function to extract date columns dynamically
def get_date_columns(df):
    # Assuming date columns start with "date_of_visit" or similar prefix
    return [col for col in df.columns if col.startswith("date_of_visit")]

# Helper function to filter data by date range
def filter_data_by_date(df, date_columns, start_date, end_date):
    filtered_data = pd.DataFrame()
    for col in date_columns:
        if col in df.columns:
            # Ensure we filter by dates that are in the right format
            temp_data = df[(df[col] >= start_date) & (df[col] <= end_date)]
            filtered_data = pd.concat([filtered_data, temp_data])
    return filtered_data

# Line chart for comparing countries
def daily_visit_trends(data, country_columns, date_columns, selected_countries):
    daily_counts = pd.DataFrame()

    for col in country_columns:
        if col in data.columns:
            # Filter out rows with missing or empty country values
            valid_data = data[data[col].notna() & (data[col] != '')]
            
            for country in selected_countries:
                temp = valid_data[valid_data[col] == country]
                if not temp.empty:
                    # Process date columns to count events (previously visits) per day
                    melted_data = temp[date_columns].melt(value_name="date").dropna()
                    melted_data["country"] = country
                    melted_data["count"] = 1  # Each row represents an event (visit)
                    daily_counts = pd.concat([daily_counts, melted_data], ignore_index=True)

    if not daily_counts.empty:
        # Format the dates
        daily_counts["date"] = pd.to_datetime(daily_counts["date"])

        # Ensure all selected countries appear in the data, even if they have no events
        date_range = pd.date_range(daily_counts["date"].min(), daily_counts["date"].max())
        all_countries_data = pd.DataFrame(
            [(d, c) for d in date_range for c in selected_countries],
            columns=["date", "country"]
        )

        # Merge to include all selected countries
        daily_counts = pd.merge(all_countries_data, daily_counts, on=["date", "country"], how="left")
        daily_counts["count"] = daily_counts["count"].fillna(0)

        # Group data for the line chart
        grouped = daily_counts.groupby(["date", "country"])["count"].sum().reset_index()
        pivot_data = grouped.pivot(index="date", columns="country", values="count").fillna(0)
        return pivot_data

    return None

def visits_by_age_group(data):
    st.markdown(
    f"""
    <h3 style="text-align: center;">Total Visits by Age Group</h3>
    """, 
    unsafe_allow_html=True
    )
    #st.subheader("Total Visits by Age Group")

    # Define age groups
    age_bins = [10, 15, 20, 100]  # 10-14, 15-19, 20+
    age_labels = ["10-14", "15-19", "20+"]

    # Identify all columns for different visits (e.g., vodan_motherage_v1, vodan_motherage_v2, ...)
    age_columns = [col for col in data.columns if col.startswith("vodan_motherage_")]

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
        col1, col2, col3 = st.columns(3)
        
        with col1:
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

        with col2:
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
          
        with col3:
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
        st.warning("No age columns (e.g., 'vodan_motherage_v1', 'vodan_motherage_v2', ...) were found in the dataset.")

def get_syphilis_columns(df):
    return [col for col in df.columns if col.startswith("vodan_syphilis_v")]

def get_hepatitis_b_columns(df):
    return [col for col in df.columns if col.startswith("vodan_hepatitisb_v")]

def get_hepatitis_c_columns(df):
    return [col for col in df.columns if col.startswith("vodan_hepatitisc_v")]
def get_HIV_columns(df):
    return [col for col in df.columns if col.startswith("vodan_hivstatus_v")]
def get_TB_columns(df):
    return [col for col in df.columns if col.startswith("vodan_tuberculosistbscreening_v")]
# Function to create pie charts for syphilis, hepatitis B, and C
def display_health_condition_pie_charts(df):
    # Syphilis pie chart
    syphilis_columns = get_syphilis_columns(df)
    if syphilis_columns:
        combined_syphilis = pd.concat([df[col] for col in syphilis_columns], axis=0, ignore_index=True)
        combined_syphilis.replace("", np.nan, inplace=True)
        combined_syphilis = combined_syphilis.dropna()
        syphilis_data = pd.DataFrame({"syphilis": combined_syphilis})
        syphilis_counts = syphilis_data["syphilis"].value_counts().sort_index()
        syphilis_fig = px.pie(names=syphilis_counts.index, values=syphilis_counts.values, title="Syphilis Distribution")
    else:
        syphilis_fig = None

    # Hepatitis B pie chart
    hepatitis_b_columns = get_hepatitis_b_columns(df)
    if hepatitis_b_columns:
        combined_hepatitis_b = pd.concat([df[col] for col in hepatitis_b_columns], axis=0, ignore_index=True)
        combined_hepatitis_b.replace("", np.nan, inplace=True)
        combined_hepatitis_b = combined_hepatitis_b.dropna()
        hepatitis_b_data = pd.DataFrame({"hepatitis_b": combined_hepatitis_b})
        hepatitis_b_counts = hepatitis_b_data["hepatitis_b"].value_counts().sort_index()
        hepatitis_b_fig = px.pie(names=hepatitis_b_counts.index, values=hepatitis_b_counts.values, title="Hepatitis B Distribution")
    else:
        hepatitis_b_fig = None

    # Hepatitis C pie chart
    hepatitis_c_columns = get_hepatitis_c_columns(df)
    if hepatitis_c_columns:
        combined_hepatitis_c = pd.concat([df[col] for col in hepatitis_c_columns], axis=0, ignore_index=True)
        combined_hepatitis_c.replace("", np.nan, inplace=True)
        combined_hepatitis_c = combined_hepatitis_c.dropna()
        hepatitis_c_data = pd.DataFrame({"hepatitis_c": combined_hepatitis_c})
        hepatitis_c_counts = hepatitis_c_data["hepatitis_c"].value_counts().sort_index()
        hepatitis_c_fig = px.pie(names=hepatitis_c_counts.index, values=hepatitis_c_counts.values, title="Hepatitis C Distribution")
    else:
        hepatitis_c_fig = None
    
    HIV_columns = get_HIV_columns(df)
    if HIV_columns:
        combined_HIV = pd.concat([df[col] for col in HIV_columns], axis=0, ignore_index=True)
        combined_HIV.replace("", np.nan, inplace=True)
        combined_HIV = combined_hepatitis_b.dropna()
        HIV_data = pd.DataFrame({"HIV": combined_HIV})
        HIV_counts = HIV_data["HIV"].value_counts().sort_index()
        HIV_fig = px.pie(names=HIV_counts.index, values=HIV_counts.values, title="HIV Distribution")
    else:
        HIV_fig = None
    
    TB_columns = get_TB_columns(df)
    if TB_columns:
        combined_TB = pd.concat([df[col] for col in TB_columns], axis=0, ignore_index=True)
        combined_TB.replace("", np.nan, inplace=True)
        combined_TB = combined_TB.dropna()
        TB_data = pd.DataFrame({"TB": combined_TB})
        TB_counts = TB_data["TB"].value_counts().sort_index()
        TB_fig = px.pie(names=TB_counts.index, values=TB_counts.values, title="TB Distribution")
    else:
        TB_fig = None


    # Display the pie charts in three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if syphilis_fig:
            st.plotly_chart(syphilis_fig, use_container_width=True)
        else:
            st.warning("No Syphilis data available.")
    
    with col2:
        if hepatitis_b_fig:
            st.plotly_chart(hepatitis_b_fig, use_container_width=True)
        else:
            st.warning("No Hepatitis B data available.")
    
    with col3:
        if hepatitis_c_fig:
            st.plotly_chart(hepatitis_c_fig, use_container_width=True)
        else:
            st.warning("No Hepatitis C data available.")
    col61, col62 =st.columns(2)
    with col61:
        if HIV_fig:
            st.plotly_chart(HIV_fig, use_container_width=True)
        else:
            st.warning("No HIV data available.")
    with col62:
        if TB_fig:
            st.plotly_chart(TB_fig, use_container_width=True)
        else:
            st.warning("No TB data available.")
           

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



# International-level dashboard
def render_international_dashboard(user=None, api_token=None):
    #df = fetch_data(api_token)
    st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">VODAN Dashboard </h1>
    </div>
    """,
    unsafe_allow_html=True,
    )
    #st.header("International Overview")
    
    
    def vodan_main(date_columns):
        today = date.today()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        # Filter data for different time periods
        today_data = filter_data_by_date(df, date_columns, today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        month_data = filter_data_by_date(df, date_columns, start_of_month.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        year_data = filter_data_by_date(df, date_columns, start_of_year.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        # Filter date columns in your dataset
        date_columns = [col for col in df.columns if col.startswith("date_of_visit_")]
        # Ensure all date columns are in datetime format
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Count the total visits for the selected day across all date columns
        selected_day_visits = df[date_columns].apply(lambda row: row.isin([pd.Timestamp(selected_day)]).sum(), axis=1).sum()
        
        
        visit_suffixes = [f"v{i}" for i in range(1, 9)]
        risky_mothers = set()  # Use a set to avoid double-counting mothers across visits
        for suffix in visit_suffixes:
            risky_mothers.update(df[is_risky_mother(df, suffix)].index)
            # Total number of unique risky mothers
        total_risky_mothers = len(risky_mothers)
        


        # Display metrics for total visits
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
                <div class="value">{len(df)}</div>
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
            visit_counts.columns = ['Visit Number', 'Count']
            fig = px.bar(visit_counts, x='Visit Number', y='Count', color='Visit Number', 
                        title=title, color_discrete_sequence=px.colors.qualitative.Set2, width=800)
            st.plotly_chart(fig)
            
            
            #visit_counts = data["redcap_event_name"].value_counts().sort_index()
            #st.write(title)
            #st.bar_chart(visit_counts)

        col4, col5= st.columns(2)
        with col4:
            visits_by_visit_number(today_data, "Today's Visits by Number")
        with col5:
            visits_by_visit_number(month_data, "This Month's Visits by Number")
        
        col6, col7 = st.columns(2)
        with col6:
            visits_by_visit_number(year_data, "This Year's Visits by Number")
        with col7:
            visits_by_visit_number(df, "Total Visits by Number")

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

        daily_data = daily_visits(df)
        st.line_chart(daily_data.set_index("date"))

    
    if not api_token:
        st.error("API token is required.")
        return

    try:
        # Fetch data
        df = fetch_data(api_token)

        if not df.empty:
            # Extract relevant country and date columns
            country_columns = get_country_columns(df)
            date_columns = get_date_columns(df)
            # Sidebar option for "Visit by Age Group"
            homepage=st.sidebar.button("Home")
            selected_day = st.sidebar.date_input("Select a Day", value=pd.Timestamp.today())
            age_group_dashboard = st.sidebar.button("Total Visits by Age Group")
            show_health_condition_charts = st.sidebar.button("Infectious Diseases")
            # Slider to select a specific day
            

            # Sidebar option to toggle country-level dashboard
            country_dashboard = st.sidebar.checkbox("Show Country-Level Dashboard")

            if age_group_dashboard:
                visits_by_age_group(df)  # Call the function to display visits by age group
            elif show_health_condition_charts:
                display_health_condition_pie_charts(df)     
            elif country_dashboard:
                # Display metrics for visits by country
                st.markdown(
                    f"""
                    <h3 style="text-align: center;">Country Level Dashboard</h3>
                    """, 
                    unsafe_allow_html=True
                    )
                

                def visits_by_country(data, title):
                    # Filter out rows where the country column is NaN or invalid
                    country_counts = pd.Series(dtype=int)
                    for col in country_columns:
                        if col in data.columns:
                            # Filter out NaN or invalid countries
                            temp_data = data[col].dropna()
                            # Count visits per country and add to the total count
                            temp_counts = temp_data.value_counts()
                            country_counts = country_counts.add(temp_counts, fill_value=0)
                            # Remove any entries where country name is NaN or empty
                    country_counts = country_counts[country_counts.index != '']
                    st.write(title)
                    col21, col22 = st.columns(2)
                    # Bar chart in the first column
                    with col21:
                        st.bar_chart(country_counts.sort_index(), height=450)
                    # Pie chart in the second column
                    with col22:
                        fig = px.pie(names=country_counts.index, values=country_counts.values, title="Visits by Country (Pie Chart)")
                        st.plotly_chart(fig, height=250)
                    
                    
                    #st.bar_chart(country_counts.sort_index())


                visits_by_country(df, "Total Visits by Country")

                # Visits by visit number for each country
                st.subheader("Visits by Visit Number per Country")

                def visits_by_visit_number_per_country(data):
                    country_counts = pd.DataFrame()
                    for col in country_columns:
                        if col in data.columns:
                            temp_data = data[data[col].notna() & (data[col] != '')]
                            temp_counts = temp_data.groupby(col)["redcap_event_name"].value_counts().unstack(fill_value=0)
                            country_counts = country_counts.add(temp_counts, fill_value=0) if not country_counts.empty else temp_counts
                    return country_counts

                visits_by_number = visits_by_visit_number_per_country(df)
                if not visits_by_number.empty:
                    visits_by_number = visits_by_number.groupby(visits_by_number.index).sum()  # Ensure each country is only listed once
                    st.write("Visits by Visit Number for Countries")
                    st.dataframe(visits_by_number)

                # Line chart for total visits day by day per country
                st.subheader("Daily Visit Trends by Country")

                # Sidebar option for selecting countries
                st.sidebar.subheader("Select Countries for Comparison")
                all_countries = df[country_columns].stack().unique()
                selected_countries = st.sidebar.multiselect(
                    "Choose Countries to Compare", 
                    options=all_countries, 
                    default=all_countries[:4]  # Preselect first 3 countries for convenience
                )

                if selected_countries:
                    # Generate line chart for selected countries
                    line_chart_data = daily_visit_trends(df, country_columns, date_columns, selected_countries)
                    if line_chart_data is not None:
                        st.line_chart(line_chart_data)
                    else:
                        st.warning("No valid data available for the selected countries.")
                else:
                    st.warning("Please select at least one country to compare.")

            elif homepage:
                vodan_main(date_columns)
            else:
                vodan_main(date_columns)
                # Define date ranges for today, this month, and this year
            
        else:
            st.warning("No data available for this international overview.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
