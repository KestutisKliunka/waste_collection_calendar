import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

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

    # Step 3: Debugging Address Filtering
    # Filter the dataset for the provided address
    filtered_data = data[data['Eiendomsnavn'].str.contains(address, case=False, na=False)]
    if filtered_data.empty:
        st.write("No data found for the given address.")
    else:
        st.write("Filtered data:")
        st.write(filtered_data.head())  # Display filtered data for debugging

    # Placeholder for Calendar Generation Logic
    st.write("Debug: Calendar generation logic goes here.")
