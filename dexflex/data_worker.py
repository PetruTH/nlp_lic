from dexflex.data_loader import load_jsons
from dexflex.util_data import (
    UNIDENTIFIED_TOKEN,
    ud_to_dex,
    banned_pos,
    banned_ent_types,
    reflexive_deps,
    reflexive_short_to_long_form,
    diacritics
)
import re
from typing import Tuple
from spacy.tokens import Token

(
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
) = load_jsons()


def get_all_forms_worker(token: Token) -> [int]:
    """
    thiw will extract every word having inflected form == token.text
    """
    token_text = token.text
    if "-" in token.text:
        token_text = token_text.replace("-", "")

    all_inflected_words_found = all_inflected_forms.find_all_inflected_forms_double_verification(
                token_text, token_text.lower()
            )

    if all_inflected_words_found[0] == UNIDENTIFIED_TOKEN:
        return [-1]

    words_prel = []
    only_one_word = [word['lexemeId'] for word in all_inflected_words_found]

    if len(set(only_one_word)) == 1:
        words_prel.append(str(only_one_word[0]))
    for word in all_inflected_words_found:
        pos_found = mapare.find_dexonline_pos_id(word['inflectionId'])
        """
            mapare.mapping['DEXONLINE_MORPH']: ["morph dexonline", "pos dexonline"],
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


def get_all_forms(token: Token) -> [{str, str}]:
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
            if id_to_word_pos.find_id_to_word_pos_form(element) == token.lemma_:
                id = element

    elif len(words_prel) == 1:
        if words_prel[0] == -1:
            return []
        else:
            id = words_prel[0]

    elif len(words_prel) == 0:
        words_found = word_to_id_pos.find_word_id_pos_double_verification(token.lemma_, token_text)

        if words_found != UNIDENTIFIED_TOKEN:
            words_prel = [str(x['id']) for x in words_found]
            id = words_prel[0]
        else:
            return []

    result = id_to_inflected_forms.find_id_to_inflected_forms(id)

    return result


def validate_token(token: Token) -> bool:
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

def get_person_and_number(token: Token) -> Tuple[str, str]:
    """
    This function will get the person and number data from token.morph
    and will convert these into dexonline database format information
    in order to select right form of verb.
    """
    # extract correct person and number for a phrase
    person = token.morph.get("Person", ["3"])
    number = token.morph.get("Number", ["Sing"])

    if is_composed_subj(token):
        number = ["Plur"]

    # formatting number and person to be recognized dexonline json
    actual_number = "plural" if number == ["Plur"] else "singular"

    if person == ["1"]:
        actual_person = "I"
    elif person == ["2"]:
        actual_person = "II"
    elif person == ["3"]:
        actual_person = "III"

    return actual_number, actual_person


def get_wanted_form(token: Token, pos_finder: str, person: str, number: str) -> str:
    """
       This function will return the morph form wanted by pos_finder, person and number
    """
    all_morph = get_all_forms(token)
    for wanted_form in all_morph:
        if pos_finder in wanted_form['pos'] and person in wanted_form['pos'] and number in wanted_form['pos']:
            return wanted_form['form']
    return "UNKNOWN"


def verify_word_at_certain_pos(token: Token, pos_verifier: str) -> bool:
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


def is_composed_subj(token: Token) -> bool:
    # extra step to verify if there is a composed subject (like 'eu cu tine mergem')
    if not token.pos_ == "VERB" and not token.pos_ == "AUX":
        if len(list(token.children)):
            for t in token.children:
                if t.text not in ["m", "te", "s"]:
                    return 1
        return 0


def get_right_person_and_number(token: Token) -> (str, str):
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


def forme_reflexive_verifier(token: Token) -> str:
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



from spacy.tokens import Token

Token.set_extension("forms_", method=get_all_forms, force=True)
Token.set_extension("is_valid", method=validate_token, force=True)


def find_lexeme_ids(inflected_forms: [str]) -> [str]:
    possible_lexeme_ids = []

    if inflected_forms != ["UNKNOWN"]:
        for inflected_form in inflected_forms:
            if inflected_form.get("lexemeId") not in possible_lexeme_ids:
                possible_lexeme_ids.append(inflected_form.get("lexemeId"))
  
    
    return possible_lexeme_ids

def find_inflection_possibilites(token: Token, inflected_forms: [str], pos_wanted: str) -> [str]:
    inflection_possibilites = []

    if inflected_forms != ["UNKNOWN"]:
        for inflected_form in inflected_forms:
            inflectionId = mapare.find_dexonline_pos_id(inflected_form["inflectionId"])
            
            inflected_form_id = str(inflected_form["inflectionId"])

            if inflectionId == pos_wanted and inflected_form_id not in inflection_possibilites:
                inflection_possibilites.append(str(inflected_form["inflectionId"]))
            elif inflectionId in ["VT", "V"] and pos_wanted in ["V", "VT"] and inflected_form_id not in inflection_possibilites:
                inflection_possibilites.append(str(inflected_form["inflectionId"]))
            elif inflectionId in ["M", "F", "N"] and pos_wanted in ["M", "F", "N"] and inflected_form_id not in inflection_possibilites:
                inflection_possibilites.append(str(inflected_form["inflectionId"]))
            elif token.dep_ in ["ROOT", "nmod"] and inflected_form_id not in inflection_possibilites:
                inflection_possibilites.append(str(inflected_form["inflectionId"]))

    return inflection_possibilites

def find_matching_lexemeIds(possible_lexeme_ids: [str], pos_wanted: str) -> [str]:
    lexeme_ids = [] 
   
    for lexemeId in possible_lexeme_ids:
        variant = id_to_word_pos.find_id_to_word_pos(lexemeId)
        if variant['pos'] == pos_wanted:
            lexeme_ids.append(lexemeId)
        elif variant['pos'] in ["VT", "V", "AUX"] and pos_wanted in ["V", "VT", "AUX"]:
            lexeme_ids.append(lexemeId)
        elif variant['pos'] in ["M", "F", "N"] and pos_wanted in ["M", "F", "N"]:
            lexeme_ids.append(lexemeId)
    
    return lexeme_ids

def find_entryIds(lexeme_ids: str) -> str:
    entry_ids = []
    for lexemeId in lexeme_ids:
        all_entries = entry_lexeme.find_entry_lexeme(lexemeId)
        if all_entries != ["no entry"]:
            for entry in all_entries:
                entry_ids.append(entry)

    return entry_ids

def find_treeIds(entry_ids: str) -> str:
    tree_ids = []
    for entryId in entry_ids:
        tree_entries = tree_entry.find_tree_entry(entryId)
        if tree_entries != ["no entry tree"]:
            for treeId in tree_entries:
                tree_ids.append(treeId)
    
    return tree_ids

def find_meaningIds(tree_ids: str) -> str:
    meaning_ids = []

    for treeId in tree_ids:
        all_meaningIds = relation.find_relation(str(treeId))
        if all_meaningIds != ["no relation"]:
            for meaningId in all_meaningIds:
                meaning_ids.append(meaningId)

    return meaning_ids


from spacy.tokens import Token
from dexflex.json_creator import incarcare_eficienta

def synonyms_builder_step1(token: Token, pos_wanted: str)  -> ([str], [str]):
    """
       This function will provide data needed from dexonline dataset for a certain word. 
    """

    token_text = re.sub('[^a-zA-ZăâîșțĂÂÎȘȚ]', '', token.text.lower())
    inflected_forms = all_inflected_forms.find_all_inflected_forms(token_text)
    inflection_possibilities = find_inflection_possibilites(token, inflected_forms, pos_wanted)
    possible_lexeme_ids = find_lexeme_ids(inflected_forms)
    lexeme_ids = find_matching_lexemeIds(possible_lexeme_ids, pos_wanted)
    entry_ids = find_entryIds(lexeme_ids)
    tree_ids = find_treeIds(entry_ids)
    meaning_ids = find_meaningIds(tree_ids)

    if len(inflection_possibilities) > 1:
        inflection_possibilities =  inflection_filter(token=token, inflection_possibilities=inflection_possibilities)
    return tree_ids, inflection_possibilities, meaning_ids

def synonyms_builder_step2(meaning_ids, tree_id_forced, token):
    """
        This function will return every possible alternative from dexonline according to its
        meaning id (contextual meaning) 
    """

    candidate_synonyms_base_form = []
    token_text = re.sub('[^a-zA-ZăâîșțĂÂÎȘȚ]', '', token.text.lower())

    for meaningId in meaning_ids:
        
        possible_synonyms = synonyms.find_synonyms(meaningId)
        tree_ids_verifier = [syn[0] for syn in possible_synonyms]

        if possible_synonyms != ["no synonyms"]:
        
            for synonym in possible_synonyms:

                syn_to_add = re.sub('[^a-zA-ZăâîșțĂÂÎȘȚ ]', '', synonym[1]).split(" ")
               
                for syn in syn_to_add:
                    syn_to_add_helper = all_inflected_forms.find_all_inflected_forms(syn, unidentified={"lexemeId": "UNKNOWN"})
                    if syn_to_add == ["UNKOWN"]:
                        break

                    syn_tuple = (syn, syn_to_add_helper[0].get("lexemeId", "dummy"))
                    if syn_tuple not in candidate_synonyms_base_form and syn_tuple[0] != token_text:  
                        if int(tree_id_forced[0]) in tree_ids_verifier:      
                            candidate_synonyms_base_form.append(syn_tuple)

    candidate_synonyms_base_form = [syn for i, syn in enumerate(candidate_synonyms_base_form) if i == 0 or syn[1] != candidate_synonyms_base_form[i-1][1]]

    return candidate_synonyms_base_form

def is_valid_for_syn(token: Token) -> bool:
    """
        This function will do a short validation before alternatives searching.
    """
    if token.pos_ == "PUNCT":
        return False
    if "aux" in token.dep_:
        return False
    if not token.text.isalpha():
        return False
    return True


def force_plural_noun(token):
    """
        This function will try to correctly choose the number of a noun.
    """
    associated_tokens = token.subtree
    for token in associated_tokens:
        if token.pos_ in ["DET", "NUM", "PRON"]:
            if token.morph.get("Number", ["dummy"])[0] == "Plur":
                return True
    return False

def force_person_and_number_verb(token):
    """
        This function will return person and number of a verb.
    """
    number, person = "_", "_"
    inf = False
    subtree = token.subtree
    
    for t in subtree:
        if t == token:
            break
        if t.dep_ == "nsubj":
            number = t.morph.get("Number", ["Sing"])[0]

            if number == "Plur":
                number = "plural"
            else:
                number = "singular"
                        
            if t.pos_ == "NOUN":
                person = "a III-a"
            elif t.pos_ == "PRON":
                person = t.morph.get("Person", ["dummy"])[0]

                if person == "1":
                    person = "I"
                elif person == "2":
                    person = "a II-a"
                elif person == "3":
                    person = "a III-a"
        elif t.dep_ == "mark":
            inf = True
    
            
    return inf, number, person

def get_verb_tense(token):
    """
        This function will map the tense from spacy to the tense from dexonline dataset.
    """
    mood = token.morph.get("Mood", ["Ind"])[0]
    tense = token.morph.get("Tense", ["dummy"])[0]
    verbform = token.morph.get("VerbForm", ["dummy"])[0]

    if tense == "Imp" or tense == "Pres" and mood == "Indicativ" and verbform == "Inf":
        tense = "imperfect"
    elif tense == "Pres":
        tense = "prezent"
    elif tense == "Past":
        tense = "perfect simplu"
    elif tense == "Pqp":
        tense = "mai mult ca perfect"
    return tense

def build_inflection_for_verb(token, inflection_dex_details):
    """
        This function will translate token.morph attribute from spacy into
        dexonlnine inflection description and choose the right form of a verb.
    """

    mood = "Indicativ" if token.morph.get("Mood", ["Ind"])[0] == "Ind" else "None"

    inf, number, person = force_person_and_number_verb(token)

    tense = get_verb_tense(token)

    if token.dep_ == "ccomp" or inf == True:
        found_dex_pos = "Verb, Infinitiv prezent"
    else:
        found_dex_pos = f"Verb, {mood}, {tense}, persoana {person}, {number}"

    if found_dex_pos == inflection_dex_details:
        return True
    else:
        found_dex_pos = f"Verb, {mood}, prezent, persoana {person}, {number}"
        if found_dex_pos == inflection_dex_details:
            return True
    return False

def get_case_for_noun(token):
    """
        This function will map the case from spacy to case from dexonline dataset.
    """

    case = token.morph.get("Case", ["Acc", "Nom"])
    if "Acc" in case[0] or "Nom" in case[0]:
        case = "Acc, Nom"

    if case == "Acc, Nom":
        case = "Nominativ-Acuzativ"
    elif case == "Dat, Gen":
        case = "Genitiv-Dativ"
    else:
        case = "Vocativ"
    return case

def get_definite(token):
    """
        This function will map the definite attribute from spacy to dexonline. 
    """
    
    definite = token.morph.get("Definite", ["dummy"])[0]
    if definite == "Ind":
        definite = "nearticulat"
    else:
        definite = "articulat"
    return definite

def get_number(token):
    """
        This function will map the number attribute from spacy to dexonline. 
    """

    number = token.morph.get("Number", ["Sing"])[0]
    
    if force_plural_noun(token):
        number = "plural"
    elif number == "Sing":
        number = "singular"
    else:
        number = "plural"
    return number

def get_gender(token):
    """
        This function will map the gender attribute from spacy to dexonline. 
    """

    gender = token.morph.get("Gender", ["dummy"])[0]
    if gender == "Masc":
        gender = "masculin"
    else: 
        gender = "feminin"

def get_case_for_pron(token):
    """
        This function will map the pron case attribute from spacy to dexonline. 
    """
    
    case = token.morph.get("Poss", ["No"])[0]
    if case == "Yes":
        case = "Genitiv-Dativ"
    else:
        case = "Nominativ-Acuzativ"
    return case

def build_inflection_for_noun(token, inflection_dex_details):
    """
        This function will translate token.morph attribute from spacy into
        dexonlnine inflection description and choose the right form of a noun.
    """

    case = get_case_for_noun(token)
    definite = get_definite(token)
    number = get_number(token)
    gender = get_gender(token)

    if token.pos_ == "NOUN":
        dex_pos = "Substantiv"
    elif token.pos_ == "ADJ":
        dex_pos = "Adjectiv"

    found_dex_pos = f"{dex_pos} {gender}, {case}, {number}, {definite}"
    found_dex_pos2 = f"{dex_pos} neutru, {case}, {number}, {definite}"
    if found_dex_pos == inflection_dex_details:
        return True
    elif found_dex_pos2 == inflection_dex_details:
        return True
    return False
    
def build_inflection_for_pron(token, inflection_dex_details):
    """
        This function will translate token.morph attribute from spacy into
        dexonlnine inflection description and choose the right form of a pron.
    """

    case = get_case_for_pron(token)
    number = get_number(token)

    for gender in ["masculin", "feminin"]:  
        found_dex_pos = f"Pronume, {gender}, {case}, {number}"
        if found_dex_pos == inflection_dex_details:
            return True
    return False

def inflection_filter(token, inflection_possibilities):
    """
        This function will try to get the one correct form of a word according to its
        number, person, etc. For each spacy.pos_ there will be a verifier to only keep
        the correct form.
    """

    if '85' in inflection_possibilities:
        return '85'

    for infl in inflection_possibilities:
        inflection_dex_details = mapare.find_dexonline_pos_detail(str(infl))
        if token.pos_ in ["VERB", "AUX"]:  
            if build_inflection_for_verb(token, inflection_dex_details) is True:
                inflection_possibilities = [infl]


        elif token.pos_ in ["NOUN", "ADJ"]:

            if build_inflection_for_noun(token, inflection_dex_details) is True:
                inflection_possibilities = [infl]

        elif token.pos_ in ["PRON", "DET"]:
            
            if build_inflection_for_pron(token, inflection_dex_details) is True:
                inflection_possibilities = [infl]

    return inflection_possibilities

from transformers import AutoTokenizer, AutoModel
import torch
import logging
logging.getLogger('torch').setLevel(logging.ERROR)
import json
import numpy

all_contexts = json.load(open("util/context.json"))

tokenizer = AutoTokenizer.from_pretrained("dumitrescustefan/bert-base-romanian-uncased-v1", do_lower_case=True)
model = AutoModel.from_pretrained("dumitrescustefan/bert-base-romanian-uncased-v1")


def get_embeddings(text):
    """
        This function will transform a text into its embedding using a BERT model.
    """

    tokenized_text = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**tokenized_text)

    word_embeddings = outputs.last_hidden_state
    averaged_embedding = torch.mean(word_embeddings, dim=0)

    return averaged_embedding

cos = torch.nn.CosineSimilarity(dim=0)

def calculate_similarity(input, compared_to):
    """
        This function will try to compute the contextual similarity between two phrases.
    """
    
    if type(input) != "<class 'torch.Tensor'>":
        input=torch.tensor(input)
   
    return cos(input, torch.tensor(compared_to))


def transform_with_mean_pooling(numpy_array, target_shape=(384,)):
    """
        This function will ensure that two embeddings have the same size.
    """

    pooled_array = numpy.reshape(numpy_array, (-1, target_shape[0]))
    mean_array = numpy.mean(pooled_array, axis=0) 
    return mean_array


def get_similarity_scores_for_syns(actual_context: list, syn_candidate_context: list, mean: bool, reshapeFlag = True):
    """
        This function will estimate the contextual similarity between the actual context and the context found in dexonline
        for a word that may be an alternative for the target word.
    """
    
    if actual_context is None or syn_candidate_context is None:
        return 0
    meansim = []
    
    if reshapeFlag == True:
        if actual_context[0].shape != (384,):
            actual_context = [transform_with_mean_pooling(numpy.array(act_ctx)) for act_ctx in actual_context]

    for act_ctx in actual_context:
        for syn_ctx in syn_candidate_context:
            actual_similarity = calculate_similarity(input=act_ctx, compared_to=syn_ctx)
            meansim.append(actual_similarity)

    if len(meansim):
        if mean is True:
            return sum(meansim)/len(meansim)
        else:
            return max(meansim)
    else:
        return 0


def get_context_for_each_candidate_syn(token_text, pos_wanted):
    """
        This function will return the context embeddings for each word.
    """
    pos_wanted = ud_to_dex[pos_wanted]
    inflected_forms = all_inflected_forms.find_all_inflected_forms(token_text)
    possible_lexeme_ids = find_lexeme_ids(inflected_forms)
    lexeme_ids = find_matching_lexemeIds(possible_lexeme_ids, pos_wanted)
    entry_ids = find_entryIds(lexeme_ids)
    tree_ids = find_treeIds(entry_ids)

    contexts_found = {}

    for treeId in tree_ids:
        contexts_found[treeId] = incarcare_eficienta(treeId)
    return contexts_found   


def raw_word(text):
    """
        This function will eliminate the diacritics of a word.
    """

    for k, v in diacritics.items():
        text = text.replace(k, v)
    return text.lower()

def count_consecutive_vowels(word):
    """
        This function will return the number of consecutive vowels.
    """

    vowels = "aeiouAEIOU"
    consecutive_vowel_count = 0
    total_consecutive_vowels = 0
    for char in word:
        if char in vowels:
            consecutive_vowel_count += 1
        else:
            total_consecutive_vowels += consecutive_vowel_count
            consecutive_vowel_count = 0
        
    total_consecutive_vowels += consecutive_vowel_count
    
    return total_consecutive_vowels


def approximate_syllables(word: str):
    """
        This function will return a approximation of the possible 
        syllables of a certain word in Romanian.
    """
    vowels = "aeiouăîâe"
    groups = ["ch", "gh"]
    word = raw_word(word).lower()
    for group in groups:
        if group == "ch":
            word = word.replace(group, "C")
        elif group == "gh":
            word = word.replace(group, "G")
    
    i = 1
    syllables = []
    last_syllable_index = 0
    while i < len(word) - 1:
        current_char = word[i]
        last_char = word[i-1]
        next_char = word[i+1]
        if i+2 < len(word):
            next2_char = word[i+2]
        # RULE1
        if current_char not in vowels and last_char in vowels and next_char in vowels:
            syllables.append(word[last_syllable_index : i])
            last_syllable_index = i
        # RULE2
        elif current_char not in vowels and next_char not in vowels and last_char in vowels and next2_char in vowels:
            # case 1
            if current_char in "bcdfghptv" and next_char in "lr":
                syllables.append(word[last_syllable_index : i])
            # case 2
            else:
                syllables.append(word[last_syllable_index : i+1])
                i+=1
            last_syllable_index = i
        # RULE3
        elif current_char not in vowels and last_char in vowels:
            cons_group = [current_char]
            j = i + 1 
            while j < len(word):
                if word[j] not in vowels:
                    cons_group.append(word[j])
                else:
                    break
                j+=1
            special_cons_groups = [["l", "p", "t"], ["m", "p", "t"],  ["n", "c", "t"],  ["n", "c", "s"], ["n", "d", "v"], ["r", "c", "t"], ["r", "t", "f"], ["s", "t", "m"]]
            
            # case1
            if cons_group in special_cons_groups:
                syllables.append(word[last_syllable_index:j-1])
                last_syllable_index = j-1
            # case2
            else:    
                syllables.append(word[last_syllable_index:i+1])
                last_syllable_index = i+1
            i=j

        i+=1

    syllables.append(word[last_syllable_index:])
    
    # handle hiat, diftong, triftong
    for syllable in syllables:
        vowels_num = count_consecutive_vowels(syllable)
        if 1 < vowels_num <= 3:
            double_vowel = True
            for i in range(len(syllable) - 1):
                
                if syllable[i] in vowels and syllable[i+1] != syllable[i]:
                    # print(syllable[i])
                    double_vowel = False
            if syllable == syllables[-1] and syllable[-1] == "i" and syllable[i-2] == "i":
                double_vowel = False

            if double_vowel is True:
                syllables.append("dbl_vowel")
        
        elif vowels_num > 3:   
            syllables.append("4vowel")
        # iae, ieu, oeu, oau, eoau, eoeu
        
        for long_hiat in ["iae", "ieu", "oeu", "oau", "eoau", "eoeu"]:
            if long_hiat in syllable:
                syllables.append("lng_hi")

            # print(syllable)
    return syllables


