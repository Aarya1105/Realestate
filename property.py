import streamlit as st # this package is required for the web app
import requests # this package is required for Bing Search API
from openai import OpenAI # this package is required for OpenAI (LLM - AI as a service) API

# Bing Search Function - a user defined function to search for properties and their prices
def bing_search(query, api_key, num_results=10):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {
        "q": query,
        "count": num_results,
        "responseFilter": "WebPages",
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json().get("webPages", {}).get("value", [])
        return [{"title": item["name"], "snippet": item["snippet"], "link": item["url"]} for item in results]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# GPT Response Function to get the response from Open AI
def generate_gpt_response(search_results, openai_api_key):
    client = OpenAI(api_key=openai_api_key)


    prompt = f"""
    Based on the search results provided, analyze whether a I can find properties within their desired budget in the specified locality and city. Include the following factors in your analysis:
	1.	Budget: {budget}
	2.	Locality: {preferred_location}
	3.	City: {city}
	4.	Search Results: {search_results}

    Provide a detailed response indicating if properties matching the budget are available. If available, mention the average price range and key features of those properties. If not, suggest nearby localities within the city that fit the user’s budget.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a knowledgeable real estate assistant in India"},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content

# Streamlit App
st.title("Is your perfect home under your budget? Let's find out!")

# Basic Inputs
family_size = st.number_input("How many members are in your family?", min_value=1, step=1)
budget = st.number_input("Enter your budget (₹):", min_value=1000000, step=50000)
city = st.text_input("Preferred City (e.g., Kolkata etc):")
preferred_location = st.text_input("Preferred location or area (e.g., Newtown, Action Area 1):")
property_type = st.selectbox("Preferred property type:", ["Flat", "Apartment", "House", "Villa", "Other"])

# Dynamic Bedrooms Input
num_bedrooms = st.number_input("How many bedrooms do you need?", min_value=1, step=1)
bedroom_sizes = [] # List to store bedroom sizes with no default value
for i in range(num_bedrooms):
    size = st.number_input(f"Enter the size of Bedroom {i + 1} (sq ft):", min_value=100, max_value=250, step=10)
    bedroom_sizes.append(size)

# Dynamic Bathrooms Input
num_bathrooms = st.number_input("How many bathrooms do you need?", min_value=1, step=1)
bathroom_sizes = []
for i in range(num_bathrooms):
    size = st.number_input(f"Enter the size of Bathroom {i + 1} (sq ft):", min_value=50, max_value=150, step=10)
    bathroom_sizes.append(size)

# Other Areas
kitchen_size = st.number_input("Enter the size of the Kitchen (sq ft):", min_value=100, max_value=250, step=10)
living_area = st.number_input("Enter the size of the Living Area (sq ft):", min_value=100, max_value=450, step=10)
other_areas = st.number_input("Enter the size of Other Areas (sq ft):", min_value=0, max_value=500, step=10)

# Summary Calculation
total_bedroom_area = sum(bedroom_sizes)
total_bathroom_area = sum(bathroom_sizes)
total_carpet_area = total_bedroom_area + kitchen_size + total_bathroom_area + living_area + other_areas
super_built_up_area = total_carpet_area * 1.50 # this is hard coded for now. You can change it as per your requirement

# Construct Query
search_query = f"""
What is the price range of affordable {property_type.lower()}s in {preferred_location}, {city} with a super built-up area of approximately {super_built_up_area} sq ft.
"""

# Search and Display - Results
if st.button("Find Properties"):
    BING_API_KEY = "0810adf6701045e0a312a9d018fa126f"
    OPENAI_API_KEY = "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"

    try:
        # Perform Bing Search
        search_results = bing_search(search_query, BING_API_KEY)
        
        if search_results:
            # Summarize Results with GPT
            gpt_response = generate_gpt_response(search_results, OPENAI_API_KEY)
            st.header("Recommended Properties")
            st.write(gpt_response)
        else:
            st.warning("No search results found. Try refining your preferences.")
    except Exception as e:
        st.error(f"Error: {str(e)}")