import rdflib
from pathlib import Path
from rdflib.namespace import RDFS

import rdflib.resource

# Lexical mapping script

# read filtered ontologies
edam_file = Path(Path(__file__).resolve().parent, "edam_bioimaging_microscopy.ttl")
edam = rdflib.Graph()
edam.parse(edam_file)


fbbi_file = Path(Path(__file__).resolve().parent, "fbbi_microscopy.ttl")
fbbi = rdflib.Graph()
fbbi.parse(fbbi_file)

# create a map for ontology 1. 
# Note properties & string simplification based on what is going on in that ontology - may need changes for use on others
edam_lookup = {}
for edam_subject, edam_string in edam.subject_objects(RDFS.label | rdflib.URIRef("http://www.geneontology.org/formats/oboInOwl#hasExactSynonym") | rdflib.URIRef("http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym")):
    if edam_subject not in edam_lookup.keys():
        edam_lookup[edam_subject] = []
    edam_lookup[edam_subject].append(str(edam_string).lower().replace("-", " "))

# create a map for ontology 2. 
# Note properties & string simplification based on what is going on in that ontology - may need changes for use on others
# goes through to try to find lexical mappings
fbbi_edam_map = {}
for fbbi_subject, fbbi_label in fbbi.subject_objects(RDFS.label, None):
    for edam_class, edam_string_list in edam_lookup.items():
        fbbi_string_label = str(fbbi_label).lower().replace("-", " ")
        if fbbi_string_label in edam_string_list:
            if fbbi_subject not in fbbi_edam_map.keys():
                fbbi_edam_map[fbbi_subject] = []
            fbbi_edam_map[fbbi_subject].append({"edam_class": edam_class, "fbbi_label": fbbi_string_label})

[print(tup) for tup in fbbi_edam_map.items()]
print(len(fbbi_edam_map))