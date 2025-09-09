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
    url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
    # url = f"https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
    # Headers for the request
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*",
    }

    files = {
        "image": open(image_path, "rb"),
        }

    prompt = "Add wine-colored embroidery to the entire dress. Ensure the embroidery is subtle, elegant, and complements the original design. Use the same base image, retaining the original color, fabric, and overall design unless specified otherwise.\n"
    predefined_prompt = "\nAlways focus exclusively on Abaya dresses. Apply changes only as specified in the prompt. If no updates or changes to the color, fabric, or design are mentioned, retain all original features. Ensure the output maintains the modesty and elegance of an Abaya dress./n"
    
    search_prompt = "Full dress"
    
    final_prompt = prompt + predefined_prompt
    
    
    data={
        "prompt": final_prompt,
        "seed" : 357599080,
        # "negative_prompt" : negative_prompt,
        "search_prompt": search_prompt,
        "output_format": "webp",
    }
    # Make the POST request
    print("Image:", image_path)
    response = requests.post(url, headers=headers, files=files, data=data, verify=False)
    response_seed = response.headers.get("seed")
    response_meta_data = response.headers
    print(response_meta_data)
    output_path = f"xedited_image_seed_yyy_{response_seed}.jpeg"

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
    api_key="sk-kpVja5dlddttmGua4GASKdEUQPS45Tb0c0B0aimMni6MnQuL",
    image_path="image_seed_gen_357599080.jpeg",
)




def image_generate(api_key="sk-iigfQer6Ijp81NgdeYhSlj1sF3fUvBfgIOa5YBVyaTL6BpEn", prompt=None, output_format="jpeg"):

    # prompt = "Generate elegant abaya ensemble is perfect for a modern woman seeking both style and modesty in her wardrobe. The navy blue abaya is complemented beautifully by the white and beige V-line blazer, creating a sophisticated and chic look suitable for a variety of environments. Underneath, the beige dress maintains a harmonious color palette, while the white chiffon hijab adds a touch of airy elegance. The bell sleeves adorned with a small star pattern infuse the outfit with a unique flair, making it ideal for both formal and semi-formal occasions."
    # - A modest and beautifully styled hijab covering the face.
    predefined_prompt = """
        Generate hyper-Realistic full-length image of an Abaya dress. The image must include:
        - Full dress details from the hijab down to the feet.
        - Ensure the feet are visible, with elegant footwear complementing the Abaya.
        - Must generate only one dress with one person\n.
    """

    user_prompt = """
        Generate me an white color abaya design, add come designs on neck and on hands only.
    """

    final_prompt = predefined_prompt + user_prompt


    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*"
        }
        data = {
            "prompt" : final_prompt,
            # "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : 0,
            "output_format" : output_format,
            "model" : "sd3.5-large",
            "cfg_scale" : 8, 
        }
        response = requests.post(url, headers=headers, files={"none": ''}, data=data)
        response_seed = response.headers.get("seed")
        response_meta_data = response.headers
        output_path = f"image_seed_gen_{response_seed}.jpeg"
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print(f"Image successfully generated and saved to: {output_path}")
            return output_path
        else:
            raise Exception(f"API Error: {response.status_code} - {response.json()}")

    except Exception as e:
        raise Exception(f"Error generating image: {e}")


# # Example usage:
# image_generate()
