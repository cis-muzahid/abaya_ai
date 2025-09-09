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

    current_api_key_index = 0
    API_KEYS = ['sk-pGQvI3GBEwQMjJrxbAsTdk5MFtZjxfOInwtcC8hDTzvfNSkA','sk-Gv2Z3SbKk3L8HP1dnNySMcCIaspS68U1MpRG5MEXQgNFuAUi','sk-kUKo7SWCvTV6wHj3pkRkC7V4Oa40cLrjTQDmHRf35JpgVeIH','sk-VSSMCDrfgEPVxBP3gSkoF0NPhr4mVkPSM1UcxjJkPevQmuhe','sk-HJWlwcVwvS5BW6H0BTOcWzvliqUsiZIRt3G6EzuDeWw9nhGs','sk-Z3WLhLhHSiSrQZXbTBMLKv2GlUEOrvQ3R92OXo21OYUCdeMC','sk-XVgDxOypAbxCWw7kdPGP7Lb9Y9VtxinucUN7i6Eq2yjul6UJ','sk-FeCoDIHj4jdgzvIoTbRslzbuEFuXXU2JWX10EWueaPadPmOl','sk-1v5tpKPNxCBA9j68j3Jvn1M6St0fcKjB26Is8wFreGLdqpn2','sk-BHUNL1kWcUugdPl5ottMcjDoAzosheTeDa4mka3CrZztkcuf','sk-BeYiFmaUYH9abX7YhkJIxUXR0DD4tWg5GQomz2vp1kzt2jRS','sk-Ln1Dokv6dxgK45eilwkcpUbb3w3OuIaMKLkq0DfZ8m06wRut','sk-TYvQ9DTvG69fMtNB5w3n8cUfr29zVe6SmBGVQC5mPnl7f1ZB','sk-oJ8MVbhtQOnzEnoNkhBnkNXL0zBWYkicJWsl5O19o81uz9eg','sk-PfTaeyZ1OOXHSFJFC4CR2ckDC5phs8KgrWObWsuKwtGokSpo']

    def connect(self):
        print("Socket Connected >>>>")
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
        user_previous_prompt = editable_image_data.get('previous_user_input') if editable_image_data is not None else None
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
                edited_image_url, generated_smart_prompt = self.edit_image_with_image_sd(edit_prompt_data, editable_image_url, user_previous_prompt)
                self.chat_send({
                    "response": generated_smart_prompt,
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
                    "response": f"{message}",
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
        predefined_prompt = """
            Generate hyper Realistic full-length image of an Abaya dress with beautifull face. The image must include:
            - Full dress from the hijab down to the feet.\n
            - The face and forehead of an Arabic girl should be visible and modestly framed with a scarf.\n
            - Ensure the heels or sendal are visible.\n
        """

        negative_prompt = """Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or any other unrelated garments. Avoid adding unnecessary elements like accessories, hats, or backgrounds unrelated to abaya presentation. Keep the design focused only on the abaya without incorporating unrelated garments or elements.
            sitting image, half portrait image, animated image, catoon image, text, watermarks, scarfless, transparent"""

        
        final_prompt = predefined_prompt + "\n" + user_prompt
        # EXPRIMENTAL >>>>>>>>>>>>>> REMOVE THIS SECTION AFTER TESTING
        # file_path = f"{self.LOCAL_IMAGE_PATH}media/edited_image_seed_352145038.jpeg"
        # import time
        # time.sleep(3)
        # return file_path
        # EXPRIMENTAL <<<<<<<<<<<<<<<<

        # url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

        data = {
            "prompt" : final_prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : 0,
            "output_format" : "jpeg",
        }

        # Attempt API call with rotation
        for _ in range(len(self.API_KEYS)):
            current_api_key = self.API_KEYS[self.current_api_key_index]
            headers = {
                "authorization": f"Bearer {current_api_key}",
                "accept": "image/*"
            }
            try:    
                print(f"Generating the image..")
                response = requests.post(url, headers=headers, files={"none": ''}, data=data)
                response_seed = response.headers.get("seed")
                dynamic_filename = f"Abaya_gen_{response_seed}.jpeg"
                abaya_gen_path = os.path.join(settings.MEDIA_ROOT, dynamic_filename) 

                if response.status_code == 200:
                    print(f"Key used ::{self.API_KEYS}")
                    with open(abaya_gen_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Image successfully generated and saved as: {abaya_gen_path}")
                    file_path = f"{self.LOCAL_IMAGE_PATH}media/{dynamic_filename}"
                    return file_path
                else:
                    self.current_api_key_index = (self.current_api_key_index + 1) % len(self.API_KEYS)
                    print(f"Error with API key {current_api_key}")
            except requests.exceptions.RequestException as e:
                self.current_api_key_index = (self.current_api_key_index + 1) % len(self.API_KEYS)
                print(f"Error with API key {current_api_key}")


    def edit_image_with_image_sd(self, user_prompts, editable_image_data, user_previous_prompt):
        """
        Combines a provided image with a prompt to generate a new image using DALL-E.
        """
        user_prompts = user_prompts.get('mainedit_message')
        # user_search_prompt = user_prompts.get('search_message')
        # search_prompt = f"Abaya Dress only febric {user_search_prompt}"
        # smart_prompt = self.enhance_user_prompt(user_prompts, user_previous_prompt)
        formatted_prompt = (
                f"{user_previous_prompt} but now {user_prompts}"
            )
        print("New edited prompt: ", formatted_prompt)
        smart_prompt = formatted_prompt
        predefined_prompt = """
            Focus exclusively on abaya dresses. Apply only the changes specified in the user prompt. 
            If no updates to the color, fabric, or design are mentioned, retain all original features. 
            Ensure the output maintains the modesty, elegance, and overall style of an abaya.
        """
        negative_prompt = """
            Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or other unrelated garments. 
            Avoid unnecessary elements like accessories, hats, or unrelated backgrounds. 
            Focus solely on the abaya. Ensure high image quality with a clear and cohesive design. 
            Avoid half-portraits, sitting poses, no side posses, animations, or cartoon-style images.
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
        # files = {"image": open(editable_image_path, "rb"),}
        files = {"none": ''}
        seed_value = image_url.split('_')[-1].split('.')[0]

        # if 'generate' in main_prompt.lower() or 'add' in main_prompt.lower() or 'fabric type' in main_prompt.lower():
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        data = {
            "prompt" :  smart_prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : seed_value,
            "output_format" : "jpeg", 
            # "strength" : 0.3,
        }
        # if 'change fabric color' in main_prompt.lower() or 'change dress color' in main_prompt.lower() or 'change fabric color' in main_prompt.lower():
        #     url, data = self.search_and_recolor(seed_value, smart_prompt, negative_prompt, search_prompt)
        # Attempt API call with rotation
        
        for _ in range(len(self.API_KEYS)):
            current_api_key = self.API_KEYS[self.current_api_key_index]
            headers = {
                "authorization": f"Bearer {current_api_key}",
                "accept": "image/*"
            }
            try:
                print("Editing in progress..", files)
                response = requests.post(url, headers=headers, files=files, data=data)
                if response.status_code == 200:
                    response_seed = response.headers.get("seed")
                    edited_image_name = f"edited_image_seed_{response_seed}.jpeg"
                    edited_image_path_dir = os.path.join(settings.MEDIA_ROOT, edited_image_name)
                    edited_image_path_local = f"{self.LOCAL_IMAGE_PATH}media/{edited_image_name}"
                    with open(edited_image_path_dir, 'wb') as file:
                        file.write(response.content)
                    print("Editing Finished..")
                    print(f"Image successfully generated and saved to: {edited_image_path_local} and {edited_image_path_local}")
                    return edited_image_path_local, smart_prompt
                else:
                    self.current_api_key_index = (self.current_api_key_index + 1) % len(self.API_KEYS)
                    print(f"Error with API key {current_api_key}")
                    # raise Exception(f"API Error: {response.status_code} - {response.json()}")
            except Exception as e:
                self.current_api_key_index = (self.current_api_key_index + 1) % len(self.API_KEYS)
                print(f"Error with API key {current_api_key}")


    def search_and_recolor(self, seed_value, smart_prompt, negative_prompt, search_prompt):
        print("Changing color...")
        url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
        data={
            "prompt": smart_prompt,
            # "search_prompt": search_prompt,
            "negative_prompt" : negative_prompt,
            "output_format": "jpeg",
            "seed": seed_value,
            "model": "sd3.5-large",
            "select_prompt": search_prompt,
            "grow_mask": 3
            }
        return url, data
        
    def enhance_user_prompt(self, prompt, user_previous_prompt):
        """Sends a request to OpenAI API for image analysis."""
        client = OpenAI(
            api_key=OPENAI_API_KEY,  # This is the default and can be omitted
            )
        predefined_prompts = f"""Your job is to enhance the `user_previous_prompt` prompt according abaya design for stable diffusion image generator, and add whatever is in `prompt` and make sensable sentance.\n

        NOTE: If user ask to change the fabric pattern, then modify the prompt for stable diffusion model.
        MUST FOLLOW ABAYA RULES, lIKE Always include hijab with the dress, Never generate like bikini.
        MUST INCLUDE SCARF ON HEAD AND FACE MUST BE VISIBLE.
        IN SIMPLE TERM:
        '{user_previous_prompt}' is the main message, and '{prompt}' is what user want to change in the previous message.
        """

        PREDEFINED_PROMPTS = """Your task is to preserve the content from `user_previous_prompt` and modify it based on `prompt`.\n
        Simply apply the specified changes while keeping everything else unchanged if not asked in `prompt`"""

        formatted_prompt = (
            f"user_previous_prompt: {user_previous_prompt}\n"
            f"prompt: {prompt}"
        )
        print("\n\nFormatted and edited Prompt by AI :", formatted_prompt, "\n\n")
        try:
            requested_prompt = predefined_prompts + user_previous_prompt + prompt
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional abaya dress designer assistant. Assist in generating the prompt based on user requests. Do not include extra design or patterns or color or etc if not mentioned in the prompt, keep the prompt short and meaningful. Do not include Example in the response."
                    },
                    {
                        "role": "user",
                        "content": f"{PREDEFINED_PROMPTS}\n\n{formatted_prompt}",
                    },
                    ],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            formatted_prompt = (
                f"{user_previous_prompt} but now the {prompt}"
            )
            # Handle API errors gracefully
            return f"Error occurred in OpenAI: {e}:: {formatted_prompt}"



