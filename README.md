# dexflex
## Romanian language plugin

Dexflex leverages the SpaCy package by adding new features for the Romanian language:
- Synonym suggestion sorted by simplicity
- Automatic change for vebrs from past perfect to past simple in Romanian 
- Extracting all inflected forms available for a word


 The dexflex package is open source with a public repository available on GitHub at https://github.com/PetruTH/nlp_lic. Bellow is attached a code snippet for a better understanding of the framework.

```python

from dexflex.prototype import *
import spacy

nlp = spacy.load("ro_core_news_lg")

doc = nlp("Acesta a fost un test.")
print(doc, doc._.oltenizare())

doc = nlp("Noi vom testa imediat.")
print(doc[-2]._.get_syns())