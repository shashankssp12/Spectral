from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import requests
from io import BytesIO

def search_similar_images(query_image_url, image_urls):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    response = requests.get(query_image_url)
    query_image = Image.open(BytesIO(response.content))
    query_inputs = processor(images=query_image, return_tensors="pt")
    query_features = model.get_image_features(**query_inputs)

    similarities = []
    for img_url in image_urls:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))
        inputs = processor(images=img, return_tensors="pt")
        features = model.get_image_features(**inputs)

        similarity = torch.nn.functional.cosine_similarity(query_features, features)
        similarities.append((img_url, similarity.item()))

    return sorted(similarities, key=lambda x: x[1], reverse=True)