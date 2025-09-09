"""Stable diffussion"""

import os
import re
import time
import json
import base64
from io import BytesIO
from PIL import Image
import requests
from openai import OpenAI
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SD_API_KEY = os.getenv("SD_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

class ChatConsumer(WebsocketConsumer):
    USER_INPUT_LIST = []
    DEFAULT_IMAGE_PATH = "http://localhost:8000/media/abaya1.webp"
    LOCAL_IMAGE_PATH = "http://localhost:8000/"
    
    def connect(self):
        print("Connected >>>>")
        self.accept()

    def disconnect(self, close_code):
        print("DiConnected <<<<<<<")
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        edit_prompt_data = data.get('edit_prompt_data')
        base64_image = data.get('image_url')
        editable_image_data = data.get('reply_to')
        editable_image_url = editable_image_data.get('content') if editable_image_data is not None else None
        print("Data:", data)
        if base64_image:
            # Handle base64 image
            try:
                saved_image_url = self.save_base64_image(base64_image)
                response = "Image uploaded successfully!"
                self.chat_send({
                    "response": response,
                    "image_url": saved_image_url,
                    "reply_to": "reply_to_message", 
                })
            except Exception as e:
                # Handle decoding or saving errors
                self.chat_send({
                    "response": f"Failed to upload image: {str(e)}",
                    "image_url": saved_image_url,
                    "reply_to": "reply_to_message", 
                })
        elif edit_prompt_data and editable_image_url is not None:
            try:
                edited_image_url = self.edit_image_with_image_sd(edit_prompt_data, editable_image_url)
                self.chat_send({
                    "response": f"Here is your edited Abaya design",
                    "image_url": edited_image_url,
                    "reply_to": editable_image_url,
                })
            except Exception as e:
                self.chat_send({
                    "response": f"Failed to edit image.",
                    "image_url": None,
                    "reply_to": editable_image_url,
                })
        
        else:
            # Process other text-based messages
            try:
                image_url = self.generate_image_with_sd(message)
                self.chat_send({
                    "response": f"Here is your Abaya design for: {message}",
                    "image_url": image_url
                })
            except Exception as e:
                # Send fallback message with default image
                print(str(e))
                self.chat_send({
                    "response": f"Failed to generate design",
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
    def generate_image_with_sd(self, user_prompt):
        try:    
            predefined_prompt = """
                Generate hyper Realistic full-length image of an Abaya dress. The image must include:
                - Full dress details from the hijab down to the feet.\n
                - Ensure the feet are visible, with elegant footwear complementing the Abaya.\n
                - Must generate only one dress with one person\n.
            """

            negative_prompt = """Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or any other unrelated garments. Avoid adding unnecessary elements like accessories, hats, or backgrounds unrelated to abaya presentation. Keep the design focused only on the abaya without incorporating unrelated garments or elements.
            No sitting image, no half portrait image, no animated image, no catoon image, no text, no watermarks.
            """

            final_prompt = predefined_prompt + user_prompt
            # EXPRIMENTAL >>>>>>>>>>>>>> REMOVE THIS SECTION AFTER TESTING
            # file_path = f"{self.LOCAL_IMAGE_PATH}media/edited_image_seed_352145038.jpeg"
            # import time
            # time.sleep(3)
            # return file_path
            # EXPRIMENTAL <<<<<<<<<<<<<<<<


            # url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
            url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
            headers = {
                "authorization": f"Bearer {SD_API_KEY}",
                "accept": "image/*"
            }

            data = {
                "prompt" : final_prompt,
                "negative_prompt": negative_prompt,
                "aspect_ratio" : "5:4",
                "seed" : 0,
                "output_format" : "jpeg",
            }

            print(f"Generating the image..\nPayload: {data}\n\n")
            response = requests.post(url, headers=headers, files={"none": ''}, data=data)
            response_seed = response.headers.get("seed")
            dynamic_filename = f"Abaya_gen_{response_seed}.jpeg"
            abaya_gen_path = os.path.join(settings.MEDIA_ROOT, dynamic_filename) 

            if response.status_code == 200:
                with open(abaya_gen_path, 'wb') as file:
                    file.write(response.content)
                print(f"Image successfully generated and saved as: {abaya_gen_path}")
                file_path = f"{self.LOCAL_IMAGE_PATH}media/{dynamic_filename}"
                return file_path
            else:
                raise Exception(f"API Error: {response.status_code} - {response.json()}")
        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"
        except ValueError:
            return "Error parsing the response. Ensure the API returned a valid JSON."
        except KeyError:
            return "Unexpected response format. Could not find the expected data."


    def edit_image_with_image_sd(self, user_prompts, editable_image_data):
        """
            Combines a provided image with a prompt to generate a new image using DALL-E.
        """
        main_prompt = user_prompts.get('mainedit_message')
        user_search_prompt = user_prompts.get('search_message')
        search_prompt = "Abaya Dress only"
        user_prompts = f"{main_prompt} +\n Where to modify: {search_prompt}"
        
        smart_prompt = self.enhance_user_prompt(user_prompts)
        print("Openai prompt: ", smart_prompt)

        predefined_prompt = """
            Focus exclusively on abaya dresses. Apply only the changes specified in the user prompt. 
            If no updates to the color, fabric, or design are mentioned, retain all original features. 
            Ensure the output maintains the modesty, elegance, and overall style of an abaya.
        """
        negative_prompt = """
            Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or other unrelated garments. 
            Avoid unnecessary elements like accessories, hats, or unrelated backgrounds. 
            Focus solely on the abaya. Ensure high image quality with a clear and cohesive design. 
            Avoid half-portraits, sitting poses, animations, or cartoon-style images.
        """
        editable_image_url = re.search(r'src=([^\s>]+)', editable_image_data)

        if editable_image_url:
            image_url = editable_image_url.group(1)
            image_name = image_url.split('media/')[-1]
            print("Extracted URL:", image_url)
        else:
            print("No URL found.")
        headers = {
            "authorization": f"Bearer {SD_API_KEY}",
            "accept": "image/*"
        }
        editable_image_path = os.path.join(settings.MEDIA_ROOT, image_name)
        files = {"image": open(editable_image_path, "rb"),}
        seed_value = image_url.split('_')[-1].split('.')[0]

        self.handle_input(main_prompt, seed_value, smart_prompt, negative_prompt, search_prompt)
        
        data = regenerate_image_with_ultra(main_prompt, smart_prompt, negative_prompt, seed_value)
        try:
            print("Editing in progress..")
            response = requests.post(url, headers=headers, files=files, data=data)
            print("Response Meta data:: ", response.headers)
            if response.status_code == 200:
                response_seed = response.headers.get("seed")
                edited_image_name = f"edited_image_seed_{response_seed}.jpeg"
                edited_image_path_dir = os.path.join(settings.MEDIA_ROOT, edited_image_name)
                edited_image_path_local = f"{self.LOCAL_IMAGE_PATH}media/{edited_image_name}"
                with open(edited_image_path_dir, 'wb') as file:
                    file.write(response.content)
                print("Editing Finished..")
                print(f"Image successfully generated and saved to: {edited_image_path_local} and {edited_image_path_local}")
                return edited_image_path_local
            else:
                raise Exception(f"API Error: {response.status_code} - {response.json()}")
        except Exception as e:
            raise Exception(f"Error generating image: {e}")


    def enhance_user_prompt(self, prompt):
        """Sends a request to OpenAI API for image analysis."""
        client = OpenAI(
            api_key=OPENAI_API_KEY,  # This is the default and can be omitted
            )
        
        predefined_prompts = {
            "change the color": f"Change the dress color to the specified shade in the {prompt} and dress part without altering other design elements.",
            "modify the design": "Update the design of the abaya as specified in the {prompt}, maintaining modesty and elegance.",
            "add a pattern": "Add the requested pattern to the abaya in the {prompt} while keeping the rest of the design intact.",
        }
        # Normalize user input for matching (case-insensitive)
        normalized_prompt = prompt.strip().lower()
        
        # Check if the prompt matches predefined inputs
        for key, predefined_response in predefined_prompts.items():
            if key in normalized_prompt:
                prompt = predefined_response
                break
        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional abaya dress designer assistant. Assist in creating elegant and modest abaya designs based on user requests. Do not include extra design or patterns or color or etc if not mentioned in the prompt, keep the prompt short and meaningful."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                    ],
                max_tokens=50
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle API errors gracefully
            return f"Error occurred in OpenAI: {e}"


    def search_and_recolor(self, seed_value, smart_prompt, negative_prompt, search_prompt):
        """This function returns the URL and data required for changing the color of a dress, design, or pattern in an image using the Stability AI API"""
        print("Changing color...")
        url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
        data={
            "prompt": smart_prompt,
            "negative_prompt" : negative_prompt,
            "output_format": "jpeg",
            "seed": seed_value,
            "model": "sd3.5-large",
            "select_prompt": search_prompt,
            "grow_mask": 3
            }
        return url, data

    def search_and_replace(self, seed_value, smart_prompt, negative_prompt, search_prompt):
        """
            This function returns the URL and data required for replacing parts of an image, 
            such as the dress fabric material, dress part, or any existing part of the image, 
            using the Stability AI API.
        """
        print("Search and replacing...")
        url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
        data={
            "prompt": smart_prompt,
            "negative_prompt" : negative_prompt,
            "output_format": "jpeg",
            "seed": seed_value,
            "model": "sd3.5-large",
            "select_prompt": search_prompt,
            "grow_mask": 3,
            }          
        return url, data

    def handle_input(self, seed_value, smart_prompt, negative_prompt, search_prompt):
        functions = [
            {
                "name": "search_and_recolor",
                "description": "Change the color of a dress, design, or pattern in an image.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seed_value": {"type": "integer", "description": "The seed value for reproducibility."},
                        "smart_prompt": {"type": "string", "description": "The prompt describing the desired color change."},
                        "negative_prompt": {"type": "string", "description": "The negative prompt for the operation."},
                        "search_prompt": {"type": "string", "description": "The search term for locating the element to recolor."}
                    },
                    "required": ["seed_value", "smart_prompt", "negative_prompt", "search_prompt"]
                }
            },
            {
                "name": "search_and_replace",
                "description": "Replace parts of an image such as dress fabric, materials, or components.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seed_value": {"type": "integer", "description": "The seed value for reproducibility."},
                        "smart_prompt": {"type": "string", "description": "The prompt describing the replacement action."},
                        "negative_prompt": {"type": "string", "description": "The negative prompt for the operation."},
                        "search_prompt": {"type": "string", "description": "The search term for locating the element to replace."}
                    },
                    "required": ["seed_value", "smart_prompt", "negative_prompt", "search_prompt"]
                }
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that decides which function to call based on user input."},
                {"role": "user", "content": user_input}
            ],
            functions=functions,
            function_call="auto"  # Let OpenAI decide which function to call
        )

        # Parse the response to determine which function to execute
        breakpoint()
        if "function_call" in response["choices"][0]["message"]:
            function_call = response["choices"][0]["message"]["function_call"]
            function_name = function_call["name"]
            arguments = eval(function_call.get("arguments", "{}"))
            
            # Call the appropriate function with extracted arguments
            if function_name == "search_and_recolor":
                seed_value = arguments.get("seed_value")
                smart_prompt = arguments.get("smart_prompt")
                negative_prompt = arguments.get("negative_prompt")
                search_prompt = arguments.get("search_prompt")
                self.search_and_recolor(seed_value, smart_prompt, negative_prompt, search_prompt)
            elif function_name == "search_and_replace":
                seed_value = arguments.get("seed_value")
                smart_prompt = arguments.get("smart_prompt")
                negative_prompt = arguments.get("negative_prompt")
                search_prompt = arguments.get("search_prompt")
                self.search_and_replace(seed_value, smart_prompt, negative_prompt, search_prompt)
