banned_ent_types = {"ORGANIZATION", "EVENT", "GPE", "LOC"}
banned_pos = ["PUNCT", "SPACE"]
reflexive_deps = ["expl:poss", "expl:pv", "iobj", "obj"]
root_forms = ["ROOT", "advcl", "acl", "cop", "conj", "parataxis"]

reflexive_short_to_long_form = {
    "mi-": "îmi",
    "ți-": "îți",
    "și-": "își",
    "v-": "vă",
    "s-": "se",
    "ne-": "ne",
    "te-": "te"
}

ud_to_dex = {
        "VERB": "V",
        "AUX": "V",
        "PART": "I",
        "NOUN": "M",
        "PROPN": "SP",
        "PRON": "P",
        "DET": "P",
        "SCONJ": "I",
        "CCONJ": "I",
        "NUM": "P",
        "INTJ": "I",
        "ADV": "I",
        "ADP": "I",
        "ADJ": "A"
   }
end_of_phrase = ["!", "?", ".", "\n"]

json_archive = "util/utils_json.zip"
json_archive_url = f"https://github.com/PetruTH/nlp_lic/releases/download/Resources/utils_json.zip"
UNIDENTIFIED_TOKEN = "unidentified"
MAPARE_PATH = "util/forme_morfologice.json"
ALL_INFLECTED_FORMS_PATH = "util/inflected_form_lexemeId_inflectionId.json"
WORD_TO_ID_POS_PATH = "util/word_id_pos.json"
ID_TO_WORD_POS_PATH = "util/id_word_pos.json"
ID_TO_INFLECTED_FORMS_PATH = "util/wordId_inflected_forms.json"