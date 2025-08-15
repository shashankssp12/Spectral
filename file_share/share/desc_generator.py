
import requests
import base64
import json
import os
from django.conf import settings
from PIL import Image
import io

def generate_tag(file_path):
  invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
  stream = True

  def get_base64_from_file(file_path):
      # Construct the full path to the file
      full_path = os.path.join(settings.MEDIA_ROOT, file_path)
      
      if not os.path.exists(full_path):
          raise ValueError(f"File does not exist: {full_path}")
      
      try:
          # Open and potentially resize the image
          with Image.open(full_path) as img:
              # Convert to RGB if necessary (for PNG with transparency, etc.)
              if img.mode != 'RGB':
                  img = img.convert('RGB')
              
              # Calculate the base64 size and resize if necessary
              img_copy = img.copy()
              quality = 85
              max_size = (1024, 1024)  # Maximum dimensions
              
              # Resize if image is too large
              if img_copy.size[0] > max_size[0] or img_copy.size[1] > max_size[1]:
                  img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
              
              # Keep reducing quality/size until base64 is under limit
              while True:
                  buffer = io.BytesIO()
                  img_copy.save(buffer, format='JPEG', quality=quality, optimize=True)
                  img_data = buffer.getvalue()
                  base64_data = base64.b64encode(img_data).decode()
                  
                  # Check if size is acceptable (less than 180KB in base64 to be safe)
                  if len(base64_data) < 180000:
                      return base64_data
                  
                  # Reduce quality or size further
                  if quality > 60:
                      quality -= 10
                  else:
                      # Further reduce dimensions
                      current_size = img_copy.size
                      new_size = (int(current_size[0] * 0.8), int(current_size[1] * 0.8))
                      if new_size[0] < 100 or new_size[1] < 100:
                          # Image too small, return what we have
                          return base64_data
                      img_copy = img_copy.resize(new_size, Image.Resampling.LANCZOS)
                      quality = 75  # Reset quality for smaller image
              
      except Exception as e:
          raise ValueError(f"Failed to process image: {str(e)}")

  try:
      image_b64 = get_base64_from_file(file_path)
  except Exception as e:
      print(f"Error processing image: {str(e)}")
      return "Unable to generate description for this image."

  headers = {
    "Authorization": "Bearer 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",
    "Accept": "text/event-stream" if stream else "application/json"
  }

  payload = {
    "model": 'microsoft/phi-3.5-vision-instruct',
    "messages": [
      {
        "role": "user",
        "content": f'Describe the image. <img src="data:image/jpeg;base64,{image_b64}" />'
      }
    ],
    "max_tokens": 512,
    "temperature": 0.20,
    "top_p": 0.70,
    "stream": stream
  }

  try:
      response = requests.post(invoke_url, headers=headers, json=payload)
      response.raise_for_status()  # Raise an exception for bad status codes
      
      message = ""
      result = []
      if stream:
          for line in response.iter_lines():
              if line:
                  decoded = line.decode("utf-8")
                  for line in decoded.strip().split("\n"):
                      if line.startswith("data: "):
                          message = line[len("data: "):]
                          result.append(message)
      else:
          print(response.json())

      if not result:
          return "Unable to generate description for this image."
          
      result.pop()  # Remove the last entry (usually [DONE])

      message = ""
      for entry in result:
          try:
              entry_data = json.loads(entry)
              content = entry_data["choices"][0]["delta"].get("content", "")
              if content:
                  message += content
          except (json.JSONDecodeError, KeyError, IndexError):
              continue

      # Remove potential prefix if it exists
      if message.startswith("data: "):
          message = message[6:]
          
      return message.strip() if message.strip() else "Unable to generate description for this image."
      
  except requests.RequestException as e:
      print(f"API request failed: {str(e)}")
      return "Unable to generate description due to API error."
  except Exception as e:
      print(f"Error generating image description: {str(e)}")
      return "Unable to generate description for this image."