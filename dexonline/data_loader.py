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

logger = logging.getLogger(__name__)

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


class Mapare:
    def __init__(self, mapping_json) -> None:
        self.mapping = mapping_json
    
    def find_dexonline_pos_id(self, inflectionId):
        return self.mapping["DEXONLINE_MORPH"].get(
                str(inflectionId),
                "UNKNOWN"
            )[1]

    def find_dexonline_pos_detail(self, inflectionId):
        return self.mapping["DEXONLINE_MORPH"].get(
                str(inflectionId),
                "UNKNOWN"
            )[0]


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
    logger.info("Mapare file loaded.")
    all_inflected_forms = json.load(open(ALL_INFLECTED_FORMS_PATH))
    logger.info("All inflected forms file loaded.")
    word_to_id_pos = json.load(open(WORD_TO_ID_POS_PATH))
    logger.info("Mapping word to id and pos file loaded.")
    id_to_word_pos = json.load(open(ID_TO_WORD_POS_PATH))
    logger.info("Mapping word id to word and pos file loaded.")
    id_to_inflected_forms = json.load(open(ID_TO_INFLECTED_FORMS_PATH))
    logger.info("Mapping id to inflected forms file loaded.")
    entry_lexeme = json.load(open(ENTRY_LEXEME))
    logger.info("Mapping entry id to lexeme id file loaded.")
    tree_entry = json.load(open(TREE_ENTRY))
    logger.info("Mapping tree id to entry id file loaded.")
    relation = json.load(open(RELATION))
    logger.info("Mapping meaning id to tree id file loaded.")
    synonyms = json.load(open(SYNONYMS))
    logger.info("Mapping synonyms file loaded.")

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
