import mariadb
import sys
import spacy
import json

write = open("extras.txt", "w")
f = open('forme_morfologice.json')
mapare = json.load(f)
all_words_extracted = []

def connect_to_db():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="admin",
            host="127.0.0.1",
            port=3306,
            database="dexonline"
        )

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn

def mapare_inflections_dexonline(cursor):
    cursor.execute(f'select id, description, modelType from Inflection')
    for x in cursor:
        write.write('"' + str(x[0]) + '": ' + '[' + x[1] + ", " + x[2] + "]," + "\n")


def find_entry_by_inflected_form(cur, cuvant):
    # alta idee de a cauta cuvantul direct in inflectedForm dar tot apar conflicte (vezi inflection id)
    cur.execute(f'select lexemeId, inflectionId from InflectedForm where formNoAccent = "{cuvant}" order by lexemeId')
    row = cur.fetchone()
    idLexeme = row[0]
    inflectionId = row[1]

    pos = mapare['DEXONLINE_MORPH'][str(inflectionId)]
    
    cur.execute(f'select * from Lexeme where id like "{idLexeme}"')
    rows_resulted = []
    for el in cur:
        rows_resulted.append(el)
    
    word_to_return = ""

    for word in rows_resulted:
        if word[14] == pos:
            word_to_return = word

    return word_to_return

def extract_all_infected_forms_for_word(cur, lexemeId):
    global all_words_extracted

    cur.execute(f'select Inflection.description, InflectedForm.formNoAccent from InflectedForm \
                join Inflection on Inflection.id = InflectedForm.inflectionId \
                where lexemeId = {lexemeId}')
    
    rows_resulted = []
    for el in cur:
        rows_resulted.append(el)

    if rows_resulted[0] not in all_words_extracted:
        all_words_extracted.append(rows_resulted[0])
        for x in rows_resulted[1:]:
            write.write(str(x)+"\n")
        write.write("\n\n\n\n")
    else:
        return

def find_entry_by_lexeme(cur, cuvant, parte_de_vorbire):
    cur.execute(f'select * from Lexeme where formNoAccent like "{cuvant}"')
    rows_resulted = []
    for el in cur:
        rows_resulted.append(el)
    
    word_to_return = ""

    for word in rows_resulted:
        if word[14] == parte_de_vorbire:
            word_to_return = word
            break

    return word_to_return

def find_entry_final(cursor, token):
    actual_pos = ""

    for forms in mapare['UNIVERSAL_DEPENDECIES'][token.pos_]:
        morph = str(token.morph)
        if morph in forms or forms in morph:
            actual_pos = mapare['UNIVERSAL_DEPENDECIES'][token.pos_][forms]

    cuvant = find_entry_by_lexeme(cursor, token.lemma_, actual_pos)
    
    err_subst_prop = 0
    # case-uri tratate
    if token.pos_ == "NOUN":
        if not len(cuvant):
            cuvant = find_entry_by_lexeme(cursor, token.lemma_, "N")

    elif token.pos_ == "VERB" or token.pos_ == "AUX":
        if not len(cuvant):
            cuvant = find_entry_by_lexeme(cursor, token.lemma_, "VT")
    
    elif token.pos_ == "PROPN":
        if not len(cuvant):
            cuvant = find_entry_by_lexeme(cursor, token.lemma_, "I")
        if not len(cuvant):
            cuvant = find_entry_by_lexeme(cursor, token.lemma_, "T")
        if not len(cuvant):
            err_subst_prop = 1
    
    if token.ent_type_ == "PERSON" and token.text[0].isupper():
        err_subst_prop = 1
    
    err_no_found = 0
    if len(cuvant) == 0:
        try:
            cuvant = find_entry_by_inflected_form(cursor, token.text)
        except:
            err_no_found = 1

    if err_subst_prop:
        print(f"Cuvantul: {token.text} este substantiv propriu de forma invariabila!")
        write.write(f"Cuvantul: {token.text} este substantiv propriu de forma invariabila!\n\n\n")
        return 
    elif err_no_found:
        print(f"Cuvantul: {token.text} nu se afla in baza de date!")
        write.write(f"Cuvantul: {token.text} nu se afla in baza de date!\n\n\n")
        return 

    if cuvant:
        extract_all_infected_forms_for_word(cursor, cuvant[0])
    return cuvant

def validate_token(token):
    if token.lang_ != "ro":
        return False
    if not token.text.isalpha():
        return False
    if token.ent_type_ in ["ORGANIZATION", "EVENT", "GPE"]:
        return False
    
    return True

def main():
    global all_words_extracted

    cursor = connect_to_db().cursor()
    
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
            # print(token, token.ent_type_)
            if validate_token(token) == True: 
                # print(token, token.pos_, token.ent_type_, "accepted")
                # vezi cum banezi PERSON
                # # continue
                find_entry_final(cursor, token)
    
    print(all_words_extracted)

    t2 = time.time() - t1
    print("TIMP: ", t2)


main()

# pt mama merge la magazin: 0.47 s
# pt textul cu romania ia 10.5s