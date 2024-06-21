import json
from pathlib import Path
import zipfile
import requests
import os
from tqdm import tqdm
import logging
from dexflex.util_data import (
    MAPARE_PATH,
    ID_TO_WORD_POS_PATH,
    WORD_TO_ID_POS_PATH,
    ID_TO_INFLECTED_FORMS_PATH,
    ALL_INFLECTED_FORMS_PATH,
    RELATION,
    TREE_ENTRY,
    ENTRY_LEXEME,
    SYNONYMS,
    CONTEXT_PATH,
    json_archive,
    json_archive_url,
)
from dexflex.util_data import UNIDENTIFIED_TOKEN


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
        self.mapping = json.load(open(mapping_json))

    def find_dexonline_pos_id(self, inflectionId: str) -> str:
        return self.mapping["DEXONLINE_MORPH"].get(
                                                   str(inflectionId),
                                                   "UNKNOWN"
                                                )[1]

    def find_dexonline_pos_detail(self, inflectionId: str) -> str:
        return self.mapping["DEXONLINE_MORPH"].get(
                                                   str(inflectionId),
                                                   "UNKNOWN"
                                                )[0]


class IdToWordPos:
    def __init__(self, id_to_word_pos_json):
        self.id_to_word_pos = json.load(open(id_to_word_pos_json))

    def find_id_to_word_pos(self, id) -> str:
        return self.id_to_word_pos.get(str(id), "UNKNOWN")[0]

    def find_id_to_word_pos_form(self, id) -> str:
        return self.id_to_word_pos.get(str(id), "UNKNOWN")[0].get("form")


class IdToInflectedForms:
    def __init__(self, id_to_inflected_forms_json):
        self.id_to_inflected_forms = json.load(
                                        open(
                                            id_to_inflected_forms_json
                                            )
                                    )

    def find_id_to_inflected_forms(self, id) -> list:
        return self.id_to_inflected_forms.get(
            str(id), [{"form": "no pos", "pos": "no form"}]
        )


class EntryLexeme:
    def __init__(self, entry_lexeme_jsons):
        self.entry_lexeme = json.load(open(entry_lexeme_jsons))

    def find_entry_lexeme(self, id) -> list[str]:
        return self.entry_lexeme.get(str(id), ["no entry"])


class TreeEntry:
    def __init__(self, tree_entry_json):
        self.tree_entry = json.load(open(tree_entry_json))

    def find_tree_entry(self, id) -> list[str]:
        return self.tree_entry.get(str(id), ["no entry tree"])


class Relation:
    def __init__(self, relation_json):
        self.relation = json.load(open(relation_json))

    def find_relation(self, id) -> list[str]:
        return self.relation.get(str(id), ["no relation"])


class Synonyms:
    def __init__(self, synonyms_json):
        self.synonyms = json.load(open(synonyms_json))

    def find_synonyms(self, id) -> list[str]:
        return self.synonyms.get(str(id), ["no synonyms"])


class WordToIdPos:
    def __init__(self, word_to_id_pos_json):
        self.word_to_id_pos = json.load(open(word_to_id_pos_json))

    def find_word_id_pos(self, word) -> list[str]:
        return self.word_to_id_pos.get(word, [UNIDENTIFIED_TOKEN])

    def find_word_id_pos_double_verification(
        self, first_word, second_word
    ) -> list[str]:
        return self.word_to_id_pos.get(
                                        first_word,
                                        self.find_word_id_pos(second_word)
                                    )

class Context:
    def __init__(self, context):
        self.context = json.load(open(context))
    
    def find_context(self, treeId):
        return self.context.get(
                                str(treeId),
                                [UNIDENTIFIED_TOKEN]
                            )

class AllInflectedForms:
    def __init__(self, all_inflected_forms_json):
        self.all_inflected_forms = json.load(open(all_inflected_forms_json))

    def find_all_inflected_forms(
        self, word, unidentified=UNIDENTIFIED_TOKEN
    ) -> list[str]:
        return self.all_inflected_forms.get(word, [unidentified])

    def find_all_inflected_forms_double_verification(
        self, first_word, second_word, unidentified=UNIDENTIFIED_TOKEN
    ) -> list[str]:
        return self.all_inflected_forms.get(
            first_word,
            self.find_all_inflected_forms(
                                        second_word,
                                        unidentified=unidentified
                                    ),
        )


def load_jsons() -> tuple:
    logging.info("Start loading needed data in memory!")

    if not os.path.exists(os.getcwd() / Path("util")):
        os.mkdir("util")

    if not os.path.exists(json_archive):
        download_file(json_archive_url, json_archive)
        unzip(json_archive, os.getcwd())
    elif not os.path.exists(ALL_INFLECTED_FORMS_PATH):
        unzip(json_archive, os.getcwd())

    mapare = Mapare(MAPARE_PATH)
    logger.info("Mapare file loaded.")
    all_inflected_forms = AllInflectedForms(ALL_INFLECTED_FORMS_PATH)
    logger.info("All inflected forms file loaded.")
    word_to_id_pos = WordToIdPos(WORD_TO_ID_POS_PATH)
    logger.info("Mapping word to id and pos file loaded.")
    id_to_word_pos = IdToWordPos(ID_TO_WORD_POS_PATH)
    logger.info("Mapping word id to word and pos file loaded.")
    id_to_inflected_forms = IdToInflectedForms(ID_TO_INFLECTED_FORMS_PATH)
    logger.info("Mapping id to inflected forms file loaded.")
    entry_lexeme = EntryLexeme(ENTRY_LEXEME)
    logger.info("Mapping entry id to lexeme id file loaded.")
    tree_entry = TreeEntry(TREE_ENTRY)
    logger.info("Mapping tree id to entry id file loaded.")
    relation = Relation(RELATION)
    logger.info("Mapping meaning id to tree id file loaded.")
    synonyms = Synonyms(SYNONYMS)
    logger.info("Mapping synonyms file loaded.")
    context = Context(CONTEXT_PATH)
    logger.info("Mapping contexts file loaded.")

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
        context
    )
