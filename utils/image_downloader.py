import os
import requests
from PIL import Image

def download_image(url, name, nfo_dir, min_height=300, poster=False):
    """
    Download an image from a URL and save it to the specified directory.
    If downloading a poster, check its height.

    Args:
        url (str): Image URL.
        name (str): Output filename (without extension).
        nfo_dir (str): Directory to save the image.
        min_poster_height (int): Minimum height for poster images.
        poster_check_name (str): If name matches this, check height.

    Returns:
        bool: True if download (and check) succeeded, False otherwise.
    """
    if not url:
        return False
    ext = os.path.splitext(url)[1] or ".jpg"
    path = os.path.join(nfo_dir, f"{name}{ext}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return False
        with open(path, "wb") as f:
            f.write(r.content)
        # If this a poster, verify dimensions
        if poster and name == "folder":
            with Image.open(path) as img:
                width, height = img.size
                if height < min_height:
                    os.remove(path)
                    return False
        return True
    except Exception as e:
        print(f"Error downloading {name}: {e}")
        return False

def crop_image(cover_path, poster_path, min_height=300):
    """
    Crop the cover image to create a poster image.

    Args:
        cover_path (str): Path to the cover image.
        poster_path (str): Path to save the cropped poster.
        min_height (int): Minimum height for the poster.

    Returns:
        bool: True if cropping and saving succeeded, False otherwise.
    """
    try:
        original_cover = Image.open(cover_path)
        width, height = original_cover.size
        left = width / 1.895734597
        top = 0
        right = width
        bottom = height
        cropped_cover = original_cover.crop((left, top, right, bottom))
        if cropped_cover.size[1] >= min_height:
            cropped_cover.save(poster_path)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error creating poster from cover: {e}")
        return False
