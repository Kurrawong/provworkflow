from provworkflow import Workflow, PROVWF, ProvWorkflowException
import provworkflow.block
from rdflib import Literal
from rdflib.namespace import OWL, RDF, PROV, XSD
from datetime import datetime


def test_prov_to_graph():
    """A basic Workflow should prov_to_graph an Activity which is specialised as provwf:Workflow and has at least
    1 Block within it

    :return: None
    """

    w = Workflow()
    b1 = provworkflow.block.Block()
    b2 = provworkflow.block.Block()
    w.blocks.append(b1)
    w.blocks.append(b2)

    rdf = w.prov_to_graph().serialize(format="longturtle")
    for line in rdf.split("\n"):
        if "startedAtTime" in line:
            words = line.split('"')
            assert words[1].endswith(':00')
