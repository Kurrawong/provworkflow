from __future__ import annotations
from typing import Optional
from typing_extensions import Annotated

from pydantic import Field
from rdflib import Graph, URIRef
from rdflib.namespace import PROV, RDF, SDO

from .agent import Agent
from .prov_reporter import PROVWF
from .utils import convert_to_uriref


class Machine(Agent):
    """provwf:Machine

    :param uri: A URI you assign to the Machine instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to None
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional
    """

    class_uri: URIRef = Field(default=PROVWF.Machine, frozen=True)

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        # Add in type
        g.add((self.uri, RDF.type, PROVWF.Machine))
        g.remove((self.uri, RDF.type, PROV.Agent))

        return g
