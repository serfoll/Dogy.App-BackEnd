import base64
import mimetypes
import subprocess
import os
from PIL import Image
import io

def encode_image(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError("Could not determine the MIME type of the image")

    # Special handling for HEIC files using ImageMagick for conversion
    if mime_type == "image/heic":
        converted_image_path = image_path + ".jpeg"
        subprocess.run(["magick", "convert", image_path, converted_image_path], check=True)
        image_path = converted_image_path
        mime_type = "image/jpeg"  # Update MIME type to JPEG after conversion

    with open(image_path, "rb") as image_file:
        base64_encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Clean up the converted file
    if mime_type == "image/jpeg" and image_path.endswith(".jpeg"):
        os.remove(image_path)

    return base64_encoded_image, mime_type
