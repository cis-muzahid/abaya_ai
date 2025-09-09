import requests
import json
from openai import OpenAI
OPENAI_API_KEY=''



def image_editing(api_key="sk-GLEriZVLJT4cJoyQ2gBeUgyX1WAfIJ2YDrCnZJRed9sB2THG"):

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

    user_prompt = 'Change the color of design to black'
    select_prompt = 'embroidery'
    try:
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        # files = {"image" : open("edited_image_seed_3911952337.jpeg", "rb")}
        files={
            "image": open("Abaya_gen_838743895.PNG", "rb"),
            # "mask": open("MASKED_Abaya_gen_838743895.PNG", "rb"),
        }
        data = {
            "prompt" :  user_prompt,
            # "negative_prompt": negative_prompt,
            "select_prompt": select_prompt,
            "seed" : 838743895,
            "output_format" : "webp", 
            # "strength" : 0.5,
        
        }
        response = requests.post(url, files=files, headers=headers, data=data)
        response_seed = response.headers.get("seed")
        output_path = f"recolor/recolor_{response_seed}.webp"
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"Image recolor and saved to: {output_path}")
            return output_path
        else:
            raise Exception(f"API Error: {response.status_code} - {response.json()}")

    except Exception as e:
        raise Exception(f"Error generating image: {e}")


image_editing()
