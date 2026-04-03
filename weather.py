import httpx
import logging
from typing import Optional
from config import OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


async def get_weather(city: str, units: str = "celsius") -> str:
    """
    Get weather for a city using OpenWeatherMap API.
    Requires OPENWEATHER_API_KEY env variable.
    """
    from config import OPENWEATHER_API_KEY

    if not OPENWEATHER_API_KEY:
        from config import OPENWEATHER_API_KEY as key

        OPENWEATHER_API_KEY = key

    if not OPENWEATHER_API_KEY:
        return "ERRO: OPENWEATHER_API_KEY não configurada. Configure no .env para usar esta função."

    try:
        unit_map = {"celsius": "metric", "fahrenheit": "imperial"}
        units_param = unit_map.get(units.lower(), "metric")

        async with httpx.AsyncClient() as client:
            geo_response = await client.get(
                f"http://api.openweathermap.org/geo/1.0/direct",
                params={"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY},
                timeout=OLLAMA_TIMEOUT,
            )

            if geo_response.status_code != 200:
                return f"ERRO: Falha ao buscar coordenadas para {city}"

            geo_data = geo_response.json()
            if not geo_data:
                return f"ERRO: Cidade '{city}' não encontrada"

            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            city_name = geo_data[0]["name"]
            country = geo_data[0].get("country", "")

            weather_response = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "units": units_param,
                    "appid": OPENWEATHER_API_KEY,
                    "lang": "pt_br",
                },
                timeout=OLLAMA_TIMEOUT,
            )

            if weather_response.status_code != 200:
                return f"ERRO: Falha ao buscar dados meteorológicos"

            data = weather_response.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]

            unit_symbol = "°C" if units_param == "metric" else "°F"

            return (
                f"Clima em {city_name}, {country}:\n"
                f"Temperatura: {temp}{unit_symbol} (sensação: {feels_like}{unit_symbol})\n"
                f"Condição: {description.capitalize()}\n"
                f"Umidade: {humidity}%\n"
                f"Vento: {wind_speed} m/s"
            )
    except httpx.TimeoutException:
        return f"ERRO: Timeout ao acessar OpenWeatherMap"
    except Exception as e:
        logger.error(f"Erro no get_weather: {e}")
        return f"ERRO: {str(e)}"
