import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Global variable to hold the dataset
data = None

# Title and Instructions
st.title("Interactive Waste Collection Calendar")
st.write("Upload your dataset and enter an address to see the collection calendar.")

# Step 1: File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
if uploaded_file is not None:
    # Load the dataset into a DataFrame
    data = pd.read_csv(uploaded_file, encoding='ISO-8859-1', delimiter=';', quotechar='"')
    st.write("Dataset loaded successfully!")
    st.write(data.head())  # Display the first few rows for debugging

# Step 2: Address Input
address = st.text_input("Enter an address")
if address and data is not None:
    st.write(f"Generating calendar for address: {address}")

    # Step 3: Filter Data for the Given Address
    filtered_data = data[data['Eiendomsnavn'].str.contains(address, case=False, na=False)]
    if filtered_data.empty:
        st.write("No data found for the given address.")
    else:
        st.write("Filtered data:")
        st.write(filtered_data.head())  # Display filtered data for debugging

        # Step 4: Extract Collection Schedule
        def extract_schedule(route_number):
            route_str = str(route_number).zfill(5)  # Ensure 5 digits
            weekday_digit = int(route_str[3])  # Fourth digit: Weekday
            cycle_week_digit = int(route_str[4])  # Fifth digit: Cycle week
            return weekday_digit, cycle_week_digit

        # Add weekday and cycle week to the filtered data
        filtered_data['Weekday'], filtered_data['CycleWeek'] = zip(
            *filtered_data['Rutenummer'].apply(extract_schedule)
        )

        # Convert numeric data to integers for display (removing decimals)
        filtered_data['Weekday'] = filtered_data['Weekday'].astype(int)
        filtered_data['CycleWeek'] = filtered_data['CycleWeek'].astype(int)

        # Display the extracted schedule for debugging
        st.write("Extracted schedule:")
        st.write(filtered_data[['Eiendomsnavn', 'Rutenummer', 'Weekday', 'CycleWeek']])

        # Step 5: Generate Calendar Visualization
        def generate_calendar(filtered_data):
            # Define the 2025 cycle mapping
            def generate_corrected_2025_schedule():
                start_date = datetime(2025, 1, 1)
                days_in_2025 = 365 if calendar.isleap(2025) else 364
                schedule = {}
                for day_offset in range(days_in_2025):
                    current_date = start_date + timedelta(days=day_offset)
                    week_number = current_date.isocalendar()[1]
                    cycle_week = ((week_number - 2) % 4) + 1 if week_number > 1 else 4
                    schedule[current_date] = cycle_week
                return schedule

            # Get the 2025 schedule
            corrected_cycle_schedule_2025 = generate_corrected_2025_schedule()

            # Generate the calendar visualization
            colors = plt.cm.tab10.colors
            route_colors = {route: colors[i % len(colors)] for i, route in enumerate(filtered_data['Rutenummer'].unique())}

            plt.figure(figsize=(16, 12))
            for month in range(1, 13):
                ax = plt.subplot(4, 3, month)
                ax.set_title(calendar.month_name[month], fontsize=14)

                # Get all dates for the month
                num_days_in_month = calendar.monthrange(2025, month)[1]
                month_dates = [datetime(2025, month, day) for day in range(1, num_days_in_month + 1)]

                # Group dates by ISO weeks
                weeks = {}
                for date in month_dates:
                    iso_week = date.isocalendar()[1]
                    if iso_week not in weeks:
                        weeks[iso_week] = []
                    weeks[iso_week].append(date)

                # Plot the days for each week
                for week_num, week_dates in weeks.items():
                    for date in week_dates:
                        day_index = date.weekday()
                        ax.text(day_index + 0.5, -week_num, str(date.day), ha='center', va='center', fontsize=10)

                        # Highlight collection dates
                        for _, row in filtered_data.iterrows():
                            if date in corrected_cycle_schedule_2025:  # Check key existence
                                if (
                                    corrected_cycle_schedule_2025[date] == row['CycleWeek']
                                    and date.weekday() + 1 == row['Weekday']
                                ):
                                    ax.add_patch(Rectangle(
                                        (day_index, -week_num - 1 + 0.4),  # Move up by 40% of the height
                                        1, 1,
                                        color=route_colors[row['Rutenummer']], alpha=0.3
                                    ))
                ax.set_xlim(-0.5, 6.5)
                ax.set_ylim(-7, 0)
                ax.axis('off')
            plt.tight_layout()
            plt.suptitle(f"Collection Calendar for {address} - 2025", fontsize=18, y=1.02)
            st.pyplot(plt)

        generate_calendar(filtered_data)
