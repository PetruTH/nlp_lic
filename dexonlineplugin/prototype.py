from spacy.tokens import Token, Doc
from util.util_data import *
from dexonlineplugin.data_worker import *

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
                # actual_number, actual_person, token_to_append = procesare_extract_data_from_subject(doc[i])
            
            elif doc[i].dep_ == "ROOT" and doc[i-1].dep_ == "aux:pass" and doc[i-2].dep_ == "aux":
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
#     reader = open("/Users/inttstbrd/Desktop/licenta/nlp_lic/text.txt", "r")
#     text = reader.read()
#     # text="După ce am terminat de făcut temele, mi-am făcut timp liber."
#     nlp = spacy.load("ro_core_news_sm")
#     doc = nlp(text) 
#     prop = nlp(doc._.oltenizare())
#     print(prop)
#     # for token in doc: 
#     #     if token._.is_valid() == True:
#     #         print(token._.forms_())
#     #         print(token, token.dep_, token.pos_, token.morph, token.lemma_)
#     t2 = time.time() - t1
#     print("TIMP: ", t2)

# main()