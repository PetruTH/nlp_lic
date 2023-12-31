from dexonline.data_loader import load_jsons
from dexonline.util_data import (
    UNIDENTIFIED_TOKEN,
    ud_to_dex,
    banned_pos,
    banned_ent_types,
    reflexive_deps,
    reflexive_short_to_long_form
)

mapare = {}
all_inflected_forms = {}
word_to_id_pos = {}
id_to_word_pos = {}
id_to_inflected_forms = {}

mapare, all_inflected_forms, word_to_id_pos, id_to_word_pos, id_to_inflected_forms = load_jsons()


def get_all_forms_worker(token):
    """
    thiw will extract every word having inflected form == token.text
    """
    token_text = token.text
    if "-" in token.text:
        token_text = token_text.replace("-", "")

    all_inflected_words_found = all_inflected_forms.get(
        token_text,
        all_inflected_forms.get(
            token_text.lower(),
            UNIDENTIFIED_TOKEN
        )
    )

    if all_inflected_words_found == UNIDENTIFIED_TOKEN:
        return []

    words_prel = []
    only_one_word = [word['lexemeId'] for word in all_inflected_words_found]

    if len(set(only_one_word)) == 1:
        words_prel.append(str(only_one_word[0]))
    for word in all_inflected_words_found:
        pos_found = mapare['DEXONLINE_MORPH'][str(word['inflectionId'])][1]
        """
            mapare['DEXONLINE_MORPH']: ["morph dexonline", "pos dexonline"],
            this will help for mapping spacy pos to dexonline pos
            mapping spacy pos with dexonline pos
            looking after an id found from dexonline
        """

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
    words_prel = get_all_forms_worker(token)
    token_text = token.text

    if len(words_prel) > 1:
        for element in words_prel:
            if id_to_word_pos[str(element)][0]['form'] == token.lemma_:
                id = element

    elif len(words_prel) == 1:
        id = words_prel[0]

    elif len(words_prel) == 0:
        words_found = word_to_id_pos.get(
            token.lemma_,
            word_to_id_pos.get(
                token_text,
                UNIDENTIFIED_TOKEN
            )
        )

        if words_found != UNIDENTIFIED_TOKEN:
            words_prel = [str(x['id']) for x in words_found]
            id = words_prel[0]
        else:
            return []

    result = id_to_inflected_forms[id]

    return result


def validate_token(token):
    """
        Function that validates if a token can be found in dexonline database.
        It will exclude words that describe names or places, organizations, etc.
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
    return "UNKNOWN"


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


def is_composed_subj(token):
    # extra step to verify if there is a composed subject (like 'eu cu tine mergem')
    if not token.pos_ == "VERB" and not token.pos_ == "AUX":
        if len(list(token.children)):
            for t in token.children:
                if t.text not in ["m", "te", "s"]:
                    return 1
        return 0


def get_right_person_and_number(token):
    """
        This function will get the person and number data from token.morph
        and will convert these into dexonline database format information
        in order to select right form of verb.
    """
    # extract correct person and number for a phrase
    person = token.morph.get("Person", ['3'])
    number = token.morph.get("Number", ['Sing'])

    if is_composed_subj(token):
        number = ["Plur"]

    # formatting number and person to be recognized dexonline json
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
        This function will map short reflexive forms into long ones
        using data from reflexive_deps from util_data.py
    """
    word_added = token.text
    if token.dep_ in reflexive_deps:
        case_condition = token.morph.get("Case", ["dummy"])[0] in ["Dat", "Acc"]
        variant_condition = token.morph.get("Variant", ["dummy"])[0] == "Short"
        if case_condition and variant_condition:
            word_added = reflexive_short_to_long_form[token.text]

    return word_added
