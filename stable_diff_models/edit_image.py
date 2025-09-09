import requests
import json

def edit_image(api_key, image_path):
    """
    Edits an image using Stability AI's inpainting API.

    Parameters:
        api_key (str): API key for authentication.
        image_path (str): Path to the image file to be edited.
        mask_path (str): Path to the mask file specifying areas to edit.
        prompt (str): Text prompt describing the desired edit.
        output_path (str): Path to save the edited image.

    Returns:
        None
    """
    # API endpoint for Stability AI's inpainting
    # url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
    url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
    # Headers for the request
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*",
    }

    files = {
        "image": open(image_path, "rb"),
        }
    seed_value = image_path.split("_")[-1].split('.')[0]
    # breakpoint()

    user_prompt = "An abaya royal blue colored dress"
    
    # predefined_prompt = "\nAlways focus exclusively on Abaya dresses. Apply changes only as specified in the prompt. If no updates or changes to the color, fabric, or design are mentioned, retain all original features. Ensure the output maintains the modesty and elegance of an Abaya dress./n"

    # prompt = f"""
    # IMPORTANT NOTES: 
    # - Incorporate the requested design changes or features precisely as described.\n 
    # - Apply edits only to - the specified area without altering unrelated parts of the design.\n 
    # - Ensure edits apply only to the mentioned area (e.g., 'change the bottom part only without altering other parts') and retain the rest of the design untouched. \n
    # - The abaya should appear in a neutral setting or on a mannequin. \n
    # - The output must reflect a single, cohesive design. Do not change abaya dress color without USER INSTRUCTION.\n
    
    # USER INSTRUCTION : (({user_prompt})).
    # """
    
    search_prompt = "Abaya Dress only febric"
    negative_prompt = """Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or any other unrelated garments. Avoid adding unnecessary elements like accessories, hats, or backgrounds unrelated to abaya presentation. Keep the design focused only on the abaya without incorporating unrelated garments or elements.
    No low image quality, No sitting image, no half portrait image, no animated image, no catoon image.
    """

    # final_prompt =  predefined_prompt + prompt
    final_prompt =  user_prompt
    
    data={
        "prompt": final_prompt,
        # "search_prompt": search_prompt,
        "negative_prompt" : negative_prompt,
        "output_format": "jpeg",
        "seed": 0,
        "model": "sd3.5-large",


        "select_prompt": search_prompt,
        "grow_mask": 3
        # "image": open(image_path, "rb"),
    }
    # Make the POST request
    print("Generating Image:", image_path)
    response = requests.post(url, headers=headers, files=files, data=data)
    response_seed = response.headers.get("seed")
    response_meta_data = response.headers
    print(response_meta_data)
    output_path = f"xedited_image_seed_yyy___{response_seed}.jpeg"

    # Handle the response
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully edited and saved to {output_path}")
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.json()}")


# Example usage
import os
edit_image(
    api_key="sk-7eroyIQcdEq0Hy10CmF5LfztRTJuWUJ3rjEInzxlH66JtxQA",
    image_path="Amage_seed_gen4246354187.jpeg",
)

