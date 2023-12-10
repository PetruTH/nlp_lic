import json
from pathlib import Path
import zipfile
import requests
import os
from tqdm import tqdm
import logging
from dexonline.util_data import (
    MAPARE_PATH,
    ID_TO_WORD_POS_PATH,
    WORD_TO_ID_POS_PATH,
    ID_TO_INFLECTED_FORMS_PATH,
    ALL_INFLECTED_FORMS_PATH,
    RELATION,
    TREE_ENTRY,
    ENTRY_LEXEME,
    SYNONYMS,
    json_archive,
    json_archive_url,
)


LOG_CONFIG = " [%(levelname)s] %(asctime)s %(name)s:%(lineno)d - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_CONFIG)


def unzip(archive_path, folder_choosen):
    logging.info("Unzipping jsons files")
    with zipfile.ZipFile(archive_path, "r") as arhiva:
        if not os.path.exists(folder_choosen):
            os.makedirs(folder_choosen)

        arhiva.extractall(folder_choosen)


def download_file(url, local_filename, chunk_size=128):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    logging.info("The download with jsons archive will start now!")
    with tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=local_filename,
    ) as pbar:
        with open(local_filename, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                pbar.update(len(data))
                file.write(data)

    return local_filename


def load_jsons():
    logging.info("Start loading needed data in memory!")

    if not os.path.exists(os.getcwd() / Path("util")):
        os.mkdir("util")

    if not os.path.exists(json_archive):
        download_file(json_archive_url, json_archive)
        unzip(json_archive, os.getcwd())
    elif not os.path.exists(ALL_INFLECTED_FORMS_PATH):
        unzip(json_archive, os.getcwd())

    mapare = json.load(open(MAPARE_PATH))
    all_inflected_forms = json.load(open(ALL_INFLECTED_FORMS_PATH))
    word_to_id_pos = json.load(open(WORD_TO_ID_POS_PATH))
    id_to_word_pos = json.load(open(ID_TO_WORD_POS_PATH))
    id_to_inflected_forms = json.load(open(ID_TO_INFLECTED_FORMS_PATH))
    entry_lexeme = json.load(open(ENTRY_LEXEME))
    tree_entry = json.load(open(TREE_ENTRY))
    relation = json.load(open(RELATION))
    synonyms = json.load(open(SYNONYMS))

    logging.info("The data from jsons files is now loaded in memory!")
    return (
        mapare,
        all_inflected_forms,
        word_to_id_pos,
        id_to_word_pos,
        id_to_inflected_forms,
        entry_lexeme,
        tree_entry,
        relation,
        synonyms,
    )
