from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import os
from django.conf import settings

def search_similar_images(query_image_path, image_paths):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Open query image from file path
    try:
        query_image = Image.open(query_image_path)
        query_inputs = processor(images=query_image, return_tensors="pt")
        query_features = model.get_image_features(**query_inputs)
    except Exception as e:
        print(f"Error opening query image {query_image_path}: {e}")
        return []

    similarities = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            inputs = processor(images=img, return_tensors="pt")
            features = model.get_image_features(**inputs)

            similarity = torch.nn.functional.cosine_similarity(query_features, features)
            similarities.append((img_path, similarity.item()))
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
            continue

    return sorted(similarities, key=lambda x: x[1], reverse=True)