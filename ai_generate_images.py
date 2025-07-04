import requests
import os
from google import genai
from google.genai import types
from datetime import date


def get_weather_data(lat, lng, api_key):
    """
    Query the OpenWeatherMap API to get current weather data for a specified city.

    Args:
        city_name (str): Name of the city to get weather data for
        api_key (str): Your OpenWeatherMap API key

    Returns:
        dict: JSON response from the API containing weather data
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    # Parameters for the API request
    params = {
        "lat": lat,
        "lon": lng,
        "appid": api_key,
        "units": "metric",  # Use metric units (Celsius)
    }

    try:
        # Make the API request
        response = requests.get(base_url, params=params)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        weather_data = response.text
        return weather_data

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print("Error: City not found.")
        elif response.status_code == 401:
            print("Error: Invalid API key.")
        else:
            print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None


def save_binary_file(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "wb") as f:
        f.write(data)


def generate_image_prompt_template_from_weather_data(weather_data):
    user_prompt = f"""Given this weather data modify given template
- Analyse weather according to current date and season.
```json
{weather_data}
```
template::
```
Create a highly detailed, satirical digital illustration of a developer's workspace during [WEATHER_CONDITION] weather. The scene should be cinematic and well-lit, with a focus on dramatic lighting and atmospheric effects.

Key Elements:
1. Developer Character:
   - A frustrated developer with realistic facial expressions showing [EMOTION_BASED_ON_WEATHER]
   - Visible dark circles under eyes and slightly disheveled appearance
   - Wearing casual developer attire appropriate for the [TEMPERATURE] degree temperature
   - Sitting in a modern ergonomic chair

2. Workspace Details:
   - Multiple high-end monitors displaying code and error messages
   - Mechanical keyboard with RGB lighting
   - At least 3-4 coffee cups in various states of emptiness
   - Modern desk setup with cable management
   - Some tech gadgets and developer tools scattered around

3. Room Environment:
   - Modern tech office space with clean lines
   - Temperature set to [TEMPERATURE] degrees, making it [COMFORTABLE/UNCOMFORTABLE]
   - Subtle RGB lighting elements
   - Indoor plants that react to the weather outside

4. Window View:
   - Large window showing [WEATHER_DESCRIPTION] outside
   - [WEATHER_DETAILS_EXAGGERATED] visible through the window
   - [APPROPRIATE_LIGHTING_EFFECT] casting dramatic shadows
   - Window frame with modern design

5. Emotional Support Duck:
   - A rubber duck wearing [DUCK_CLOTHING_BASED_ON_WEATHER]
   - Positioned prominently on the desk
   - Detailed enough to show weather-appropriate accessories

Technical Requirements:
- Use a cinematic aspect ratio (21:9 or 16:9)
- Implement dramatic lighting with clear light sources
- Maintain high contrast while keeping details visible
- Use a modern, clean art style with attention to small details
- Ensure the composition leads the eye through the scene
- Include subtle weather-appropriate color grading
```
"""
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text=f"""You are an export weather data analyzer.
Given a weather data in JSON form, perform modifications on user provided templates. The weather data json will always going to be openweathermap API response.
### Some Details about the api response 
1. **Group 2xx: Thunderstorm**
   - **200-232**: Various intensities of thunderstorms, from light to heavy, with or without rain or drizzle.
   - **Icon**: 11d (Thunderstorm)
2. **Group 3xx: Drizzle**
   - **300-321**: Various intensities of drizzle, from light to heavy, sometimes mixed with rain.
   - **Icon**: 09d (Shower rain)
3. **Group 5xx: Rain**
   - **500-531**: Various intensities of rain, from light to extreme, including freezing rain and shower rain.
   - **Icons**: 10d (Rain), 13d (Snow) for freezing rain, 09d (Shower rain)
4. **Group 6xx: Snow**
   - **600-622**: Various intensities of snow, including sleet and mixed rain and snow.
   - **Icon**: 13d (Snow)
5. **Group 7xx: Atmosphere**
   - **701-781**: Various atmospheric conditions like mist, smoke, haze, dust, fog, sand, ash, squalls, and tornadoes.
   - **Icon**: 50d (Mist)
6. **Group 800: Clear**
   - **800**: Clear sky.
   - **Icon**: 01d (Clear sky)
7. **Group 80x: Clouds**
   - **801-804**: Various cloud coverages from few clouds to overcast clouds.
   - **Icons**: 02d (Few clouds), 03d (Scattered clouds), 04d (Broken clouds)
### Icon List
- **Day Icons**: 01d.png (Clear sky), 02d.png (Few clouds), 03d.png (Scattered clouds), 04d.png (Broken clouds), 09d.png (Shower rain), 10d.png (Rain), 11d.png (Thunderstorm), 13d.png (Snow), 50d.png (Mist)
- **Night Icons**: 01n.png (Clear sky), 02n.png (Few clouds), 03n.png (Scattered clouds), 04n.png (Broken clouds)

# Important Notes
- Cloudy doesn't mean it will rain, it just means there are clouds in the sky.
- Current date is {date.today().strftime("%B %d, %Y")} make sure to account it to get weather idea according to natural weather cycle.
- Check the openweathermap API response and understand the weather details.
- The weather details will be in metric units.
- Modify the template text according to the weather details you can be creative but don't exaggerate the weather details too much.
- Make sure to only return modified template text according to given data in response, don't include any other text.
"""
            ),
        ],
    )

    template_str = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        template_str += chunk.text

    return template_str


def generate_ai_image_with_weather_data(weather_data):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    image_gen_prompt = generate_image_prompt_template_from_weather_data(weather_data).replace('\\n', "\n")

    user_prompt = f""""{image_gen_prompt}

# Critical Image Generation Instructions:
1. Style and Quality:
   - Generate a highly detailed, cinematic digital illustration
   - Use dramatic lighting with clear light sources and shadows
   - Maintain high contrast while preserving detail in both shadows and highlights
   - Follow a modern, clean art style with meticulous attention to small details
   - Ensure the composition has clear focal points and visual hierarchy

2. Technical Requirements:
   - Use a cinematic aspect ratio (21:9 or 16:9)
   - Include subtle weather-appropriate color grading
   - Maintain consistent lighting throughout the scene
   - Ensure all text elements (monitors, etc.) are readable but not dominant
   - Create depth through layering and atmospheric effects

3. Important Restrictions:
   - NO text overlays or watermarks
   - NO weather-related text in the image
   - NO cartoonish or overly exaggerated elements
   - NO cluttered or messy composition
   - NO low-quality or blurry elements

4. Focus Areas:
   - Developer's facial expression and body language
   - Weather effects visible through the window
   - Lighting and atmosphere of the room
   - Details of the workspace and equipment
   - The emotional support duck's weather-appropriate appearance

The final image should be a professional-quality illustration that could be used as a header image, with clear storytelling and emotional impact.
"""

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_modalities=[
            "image",
            "text",
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            not chunk.candidates
            or not chunk.candidates[0].content
            or not chunk.candidates[0].content.parts
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = "./img/generated/header.jpeg"
            save_binary_file(
                file_name, chunk.candidates[0].content.parts[0].inline_data.data
            )
            print(
                "File of mime type"
                f" {chunk.candidates[0].content.parts[0].inline_data.mime_type} saved"
                f"to: {file_name}"
            )
        else:
            print(chunk.text)


if __name__ == "__main__":
    # You need to sign up for a free API key at https://openweathermap.org/
    API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    if not API_KEY:
        raise RuntimeError(
            "API key not found. Please set the OPENWEATHERMAP_API_KEY environment variable."
        )

    city_lat = 22.3039
    city_lon = 70.8022
    weather_data = get_weather_data(city_lat, city_lon, API_KEY)

    if not weather_data:
        print("Failed to retrieve weather data.")
    else:
        generate_ai_image_with_weather_data(weather_data)
