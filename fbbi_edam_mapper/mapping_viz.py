from __future__ import annotations
import rdflib
from pathlib import Path
from rdflib.namespace import RDFS
import graphviz
import rdflib.resource
import csv

# read filtered ontologies
edam_file = Path(Path(__file__).resolve().parent, "ontologies/edam_bioimaging_microscopy.ttl")
edam = rdflib.Graph()
edam.parse(edam_file)

fbbi_file = Path(Path(__file__).resolve().parent, "ontologies/fbbi_microscopy.ttl")
fbbi = rdflib.Graph()
fbbi.parse(fbbi_file)


proposed_file = Path(Path(__file__).resolve().parent, "ontologies/new_taxonomy.ttl")
proposed = rdflib.Graph()
proposed.parse(proposed_file)


def RenderTaxonomy(node_set: NodeSet):
    graph = graphviz.Digraph(graph_attr={"rankdir": "RL"})
    for node in node_set:
        node.graphviz_render_label(graph)
    return graph

class Node:
    def __init__(self, uri: rdflib.URIRef, parents: NodeSet, label: str):
        self.uri = uri
        self.parents = parents
        self.label = label
        self.color = None
    
    def __eq__(self, other):
        if isinstance(other, Node):
            if other.uri == self.uri:
                return True
        else:
            return False
    
    def __hash__(self):
        return hash((self.uri))
        
    def add_parent(self, parent: Node):
        self.parents.add(parent)

    def reparent(self, new_parents: NodeSet):
        self.parents = new_parents
    
    def graphviz_render_label(self, graph: graphviz.Digraph):
        node_ref = self.dot_reference()
        graph.node(node_ref, color=self.color, fontcolor=self.color)
        for parent in self.parents:
            graph.edge(node_ref, parent.dot_reference())
    
    def dot_reference(self):
        if 'edamontology' in str(self.uri):
            dot_ref = "edamontology_" + self.label
            self.color = '#236A65'
        elif 'FBbi_'in str(self.uri):
            dot_ref = "fbbi_" + self.label
            self.colour = 'black'
        return dot_ref





class NodeSet(list):
    def add(self, item: Node):
        if not self.__contains__(item):
            self.append(item)
        else:
            node_in_set = self[self.index(item)]
            for parent in item.parents:
                node_in_set.add_parent(parent)
    

# build class tree
def build_class_tree(graph: rdflib.Graph, start_class: rdflib.URIRef) -> tuple[Node, NodeSet]:
    node_set = NodeSet()
    label = str(next(graph.objects(start_class, RDFS.label)))
    start_node = Node(uri=start_class, parents=NodeSet(), label=label)
    node_set.add(start_node)
    recursive_build_class_tree(graph, start_class, start_node, node_set)
    return start_node, node_set
        
def recursive_build_class_tree(graph: rdflib.Graph, start_class: rdflib.URIRef, start_node: Node, node_set: NodeSet) -> None:
    for cls in graph.subjects(RDFS.subClassOf, start_class):
        label = str(next(graph.objects(cls, RDFS.label)))
        node = Node(uri=cls, parents=NodeSet(), label=label)
        node.add_parent(start_node)
        node_set.add(node)
        recursive_build_class_tree(graph, cls, node, node_set)


edam_top, edam_nodes = build_class_tree(edam, rdflib.URIRef("http://edamontology.org/topic_Microscopy"))
fbbi_top, fbbi_nodes = build_class_tree(fbbi, rdflib.URIRef("http://purl.obolibrary.org/obo/FBbi_00000241"))
proposed_top, proposed_nodes = build_class_tree(proposed, rdflib.URIRef("http://purl.obolibrary.org/obo/FBbi_00000241"))


edam_graph = RenderTaxonomy(edam_nodes)
edam_graph.render('ontologies/edam_graph.gv', view=True) 
fbbi_graph = RenderTaxonomy(fbbi_nodes)
fbbi_graph.render('ontologies/fbbi_graph.gv', view=True) 
proposed_graph = RenderTaxonomy(proposed_nodes)
proposed_graph.render('ontologies/proposed.gv', view=True)