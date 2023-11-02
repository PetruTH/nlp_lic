import spacy
import json

mapare = json.load(open('forme_morfologice.json'))
all_inflected_forms = json.load(open('inflected_form_lexemeId_inflectionId.json'))
word_to_id_pos = json.load(open('word_id_pos.json'))
id_to_word_pos = json.load(open('id_word_pos.json'))
id_to_inflected_forms = json.load(open('wordId_inflected_forms.json'))


def extract_all_infected_forms_for_word(lexemeId):
    #prototip pentru functia care va stoca intr o structura de date toate formele morfologice ale unui cuvant
    result = id_to_inflected_forms[lexemeId]

    print(f"Toate formele la care poate aparea cuvantul {id_to_word_pos[lexemeId]}:\n")
    for word in result:
        print(str(word))
            
    print("\n\n")

def find_entry_by_inflected_form(token):
    global id_to_word_pos, all_inflected_forms

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

    all_inflected_words_found = all_inflected_forms[token.text.lower()]
    # pos_found_by_spacy = mapare["UNIVERSAL_DEPENDECIES"][token.pos_]
    # print(pos_found_by_spacy, "POS FOUND", token.pos_, "TOKEN POS")
    
    # exemplu pt a -> token.lemma_ = a vrea si stiu ca e verb
    # all_inflected_words are mai multe elemente verbe si nu stiu pe care sa il aleg
    # in cazul asta, caut iau in cosiderare ambele verbe si in final verific ca si form sa fie == token.lemma 
    # mai trb adaugata o mapare ca VERB sa se duca in V si ai grija sa verifici si pe VT
    id = ""
    
    words_prel = []
    for word in all_inflected_words_found:

        pos_found = mapare['DEXONLINE_MORPH'][str(word['inflectionId'])]
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
                cuvant = id_to_word_pos[str(element)][0]['form']
                id = element

    elif len(words_prel) == 1:
        cuvant = id_to_word_pos[words_prel[0]][0]['form']
        id = words_prel[0]

    elif len(words_prel) == 0:
        words_prel = [str(x['id']) for x in word_to_id_pos[token.lemma_]]
        id = words_prel[0]
        cuvant = id_to_word_pos[id][0]['form']
    
    return id

def validate_token(token):
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

def main():
    global all_words_extracted
    
    import time
    t1 = time.time()
    
    reader = open("text.txt", "r")
    text = reader.read()

    if "-" in text:
        text = text.replace("-", " ")
    
    nlp = spacy.load("ro_core_news_sm")
    doc = nlp(text) 

    for token in doc:
        if token.pos_ not in ["PUNCT", "SPACE"]:
            if validate_token(token) == True: 
                idLexeme = find_entry_by_inflected_form(token)
                extract_all_infected_forms_for_word(idLexeme)
    
    t2 = time.time() - t1
    print("TIMP: ", t2)


main()

#TODO: implementeaza o serie de teste care sa verifice daca rezultatele obtinute de acest script sunt cele asteptate (hardcodate intr-o structura de date)