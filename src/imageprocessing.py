import os
from PIL import Image
import io

class ProcessImage:
    def __init__(self, path, name, artist, album):
        self.path = path
        self.name = name
        self.artist = artist
        self.album = album
    async def img_path(self):
        for entry in os.scandir(self.path):
            if entry.is_file() and 'cover' in entry.name.lower():
                image_path = os.path.join(self.path, entry.name)
                image_resized = await self.resize_image(image_path)
                return image_resized
            else:
                continue
            return False

    async def resize_image(self, image_path, quality=100):
        with open(image_path, "rb") as f:
            image_data = f.read()
        # Open the image from bytes
        img = Image.open(io.BytesIO(image_data))
        
        # Resize (ANTIALIAS is deprecated, use LANCZOS or BILINEAR)
        img = img.resize((600, 600), resample=5, reducing_gap=3)
        
        img.save(f'{os.getcwd()}/tmp/{self.name}/cover.png')
        return f'{os.getcwd()}/tmp/{self.name}/cover.png'


