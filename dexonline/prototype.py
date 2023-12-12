from spacy.tokens import Token, Doc
from dexonline.util_data import (
    root_forms,
    end_of_phrase,
    banned_pos,
    ud_to_dex
)

from dexonline.data_worker import (
    get_all_forms,
    validate_token,
    get_person_and_number,
    get_wanted_form,
    forme_reflexive_verifier,
    find_entryIds,
    find_inflection_possibilites,
    find_lexeme_ids,
    find_matching_lexemeIds,
    find_meaningIds,
    find_treeIds,
    mapare,
    all_inflected_forms,
    synonyms,
    id_to_inflected_forms,
)
import re


def oltenizare_worker(doc):
    """
    This function will find every at a perfect present tense and
    turn it into its past perfect form.
    """
    new_phrase = []
    actual_pers = ""
    actual_num = ""
    for i in range(0, len(doc)):
        if doc[i].pos_ not in banned_pos:
            if doc[i].dep_ == "nsubj" or doc[i].dep_ == "nsubj:pass":
                # extract data from the phrase-subject to get right form
                # of verb there will be needed for person and number
                actual_num, actual_pers = get_person_and_number(doc[i])
                new_phrase.append(doc[i].text if doc[i].text != "s" else "se")

            elif (
                doc[i].dep_ == "ROOT"
                and doc[i - 1].dep_ == "aux:pass"
                and doc[i - 2].dep_ == "aux"
            ):
                # handle cases like these: "Eu am fost plecat."
                if actual_pers == "" and actual_num == "":
                    actual_num, actual_pers = get_person_and_number(
                        doc[i-2]
                    )
                new_phrase.append(
                    get_wanted_form(
                        doc[i-1], "perfect simplu", actual_pers, actual_num
                    )
                )
                new_phrase.append(doc[i].text)

            elif (
                doc[i].dep_ == "ROOT"
                and doc[i-1].dep_ == "cc"
                and doc[i-2].dep_ == "aux"
            ):
                if actual_pers == "" and actual_num == "":
                    actual_num, actual_pers = get_person_and_number(
                        doc[i-2]
                    )
                new_phrase.append(
                    get_wanted_form(
                        doc[i], "perfect simplu", actual_pers, actual_num
                    )
                )

            elif doc[i].dep_ in root_forms and doc[i-1].dep_ == "aux":
                if doc[i - 2].dep_ == "aux":
                    new_phrase += [doc[i-2].text, doc[i-1].text, doc[i].text]
                    i += 2

                else:
                    # handle cases like these: "Eu am plecat"
                    # ensure that the construction found
                    # (aux + verb) is not at a future tense
                    if doc[i].morph.get("VerbForm")[0] != "Inf":
                        if doc[i - 1].pos_ == "AUX":
                            if actual_pers == "" and actual_num == "":
                                # if person and number paramateres cant be
                                # found from subject of a phrase,
                                # the verb will get this from its inflection
                                (
                                    actual_num,
                                    actual_pers,
                                ) = get_person_and_number(doc[i - 1])
                            new_phrase.append(
                                get_wanted_form(
                                    doc[i],
                                    "perfect simplu",
                                    actual_pers,
                                    actual_num,
                                )
                            )

                        else:
                            # trick to handle exceptions found
                            if actual_pers == "" and actual_num == "":
                                (
                                    actual_num,
                                    actual_pers,
                                ) = get_person_and_number(doc[i - 1])
                            new_phrase.append(doc[i].text)

                    else:
                        # the construction is at a future tense
                        new_phrase.append(doc[i - 1].text)
                        new_phrase.append(doc[i].text)

            elif doc[i].dep_ == "aux:pass" and doc[i].lemma_ == "fi":
                if doc[i - 1].dep_ == "aux":
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
            actual_num, actual_pers = "", ""

    return new_phrase


def oltenizare(doc):
    new_phrase = oltenizare_worker(doc)
    phrase_to_return = ""

    for i in range(len(new_phrase)):
        # building the initial phrase back following the next
        # rule: word, word (or any other PUNCT)
        # edge-case 1: for "-" where the rule is word-word
        # edge-case 2: word. Word (the same for ?, !, \n)
        if "-" in new_phrase[i]:
            phrase_to_return += " " + new_phrase[i]

        elif not new_phrase[i].isalpha():
            phrase_to_return += new_phrase[i]

        else:
            if new_phrase[i - 1] in end_of_phrase:
                phrase_to_return += " " + new_phrase[i].capitalize()
            elif new_phrase[i - 1][-1] == "-":
                phrase_to_return += new_phrase[i]
            else:
                phrase_to_return += " " + new_phrase[i]

    return phrase_to_return


def synonyms_builder(token, pos_wanted):
    """
    This function will extract each synonym found for a certain word at a
    base form.
    Returns:
        inflection_possibilities = a list of inflection id s for matching
                                   with the inflection found in input
        candidates_synonyms_base_form = a list of synonyms at a base form
    """

    token_text = re.sub('[^a-zA-ZăâîșțĂÂÎȘȚ]', '', token.text.lower())
    inflected_forms = all_inflected_forms.get(token_text, ["UNKNOWN"])
    
    inflection_possibilities = find_inflection_possibilites(token, inflected_forms, pos_wanted)
    possible_lexeme_ids = find_lexeme_ids(inflected_forms)
    lexeme_ids = find_matching_lexemeIds(token, possible_lexeme_ids, pos_wanted)
    entry_ids = find_entryIds(lexeme_ids)
    tree_ids = find_treeIds(entry_ids)
    meaning_ids = find_meaningIds(tree_ids)

    candidate_synonyms_base_form = []

    for meaningId in meaning_ids:
        possible_synonyms = synonyms.get(str(meaningId), ["no synonyms"])
        if possible_synonyms != ["no synonyms"]:
            for synonym in possible_synonyms:
                syn_to_add = re.sub('[^a-zA-ZăâîșțĂÂÎȘȚ ]', '', synonym[1]).split(" ")
                
                for syn in syn_to_add:
                    syn_to_add_helper = all_inflected_forms.get(syn, [{"lexemeId": "UNKNOWN"}])
                    if syn_to_add == ["UNKOWN"]:
                        break

                    syn_tuple = (syn, syn_to_add_helper[0].get("lexemeId", "dummy"))
                    if syn_tuple not in candidate_synonyms_base_form and syn_tuple[0] != token_text:
                        candidate_synonyms_base_form.append(syn_tuple)

    candidate_synonyms_base_form = [syn for i, syn in enumerate(candidate_synonyms_base_form) if i == 0 or syn[1] != candidate_synonyms_base_form[i-1][1]]

    return inflection_possibilities, candidate_synonyms_base_form


def is_valid_for_syn(token):
    if token.pos_ == "PUNCT":
        return False
    if "aux" in token.dep_:
        return False
    if not token.text.isalpha():
        return False
    return True

def get_synonyms(token):
    if is_valid_for_syn(token):
        pos_found = ud_to_dex[token.pos_]
        inflection_possibilites, candidate_synonyms_base_form = synonyms_builder(token, pos_found)

        synonyms_found = []
        for syn in candidate_synonyms_base_form:
            inflected_forms_syn = id_to_inflected_forms.get(str(syn[1]), [{"form": "no pos", "pos": "no form"}])

            for inflectionId in inflection_possibilites:
                inflection = mapare["DEXONLINE_MORPH"].get(
                                str(inflectionId),
                                "UNKNOWN"
                            )[0]
                for pos_syn in inflected_forms_syn:
                    pos_found_on_syn = pos_syn.get("pos")
                    form_found_on_syn = pos_syn.get("form")
                    if pos_found_on_syn == inflection:
                            if form_found_on_syn not in synonyms_found:
                                synonyms_found.append(form_found_on_syn)


        return synonyms_found
    else:
        return [f"The token: '{token.text}' is not eligible for synonym search."]


"""
    There next four lines will add to Token and Doc from spacy new features.
        forms_ -> will return each inflected form for a certain word
        is_valid -> will verify if token can be found in dexonline
                    database based on the rules described before
        oltenizare -> will automatically change tense of verbs from:
                      present perfect (perfect compus)
                      to: past perfect (perfect simplu)
        get_synonyms -> will return all the synonyms found in
                        dexonline database for a certain word
"""
Token.set_extension("forms_", method=get_all_forms, force=True)
Token.set_extension("is_valid", method=validate_token, force=True)
Doc.set_extension("oltenizare", method=oltenizare, force=True)
Token.set_extension("get_synonyms", method=get_synonyms, force=True)


"""
    Short demo to show how it actually works.
    Uncomment and run the main() function.
"""


# def main():
#     import time
#     import spacy

#     t1 = time.time()
#     # reader = open("/Users/inttstbrd/Desktop/licenta/nlp_lic/text.txt", "r")
#     # text = reader.read()
#     text = "PLantai un copac. Are harbuz sinonim?"
#     nlp = spacy.load("ro_core_news_sm")
#     doc = nlp(text)
#     # doc = nlp(doc._.oltenizare())
#     print(doc)
#     for token in doc:    
#         print(token, "sinonime:", token._.get_synonyms())

#     t2 = time.time() - t1
#     print("TIMP: ", t2)


# main()
