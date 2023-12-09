import mariadb
import sys
import json


def connect_to_db():
    """
        Connects to mariaDB database of dexonline
    """
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


"""
The next 4 functions will store all data needed for finding a word in dexonline database.
"""


def json_creator_lexeme_info(cursor):
    json_dict = {}
    cursor.execute('select formNoAccent, id, modelType from Lexeme')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [{"id": row[1], "pos": row[2]}]
        else:
            json_dict[row[0]].append({"id": row[1], "pos": row[2]})

    with open("word_id_pos.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

def json_creator_inflected_forms(cursor):
    json_dict = {}
    
    working_dict = {}
    with open("word_id_pos.json", 'r') as fisier_json:
        working_dict = json.load(fisier_json)
    
    for element in working_dict.keys():
        wordList = working_dict[element]

        for word in wordList:
            wordId = word["id"]
            cursor.execute(f'select Inflection.description, InflectedForm.formNoAccent from InflectedForm \
                    join Inflection on Inflection.id = InflectedForm.inflectionId \
                    where lexemeId = {wordId}')
            
            json_dict[wordId] = []
            
            for inflected_form in cursor:
                if wordId not in json_dict.keys():
                    json_dict[wordId] = [{"pos": inflected_form[0], "form": inflected_form[1]}]
                else:
                    json_dict[wordId].append({"pos": inflected_form[0], "form": inflected_form[1]})
        
    with open("wordId_inflected_forms.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_inflected_form_id_and_pos(cursor):
    json_dict = {}
    cursor.execute('select formNoAccent, lexemeId, inflectionId from InflectedForm')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [{"lexemeId": row[1], "inflectionId": row[2]}]
        else:
            json_dict[row[0]].append({"lexemeId": row[1], "inflectionId": row[2]})

    with open("inflected_form_lexemeId_inflectionId.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_wordId_form_pos(cursor):
    json_dict = {}
    cursor.execute('select formNoAccent, id, modelType from Lexeme')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[1]] = [{"form": row[0], "pos": row[2]}]
        else:
            json_dict[row[1]].append({"form": row[0], "pos": row[2]})

    with open("id_word_pos.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

def json_creator_entrylexeme(cursor):
    json_dict = {}
    cursor.execute('select lexemeId, entryId from EntryLexeme')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("entry_lexeme.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

def json_creator_entrytree(cursor):
    json_dict = {}
    cursor.execute('select entryId, treeId from TreeEntry')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("tree_entry.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

def json_creator_relation(cursor):
    json_dict = {}
    cursor.execute('select treeId, meaningId from Relation where type=1')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("relation.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

def json_creator_synonyms_storage(cursor):
    json_dict = {}
    cursor.execute('select Relation.meaningId, Relation.treeId, Tree.description from Relation join Tree on Tree.id = Relation.treeId where Relation.type = 1')
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [(row[1], row[2])]
        else:
            json_dict[row[0]].append((row[1], row[2]))

    with open("synonyms.json", 'w') as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)
    

def main():
    """
        If there is need for an update, uncomment following function calls to update all JSON files needed.
    """

    cursor = connect_to_db().cursor()
    
    # calling json_creators functions to store all data needed from DB
    # json_creator_lexeme_info(cursor)
    # print("done 1/3")
    #json_creator_inflected_forms(cursor)
    #print("done 2/3")
    #json_creator_inflected_form_id_and_pos(cursor)
    #print("done 3/3")
    # json_creator_wordId_form_pos(cursor)
    # json_creator_entrylexeme(cursor)
    # json_creator_entrytree(cursor)
    # json_creator_relation(cursor)
    # json_creator_synonyms_storage(cursor)


main()