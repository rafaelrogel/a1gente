import logging
import httpx
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def generate_image(prompt: str, width: int = 512, height: int = 512) -> str:
    """
    Generates an image from a text prompt using Pollinations.ai free API.

    Args:
        prompt: Text description of the image to generate
        width: Image width in pixels (default: 512)
        height: Image height in pixels (default: 512)

    Returns:
        Status message with image URL or error information
    """
    try:
        # Validate prompt
        if not prompt or not prompt.strip():
            return "ERRO_GERACAO_IMAGEM: Prompt não pode estar vazio"

        # Validate and correct dimensions
        original_width, original_height = width, height
        if width < 64:
            width = 64
        elif width > 1024:
            width = 1024

        if height < 64:
            height = 64
        elif height > 1024:
            height = 1024

        # Warn if dimensions were corrected
        dimension_warning = ""
        try:
            if int(original_width) != width or int(original_height) != height:
                dimension_warning = f"\n*Nota: Dimensões ajustadas de {original_width}x{original_height} para {width}x{height}*"
        except (ValueError, TypeError):
            # If conversion fails, skip the warning
            pass

        # Format prompt for URL (handle special characters)
        # Replace spaces with %20 and handle other URL-unsafe characters
        formatted_prompt = prompt.strip().replace(" ", "%20")

        # Construct Pollinations.ai URL
        image_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width={width}&height={height}"

        # Try to generate the image with retry logic for better reliability
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # First try HEAD request to check if image exists
                    response = await client.head(image_url)

                    if response.status_code == 200:
                        # Image is ready
                        return f"IMAGEM_GERADA: {prompt}\nURL: {image_url}\nDimensões: {width}x{height}{dimension_warning}\n\n*Imagem gerada gratuitamente via Pollinations.ai*"
                    elif response.status_code == 429:
                        # Rate limited, wait and retry
                        if attempt < max_retries:
                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        else:
                            return f"ERRO_GERACAO_IMAGEM: Serviço sobrecarregado. Tente novamente em alguns momentos."
                    else:
                        # Other error, try GET request as fallback
                        get_response = await client.get(
                            image_url, follow_redirects=True
                        )
                        if get_response.status_code == 200:
                            return f"IMAGEM_GERADA: {prompt}\nURL: {image_url}\nDimensões: {width}x{height}{dimension_warning}\n\n*Imagem gerada gratuitamente via Pollinations.ai*"
                        elif attempt < max_retries:
                            await asyncio.sleep(2**attempt)
                            continue
                        else:
                            logger.error(
                                f"Image generation failed with status {response.status_code}"
                            )
                            return f"ERRO_GERACAO_IMAGEM: Falha ao gerar imagem. Status: {response.status_code}"

            except httpx.TimeoutException:
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    return f"ERRO_GERACAO_IMAGEM: Timeout ao gerar imagem. Tente com uma descrição mais simples."
            except Exception as e:
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    logger.error(f"Erro ao gerar imagem (tentativa {attempt + 1}): {e}")
                    if attempt == max_retries:
                        return f"ERRO_GERACAO_IMAGEM: Erro ao gerar imagem: {str(e)}"

        return f"ERRO_GERACAO_IMAGEM: Falha ao gerar imagem após várias tentativas."

    except Exception as e:
        logger.error(f"Erro inesperado ao gerar imagem: {e}")
        return f"ERRO_GERACAO_IMAGEM: Erro inesperado: {str(e)}"
