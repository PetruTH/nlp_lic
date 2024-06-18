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
            database="dexonline",
        )

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn


"""
The next 4 functions will store all data needed for
finding a word in dexonline database.
"""


def json_creator_lexeme_info(cursor):
    json_dict = {}
    cursor.execute("select formNoAccent, id, modelType from Lexeme")
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [{"id": row[1], "pos": row[2]}]
        else:
            json_dict[row[0]].append(
                {"id": row[1], "pos": row[2]}
            )

    with open("word_id_pos.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_inflected_forms(cursor):
    json_dict = {}

    working_dict = {}
    with open("word_id_pos.json", "r") as fisier_json:
        working_dict = json.load(fisier_json)

    for element in working_dict.keys():
        wordList = working_dict[element]

        for word in wordList:
            wordId = word["id"]
            cursor.execute(
                f"select Inflection.description, InflectedForm.formNoAccent \
                    from InflectedForm \
                    join Inflection \
                    on Inflection.id=InflectedForm.inflectionId \
                    where lexemeId={wordId}"
            )

            json_dict[wordId] = []

            for inflected_form in cursor:
                if wordId not in json_dict.keys():
                    json_dict[wordId] = [
                        {"pos": inflected_form[0], "form": inflected_form[1]}
                    ]
                else:
                    json_dict[wordId].append(
                        {"pos": inflected_form[0], "form": inflected_form[1]}
                    )

    with open("wordId_inflected_forms.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_inflected_form_id_and_pos(cursor):
    json_dict = {}
    cursor.execute(
        "select formNoAccent, lexemeId, inflectionId \
                   from InflectedForm"
    )
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [{"lexemeId": row[1], "inflectionId": row[2]}]
        else:
            json_dict[row[0]].append(
                {"lexemeId": row[1], "inflectionId": row[2]}
            )

    with open("inflected_form_lexemeId_inflectionId.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_wordId_form_pos(cursor):
    json_dict = {}
    cursor.execute("select formNoAccent, id, modelType from Lexeme")
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[1]] = [{"form": row[0], "pos": row[2]}]
        else:
            json_dict[row[1]].append(
                {"form": row[0], "pos": row[2]}
            )

    with open("id_word_pos.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_entrylexeme(cursor):
    json_dict = {}
    cursor.execute("select lexemeId, entryId from EntryLexeme")
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("entry_lexeme.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_entrytree(cursor):
    json_dict = {}
    cursor.execute("select entryId, treeId from TreeEntry")
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("tree_entry.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_relation(cursor):
    json_dict = {}
    cursor.execute("select treeId, meaningId from Relation where type=1")
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [row[1]]
        else:
            json_dict[row[0]].append(row[1])

    with open("relation.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)


def json_creator_synonyms_storage(cursor):
    json_dict = {}
    cursor.execute(
        "select Relation.meaningId, Relation.treeId, Tree.description \
        from Relation \
        join Tree on Tree.id=Relation.treeId where Relation.type=1"
    )
    for row in cursor:
        if row[0] not in json_dict.keys():
            json_dict[row[0]] = [(row[1], row[2])]
        else:
            json_dict[row[0]].append((row[1], row[2]))

    with open("synonyms.json", "w") as fisier_json:
        json.dump(json_dict, fisier_json, indent=4, sort_keys=True)

import numpy
import json
from json import JSONEncoder

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

from transformers import AutoTokenizer, AutoModel
import torch
tokenizer = AutoTokenizer.from_pretrained("dumitrescustefan/bert-base-romanian-uncased-v1", do_lower_case=True)
model = AutoModel.from_pretrained("dumitrescustefan/bert-base-romanian-uncased-v1")


def get_embeddings(text):
    tokenized_text = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**tokenized_text)

    word_embeddings = outputs.last_hidden_state
    averaged_embedding = torch.mean(word_embeddings, dim=0)

    return averaged_embedding


def json_creator_context(cursor):
    """
        This function will store every context example as its embedding into files to
        easily compute contextual similarity between them.
    """
    
    import time
    tree_ids_distinct = []
    cursor.execute("select distinct treeId from Meaning order by treeId")

    for row in cursor:
        tree_ids_distinct.append(row[0])

    json_dict = {}
    ln = len(tree_ids_distinct)

    t1 = time.time()
    last_tree_id_saved = 0
    cluster_counter = 0
    for treeId in tree_ids_distinct:
        
        cursor.execute(f"select treeId, internalRep from Meaning where treeId={treeId}")
        
        if cluster_counter % 45 == 0:
            print(cluster_counter, " / ", ln, "a salvat 45 treids in: ", time.time() - t1)
            t1 = time.time()

            stocare_eficienta(json_dict, filename=f"context_stock/range_{last_tree_id_saved}_{treeId}.feather")
            last_tree_id_saved = treeId
            json_dict = {}

        cluster_counter += 1

        for row in cursor:
            emb = get_embeddings(row[1])
            last_emb = torch.mean(emb, dim=0)
            if row[0] not in json_dict.keys():
                json_dict[row[0]] = [numpy.array(last_emb)]
            else:
                json_dict[row[0]].append(numpy.array(last_emb))

    stocare_eficienta(json_dict, filename=f"context_stock/range_{last_tree_id_saved}_{tree_ids_distinct[-1]}.feather")
    

import feather
import pyarrow as pa

def stocare_eficienta(data_dict, filename="data.feather"):
    """
        This function will store data in a .feather format
    """
    try:
        comprimat_dict = {}
        for cheie, matrice_list in data_dict.items():
            comprimat_dict[cheie] = [comprima_matrice(matrice) for matrice in matrice_list]
        
        pyarrow_data = {
            "id": list(comprimat_dict.keys()),
            "examples": list(comprimat_dict.values()),
        }

        table = pa.Table.from_pydict(pyarrow_data) 
        feather.write_dataframe(table, filename)
        print(f"Date salvate cu succes în {filename}")

    except Exception as e:
        print(f"Eroare la stocarea datelor: {e}")

def comprima_matrice(matrice):
    """
        This function will return a zipped content.
    """
    import zstandard as zstd
    return zstd.compress(matrice.tobytes())

def make_intervals_files():
    import re
    """
        intervals.txt (manually created - ls in context_stock) has already all range_x_y.feather files as this:
        file1 file2
        file3 file4
        and so on
    """
    regex_interval = re.compile('range_(\d+_\d+)\.feather')
    intervale = []
    f = open("nlp_lic/dexonline/util/intervals.txt", "r")
    files = f.readlines()
    files_interval = []
    for file in files:
        for onefile in file.split("\t"):
            files_interval.append(onefile)

    for nume_fisier in files_interval:
        match = regex_interval.match(nume_fisier)
        if match:
            intervale.append(match.group(1))
        
    def suma_interval(interval):
        x, y = interval.split("_")
        return int(x) + int(y)

    intervale = sorted(intervale, key=suma_interval)
    r = open("nlp_lic/dexonline/util/intervals_v2.txt", "w")
    for interval in intervale:
        r.write(interval + "\n")

def binary_interval_search(intervale, z):
    """
        This function will binary search the interval of a treeId to found its
        contextual examples
    """
    
    left = 0
    right = len(intervale) - 1

    while left <= right:
        mid = (left + right) // 2
        x_mid, y_mid = intervale[mid]

        if z < x_mid:
            right = mid - 1
        elif z > y_mid:
            left = mid + 1
        else:
            return intervale[mid]

    return None

def incarcare_eficienta(id_exemplu=None):
        """
        find the interval for id_exemplu using binary search
        """
        
        f = open("util/intervals_v2.txt", "r")
        intervals = f.readlines()
        intervals_for_binary_search = []
        for interval in intervals:
            splitted_interval = interval.split("_")
            left = splitted_interval[0]
            right = splitted_interval[1]
            intervals_for_binary_search.append((int(left), int(right)))

        minrange, maxrange = binary_interval_search(intervale=intervals_for_binary_search, z=id_exemplu)

        filename = f"util/context_stock/range_{minrange}_{maxrange}.feather"
        comprimat_dict = feather.read_dataframe(filename)
        decomprimat_list = []

        filtered_row = comprimat_dict.query(f"id == {id_exemplu}")

        for prop_comprimate in filtered_row["examples"]:
            for context_ex in prop_comprimate:
                el_decomprimat = decomprima_matrice(context_ex)
                decomprimat_list.append(el_decomprimat)

        return decomprimat_list
    

def decomprima_matrice(comprimat):
    """
        This function will unzip the content of a file and it will cast in a numpy array.
    """
    import zstandard as zstd
    decompressed_bytes = zstd.decompress(comprimat)
    decomp = numpy.frombuffer(decompressed_bytes)
    return decomp

# def main():
#     """
#     If there is need for an update, uncomment following function
#     calls to update all JSON files needed.
#     """

    # cursor = connect_to_db().cursor()
# 
    # calling json_creators functions to store all data needed from DB
    # json_creator_lexeme_info(cursor)
    # print("done 1/3")
    # json_creator_inflected_forms(cursor)
    # print("done 2/3")
    # json_creator_inflected_form_id_and_pos(cursor)
    # print("done 3/3")
    # json_creator_wordId_form_pos(cursor)
    # json_creator_entrylexeme(cursor)
    # json_creator_entrytree(cursor)
    # json_creator_relation(cursor)
    # json_creator_synonyms_storage(cursor)

    # import time
    # t1 = time.time()
    # # print("am inceput la ", t1)
    # json_creator_context(cursor) 
    # t2 = time.time() - t1
    # # print("s a terminat la: ", time.time())
    # print("a durat: ", t2)

    # decompressed = incarcare_eficienta(id_exemplu=47082)
    # print(decompressed.shape)
    # for cheie, matrice in decompressed.items():
        # print(f"Cheie: {cheie}")
        # print(f"Valoare: {matrice}")



# main()
