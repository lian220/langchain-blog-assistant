from langchain.tools import tool
from typing import Optional
import requests
from app.config import get_settings


@tool
def image_search(topic: str) -> str:
    """Find high-quality, royalty-free stock images related to the given topic.

    This tool searches for appropriate images that can be used as cover images
    for blog posts. It returns the URL of a suitable image.

    Args:
        topic: The topic or description of the image to search for

    Returns:
        A URL string pointing to a royalty-free image
    """
    print(f">>> Searching for image about: {topic}")

    # Try to use Pexels API if available
    settings = get_settings()
    pexels_api_key = settings.pexels_api_key
    print(f">>> Pexels API Key present: {bool(pexels_api_key)}")
    if pexels_api_key:
        print(f">>> Pexels API Key (first 20 chars): {pexels_api_key[:20]}...")

    if pexels_api_key:
        try:
            headers = {"Authorization": pexels_api_key}
            print(f">>> Making Pexels API request for: {topic}")
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params={"query": topic, "per_page": 1},
                timeout=10,
            )
            print(f">>> Pexels API Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                print(f">>> Pexels API returned {len(photos)} photos")
                if photos:
                    image_url = photos[0]["src"]["large"]
                    print(f">>> ✅ Using Pexels image: {image_url}")
                    return image_url
                else:
                    print(f">>> ⚠️  No photos found for query: {topic}")
                    return fallback_image(topic)
            else:
                print(f">>> ⚠️  Pexels API error status: {response.status_code}")
                print(f">>> Response: {response.text[:200]}")
                return fallback_image(topic)
        except Exception as e:
            print(f">>> ❌ Pexels API exception: {e}")
            return fallback_image(topic)
    else:
        print(f">>> ⚠️  No Pexels API key found, using fallback")
        return fallback_image(topic)


def fallback_image(topic: str) -> str:
    """Fallback when Pexels API is not available."""
    # Return a placeholder image service URL
    # Using picsum.photos as a fallback for demonstration
    return f"https://picsum.photos/1200/630?random={hash(topic) % 1000}"
