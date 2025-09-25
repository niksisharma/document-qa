import streamlit as st
import requests
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_current_weather(location, API_key=None):
    if API_key is None:
        API_key = st.secrets["OPENWEATHERMAP_API_KEY"]
    
    # Clean location name
    if "," in location:
        location = location.split(",")[0].strip()
    
    # Construct API URL
    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        # Extract temperatures & Convert Kelvin to Celsius
        temp = data['main']['temp'] - 273.15
        feels_like = data['main']['feels_like'] - 273.15
        temp_min = data['main']['temp_min'] - 273.15
        temp_max = data['main']['temp_max'] - 273.15
        humidity = data['main']['humidity']
        
        # Extract additional weather information
        description = data['weather'][0]['description']
        main_weather = data['weather'][0]['main']
        wind_speed = data.get('wind', {}).get('speed', 0)  # m/s
        
        return {
            "location": data['name'],
            "temperature": round(temp, 2),
            "feels_like": round(feels_like, 2),
            "temp_min": round(temp_min, 2),
            "temp_max": round(temp_max, 2),
            "humidity": round(humidity, 2),
            "description": description,
            "main_weather": main_weather,
            "wind_speed": round(wind_speed, 2)
        }
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None
    except KeyError as e:
        st.error(f"Error parsing weather data: Missing key {e}")
        return None

def get_weather_for_openai(location):
    """
    Wrapper function for OpenAI function calling.
    Returns weather data as a JSON string.
    """
    if not location:
        location = "Syracuse, NY"  
    
    weather_data = get_current_weather(location)
    if weather_data:
        return json.dumps(weather_data)
    else:
        return json.dumps({"error": "Could not retrieve weather data"})

def get_clothing_suggestions(location):
    # Define the weather function for OpenAI
    weather_function = {
        "type": "function",
        "function": {
            "name": "get_weather_for_openai",
            "description": "Get current weather information for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'Syracuse, NY' or 'London, England')"
                    }
                },
                "required": ["location"]
            }
        }
    }
    
    messages = [
        {
            "role": "system",
            "content": """You are a helpful weather and clothing advisor. When asked about clothing suggestions 
            for a location, first get the current weather information, then provide detailed clothing recommendations 
            and advice about whether it's a good day for a picnic. Be specific about clothing items and explain 
            your reasoning based on the weather conditions."""
        },
        {
            "role": "user",
            "content": f"What should I wear today in {location}? Also, is it a good day for a picnic?"
        }
    ]
    
    try:
        # First OpenAI API call with function calling
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[weather_function],
            tool_choice="auto"
        )
        
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_weather_for_openai":
                weather_result = get_weather_for_openai(function_args.get("location", location))
                
                messages.append(response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "content": weather_result,
                    "tool_call_id": tool_call.id
                })
                
                # Second OpenAI API call with weather information
                final_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                return final_response.choices[0].message.content
        
        else:
            return response.choices[0].message.content
            
    except Exception as e:
        st.error(f"Error getting clothing suggestions: {e}")
        return "Sorry, I couldn't process your request. Please try again."

def main():
    st.title("🌤️ Nikita's What to wear Bot")
    st.markdown("Get personalized clothing recommendations based on current weather!")
    
    st.sidebar.header("🧪 Test Weather Function")
    test_location = st.sidebar.text_input("Test Location:", value="Syracuse, NY")
    
    if st.sidebar.button("Test Weather API"):
        with st.sidebar:
            with st.spinner("Fetching weather data..."):
                weather_data = get_current_weather(test_location)
                if weather_data:
                    st.success("Weather API Test Successful!")
                    st.json(weather_data)
                else:
                    st.error("Failed to fetch weather data")
    
    st.header("Get Your Daily Outfit Suggestions")
    
    # Location input
    location = st.text_input(
        "Enter a city name:", 
        value="Syracuse, NY",
        placeholder="e.g., Syracuse NY, London England, Paris France"
    )
    
    if st.button("Get Weather & Clothing Suggestions", type="primary"):
        if location:
            with st.spinner("Analyzing weather and preparing suggestions..."):
                suggestions = get_clothing_suggestions(location)
                
                st.markdown("### 👔 Your Personalized Recommendations:")
                st.markdown(suggestions)
                
                with st.expander("📊 View Raw Weather Data"):
                    weather_data = get_current_weather(location)
                    if weather_data:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("🌡️ Temperature", f"{weather_data['temperature']}°C")
                            st.metric("🤒 Feels Like", f"{weather_data['feels_like']}°C")
                            st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                        
                        with col2:
                            st.metric("🌡️ Min Temp", f"{weather_data['temp_min']}°C")
                            st.metric("🌡️ Max Temp", f"{weather_data['temp_max']}°C")
                            st.metric("💨 Wind Speed", f"{weather_data['wind_speed']} m/s")
                        
                        st.info(f"☁️ **Weather**: {weather_data['description'].title()}")
        else:
            st.warning("Please enter a city name!")
    
    st.markdown("### 📍 Example locations to try:")
    st.markdown("• Syracuse, NY • London, England • Tokyo, Japan • Sydney, Australia • Bengaluru, India")

if __name__ == "__main__":
    main()