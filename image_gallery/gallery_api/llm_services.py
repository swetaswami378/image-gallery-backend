import time
import logging
import os
from PIL import Image
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded, InternalServerError, ServiceUnavailable

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("API_KEY")

genai.configure(api_key=API_KEY)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-exp:free"


def generate_caption_for_image(image_path: str, max_retries: int = 2, base_delay: float = 2.0) -> str:
    """
    Generate a concise caption for an image using Google's Gemini model directly.
    Requires google-generativeai package.
    """
    try:
        # Load the image file
        img = Image.open(image_path)

        # Initialize the Gemini multimodal model
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        prompt = "Provide a concise descriptive caption for the image (one sentence)."

        # Generate response (Gemini supports multimodal input: text + image)
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    [prompt, img],
                    generation_config={"temperature": 0.0},
                )

                if hasattr(response, "text") and response.text:
                    return response.text.strip()

                raise Exception("Empty response from Gemini model.")

            except (ResourceExhausted, DeadlineExceeded, InternalServerError, ServiceUnavailable) as e:
                # Handle transient or quota-related errors
                wait_time = base_delay * (2 ** attempt)
                logger.warning(
                    f"[Gemini Retry {attempt + 1}/{max_retries}] "
                    f"Temporary error: {e}. Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
                continue

            except Exception as e:
                # Catch-all for unexpected exceptions (e.g., network)
                wait_time = base_delay * (2 ** attempt)
                logger.error(
                    f"[Gemini Retry {attempt + 1}/{max_retries}] "
                    f"Unexpected error: {e}. Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
                continue

        raise Exception("Gemini API: All retry attempts failed.")

    except Exception as e:
        logger.exception(f"Gemini API error: {e}")
        raise Exception(f"Gemini API error: {e}")


def encode_image_to_data_url(path):
    with open(path, "rb") as f:
        b = f.read()
    ext = path.split(".")[-1].lower()
    mime = "image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:{mime};base64,{b64}"
