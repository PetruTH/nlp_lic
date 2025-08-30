import numpy
from spacy.tokens import Token, Doc
import spacy
nlp = spacy.load("ro_core_news_sm")
from dexflex.util_data import (
    root_forms,
    end_of_phrase,
    banned_pos,
    ud_to_dex
)
import torch
from typing import Tuple
from dexflex.data_worker import (
    get_all_forms,
    validate_token,
    get_right_person_and_number,
    get_wanted_form,
    forme_reflexive_verifier,
    is_valid_for_syn,
    synonyms_builder_step1,
    synonyms_builder_step2,
    mapare,
    id_to_inflected_forms
)
from dexflex.data_worker import approximate_syllables, get_context_for_each_candidate_syn, get_embeddings, get_similarity_scores_for_syns, synonyms_builder_step1
from dexflex.json_creator import incarcare_eficienta
from wordfreq import zipf_frequency
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def oltenizare_worker(doc: Doc) -> list[str]:
    """
    This function will find every at a perfect present tense and
    turn it into its past perfect form.
    """
    new_phrase = []
    actual_pers = ""
    actual_num = ""
    # print("OLTENIZARE")
    docgen = iter(range(0, len(doc)))
    for i in docgen:
        if doc[i].pos_ not in banned_pos:
            if doc[i].dep_ == "nsubj" or doc[i].dep_ == "nsubj:pass":
                # extract data from the phrase-subject to get right form
                # of verb there will be needed for person and number
                actual_num, actual_pers = get_right_person_and_number(doc[i])
                new_phrase.append(doc[i].text if doc[i].text != "s" else "se")

            elif (
                doc[i].dep_ == "ROOT"
                and doc[i-1].dep_ in {"aux", "aux:pass", "cop"} 
                and doc[i-2].dep_ == "aux"
            ):
                # handle cases like these: "Eu am fost plecat."

                if actual_pers == "" and actual_num == "":
                    actual_num, actual_pers = get_right_person_and_number(doc[i-2])

                if doc[i].pos_ != "VERB":
                    new_phrase.append(doc[i].text)
               
                elif doc[i-1].morph.get("VerbForm") == ["Part"]:
                    new_phrase.append(
                        get_wanted_form(
                            doc[i-1], "perfect simplu", actual_pers, actual_num
                        )
                    )
                    new_phrase.append(doc[i].text)
                elif doc[i-1].morph.get("VerbForm") == ["Inf"]:
                    new_phrase += [doc[i-2].text, doc[i-1].text, doc[i].text]
                    i += 2
                
                elif doc[i].morph.get("VerbForm") == ["Inf"]:
                    new_phrase += [doc[i].text]

            elif (
                doc[i].dep_ == "ROOT"
                and doc[i-1].dep_ == "cc"
                and doc[i-2].dep_ == "aux"
            ):
                
                if actual_pers == "" and actual_num == "":
                    actual_num, actual_pers = get_right_person_and_number(doc[i-2])
                new_phrase.append(
                    get_wanted_form(
                                    doc[i],
                                    "perfect simplu",
                                    actual_pers,
                                    actual_num
                                )
                )
            
            elif (
                doc[i].dep_ == "ROOT"
                and doc[i-2].dep_ == "aux"
            ):
                
                if actual_pers == "" and actual_num == "":
                    actual_num, actual_pers = get_right_person_and_number(doc[i-2])
                
                if doc[i].morph.get("VerbForm") == ["Part"]:
                    new_phrase.append(
                        get_wanted_form(
                                        doc[i],
                                        "perfect simplu",
                                        actual_pers,
                                        actual_num
                                    )
                    )
                else:
                    new_phrase.append(doc[i].text)

            elif doc[i].dep_ in root_forms and doc[i-1].dep_ == "aux":
                if doc[i-2].dep_ == "aux":
                    if len(new_phrase) > 0 and doc[i-2].text == new_phrase[-1]:            
                        new_phrase += [doc[i-1].text, doc[i].text]
                    else:
                        new_phrase += [doc[i-2].text, doc[i-1].text, doc[i].text]
            
                    i += 2

                else:
                    # handle cases like these: "Eu am plecat"
                    # ensure that the construction found
                    # (aux + verb) is not at a future tense
                
                    if doc[i].morph.get("VerbForm", ["UNKNONWN"])[0] in {"Part"}:
                        if doc[i-1].pos_ == "AUX":
                            # if actual_pers == "" and actual_num == "":
                                # if person and number paramateres cant be
                                # found from subject of a phrase,
                                # the verb will get this from its inflection
                            (
                                actual_num,
                                actual_pers,
                            ) = get_right_person_and_number(doc[i-1])
                            # print(get_right_person_and_number(doc[i-1]))
                            word_to_add = get_wanted_form(
                                    doc[i],
                                    "perfect simplu",
                                    actual_pers,
                                    actual_num,
                                )
                            if word_to_add == "UNKNOWN":
                                if doc[i-1].lemma_ == "avea":
                                    new_phrase.append(doc[i-1].text)
                                    
                                new_phrase.append(
                                    doc[i].text
                                )
                            else:
                                new_phrase.append(word_to_add)

                        else:
                            # trick to handle exceptions found
                            if actual_pers == "" and actual_num == "":
                                (
                                    actual_num,
                                    actual_pers,
                                ) = get_right_person_and_number(doc[i-1])
                            new_phrase.append(doc[i].text)

                    else:
                        if doc[i].dep_ != "cop":
                            if len(new_phrase) > 0:
                                if doc[i-1].text != new_phrase[-1]:
                            # the construction is at a future tense or cond opt
                                    new_phrase.append(doc[i-1].text)
                            else:
                                new_phrase.append(doc[i].text)
                            
                        new_phrase.append(doc[i].text)
                        

            elif doc[i].dep_ == "aux:pass" and doc[i].lemma_ == "fi":
                    # AM COMENTAT PT EXEMPLUL ASTA El va pleca, dar ieri ar fi stat apoi a plecat.
                if doc[i-1].dep_ == "aux":
                    if doc[i+1].dep_ in root_forms and doc[i+1].pos_ not in {"VERB", "AUX"}:
                        (
                            actual_num,
                            actual_pers,
                        ) = get_right_person_and_number(doc[i-1])
                        new_phrase.append(get_wanted_form(
                                    doc[i],
                                    "perfect simplu",
                                    actual_pers,
                                    actual_num,
                                ))
                    elif doc[i+1].dep_ not in {"ROOT"}:
                    # else:
                        new_phrase.append(doc[i].text)
                    pass

                else:
                    new_phrase.append(doc[i].text)

            elif doc[i].dep_ == "det" and doc[i].pos_ == "AUX" and doc[i+1].dep_ == "dep" and doc[i+1].pos_ == "AUX":
                (
                    actual_num,
                    actual_pers,
                ) = get_right_person_and_number(doc[i])

                new_phrase.append(
                    get_wanted_form(
                                    doc[i+1],
                                    "perfect simplu",
                                    actual_pers,
                                    actual_num,
                                )
                )
                next(docgen)


            elif doc[i].dep_ == "aux":
                add = True
                anc_verb = {}
                for t in doc[i].ancestors:
                    if t.pos_ in {"VERB", "AUX"}:
                        add = False
                        anc_verb = t
                        
                if anc_verb == {}:
                    anc_verb=t

                if doc[i+1].dep_ == "mark" and doc[i+1].pos_ in {"ADP", "PART"} and doc[i+2].dep_ == "ROOT" and doc[i+2].pos_ == "VERB":
                    new_phrase += [doc[i].text, doc[i+1].text, doc[i+2].text]
                    next(docgen)
                    next(docgen)
                    # next(docgen)
                    # continue

                elif doc[i+1].morph.get("VerbForm") == ["Part"] or anc_verb.morph.get("VerbForm") == ["Part"]:
                    if doc[i].morph.get("VerbForm") in [["Fin"], ["Inf"]]:
                        new_phrase.append(doc[i].text)
                        new_phrase.append(doc[i+1].text)
                        next(docgen)
                    elif doc[i].text in {"ar", "ai", "am", "aș", "ați"} and doc[i+1].morph.get("VerbForm") in [["Fin"], ["Inf"]]:
                        new_phrase.append(doc[i].text)
                        new_phrase.append(doc[i+1].text)
                        new_phrase.append(doc[i+2].text)
                        next(docgen)
                        next(docgen)
                   
                    
                elif add is True or doc[i+1].morph.get("VerbForm") == ["Inf"] or anc_verb.morph.get("VerbForm") == ["Inf"]:
                    # print(new_phrase[-1], doc[i].text)
                    if len(new_phrase) > 0:
                        if new_phrase[-1] != doc[i].text:
                            new_phrase.append(doc[i].text)
                    else:
                        new_phrase.append(doc[i].text)
                else:
                    new_phrase.append(doc[i].text)
               
            # elif doc[i].dep_ == "dep" and doc[i].dep_ == "dep" and doc[i].pos_ == and doc[i].dep
                        # A FOST A MAMEI
                
            else:
                if doc[i].pos_ == "PRON" or doc[i].dep_ == "expl":
                    if doc[i].text[-1] == "-":

                        try:
                            anc = list(doc[i].ancestors)[0]                            
                            if anc.morph.get("VerbForm") == ["Part"]:
                                word_added = forme_reflexive_verifier(doc[i])
                            else:
                                word_added = doc[i].text
                        except:
                            word_added = doc[i].text
                    else:
                        word_added = doc[i].text
                else:
                    word_added = doc[i].text

                # print(word_added, doc[i].pos_, doc[i].dep_,)
                new_phrase.append(word_added)

        else:
            new_phrase.append(doc[i].text)
            actual_num, actual_pers = "", ""

    return new_phrase


def oltenizare(doc: Doc) -> str:
    """
        This function builds a new phrase with the verbs modified by the oltenizare_worker flow.
    """
    new_phrase = oltenizare_worker(doc)
    phrase_to_return = ""

    for i in range(len(new_phrase)):
        new_phrase[i] = new_phrase[i].replace("n-", "nu")
        new_phrase[i] = new_phrase[i].replace("l-", "îl")
        new_phrase[i] = new_phrase[i].replace("ţi-", "îţi")
        new_phrase[i] = new_phrase[i].replace("le-", "le")
        new_phrase[i] = new_phrase[i].replace("c-", "că")
        
        # building the initial phrase back following the next
        # rule: word, word (or any other PUNCT)
        # edge-case 1: for "-" where the rule is word-word
        # edge-case 2: word. Word (the same for ?, !, \n)
        # print(new_phrase[i])
        if "-" in new_phrase[i][1:]:
            phrase_to_return += " " + new_phrase[i]
        elif "-" == new_phrase[i][0]:
            phrase_to_return += "-"+new_phrase[i]

        elif not new_phrase[i].isalpha():
            phrase_to_return += new_phrase[i]

        else:
            if new_phrase[i-1] in end_of_phrase:
                phrase_to_return += " " + new_phrase[i].capitalize()
            elif new_phrase[i-1][-1] == "-":
                phrase_to_return += new_phrase[i]
            else:
                phrase_to_return += " " + new_phrase[i]

    phrase_to_return = phrase_to_return.replace("--", "-")
    
    words = phrase_to_return.split()
    phrase = []
    for word in words:
        if word.endswith("-o"):
            word_modfied = f"o {word[:-2]}"
        else:
            word_modfied = word
        phrase.append(word_modfied)
    return " ".join(phrase) + "\n"


def get_synonyms(token: Token, tree_id_forced = []) -> [str]:
    """
        This function will extract the raw alternatives from dexonline dataset.
    """

    if is_valid_for_syn(token):
        pos_found = ud_to_dex[token.pos_]
        tree_ids, inflection_possibilites, meaning_ids = synonyms_builder_step1(token, pos_found)

        candidate_synonyms_base_form = synonyms_builder_step2(meaning_ids, tree_id_forced, token)

        synonyms_found = []

        for syn in candidate_synonyms_base_form:
            inflected_forms_syn = id_to_inflected_forms.find_id_to_inflected_forms(str(syn[1]))

            for inflectionId in inflection_possibilites:
                inflection = mapare.find_dexonline_pos_detail(str(inflectionId))

                for pos_syn in inflected_forms_syn:
                    pos_found_on_syn = pos_syn.get("pos")
                    form_found_on_syn = pos_syn.get("form")
                    if pos_found_on_syn == inflection:
                            if form_found_on_syn not in synonyms_found:
                                synonyms_found.append(form_found_on_syn)
                                
       
        return synonyms_found
    else:
        return []

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


def choose_meaning(contexts_found, actual_context):
    """
       Returns the most similar context of the word referring to the actual context
    """
    max_score = -100
    key_to_return = ""
    actual_context = torch.mean(get_embeddings(actual_context), dim=0)

    for key in contexts_found:
        score = get_similarity_scores_for_syns(actual_context=[actual_context], syn_candidate_context=contexts_found[key], mean=False)
        if score > max_score:
            max_score = score
            key_to_return = key
 
    return key_to_return


def heuristic_comparator(word: str, actual_context: str, token_pos: str, dexonline_order: int, syns_number: int):
    """
        The function used to compare the complexity of each alternative by a list of features. 
        Each feature has a different weight depending on its impact.
    """
    # these can be modified, still testing
    len_weight = -50
    number_of_syllabes_weight = -120
    freq_in_ro_lang_weight = 30
    similarity_with_actual_context_weight = 1500
    dexonline_order_weight = 90

    def transform_with_mean_pooling(numpy_array, target_shape=(384,)):
        pooled_array = numpy.reshape(numpy_array, (-1, target_shape[0]))
        mean_array = numpy.mean(pooled_array, axis=0) 
        return mean_array

    emb1 = [torch.tensor(transform_with_mean_pooling(numpy.array(get_embeddings(actual_context))))]
   
    sin_context = get_context_for_each_candidate_syn(token_text=word, pos_wanted=token_pos)
    
    similarity_score = 0
    if len(sin_context):
        for key in sin_context:
            similarity_score = get_similarity_scores_for_syns(actual_context=emb1, syn_candidate_context=sin_context[key], mean=False)
    
    try:
        base_form = get_all_forms(nlp(word)[0])[0].get("form")
    except:
        base_form = word

    word_len = len_weight * len(word)
    apx_syllables_number = number_of_syllabes_weight * len(approximate_syllables(word))
    freq = freq_in_ro_lang_weight * (zipf_frequency(base_form, 'ro')) 
    dexonline_order = dexonline_order_weight * (syns_number - dexonline_order)
    
    return word_len + apx_syllables_number + freq + similarity_with_actual_context_weight * similarity_score + dexonline_order


def get_matching_syns(token, actual_context, pos_found):
    """
        This function ensures that all the returned alternatives are in the right form and meaning.
        Also, in this function the alternatives will be sorted with the heuristic_comparator.
    """
    
    tree_ids, inflection_possibilites, meaning_ids = synonyms_builder_step1(token, pos_found)
    contexts_found = {}
        
    for treeId in tree_ids:
        contexts_found[treeId] = incarcare_eficienta(treeId)    

    try:
        if len(contexts_found.keys()) > 1:
            chosen_context = str(choose_meaning(contexts_found, actual_context))
        else:
            chosen_context = str(list(contexts_found.keys())[0])
        syns_found_in_dex = token._.get_synonyms([chosen_context])
        
        syns_to_return = []

        for i in range(len(syns_found_in_dex)):
            syn = syns_found_in_dex[i]
            if syn == token.text[1:] or syn == syns_found_in_dex[i-1][1:]:
                continue
            else:
                syns_to_return.append(
                    (
                        syn, 
                        heuristic_comparator(
                            syn, 
                            actual_context,
                            token.pos_,
                            i,
                            len(syns_found_in_dex)
                        )
                    )
                )
        
        return sorted(syns_to_return, key=lambda x: x[1], reverse=True)
    
    except IndexError:
        print("no synonyms")
        pass



# Uncomment the lines below to see a short demo

# import time
# import spacy
# t1 = time.time()

# # pentru teste
# cuv = "harbuz"
# # contextele pe care vreau sa l testez


# text = "Eu am mers la un copac. Are harbuz sinonim?"
# doc = nlp(text)
# doc = nlp(doc._.oltenizare())
# # print(doc)
# def main():
#     for token in doc:
#         if token.text == cuv:
#             pos_found = ud_to_dex[token.pos_]
#             syns = get_matching_syns(token, actual_context=doc.text, pos_found=pos_found)
#             if syns:
#                 for x in syns[:10]:
#                     if x[0] == cuv:
#                         continue
#                     else:
#                         print(x)
                
#     t2 = time.time() - t1
#     print("TIMP: ", t2)

# main()


# import spacy

# nlp = spacy.load("ro_core_news_sm")

def identifica_diateza(sentence):
    doc = nlp(sentence)
    rezultate = []
    diateza_pasiva_flags = {
        "nsubj:pass": False,
        "aux": False,
        "obl:agent": False
    }

    diateza_reflexiva_flags = {
        "expl": False,
    }

    
    for token in doc:
        for key in diateza_pasiva_flags.keys():
            if token.dep_ in key or key in token.dep_:
                diateza_pasiva_flags[key] = True

        for key in diateza_reflexiva_flags.keys():
            if (token.dep_ in key or key in token.dep_):
                diateza_reflexiva_flags[key] = True
            elif token.morph.get("Reflex", [None])[0] == "Yes" or (token.morph.get("Case", [None])[0] == "Acc" and token.morph.get("Strength", [None])[0] == "Weak"):
                diateza_reflexiva_flags["expl"] = True
        
    
    diateza_pasiva = True if all(diateza_pasiva_flags[key] for key in diateza_pasiva_flags) else False
    diateza_reflexiva = True if all(diateza_reflexiva_flags[key] for key in diateza_reflexiva_flags) else False
  
    if diateza_pasiva is False and diateza_reflexiva is False:
        diateza_activa = True
    else:
        diateza_activa = False        

    rezultate_diateze = {
        "activa": diateza_activa,
        "pasiva": diateza_pasiva,
        "reflexiva": diateza_reflexiva,
    }

    for key in rezultate_diateze:
        if rezultate_diateze[key] == True:
            return key

def get_actual_inflection(token):
    inflections = get_all_forms(token)

    found_case = token.morph.get("Case", ["Acc,Nom"])[0]
    if found_case in ["Acc,Nom", "Acc", "Nom"]:
        found_case = "Nominativ-Acuzativ"
    else:
        found_case = "Genitiv-Dativ"

    for inflection in inflections:
        token_text = token.text
        if token.pos_ != "PROPN":
            token_text = token_text.lower()
        if inflection["form"] == token_text:
            if token.pos_ == "NOUN":
                if found_case in inflection["pos"]:
                    return inflection
            else:
                return inflection

def get_new_subject(token, pos):
    subtree = list(token.subtree)
    phrase = " ".join([t.text for t in subtree])

    if len(subtree) > 1:
        return phrase
    else:
        return get_defined_word(token, pos)

def get_right_aux_form(obj_pos, root_pos, obj_number):
    aux = nlp("este")
    aux_inflections_filtered_by_person = [form for form in get_all_forms(aux[0]) if "persoana a III-a" in form["pos"] and "Indicativ" in form["pos"]]

    obj_pos_details = [x.strip() for x in obj_pos.split(",")]
    root_pos_details = [x.strip() for x in root_pos.split(",")]

    number = "plural"
    if "plural" not in obj_pos_details:
        number = "singular"
    
    aux_inflections_filtered_by_person_number = [form for form in aux_inflections_filtered_by_person if number in form["pos"]]

    time_found = "prezent"
    time_choices = ["prezent", "perfect simplu", "mai mult ca perfect", "imperfect", "participiu pasiv"]
    for time in time_choices:
        for detail in root_pos_details:
            if time.lower() == detail.lower():
                time_found = detail.lower()

    if time_found == "participiu pasiv":
        if obj_number == "Sing":
            return "a fost"
        else:
            return "au fost"
    else:
        aux_inflection_filtered_by_person_number_time = [form for form in aux_inflections_filtered_by_person_number if time_found in form["pos"]]

        return aux_inflection_filtered_by_person_number_time[0]["form"]
    return None

def get_verb_part(token):
    inflections = get_all_forms(token)
    part = [form for form in inflections if "Participiu pasiv" in form["pos"]]
    return part[0]

def get_new_root_form(root_verb_part, obj_token):
    number = obj_token.morph.get("Number", [None])[0]
    gender = obj_token.morph.get("Gender", [None])[0]
    root_verb_part_form = root_verb_part["form"]

    if number == "Sing" and gender == "Fem" and root_verb_part_form[-1]=="t":
        return f"{root_verb_part_form[:-1]}tă"
    elif number == "Sing" and gender == "Masc" and root_verb_part_form[-1]=="t":
        return f"{root_verb_part_form[:-1]}t"
    elif number == "Plur" and gender == "Fem" and root_verb_part_form[-1]=="t":
        return f"{root_verb_part_form[:-1]}te"
    elif number == "Plur" and gender == "Masc" and root_verb_part_form[-1]=="t":
        return f"{root_verb_part_form[:-1]}ți"
    elif number == "Sing" and gender == "Fem" and root_verb_part_form[-1]=="s":
        return f"{root_verb_part_form[:-1]}să"
    elif number == "Sing" and gender == "Masc" and root_verb_part_form[-1]=="s":
        return f"{root_verb_part_form[:-1]}s"
    elif number == "Plur" and gender == "Fem" and root_verb_part_form[-1]=="s":
        return f"{root_verb_part_form[:-1]}se"
    elif number == "Plur" and gender == "Masc" and root_verb_part_form[-1]=="s":
        return f"{root_verb_part_form[:-1]}și"

    return root_verb_part

def get_undefined_word(token, subj_pos):
    if token.pos_ == "PROPN":
        return token.text
    
    inflections = get_all_forms(token)
    if ", articulat" in subj_pos:
        subj_pos = subj_pos.replace(", articulat", ", nearticulat")
    
    return [form for form in inflections if form["pos"] == subj_pos][0]["form"]

def get_defined_word(token, subj_pos):
    if token.pos_ == "PROPN":
        return token.text
    
    inflections = get_all_forms(token)
    if ", nearticulat" in subj_pos:
        subj_pos = subj_pos.replace(", nearticulat", ", articulat")
    
    return [form for form in inflections if form["pos"] == subj_pos][0]["form"]


def active_to_passive(sentence):
    doc = nlp(sentence)
    
    ok_transform = False

    obj_number = "Sing"
    root_verb_part_form = []
    obj_token = ""
    old_subj = ""
    punct = "."
    for token in doc:
        if token.dep_ == "nsubj":
            subj_pos = get_actual_inflection(token)["pos"]
            subtree = list(token.subtree)
            if token.text.lower() == "eu":
                old_subj = "mine"
            elif token.text.lower() == "tu":
                old_subj = "tine"
            elif len(subtree) > 1:
                old_subj = " ".join([t.text.lower() if t.pos_ != "PROPN" else t.text for t in subtree])
            else:
                old_subj = get_undefined_word(token, subj_pos)

            
        elif token.dep_ == "ROOT":
            subtree = list(token.subtree)
            old_root = " ".join([t.text for t in subtree])

            root_pos = get_actual_inflection(token)["pos"]
            root_verb_part_form = get_verb_part(token)
            
        elif token.dep_ in "obj" or "obj" in token.dep_:
            ok_transform = True
            obj_number = token.morph.get("Number", [None])[0]
            obj_pos = get_actual_inflection(token)["pos"]
            obj_token = token
        
        elif token.pos_ == "PUNCT":
            punct = token.text
    
    if ok_transform is False:
        print(f"Propozitia: {sentence} nu se poate trece la diateza pasiva!")
        return None

    new_subject = get_new_subject(obj_token, obj_pos)
    
    # acord nou subiect cu predicat
    aux_form = get_right_aux_form(obj_pos, root_pos, obj_number)
    new_root = get_new_root_form(root_verb_part_form, obj_token)

    return " ".join([new_subject.capitalize(), aux_form, new_root, "de", old_subj]) + punct

def get_root_form_p2a(token, subj_pos, new_subject, aux_pos):
    new_token = nlp(token)
    all_inflections_for_root = get_all_forms(new_token[0])

    time_found = "prezent"
    time_choices = ["prezent", "perfect simplu", "mai mult ca perfect", "imperfect", "participiu pasiv"]
    for time in time_choices:
        if time.lower() in aux_pos.lower():    
            time_found = time

    number = "singular"
    if "plural" in subj_pos:
        number = "plural"

    person = "persoana a III-a"
    try:
        person = new_subject.morph.get("Person", ["persoana a III-a"])[0]
        if person == "1":
            person = "persoana I"
        elif person == "2":
            person = "persoana a II-a"
        elif person == "3":
            person = "persoana a III-a"
    except: 
        pass

    if time_found == "participiu pasiv":
        inflection_found = [form for form in all_inflections_for_root if time_found in form["pos"].lower()][0]["form"]
        if number == "singular" and person == "persoana I":
            return f"am {inflection_found}"
        elif number == "singular" and person == "persoana a II-a":
            return f"ai {inflection_found}"
        elif number == "singular" and person == "persoana a III-a":
            return f"a {inflection_found}"
        elif number == "plural" and person == "persoana I":
            return f"am {inflection_found}"
        elif number == "plural" and person == "persoana a II-a":
            return f"ați {inflection_found}"
        elif number == "plural" and person == "persoana a III-a":
            return f"au {inflection_found}"
    else:
        all_inflections_filtered_tense = [form for form in all_inflections_for_root if time_found in form["pos"].lower()]
        all_inflections_filtered_tense_number = [form for form in all_inflections_for_root if number in form["pos"] and "Indicativ" in form["pos"]]
        all_inflections_filtered_tense_number_person = [form for form in all_inflections_filtered_tense_number if person in form["pos"]][0]

        return all_inflections_filtered_tense_number_person["form"]
    # # pass

def get_nominative_form(token, subj_pos):
    if token.morph.get("Case", ["Acc,Nom"])[0] == "Acc":
        number = "singular"
        if "plural" in subj_pos:
            number = "plural"

        gender = ""
        try:
            gender = new_subject.morph.get("Gender", ["Masc"])[0]
            if gender == "Fem":
                gender = "feminin"
            else:
                gender = "masculin"
        except: 
            pass

        inflections = get_all_forms(token)
        nominative_form = [form["form"] for form in inflections if gender in form["pos"] and number in form["pos"]][0]
        token_to_return = nlp(nominative_form)
        return token_to_return[0]

def passive_to_active(sentence):
    doc = nlp(sentence)

    new_subject = ""
    new_root_form = ""
    new_obl = ""
    subj_pos = ""
    obj_pos = ""
    punct = ""
    aux_token = ""
    aux_pos = ""

    for token in doc:
        if token.dep_ in "nsubj" or "nsubj" in token.dep_:
            new_obl = token.text
            obj_pos = get_actual_inflection(token)["pos"]
            subtree = [t for t in token.subtree]
            if len(subtree) > 1:
                new_obl = " ".join([t.text.lower() for t in subtree])

        elif token.dep_ == "ROOT":
            new_root_form = token
            
        elif token.dep_ in "obl:agent":
            new_subject_original = token
            new_subject = token
            subj_pos = get_actual_inflection(token)["pos"]

            if new_subject.pos_ == "PRON":
                new_subject = get_nominative_form(new_subject, subj_pos)

            subtree = [t for t in token.subtree if t.text != "de"]
            subtree_pos = [t.pos_ for t in token.subtree if t.text != "de"]
            if len(subtree) > 1:
                if "DET" not in subtree_pos:
                    new_subject = " ".join([get_defined_word(new_subject, subj_pos) if t == new_subject else t.text for t in subtree])
                else:
                    new_subject = " ".join([t.text for t in subtree])

       
        elif token.pos_ == "PUNCT":
            punct = token.text

        elif token.dep_ in "aux" or "aux" in token.dep_:
            aux_token = token
            aux_pos = get_actual_inflection(token)["pos"]

    new_root = get_root_form_p2a(new_root_form.lemma_, subj_pos, new_subject_original, aux_pos)

    if isinstance(new_subject, str):
        return " ".join([new_subject.capitalize(), new_root, new_obl]) + punct
    else:
        new_subject = get_defined_word(new_subject, subj_pos)
        return " ".join([new_subject.capitalize(), new_root, new_obl]) + punct
        

