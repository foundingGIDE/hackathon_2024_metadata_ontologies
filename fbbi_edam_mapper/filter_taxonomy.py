import rdflib
from pathlib import Path
from rdflib.namespace import RDFS

import rdflib.resource

# Script to narrow down the class heirachry to classes we care about based on the class tree, and write out as TTL
# FSHERWOOD prefers TTL for reading purposes

edam_file = Path(Path(__file__).resolve().parent, "EDAM-bioimaging_alpha06.owl")
edam = rdflib.Graph()
edam.parse(edam_file)
edam_out = rdflib.Graph()

edam_label_map = {}
for edam_class in edam.subjects(RDFS.subClassOf * "*", rdflib.URIRef("http://edamontology.org/topic_Microscopy")):
    edam_out += edam.triples((edam_class, None, None))

edam_out.serialize("edam_bioimaging_microscopy.ttl")

fbbi_file = Path(Path(__file__).resolve().parent, "fbbi.owl")
fbbi = rdflib.Graph()
fbbi.parse(fbbi_file)
fbbi_out = rdflib.Graph()

fbbi_label_map = {}
for fbbi_class in fbbi.subjects(RDFS.subClassOf * "*", rdflib.URIRef("http://purl.obolibrary.org/obo/FBbi_00000241")):
    fbbi_out += fbbi.triples((fbbi_class, None, None))

fbbi_out.serialize("fbbi_microscopy.ttl")
