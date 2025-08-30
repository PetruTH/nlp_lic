# DexFlex Documentation

DexFlex is a Python package for Romanian language processing.  
It leverages [dexonline](https://github.com/dexonline/dexonline) to extract dictionary data, applies rule-based methods, and integrates **spaCy** with the Romanian model [`ro_core_news_lg`](https://spacy.io/models/ro).  
The library provides functionality such as inflection handling, synonym suggestions, and transformations between tenses and voices.

---

## Installation

DexFlex is available on PyPI:

pip install dexflex

Note: On the first run, a setup script will be executed to fetch and prepare the dictionary data required by DexFlex.
This process may take a few minutes depending on your internet connection.
---

## Features

### 🔹 Inflection Handling

* For a given target word, extract **all inflectional forms**.

### 🔹 Tense Transformation

* Automated switching between **past perfect** and **past simple**.

### 🔹 Synonym Suggestions

* Context-aware synonym generation.

### 🔹 Voice Transformation

* Convert **active → passive** voice and **passive → active** voice.

---

## Synonym Suggestion Process

Synonym generation is performed in **four steps**:

1. Identify the current contextual meaning of the word
2. Select synonyms that match the sentence’s meaning
3. Inflect synonyms to match the contextual grammatical form
4. Heuristically sort and return synonyms

### Sorting Criteria

* Length of the word
* Dictionary ordering
* Approximate syllable count
* Similarity with context embeddings
* Frequency

---

## Usage

### Import

```python
pip install dexflex
```

```python
from dexflex.prototype import *
import spacy

nlp = spacy.load("ro_core_news_lg")
```

---

### Example 1: Inflection Handling

```python
data_aif = [
    ("ocol", 0),
    ("Rece, crudă, geloasă pe frumusețea și șarmul Cenușăresei,", 2),
    ("Ea era hotărâtă să susțină interesele propriilor sale fiice.", 0),
    ("Castelul a ajuns o ruină.", 0),
]

for sample in data_aif:
    doc = nlp(sample[0])
    all_forms_for_word = get_all_forms(doc[sample[1]])

    print(f"For target-word: {doc[sample[1]]} there are all the inflected forms:")
    for form in all_forms_for_word:
        print(form)
    print("\n\n")
```

---

### Example 2: Synonym Suggestions

```python
samples = [
    ("Am observat eroarea la timp.", 2),
    ("Ea a învățat să cânte la pian.", 4),
    ("Am observat eroarea la timp.", 1),
    ("Ei au reparat mașina stricată.", -2),
    ("Tu ai scris o poezie frumoasă.", -2),
    ("Ea s-a gătit pentru o cină delicioasă.", 3),
    ("El a uitat să aducă documentele.", -2),
    ("Ea a primit un cadou de ziua ei.", 4),
    ("Tu ai vorbit cu profesorul?", -2),
    ("Ei au construit un parc nou.", 2),
    ("El a plecat la camera lui.", -3)
]

for sample in samples:
    doc = nlp(sample[0])
    syn_list = [syn[0] for syn in doc[sample[1]]._.get_syns()]
    print(f"Synonyms for: {doc[sample[1]]} are {syn_list}")
```

---

## Additional Notes

* DexFlex uses **dexonline data**, transformed into JSON files for efficient lookups.
* Example contexts are stored as **embeddings in `.feather` format** for better memory handling.
* A working **demo** is provided in [`demo.ipynb`](demo.ipynb).

---

## Resources

* 📚 DexOnline reference: [github.com/dexonline/dexonline](https://github.com/dexonline/dexonline)
* 📦 PyPI package: [pypi.org/project/dexflex](https://pypi.org/project/dexflex/)
* 🔎 SpaCy Romanian model: [`ro_core_news_lg`](https://spacy.io/models/ro)

---