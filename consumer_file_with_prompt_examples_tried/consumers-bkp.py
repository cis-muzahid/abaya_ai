import os
import re
import time
import json
import base64
from io import BytesIO

import requests
from openai import OpenAI

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

class ChatConsumer(WebsocketConsumer):
    DEFAULT_IMAGE_PATH = "http://localhost:8000/media/abaya1.webp"
    LOCAL_IMAGE_PATH = "http://localhost:8000/"

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        base64_image = data.get('image_url')
        reply_to_message = data.get('reply_to')
        print("Data:", data)

        if base64_image:
            # Handle base64 image
            try:
                saved_image_url = self.save_base64_image(base64_image)
                response = "Image uploaded successfully!"
                self.chat_send({
                    "response": response,
                    "image_url": saved_image_url,
                    "reply_to": reply_to_message, 
                })
            except Exception as e:
                # Handle decoding or saving errors
                self.chat_send({
                    "response": f"Failed to upload image: {str(e)}",
                    "image_url": saved_image_url,
                    "reply_to": reply_to_message, 
                })
        elif message and reply_to_message:
            # Process message with reply context
            try:
                breakpoint()
                edited_image_url = self.edit_image_with_prompt(prompt=message, previous_msg_image_path=reply_to_message)
                print(edited_image_url)
                self.chat_send({
                    "response": f"Here is your edited Abaya design for: {message}",
                    "image_url": edited_image_url,
                    "reply_to": reply_to_message,
                })
            except Exception as e:
                self.chat_send({
                    "response": f"Failed to edit image: {str(e)}",
                    "image_url": None,
                    "reply_to": reply_to_message,
                })
         
        else:
            # Process other text-based messages
            response = "Tell me your preferences: style, color, or length?"
            try:
                image_url = self.generate_dalle_image(message)
                self.chat_send({
                    "response": f"Here is your Abaya design for: {message}",
                    "image_url": image_url
                })
            except Exception as e:
                # Send fallback message with default image
                self.chat_send({
                    "response": f"Failed to generate design: {str(e)}",
                    "image_url": self.DEFAULT_IMAGE_PATH
                })

    def save_base64_image(self, base64_image):
        """
        Decodes a base64 image and saves it to the media directory.
        Returns the URL of the saved image.
        """
        img_format, img_str = base64_image.split(';base64,')
        ext = img_format.split('/')[-1]  # Extract the file extension (e.g., png, jpeg)
        # file_name = f"uploaded_{self.scope.get('session').session_key}.{ext}"
        file_name = f"image_{time.time()}.{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # self.LOCAL_IMAGE_PATH
        # Decode and save the image
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(img_str))

        # Generate path for the saved image
        file_path = f"{self.LOCAL_IMAGE_PATH}media/{file_name}"
        return file_path


    def chat_send(self, response_data):
        """
        Sends structured response data directly.
        """
        self.send(text_data=json.dumps(response_data))


    # API key and endpoint
    def generate_dalle_image(self, prompt):
        url = "https://api.openai.com/v1/images/generations"
        # size="1024x1024"
        size="256x256"
        
        n=1
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = "Your job is to generate PNG formatted image of abaya image only here is the prompt:" + prompt
        data = {
            "prompt": prompt,
            "n": n,
            "size": size
        }
        try:
            breakpoint()
            print("Generating the image..")
            response = requests.post(url, headers=headers, json=data, verify=False)
            response.raise_for_status()
            print("Generated DONE..")

            # Parse response and return URL(s) if successful
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                image_url = [item["url"] for item in result["data"]]
                return image_url
            else:
                return "No image URL returned. Please verify the request."
        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"
        except ValueError:
            return "Error parsing the response. Ensure the API returned a valid JSON."
        except KeyError:
            return "Unexpected response format. Could not find the expected data."



    def edit_image_with_prompt(self, prompt, previous_msg_image_path):
        """
        Combines a provided image with a prompt to generate a new image using DALL-E.
        """
        print("Editable prompt:", prompt)
        match = re.search(r'src=([^\s>]+)', previous_msg_image_path)
        if match:
            image_url = match.group(1)
            print("Extracted URL:", image_url)
        else:
            print("No URL found.")

        get_image = requests.get(image_url, verify=False)
        file_name = 'previous_image2.png'
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)



        if get_image.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(get_image.content)

            # Generate path for the saved image
            file_path = f"{self.LOCAL_IMAGE_PATH}media/{file_name}"
            size="256x256"
            n=1
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "multipart/form-data"
            }
            data = {
                "prompt": prompt,
                "n": n,
                "size": size,
                "image": open(file_path,'rb'),
            }
            url = 'https://api.openai.com/v1/images/edits'

            try:
                breakpoint()
                print("Editing the image..")
                response = requests.request("POST", url, headers=headers, data=data, verify=False)

                # response = requests.post(url, headers=headers, json=data, verify=False)
                breakpoint()
                response.raise_for_status()
                print("Edited DONE..")

                # Parse response and return URL(s) if successful
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    new_image_url = [item["url"] for item in result["data"]]
                    return new_image_url
                else:
                    return "No image URL returned. Please verify the request."
            except requests.exceptions.RequestException as e:
                return f"Request failed: {e}"
            except ValueError:
                return "Error parsing the response. Ensure the API returned a valid JSON."
            except KeyError:
                return "Unexpected response format. Could not find the expected data."







    # def generate_dalle_image(self, prompt):
    #     """
    #     Generate an image using DALL-E 3 based on the user prompt.
    #     """
    #     # Example prompt customization for Abaya design
    #     prompt = f"Generate a high-quality image of an Abaya design based on: {prompt}"
    #     response = client.images.generate(
    #         model="dall-e-3",
    #         prompt=prompt,
    #         size="1024x1024",
    #         quality="standard",
    #         n=1,
    #     )
    #     # Extract the image URL
    #     image_url = response['data'][0]['url']
    #     return image_url
