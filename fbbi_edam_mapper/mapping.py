from __future__ import annotations
import rdflib
from pathlib import Path
from rdflib.namespace import RDFS
import graphviz
import rdflib.resource
import csv

# read mappings
mappings = []
mapping_tsv_path = Path(Path(__file__).resolve().parent, "mapping/FBBI-EDAM-mapping.tsv")
with open(mapping_tsv_path) as file:
    mapping_file = csv.DictReader(file, delimiter="\t")
    [mappings.append(row) for row in mapping_file]

# read filtered ontologies
edam_file = Path(Path(__file__).resolve().parent, "ontologies/edam_bioimaging_microscopy.ttl")
edam = rdflib.Graph()
edam.parse(edam_file)
# drop non-subclass statements
edam_class_tree = rdflib.Graph()
for stmt in edam.triples((None, RDFS.subClassOf, None)):
    edam_class_tree.add(stmt)

print(len(edam_class_tree))


fbbi_file = Path(Path(__file__).resolve().parent, "ontologies/fbbi_microscopy.ttl")
fbbi = rdflib.Graph()
fbbi.parse(fbbi_file)
fbbi_class_tree = rdflib.Graph()
for stmt in fbbi.triples((None, RDFS.subClassOf, None)):
    fbbi_class_tree.add(stmt)

print(len(fbbi_class_tree))

# find unmapped classes directly under mapped classes
direct_mapping = {}
for row in mappings:
    if row["EDAM Direct hit"] == 'No need to map?':
        pass
    elif row["EDAM Direct hit"] == 'no direct hit':
        pass
    else:
        direct_mapping[rdflib.URIRef(row["Fbbi URL"])] = rdflib.URIRef(row["EDAM Direct hit"])

class_tree_proposed = rdflib.Graph()
top_fbbi_class = rdflib.URIRef("http://purl.obolibrary.org/obo/FBbi_00000241")

def seek_single_subclass(parent_class: rdflib.URIRef, origin_graph: rdflib.Graph, merge_graph: rdflib.Graph, final_graph: rdflib.Graph, mapping: dict[rdflib.URIRef, rdflib.URIRef]):
    new_subclasses = set()
    for origin_class in origin_graph.subjects(RDFS.subClassOf, parent_class):
        final_graph.add((origin_class, RDFS.subClassOf, parent_class))
        new_subclasses.add(origin_class)
    if parent_class in mapping.keys():
        for merge_class in merge_graph.subjects(RDFS.subClassOf, mapping[parent_class]):
            if merge_class not in mapping.values():
                final_graph.add((merge_class, RDFS.subClassOf, parent_class))
            mapping[merge_class] = merge_class
            new_subclasses.add(merge_class)
    return new_subclasses

def recursive_subclass(top_class):
    subclasses = seek_single_subclass(top_class, fbbi_class_tree, edam_class_tree, class_tree_proposed, direct_mapping)
    for cls in subclasses:
        subclasses = recursive_subclass(cls)

recursive_subclass(top_fbbi_class)

new_graph = rdflib.Graph()
for stmt in class_tree_proposed:
    new_graph.add(stmt)

for stmt in fbbi.triples((top_fbbi_class, None, None)):
        new_graph.add(stmt)

for cls in class_tree_proposed.subjects():
    for stmt in fbbi.triples((cls, None, None)):
        if stmt[1] != RDFS.subClassOf:
            new_graph.add(stmt)
    for stmt in edam.triples((cls, None, None)):
        if stmt[1] != RDFS.subClassOf:
            new_graph.add(stmt)
print(len(fbbi))
print(len(edam))
print(len(new_graph))

new_graph.serialize("ontologies/new_taxonomy.ttl")