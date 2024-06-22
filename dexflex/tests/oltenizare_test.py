import pytest
from dexflex.prototype import *
import spacy
nlp = spacy.load("ro_core_news_lg")

data = [
    ("sunt surprinsă că te-ai întors după mine.", "Sunt surprinsă că te întorseși după mine."),
    ("dacă tu socoteşti că a fi încătuşat, jefuit,", "dacă tu socoteşti că a fi încătuşat, jefuit,"),
    ("nu-şi mai făcea griji că va fi ucis.", "Nu-şi mai făcea griji că va fi ucis."),
    ("succesul tău a fost puţin şi succesul meu.", "Succesul tău fuse puţin şi succesul meu."),
    ("Eu am plecat", "Eu plecai"),
    ("El va fi venit", "El fi venit"),
    ("El ar fi venit, dar nu", "El ar fi venit, dar nu"),
    ("nu l-am mai văzut pe aici.", "Nu îl mai văzui pe aici."),
    ("cenușăreasa va fi surprinsă.", "Cenușăreasa va fi surprinsă."),
    ("nu a mai rămas nimic în ce să crezi.", "Nu mai rămase nimic în ce să crezi."),
    ("atunci, prin ordin regal, acea fată va fi soția prințului.", "Atunci, prin ordin regal, acea fată va fi soția prințului."),
    ("dacă i-ai dat o șansă inimii tale", "dacă îi dădu o șansă inimii tale"),
    ("El va pleca, dar ieri ar fi stat apoi a plecat.", "El va pleca, dar ieri ar fi stat apoi plecă."),
    ("vor deveni realitate.", "Vor deveni realitate."),
    ("îți dai seama ce ai spus", "îți dai seama ce spuse"),
    ("o voi citi eu!", "O voi citi eu!"),
    ("dar a fost așa de frumos!", "Dar fuse așa de frumos!"),
    ("vom mai vedea", "vom mai vedea"),
    ("a fost a mamei", "fuse a mamei"),
    ("ar fi bine să te descotorosești de aceste vise.", "Ar fi bine să te descotorosești de aceste vise."),
    ("Nu mă îndoiesc că ați avut în minte întreaga scenă.", "Nu mă îndoiesc că avurăți în minte întreaga scenă."),
    ("cred că am uitat de toate!", "Cred că uitai de toate!"),
    ("tot va fi interesat de una din ele, nu-i așa?", "Tot va fi interesat de una din ele, nu-i așa?"),
    ("am să stau tot după tine.", "Am să stau tot după tine."),
    ("nu-ţi fă griji pentru mine, e ziua ta cea mare.", "Nu-ţi fă griji pentru mine, e ziua ta cea mare."),
    ("tu ai copite.", "Tu ai copite."),
    ("eu am palme.", "Eu am palme."),
    ("Am citit o carte interesantă săptămâna trecută.", "Citii o carte interesantă săptămâna trecută."),
    ("Ea a câștigat concursul de desen.", "Ea câștigă concursul de desen."),
    ("Noi am vizitat Parisul anul trecut.", "Noi vizitarăm Parisul anul trecut."),
    ("Ai terminat temele pentru astăzi?", "Terminași temele pentru astăzi?"),
    ("Ei au găsit cheia pierdută.", "Ei găsiră cheia pierdută."),
    ("Profesorul a explicat lecția foarte clar.", "Profesorul explică lecția foarte clar."),
    ("Am văzut un film bun aseară.", "Văzui un film bun aseară."),
    ("Ați fost vreodată la munte iarna?", "Fuserăți vreodată la munte iarna?"),
    ("Ei au construit o casă nouă.", "Ei construiră o casă nouă.")
]


def test_oltenizare():
    for sample in data:
        doc = nlp(sample[0])
        assert doc._.oltenizare() == sample[1], "Different result found!"

