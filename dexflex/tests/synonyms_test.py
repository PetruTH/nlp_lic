import pytest
from dexflex.prototype import *
import spacy
nlp = spacy.load("ro_core_news_lg")

data_for_test = [
    ('Am citit o carte interesantă săptămâna trecută.', 4, ['ciudată', 'interesantă', 'pasionantă', 'captivantă', 'emoționantă']),
    ('Ea a câștigat concursul de desen.', 3, ['concursul', 'concursu', 'spectacolul', 'spectacolu']),
    ('El a fugit departe.', 2, ['grăbit', 'plecat', 'evadat', 'alergat', 'risipit', 'răspândit', 'răzleț', 'gonit', 'răsfirat', 'dispersat']),
    ('Am observat o eroare.', 1, ['văzut', 'observat', 'prins', 'surprins', 'simțit', 'constatat', 'privit', 'aflat', 'sesizat', 'priceput']),
    ('Soțul ei părea o persoană nefericită, fără angajament, fără mari averi și fără prestigiu.', 12, ['averi', 'bogății', 'avuții', 'strânsuri', 'recolte', 'provizii', 'stări', 'posesii', 'bunăstări', 'posesiuni']),
    ('Polemicile din tinerețe aveau sens în lumina climatului Risorgimento, care l-a determinat pe Carducci să demonizeze tot ceea ce putea sta în calea reconquistei libertății care făcuse Roma mare și comunele italiene demne de glorie nepieritoare în Evul Mediu (idiosincrasia inițială pentru literatura străină trebuie înțeleasă în acest sens).', 0, ['disputele', 'polemicile', 'discuțiile']),
    ('În timp ce primii întruchipează virtuți precum dreptatea sau blândețea, eroii negativi sunt conduși de pofta de putere și calcă în picioare toate valorile.', 4, ['creează', 'întrupează', 'incarnează', 'plăsmuiește', 'plăsmuiesc', 'întruchipează', 'înfăptuiește', 'înfăptuiesc']),
    ('Sarcina romancierului este de a efectua o investigație științifică pentru a descoperi legile care guvernează comportamentul uman, apoi de a expune publicului, prin intermediul romanului, relatarea experimentelor sale.', -3, ['experimentelor']),
    ('În societatea italiană, lacerațiile care caracterizează relația dintre intelectual și societate nu s-au format încă, iar elanul optimist al celor care se angajează să creeze o nouă națiune prevalează asupra conflictelor.', -2, ['conflictelor', 'sentimentelor', 'războaielor', 'ordinelor', 'scandalurilor', 'dezacordurilor', 'litigiilor', 'diferendurilor', 'prejudiciilor']),
    ('Astfel, a renunțat la ideea de literatură ca plăcere și a început să scrie opere pentru un public erudit.', 5, ['ideea', 'părerea', 'reflecția', 'socoteala', 'judecata', 'prostia', 'noțiunea', 'aberanța', 'inepția', 'concepția']),
    ('Speriată, am recuperat mingea și m-am strecurat printre picioarele statuii.', 0, ['speriată', 'uluită', 'încurcată', 'fâstâcită', 'teșmenită', 'rătutită', 'timorată', 'îngrozită', 'înfricoșată', 'înfricată']),
    ('A fi foarte atins: suma mai multor mângâieri este o julitură.', 5, ['suma', 'mărimea', 'cantitatea', 'înălțimea', 'mulțimea', 'grămada', 'puzderia']),
    ('Fusese surprinsă de faptul că Taggart trecuse într-o zi, din senin, prin camera ei de mahala.', -2, ['suburbie', 'suburbia', 'periferie', 'periferia']),
    ('Deoarece ideea elementară de funcții este mai bine înțeleasă din punct de vedere clasic, o vom folosi în continuare.', -8, ['tipic', 'specific', 'ilustrativ', 'exponențial', 'caracteristic']),
    ('Uneori va trebui să manipulați expresii într-o formă utilizabilă înainte de a putea efectua operații de calcul.', 5, ['mine', 'expresii', 'zicale', 'vorbe', 'fizionomii', 'înfățișări', 'exprimări', 'zicători', 'locuțiuni']),
    ('Uneori va trebui să manipulați expresii într-o formă utilizabilă înainte de a putea efectua operații de calcul.', 4, ['mânuiți', 'mânuiați', 'maniați', 'manipulați', 'manevrați']),
    ('O astfel de cavitate poate oferi numeroase avantaje funcționale.', 6, ['ample', 'bogate', 'vaste', 'numeroase', 'intense', 'abundente', 'îmbelșugate', 'diverse', 'variate', 'îndelungate']),
    ('Clătirea cu alcool nu îndepărtează cristalul violet care maschează colorantul roșu safanin adăugat.', 2, ['spirt', 'spirit', 'spirituș']),
    ('Linia mare și curbată din stânga este îndreptată în mod elaborat spre mine (mi).', 10, ['făcut', 'scos', 'compus', 'elaborat', 'alcătuit'])
]

def test_synonyms():
    for prop in data_for_test:
        target = nlp(prop[0])[prop[1]]
        all_syns = target._.get_syns()
    
        syns_without_score = []
        for s in all_syns:
            syns_without_score.append(s[0])

        assert syns_without_score == prop[-1], "Different synonyms found!"

    
