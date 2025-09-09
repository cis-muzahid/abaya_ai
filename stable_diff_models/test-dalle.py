import requests
import ssl
import requests
from openai import OpenAI
import os
import certifi
import base64
#custom_ca_cert_path = "/home/cis/Fortinet_CA_SSL.cer"
#OpenAI.verify_ssl = certifi.where()
import warnings
custom_ca_cert_path = "/home/cis/Fortinet_CA_SSL.cer"

session = requests.Session()
session.verify = custom_ca_cert_path  # Use Fortinet_CA_SSL.cer for SSL verification


warnings.filterwarnings("ignore", message="Unverified HTTPS request")
OpenAI.verify_ssl = False
session = requests.Session()
session.verify = False  # Bypass SSL verification (debugging only)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY=""
client = OpenAI(api_key=OPENAI_API_KEY)
# Disable SSL verification globally in requests
requests.packages.urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context


def generate_dalle_image(prompt):
    """
    Generate an image using DALL-E 3 based on the user prompt.
    """
    # Customize the prompt
    prompt = f"Generate a high-quality image of an Abaya design based on: {prompt}"
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
        # Extract the image URL
    breakpoint()
    image_url = response.data[0].url
    return image_url

# generate_dalle_image("generate abaya image")



# api_key = ""
# url = "https://api.openai.com/v1/images/generations"

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# data = {
#     "prompt": "Design an abaya with a deep black base color and intricate golden floral embroidery along the sleeves and hemline. The fabric should be lightweight chiffon, with a flowy A-line cut and a front-open style adorned with a delicate gold trim. Add a matching black chiffon hijab with a golden edge to complete the look.",
#     "n": 1,
#     "size": "1024x1024"
# }

# response = requests.post(url, headers=headers, json=data,verify=False)

# if response.status_code == 200:
#     print("Image generated:", response.json()["data"][0]["url"])
# else:
#     print("Error:", response.json())




# def edit_image():
#     prompt = 'change color to red'
#     file_name = '/home/cis/ABAYA_ai/abaya_design/media/test.png'
#     files=[('image',('test.png',open('/home/cis/Downloads/test.png','rb'),'image/png'))]
#     size="256x256"
#     n=1
#     breakpoint()

#     headers = {
#         "Authorization": f"Bearer {OPENAI_API_KEY}",
#         "Content-Type": "multipart/form-data"
#     }
#     data = {
#         "prompt": prompt,
#         "n": n,
#         "size": size,
#         "image": open(file_name,'rb'),
#     }
#     payload = {'prompt': 'change background to blue','n': '1','size': '256x256'}

#     url = 'https://api.openai.com/v1/images/edits'
#     breakpoint()
#     response = requests.request("POST", url, headers=headers, data=data, verify=False)
#     response = requests.request("POST", url, headers=headers, data=payload, files=files,verify=False)
#     response = requests.post(url, headers=headers, json=payload, files=files, verify=False)
# edit_image()




def edit_image_with_prompt(new_prompt):
    from PIL import Image
    """
    Combines a provided image with a prompt to generate a new image using DALL-E.
    """

    # get_image = requests.get(image_url, verify=False)
    # image_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-CUtjNXOgfxEqMoTD6bCDytzh/user-nJoxdOWshu2qEnrE4Stkkcwd/img-4ILmUS0xAKFCsZYQxnTZjyAJ.png?st=2024-12-12T12%3A47%3A11Z&se=2024-12-12T14%3A47%3A11Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-12-12T04%3A32%3A39Z&ske=2024-12-13T04%3A32%3A39Z&sks=b&skv=2024-08-04&sig=bvw2oxfavJuGG23oMzWFdVdUtB3B3sovzbidcxQ66jQ%3D"
    # tmpImg = Image.open(requests.get(image_url, stream=True, verify=False).raw).convert("RGBA")
    original_file_name = 'Abaya_gen_838743895.PNG'
    mask_file_name = 'masked_imgpsh_fullsize_anim.PNG'
    # tmpImg = Image.open(requests.get(image_url, stream=True, verify=False).raw).convert("RGBA")
    

    # original_file_name = 'computer.png'
    # mask_file_name = 'mask.png'


    # prompt = """
    # 1. Your job is to do updation in the image that is passing in image parameter. 2. Do not change the whole image like keep the same dress, pattern, size, dimentions, base color, You need to spot the masked image, Just update whatever is passed in the promt: """+ new_prompt
    
    
    # PROMPT = "A 90s vaporwave computer showing Rick Astley on the screen"
    # PROMPT = """Modify the design of the right-hand area of the abaya where it is masked. Replace the existing embroidery with an intricate floral lace pattern featuring silver and pearl-like details. Ensure the design seamlessly integrates with the overall black and gold aesthetic of the abaya, keeping the fabric texture consistent and maintaining the luxurious appearance of the dress."""
    PROMPT = "~ patterns within the specified masked area, ensuring the embroidery complements the overall aesthetic and flows seamlessly with the existing design."
    PROMPT = 'Add white color embroidery designs on the selected area that is neck'
            
    print("Editing the image..")    
    response = client.images.edit(
        image = open(original_file_name,"rb"),
        mask = open(mask_file_name,"rb"),
        prompt=PROMPT,
        n=1,
        size="256x256",
        # size="1024x1024",
    )
    print("Edited DONE..")
    print(response)
    new_image_url = response.data[0].url
    print("Edited image: ", new_image_url)
    return new_image_url

rsponse = edit_image_with_prompt("Add red color designs")
