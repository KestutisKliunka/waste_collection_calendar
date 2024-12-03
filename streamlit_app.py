import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from fuzzywuzzy import process
import unicodedata  # For normalizing Unicode characters

# Automatically load the dataset at app start
@st.cache
def load_data():
    # Load and clean the dataset
    df = pd.read_csv("dataset.csv", encoding='utf-8', delimiter=';', quotechar='"')
    df['Eiendomsnavn'] = df['Eiendomsnavn'].apply(normalize_text)  # Normalize text
    return df

# Normalize text to handle special characters
def normalize_text(text):
    # Strip spaces and convert to lowercase
    text = text.strip().lower()
    # Normalize Unicode (e.g., å -> å, é -> e)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return text

# Load the dataset
data = load_data()

# Title and Instructions
st.title("Interactive Waste Collection Calendar")
st.markdown("""
## How to Use:
1. Enter your address in the input box below.
2. View the waste collection calendar for 2025.
""")

# Step 1: Address Input
address = st.text_input("Enter an address")
if address:
    st.write(f"Generating calendar for address: {address}")

    # Normalize the input address
    normalized_address = normalize_text(address)

    # Step 2: Fuzzy Matching to Find the Closest Address
    all_addresses = data['Eiendomsnavn'].tolist()
    closest_matches = process.extract(normalized_address, all_addresses, limit=5)  # Get top 5 matches
    st.write("Did you mean one of these addresses?")
    for match in closest_matches:
        st.write(f"- {match[0]} (Match score: {match[1]}%)")

    # Select the best match if the match score is high enough
    best_match = next((match for match in closest_matches if match[1] > 85), None)
    if best_match:
        matched_address = best_match[0]
        st.write(f"Matched address: {matched_address}")

        # Filter the data for the matched address
        filtered_data = data[data['Eiendomsnavn'] == matched_address]

        if filtered_data.empty:
            st.write("No data found for the matched address.")
        else:
            st.write("Filtered data:")
            st.write(filtered_data.head())  # Display filtered data for debugging

            # Rest of the logic remains the same
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

            # Step 4: Generate Calendar Visualization
            def generate_calendar(filtered_data):
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

                corrected_cycle_schedule_2025 = generate_corrected_2025_schedule()

                colors = plt.cm.tab10.colors
                route_colors = {route: colors[i % len(colors)] for i, route in enumerate(filtered_data['Rutenummer'].unique())}

                plt.figure(figsize=(16, 12))
                for month in range(1, 13):
                    ax = plt.subplot(4, 3, month)
                    ax.set_title(calendar.month_name[month], fontsize=14)

                    first_weekday, num_days_in_month = calendar.monthrange(2025, month)
                    for day in range(1, num_days_in_month + 1):
                        current_date = datetime(2025, month, day)
                        day_of_week = current_date.weekday()  # 0 = Monday, 6 = Sunday
                        week_number = (day + first_weekday - 1) // 7  # Row in the calendar

                        ax.text(day_of_week + 0.5, -week_number, str(day), ha='center', va='center', fontsize=10)

                        for _, row in filtered_data.iterrows():
                            if current_date in corrected_cycle_schedule_2025:
                                if (
                                    corrected_cycle_schedule_2025[current_date] == row['CycleWeek']
                                    and current_date.weekday() + 1 == row['Weekday']
                                ):
                                    ax.add_patch(Rectangle(
                                        (day_of_week, -week_number - 1 + 0.4),
                                        1, 1,
                                        color=route_colors[row['Rutenummer']], alpha=0.3
                                    ))
                    ax.set_xlim(-0.5, 6.5)
                    ax.set_ylim(-6, 0)
                    ax.axis('off')
                plt.tight_layout()
                plt.suptitle(f"Collection Calendar for {matched_address} - 2025", fontsize=18, y=1.02)
                st.pyplot(plt)

            generate_calendar(filtered_data)
    else:
        st.write("No sufficiently close match found for the address.")
