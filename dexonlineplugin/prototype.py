import json
import zipfile
import requests
from tqdm import tqdm
from spacy.tokens import Token, Doc
import os
from util.util_data import *
import logging
LOG_CONFIG = (
    " [%(levelname)s] %(asctime)s %(name)s:%(lineno)d - %(message)s"
)
logging.basicConfig(level=logging.INFO, format=LOG_CONFIG)

mapare = {}
all_inflected_forms = {}
word_to_id_pos = {}
id_to_word_pos = {}
id_to_inflected_forms = {}


def unzip(archive_path, folder_choosen):
    logging.info("Unzipping jsons files")
    with zipfile.ZipFile(archive_path, 'r') as arhiva:
        if not os.path.exists(folder_choosen):
            os.makedirs(folder_choosen)

        arhiva.extractall(folder_choosen)



def download_file(url, local_filename, chunk_size=128):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    logging.info("The download with jsons archive will start now!")
    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=local_filename) as pbar:
        with open(local_filename, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                pbar.update(len(data))
                file.write(data)

    return local_filename


def load_jsons():
    global mapare, all_inflected_forms, word_to_id_pos, id_to_word_pos, id_to_inflected_forms
    logging.info("Start loading needed data in memory!")

    if not os.path.exists(json_archive):
        download_file(json_archive_url, json_archive)
        unzip(json_archive, "util")
            
    mapare = json.load(open(MAPARE_PATH))
    all_inflected_forms = json.load(open(ALL_INFLECTED_FORMS_PATH))
    word_to_id_pos = json.load(open(WORD_TO_ID_POS_PATH))
    id_to_word_pos = json.load(open(ID_TO_WORD_POS_PATH))
    id_to_inflected_forms = json.load(open(ID_TO_INFLECTED_FORMS_PATH))

    logging.info("The data from jsons files is now loaded in memory!")

load_jsons()


def get_all_forms_worker(token):
    """this function will extract every word that has an inflected form like token.text"""
    token_text = token.text
    if "-" in token.text:
        token_text = token_text.replace("-", "")
        
    
    all_inflected_words_found = all_inflected_forms.get(token_text, 
                                                        all_inflected_forms.get(
                                                            token_text.lower(),
                                                            UNIDENTIFIED_TOKEN))

    if all_inflected_words_found == UNIDENTIFIED_TOKEN:
        return []
    
    words_prel = []
    only_one_word = [word['lexemeId'] for word in all_inflected_words_found]

    if len(set(only_one_word)) == 1:
        words_prel.append(str(only_one_word[0]))

    for word in all_inflected_words_found:
        pos_found = mapare['DEXONLINE_MORPH'][str(word['inflectionId'])][1]
        # mapare['DEXONLINE_MORPH']: ["morph dexonline", "pos dexonline"], 
        # this will help for mapping spacy pos to dexonline pos
        # mapping spacy pos with dexonline pos looking after an id found from dexonline

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

    return words_prel

def get_all_forms(token):
    """
        This function will return all the inflected forms for a certain token given as a parameter.
        It will search for that token in dexonline database and it will find the lexemeId. 
        Based on get_all_forms_worker, it will choose the word from the list returned that
        has lemma like the first form found in dexonline database. After, that,
        based on that lexemeId, it will return all inflected forms found with the same lexemeId (a list of
        dictionaries containig words form and morphological details also from dexonline database)
    """
    words_prel = []
    token_text = token.text

    if len(words_prel) > 1:
        for element in words_prel:
            if id_to_word_pos[str(element)][0]['form'] == token.lemma_:
                id = element

    elif len(words_prel) == 1:
        id = words_prel[0]

    elif len(words_prel) == 0:
        words_found = word_to_id_pos.get(token.lemma_, 
                                            word_to_id_pos.get(token_text, 
                                                            UNIDENTIFIED_TOKEN))
        
        if words_found != UNIDENTIFIED_TOKEN:
            words_prel = [str(x['id']) for x in words_found]
            id = words_prel[0]
        else:
            return []

    result = id_to_inflected_forms[id]

    return result

def validate_token(token):
    """
        Function that validates if a token can be found in dexonline database. It will exclude words that
        describe names for example or places, organizations, etc.
    """
    if "-" in token.text:
        return True
    if token.pos_ in banned_pos:
        return False
    if token.lang_ != "ro":
        return False
    if not token.text.isalpha():
        return False
    if token.ent_type_ in banned_ent_types:
        return False
    return True

def get_wanted_form(token, pos_finder, person, number):
    """
       This function will return the morph form wanted by pos_finder, person and number
    """
    all_morph = get_all_forms(token)
    for wanted_form in all_morph:
        if pos_finder in wanted_form['pos'] and person in wanted_form['pos'] and number in wanted_form['pos']:
            return wanted_form['form']

def verify_word_at_certain_pos(token, pos_verifier):
    """
    verifiy if a token is contains a specified string in its part of speech
    for example this function will return true if a verb has this description from dexonline
    as its pos "Verb, Indicativ, perfect simplu, persoana I, singular" and pos_verifier parameter
    is "perfect simplu" or "persoana I", etc  
    """
    all_morph = get_all_forms(token)
    for wanted_form in all_morph:
        if token.text == wanted_form['form']:
            for pos in pos_verifier:
                if pos in wanted_form['pos']:
                    return True

def get_right_person_and_number(token):
    """
        This function will get the person and number data from token.morph and will convert these into
        dexonline database format information in order to select right form of verb.
    """
    # extract correct person and number for a phrase
    person = token.morph.get("Person") if token.morph.get("Person") else ['3']
    number = token.morph.get("Number") if token.morph.get("Number") else ['Sing']
    # extra step to verify if there is a composed subject (like 'eu cu tine mergem')
    ok_switch_number = 0
    if not token.pos_ == "VERB" and not token.pos_ == "AUX":
        if len(list(token.children)):
            for t in token.children:
                if t.text not in ["m", "te", "s"]:
                    ok_switch_number = 1 
                    break
    if ok_switch_number:
            number = ["Plur"]

    #formatting number and person to be recognized dexonline json
    actual_number = "plural" if number == ["Plur"] else "singular"

    if person == ['1']:
        actual_person = "I"
    elif person == ['2']:
        actual_person = "II"
    elif person == ['3']:
        actual_person = "III"

    return actual_number, actual_person

def forme_reflexive_verifier(token):
    """
        This function will map short reflexive forms into long ones using data from reflexive_deps from util_data.py
    """
    word_added = token.text
    if token.dep_ in reflexive_deps:
        if token.morph.get("Case")[0] in ["Dat", "Acc"] and token.morph.get("Variant")[0] == "Short":
            word_added = reflexive_short_to_long_form[token.text]

    return word_added

def oltenizare_worker(doc):
    """
        This function will find every at a perfect present tense and turn it into its past perfect form. 
    """
    new_phrase = []
    actual_person = ""
    actual_number = ""
    
    for i in range(0, len(doc)):
        if doc[i].pos_ not in banned_pos:

            if doc[i].dep_ == "nsubj" or doc[i].dep_ == "nsubj:pass":
                # extracting data from the phrase-subject to get the right form of verb
                # there will be needed for person and number 
                actual_number, actual_person = get_right_person_and_number(doc[i])
                new_phrase.append(doc[i].text if doc[i].text != "s" else "se")

            elif doc[i].dep_ == "ROOT" and doc[i-1].dep_ == "aux:pass" and doc[i-2].dep_ == "aux":
                # if doc[i-1].morph.get
                # handle cases like these: "Eu am fost plecat."
                if actual_person == "" and actual_number == "":
                    actual_number, actual_person = get_right_person_and_number(doc[i-2])

                new_phrase.append(get_wanted_form(doc[i-1], "perfect simplu", actual_person, actual_number))
                new_phrase.append(doc[i].text)
            
            elif doc[i].dep_ == "ROOT" and doc[i-1].dep_ == "cc" and doc[i-2].dep_ == "aux":
                if actual_person == "" and actual_number == "":
                    actual_number, actual_person = get_right_person_and_number(doc[i-2])

                new_phrase.append(get_wanted_form(doc[i], "perfect simplu", actual_person, actual_number))
            

            elif doc[i].dep_ in root_forms and doc[i-1].dep_ == "aux":
                if doc[i-2].dep_ == "aux":
                    new_phrase += [doc[i-2].text, doc[i-1].text, doc[i].text]
                    i+=2
                
                else:
                    #handle cases like these: "Eu am plecat"
                    # ensure that the construction found (aux + verb) is not at a future tense
                    if doc[i].morph.get("VerbForm")[0] != "Inf":
                        if doc[i-1].pos_ == "AUX":
                            if actual_person == "" and actual_number == "":
                                # if person and number paramateres cant be found from subject of a phrase,
                                # the verb will get this from its inflection
                                actual_number, actual_person = get_right_person_and_number(doc[i-1])

                            new_phrase.append(get_wanted_form(doc[i], "perfect simplu", actual_person, actual_number))

                        else:
                            # trick to handle exceptions found
                            if actual_person == "" and actual_number == "":
                                actual_number, actual_person = get_right_person_and_number(doc[i-1])
                            
                            new_phrase.append(doc[i].text)
                    else:
                        # the construction is at a future tense
                        new_phrase.append(doc[i-1].text)
                        new_phrase.append(doc[i].text)
            
            elif doc[i].dep_ == "aux:pass" and doc[i].lemma_ == "fi":
                if doc[i-1].dep_ == "aux":
                    pass
                else:
                    new_phrase.append(doc[i].text)

            elif doc[i].dep_ == "aux":
                pass
            
            else:
                if doc[i].pos_ == "PRON":
                    if doc[i].text[-1] == "-":
                        word_added = forme_reflexive_verifier(doc[i])  
                    else:
                        word_added = doc[i].text 
                else:
                    word_added = doc[i].text   
                new_phrase.append(word_added)
        else:
            new_phrase.append(doc[i].text)
            actual_number, actual_person = "", ""
    
    return new_phrase

def oltenizare(doc):
    new_phrase = oltenizare_worker(doc)
    phrase_to_return = ""

    for i in range(len(new_phrase)):
        # building the initial phrase back following the next rule: word, word (or any other PUNCT)
        # edge-case 1: for "-" where the rule is word-word
        # edge-case 2: word. Word (the same for ?, !, \n)
        if "-" in new_phrase[i]:
            phrase_to_return += " " + new_phrase[i]
        elif not new_phrase[i].isalpha():
            phrase_to_return +=  new_phrase[i]
        else:
            if new_phrase[i-1] in end_of_phrase:
                phrase_to_return += " " + new_phrase[i].capitalize()
            elif new_phrase[i-1][-1] == "-":
                phrase_to_return += new_phrase[i]
            else: 
                phrase_to_return += " " + new_phrase[i]

    return phrase_to_return

"""
    There next three lines will add to Token and Doc from spacy three new features.
        forms_ -> will return each inflected form for a certain word
        is_valid -> will verify if token can be found in dexonline database based on the rules described before
        oltenizare -> will automatically change tense of verbs from: present perfect (perfect compus) to: past perfect (perfect simplu)
"""
Token.set_extension("forms_", method=get_all_forms, force=True)
Token.set_extension("is_valid", method=validate_token, force=True)
Doc.set_extension("oltenizare", method=oltenizare, force=True)


"""
    Short demo to show how it actually works. Uncomment and run the main() function.
"""

# def main():
#     import time
#     import spacy
#     t1 = time.time()
#     # reader = open("text.txt", "r")
#     # text = reader.read()
#     text="După ce am terminat de făcut temele, mi-am făcut timp liber."
#     nlp = spacy.load("ro_core_news_sm")
#     doc = nlp(text) 
#     prop = nlp(doc._.oltenizare())
#     print(prop)
#     # for token in doc: 
#         # if token._.is_valid() == True:
#             # print(token._.forms_())
#             # print(token, token.dep_, token.pos_, token.morph, token.lemma_)
#     t2 = time.time() - t1
#     print("TIMP: ", t2)

# main()