import os
import bpy
from .t3dn_bip import previews

icons_dir = os.path.join(os.path.dirname(__file__), "icons")


class RSN_Preview():
    def __init__(self, image, name):
        self.preview_collections = {}
        self.image = os.path.join(icons_dir, image)
        self.name = name

    def register(self):
        pcoll = previews.new(max_size=(96, 96))
        pcoll.load(self.name, self.image, 'IMAGE')
        self.preview_collections["adjt_icon"] = pcoll

    def unregister(self):
        for pcoll in self.preview_collections.values():
            previews.remove(pcoll)
        self.preview_collections.clear()

    def get_image(self):
        return self.preview_collections["adjt_icon"][self.name]

    def get_image_icon_id(self):
        image = self.get_image()
        return image.icon_id


class BatchPreview():
    def __init__(self, filter: str):
        self.images = []
        for file in os.listdir(icons_dir):
            if file.endswith(filter):
                img = RSN_Preview(name=file.split('.')[0], image=file)

                self.images.append(img)

    def register(self):
        for img in self.images: img.register()

    def unregister(self):
        for img in self.images:
            img.unregister()

    def get_icon(self, name):
        for img in self.images:
            if img.name == name: return img.get_image_icon_id()




