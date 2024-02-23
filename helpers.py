import base64
import mimetypes
import os
import subprocess
from PIL import Image
import io

def encode_image(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError("Could not determine the MIME type of the image")

    # Determine if conversion is needed (for non-JPEG images)
    if mime_type != "image/jpeg":
        # Special handling for HEIC files using ImageMagick for conversion
        if mime_type == "image/heic":
            converted_image_path = image_path + ".jpeg"
            subprocess.run(["magick", "convert", image_path, converted_image_path], check=True)
            image_path = converted_image_path
        else:
            # For other non-JPEG formats, use Pillow for conversion
            with Image.open(image_path) as img:
                bytes_io = io.BytesIO()
                img.convert('RGB').save(bytes_io, format='JPEG', quality=85)
                base64_encoded_image = base64.b64encode(bytes_io.getvalue()).decode('utf-8')
                return base64_encoded_image, "image/jpeg"

    # Handle JPEG images directly without conversion
    with open(image_path, "rb") as image_file:
        base64_encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Clean up the converted file if it's from HEIC conversion
    if image_path.endswith(".jpeg"):
        os.remove(image_path)

    return base64_encoded_image, "image/jpeg"
