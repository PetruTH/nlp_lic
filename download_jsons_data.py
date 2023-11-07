import requests
import os

def download_json():
    folder_curent = os.getcwd()

    files_to_check = ["forme_morfologice.json", "id_word_pos.json", "inflected_form_lexemeId_inflectionId.json", "word_id_pos.json", "wordId_inflected_forms.json"]

    for file in files_to_check:
        file_path = os.path.join(folder_curent, file)
        
        if not os.path.exists(file_path):
            url = f"https://github.com/PetruTH/nlp_lic/releases/download/Resources/{file}.json"
            response = requests.get(url)
            print(file, "download")
            if response.status_code == 200:
                with open(f"{file}.json", "wb") as file:
                    file.write(response.content)

download_json()