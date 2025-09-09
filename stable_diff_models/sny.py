import requests
import json


def image_generate(api_key="sk-0MkpiZkHobkeP2HA9HiokCu3pqdvuGcra34wFBRmLeC0bSp2"):

    user_prompt = "Black dress "
    final_prompt = f"""  
    Generate hyper-Realistic full-length image of an Abaya dress. The image must include:
        - Full dress details from the hijab down to the feet.
        - Ensure the feet are visible, with elegant footwear complementing the Abaya.
        - Must generate only one dress with one person\n.
        NOTE: Follow abaya dressing rules.\n
    """


    negative_prompt = """Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or any other unrelated garments. Avoid adding unnecessary elements like accessories, hats, or backgrounds unrelated to abaya presentation. Keep the design focused only on the abaya without incorporating unrelated garments or elements.
    No sitting image, no half portrait image, no animated image, no catoon image.
    """


    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        files = {"image" : open("Emage_seed_gen_x_89532638.jpeg", "rb")}
        data = {
            "prompt" :  final_prompt + user_prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : 0,
            "output_format" : "jpeg", 
            "strength" : 0.85,
        }
        response = requests.post(url, files=files, headers=headers, data=data)
        response_seed = response.headers.get("seed")
        response_meta_data = response.headers
        output_path = f"Emage_seed_gen_x_y_z_a_w_{response_seed}.jpeg"
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
image_generate()
