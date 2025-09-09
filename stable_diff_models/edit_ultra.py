import requests
import json
from openai import OpenAI
OPENAI_API_KEY=''


def enhance_user_prompt(prompt):
    """Sends a request to OpenAI API for image analysis."""
    client = OpenAI(
        api_key=OPENAI_API_KEY,  # This is the default and can be omitted
        )
    
    predefined_prompts = {
        "change the color": "Change the dress color to the specified shade without altering other design elements.",
        "modify the design": "Update the design of the abaya as specified, maintaining modesty and elegance.",
        "add a pattern": "Add the requested pattern to the abaya while keeping the rest of the design intact.",
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
                    "content": "You are a professional abaya dress designer assistant. Assist in creating elegant and modest abaya designs based on user requests."
                },
                {
                    "role": "user",
                    "content": prompt
                },
                ],
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        # Handle API errors gracefully
        return f"Error occurred in OpenAI: {e}"


def image_editing(api_key="sk-szs7VRAO0xA9TQ8bMMmO3VL1IIzk31Ua7LR2Qp3PKJTjNEK2"):

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

    # final_prompt = smart_prompt + predefined_prompt
    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        files = {"image" : open("edited_image_seed_3911952337.jpeg", "rb")}
        data = {
            "prompt" :  user_prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : 3911952337,
            "output_format" : "jpeg", 
            "strength" : 0.8,
        }
        breakpoint()
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
