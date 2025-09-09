import requests
import json


def image_generate(api_key="sk-0ewGjnJp69Fs9zhOzSE7GoaB4mrocTBzqkF6mFU2T6xHHDHO"):

    user_prompt = "Generate a royal blue color simple abaya design"
    predefined_prompt = """
        Generate hyper Realistic full-length image of an Abaya dress with beautifull face. The image must include:
        - Full dress from the hijab down to the feet.\n
        - Visibility of both Shoulers, both hands and the whole body must be front-facing in the portrait. .\n
        - The face and forehead of an Arabic girl should be visible and modestly framed with a scarf.\n
        - Ensure the heels or sendal are visible.\n
        """

    negative_prompt = """Exclude designs resembling non-abaya clothing such as shirts, pants, skirts, or any other unrelated garments. Avoid adding unnecessary elements like accessories, hats, or backgrounds unrelated to abaya presentation. Keep the design focused only on the abaya without incorporating unrelated garments or elements.
        sitting image, half portrait image, animated image, catoon image, text, watermarks, scarfless, transparent"""


    final_prompt = predefined_prompt + "\n" + user_prompt

    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        headers = {
            "authorization": f"Bearer {api_key}",
            "accept": "image/*",
        }
        data = {
            "prompt" : final_prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio" : "5:4",
            "seed" : 0,
            "output_format" : "webp",
        }
        response = requests.post(url, files={"none": ''}, headers=headers, data=data)
        response_seed = response.headers.get("seed")
        response_meta_data = response.headers
        output_path = f"generate/gen_{response_seed}.webp"
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
