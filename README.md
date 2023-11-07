# nlp_lic
If you want to use this library, you have to clone this repo and then pip install dexonlineplugin-0.0.1-py3-none-any.whl. 
Create a new file and import "PrepareData" from "nlp_lic.prototype". After that, before the first run of your program, call
the "run" function (a static method from PrepareData which will download all the data needed from dexonline database. It will 
basically try to download 5 JSONS needed as resources (if they are not downloaded yet)).

There are two additions for token in spacy. The first one is the is_valid() method to ensure that the token can be found in
dexonline database, and the second one forms_() method will return a list populated with all the morphological forms found
for a certain word in dexonline.

PS: in prototype.py file is a function called main that will provide you a demo to show the functionality of this framework.
PSS: this project is still developing so this is not the final version.
