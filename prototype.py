import spacy
import json
from spacy.tokens import Token

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

mapare = json.load(open('forme_morfologice.json'))
all_inflected_forms = json.load(open('inflected_form_lexemeId_inflectionId.json'))
word_to_id_pos = json.load(open('word_id_pos.json'))
id_to_word_pos = json.load(open('id_word_pos.json'))
id_to_inflected_forms = json.load(open('wordId_inflected_forms.json'))


def get_all_forms(token):
    """
        This function will return all the inflected forms for a certain token given as a parameter.
        It will search for that token in dexonline database and it will find the lexemeId. After, that,
        based on that lexemeId, it will return all inflected forms found with the same lexemeId (a list of
        dictionaries containig words form and morphological details also from dexonline database)
    """
    all_inflected_words_found = all_inflected_forms[token.text.lower()]
    id = ""
    
    words_prel = []
    for word in all_inflected_words_found:

        pos_found = mapare['DEXONLINE_MORPH'][str(word['inflectionId'])][1]
        if ud_to_dex[token.pos_] == pos_found:
            if str(word['lexemeId']) not in words_prel:
                words_prel.append(str(word['lexemeId']))

        elif ud_to_dex[token.pos_] == "M" and pos_found == "F":
            if str(word['lexemeId']) not in words_prel:
                words_prel.append(str(word['lexemeId']))

        elif ud_to_dex[token.pos_] == "M" and pos_found == "N":
            if str(word['lexemeId']) not in words_prel:
                words_prel.append(str(word['lexemeId']))
    
    words_prel.sort(key=lambda x: int(x))
    
    if len(words_prel) > 1:
        for element in words_prel:
            if id_to_word_pos[str(element)][0]['form'] == token.lemma_:
                id = element

    elif len(words_prel) == 1:
        id = words_prel[0]

    elif len(words_prel) == 0:
        words_prel = [str(x['id']) for x in word_to_id_pos[token.lemma_]]
        id = words_prel[0]
    
    result = id_to_inflected_forms[id]

    return result

def validate_token(token):
    """
        Function that validates if a token can be found in dexonline database. It will exclude words that
        describe names for example or places, organizations, etc.
    """
    if token.lang_ != "ro":
        return False
    if not token.text.isalpha():
        return False
    if token.ent_type_ in ["ORGANIZATION", "EVENT", "GPE", "LOC"]:
        return False
    if token.ent_type_ == "PERSON" and token.pos_ == "PROPN":
        print(f"Cuvantul: {token.text} este substantiv propriu de forma invariabila!\n\n\n")
        return False
    return True


"""
    There next two lines will add to Token from spacy two new features.
        forms_ -> will return each inflected form for a certain word
        is_valid -> will verify if token can be found in dexonline database based on the rules described before
"""
Token.set_extension("forms_", method=get_all_forms, force=True)
Token.set_extension("is_valid", method=validate_token, force=True)


"""
    Short demo to show how it actually works. Uncomment and run the main() function.
"""

# def main():
#     import time
#     t1 = time.time()
#     # reader = open("text.txt", "r")
#     # text = reader.read()
#     text = "Eu am fugit mâncând la cel mai apropiat magazin din sat pentru a-mi lua suc."

#     if "-" in text:
#         text = text.replace("-", " ")
#     nlp = spacy.load("ro_core_news_sm")
#     doc = nlp(text) 
#     for token in doc:
#         if token.pos_ not in ["PUNCT", "SPACE"]:
#             if token._.is_valid():
#                 print(token._.forms_())
#                 print("next")    
#     t2 = time.time() - t1
#     print("TIMP: ", t2)

# main()