import base64
import subprocess
from PIL import Image
import io

def encode_image(file_content: bytes, mime_type: str) -> str:
    """
    Encodes the image content to base64, converting it to JPEG if it's not already, including HEIC files.

    Args:
        file_content (bytes): The binary content of the image file.
        mime_type (str): The MIME type of the image.

    Returns:
        str: The base64 encoded JPEG image.
    """
    if mime_type == "image/heic":
        # Convert HEIC to JPEG using ImageMagick
        try:
            with io.BytesIO(file_content) as input_file:
                with io.BytesIO() as output_file:
                    subprocess.run(["magick", "convert", "heic:-", "jpeg:-"], input=input_file.read(), stdout=output_file, check=True)
                    file_content = output_file.getvalue()
            mime_type = "image/jpeg"  # Update mime type to JPEG
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to convert HEIC to JPEG: {e}")

    if not mime_type.endswith("jpeg") and not mime_type.endswith("jpg"):
        # Convert non-JPEG images to JPEG
        try:
            with Image.open(io.BytesIO(file_content)) as img:
                with io.BytesIO() as output:
                    img.convert("RGB").save(output, format="JPEG")
                    file_content = output.getvalue()
        except Exception as e:
            raise ValueError(f"Failed to convert image to JPEG: {e}")

    base64_encoded_image = base64.b64encode(file_content).decode('utf-8')
    return base64_encoded_image
