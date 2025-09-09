import requests
import json
from openai import OpenAI


def image_editing(api_key="sk-AMpYFEIrbwrVLHEzbDiyaz2F6hYlLznImhgAorbF1subt12Q"):

    user_prompt = "Generate Chiffon Open Abaya Long Sleeve dress in dark purple color with gold beads."

    prompt = f"""
    IMPORTANT NOTES: 
    - Apply the requested changes precisely as described by the user.
    - Make edits only to the specified area, leaving unrelated parts of the design untouched.
    - Ensure the abaya appears in a neutral setting or on a mannequin.
    - Preserve the modesty and elegance of the abaya design.
    - Do not alter the dress color unless explicitly instructed by the user.

    USER INSTRUCTION: {user_prompt}
    """
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

    # final_prompt = smart_prompt + predefined_prompt
    user_prompt = 'erase the cloth and add embroidery from the image where highlighted in the mask image'
    try:
        url = "https://api.stability.ai/v2beta/stable-image/edit/erase"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        files={
            "image": open("Abaya_gen_838743895.PNG", "rb"),
            "mask": open("MASKED_Abaya_gen_838743895.PNG", "rb"),
        }
        data = {
            "output_format": "webp",
            "prompt" :  user_prompt,
            # # "negative_prompt": negative_prompt,
            # "aspect_ratio" : "5:4",
            # "seed" : 3911952337,
            # "output_format" : "jpeg", 
            # "strength" : 0.8,
        }
        response = requests.post(url, files=files, headers=headers, data=data)
        response_seed = response.headers.get("seed")
        output_path = f"AAEmage_seed_gen_x__w_{response_seed}.jpeg"
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"Image successfully generated and saved to: {output_path}")
            return output_path
        else:
            raise Exception(f"API Error: {response.status_code} - {response.json()}")

    except Exception as e:
        raise Exception(f"Error generating image: {e}")


image_editing()
