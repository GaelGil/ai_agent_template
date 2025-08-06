import requests
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path("../.env"))


ARXIV_NAMESPACE = "{http://www.w3.org/2005/Atom}"
LLM = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = get_logger(__name__)


mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="get_weather",
    description="Get current temperature for provided coordinates in celsius",
)
def get_weather(latitude, longitude):
    """Get current temperature for provided coordinates in celsius
    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location

    Returns:
        dict: Current temperature
    """
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
