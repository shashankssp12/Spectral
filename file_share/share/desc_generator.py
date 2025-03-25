
import requests
import base64
import json

def generate_tag(image_url):
  invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
  stream = True

  def get_base64_from_url(image_url):
      response = requests.get(image_url)
      if response.status_code == 200:
          return base64.b64encode(response.content).decode()
      else:
          raise ValueError(f"Failed to download image from URL. Status code: {response.status_code}")

  image_b64 = get_base64_from_url(image_url)

  assert len(image_b64) < 180_000, \
    "To upload larger images, use the assets API (see docs)"

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

  response = requests.post(invoke_url, headers=headers, json=payload)
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


  result.pop()

  for entry in result:
      entry = json.loads(entry)
      content = entry["choices"][0]["delta"]["content"]
      if content:
          message += content

  return message[6:]