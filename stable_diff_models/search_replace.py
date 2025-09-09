import requests
import json
from openai import OpenAI
OPENAI_API_KEY=''



def image_editing(api_key="sk-pGQvI3GBEwQMjJrxbAsTdk5MFtZjxfOInwtcC8hDTzvfNSkA"):

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
    # smart_prompt = enhance_user_prompt(user_prompt)
    # print("Openai prompt: ", smart_prompt)
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

    user_prompt = "I want this dress in olive green color and rest design and all things remain same."
    search_prompt = 'Abaya dress'
    prompt = f"predefined_prompt:{predefined_prompt} + 'n/User prompt:- {user_prompt}'"
    try:
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        # files = {"image" : open("edited_image_seed_3911952337.jpeg", "rb")}
        files={
            "image": open("gen_1487559711.webp", "rb"),
            # "mask": open("MASKED_Abaya_gen_838743895.PNG", "rb"),
        }
        data = {
            "prompt" :  prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "search_prompt": search_prompt,
            "seed" : 1487559711,
            "output_format" : "webp", 
            # "strength" : 0.5,
        }
        print("Editing image...")
        response = requests.post(url, files=files, headers=headers, data=data)
        response_seed = response.headers.get("seed")
        output_path = f"replace/recolor_{response_seed}.webp"
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"Image replaced and saved to: {output_path}")
            return output_path
        else:
            raise Exception(f"API Error: {response.status_code} - {response.json()}")

    except Exception as e:
        raise Exception(f"Error generating image: {e}")


image_editing()
