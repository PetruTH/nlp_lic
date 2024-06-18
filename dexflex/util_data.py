banned_ent_types = {"ORGANIZATION", "EVENT", "GPE", "LOC"}
banned_pos = ["PUNCT", "SPACE"]
reflexive_deps = ["expl:poss", "expl:pv", "iobj", "obj"]
root_forms = ["ROOT", "advcl", "acl", "cop", "conj", "csubj", "ccomp:pmod", "parataxis", "ccomp"]

reflexive_short_to_long_form = {
    "mi-": "îmi",
    "ți-": "îți",
    "și-": "își",
    "v-": "vă",
    "s-": "se",
    "ne-": "ne",
    "te-": "te",
    "i-": "îi",
    "l-": "îl",
    "m-": "mă",
    "te-": "te",
    "Mi-": "Îmi",
    "Ți-": "Îți",
    "Și-": "Își",
    "V-": "Vă",
    "S-": "Se",
    "Ne-": "Ne",
    "Te-": "Te",
    "I-": "Îi",
    "L-": "Îl",
    "M-": "Mă",
    "Te-": "Te",

}

diacritics = {
      "ă": "a",
      "â": "a",
      "î": "i",
      "ș": "s",
      "ț": "t",
      "č": "c",
      "ş": "s",
      "ž": "z",
      "Ä": "A",
      "Â": "A",
      "Î": "I",
      "Ș": "S",
      "Ț": "T",
      "Č": "C",
      "Ș": "S",
      "Ž": "Z",
      "á": "a",
      "é": "e",
      "í": "i",
      "ó": "o",
      "ú": "u",
      "ű": "u",
      "Á": "A",
      "É": "E",
      "Í": "I",
      "Ó": "O",
      "Ú": "U",
      "Ű": "U",
      "ö": "o",
      "Ö": "O",
      "ü": "u",
      "Ü": "U",
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
    "ADJ": "A",
    "X": "V"
}
end_of_phrase = ["!", "?", ".", "\n"]

json_archive = "util/util.zip"
realeses_domain = "https://github.com/PetruTH/nlp_lic/releases/"
json_archive_url = f"{realeses_domain}download/Resources/util.zip"

UNIDENTIFIED_TOKEN = "unidentified"
MAPARE_PATH = "util/forme_morfologice.json"
CONTEXT_PATH = "util/context.json"
ALL_INFLECTED_FORMS_PATH = "util/inflected_form_lexemeId_inflectionId.json"
WORD_TO_ID_POS_PATH = "util/word_id_pos.json"
ID_TO_WORD_POS_PATH = "util/id_word_pos.json"
ID_TO_INFLECTED_FORMS_PATH = "util/wordId_inflected_forms.json"
RELATION = "util/relation.json"
TREE_ENTRY = "util/tree_entry.json"
ENTRY_LEXEME = "util/entry_lexeme.json"
SYNONYMS = "util/synonyms.json"
