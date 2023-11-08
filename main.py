import openai
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import json


def CallOpenAI():

    openai.api_key = "openai-key-goes-here"
    with open('data/org_data.txt', 'r', encoding='utf-8') as file:
        items = file.read().splitlines()

    target_nation = "german"
    target_list = ', '.join(items)
    prompt_list = f"Give me the {target_nation} item or person equivalent to each of these Swedish items or persons: {target_list}. Nostalgic wise." 
    prompt_opt = "Dont include an explenation of what the items or persons are. If it's an item it should be kinda similar so dont match a book with a tv series, and they need to hold kinda similar relevance."
    full_prompt = prompt_list + prompt_opt

    try:
        #What type of openai api we're using as well as some "context" messages
        #to help it understand what to send back, can cut this down if needed :)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who only answers with the name of what i'm asking for."},
                {"role": "user", "content": "Who's the american equivalent of swedens Olof Palme?"},
                {"role": "assistant", "content": "Olof Palme : John F. Kennedy"},
                {"role": "user", "content": "Who's the german equivalent of swedens Astrid Lindgren?"},
                {"role": "assistant", "content": "Astrid Lindgren : Erich Kästner"},
                {"role": "user", "content": full_prompt}
            ], max_tokens = 120
        )

        #Clearing the generated txt file before we populate it
        open(f'data/{target_nation}_data.txt', 'w').close()

        #Response
        final_items = response.choices[0].message['content'].strip()
        print(final_items)

        #Comment this & switch "result" with final_items in file.write if you want the org names as well
        lines = final_items.split('\n')
        names = [line.split(': ')[1] for line in lines]
        result = '\n'.join(names).strip()
        print(result)

        #Write the generated items to a new file
        with open(f'data/{target_nation}_data.txt', 'w', encoding='utf-8') as file:
            file.write(result)

    #OpenAI errors
    except openai.error.RateLimitError as error:
        print("Rate limit has likely been exceeded : ", error)

    except openai.error.OpenAIError as error:
        print("Error : ", error)


def FindImageUrl(name):
    #Example : quote('abc def') -> 'abc%20def'
    searchUrl = f"https://www.google.com/search?hl=en&tbm=isch&q={quote(name)}"
    response = requests.get(searchUrl)
    soup = BeautifulSoup(response.text, 'html.parser')

    #Find the images from the data we got back from beutifulsoup
    images = [img['src'] for img in soup.find_all('img')]
    if images:
        #Usually [1] is the logo for the items/person wiki
        return images[1]
    else:
        return None

def SaveImageToFolder(imageUrl, name, folder = 'images'):
    if imageUrl is not None:
        #Stream = true, means that the request does not immediately download the whole image
        #but downloads it in "chunks"
        response = requests.get(imageUrl, stream = True)
        if response.status_code == 200:
            #Check if the directory already exists, otherwise create one
            if not os.path.exists(folder):
                os.makedirs(folder)
        
            path = os.path.join(folder, f"{name.replace(' ', '_')}.jpg")
            with open(path, 'wb') as file: #wb -> writing in binary mode
                for img in response:       #Respone being the image we got back
                    file.write(img)        #"Write" the image to the file
            print(f"Saved image for : {name} -> {path}.")
        else:
            print(f"Failed to get image for : {name}.")


#"main" image webscraper method with default input
def GetImageFromFile(path = 'data/german_data.txt'):
    with open(path, 'r', encoding='utf-8') as file:
        names = file.read().splitlines()

    for name in names:
        imageUrl = FindImageUrl(name)
        SaveImageToFolder(imageUrl, name)


def GenerateJsonFromData(dataPath = 'data/german_data.txt', imageFolder = 'images', jsonFolder = 'json'):
    jsonDict = {}
    with open(dataPath, 'r', encoding='utf-8') as file:
        names = file.read().splitlines()

    #For each name in data/x_data.txt & match the image to them
    for name in names:
        imageFile = f"{name.replace(' ', '_')}.jpg"
        imagePath = os.path.join(imageFolder, imageFile)

        #Check if image exists
        if os.path.isfile(imagePath):
            jsonDict[name] = imagePath
        else:
            print(f"No image : {name}")
            jsonDict[name] = None

    if not os.path.exists(jsonFolder):
        os.makedirs(jsonFolder)

    #Write the dictionary to a JSON file
    with open('json/german_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(jsonDict, json_file, ensure_ascii = False, indent = 4)

    print('Json File Created.')

if __name__ == '__main__':
    CallOpenAI()
    GetImageFromFile()
    GenerateJsonFromData()
    
