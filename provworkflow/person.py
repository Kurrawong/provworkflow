from __future__ import annotations

from typing import Optional

from pydantic import Field, BeforeValidator
from rdflib import Graph, URIRef
from rdflib.namespace import PROV, RDF, SDO
from typing_extensions import Annotated

from .agent import Agent
from .utils import convert_to_uriref


class Person(Agent):
    """prov:Person

    :param uri: A URI you assign to the Person instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to None
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional
    """

    email: Optional[Annotated[URIRef, BeforeValidator(convert_to_uriref)]] = Field(
        default=None, description="Email address as URIRef"
    )
    class_uri: URIRef = Field(default=PROV.Person, frozen=True)

    class Config:
        arbitrary_types_allowed = True

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        # Add in type
        g.add((self.uri, RDF.type, PROV.Person))
        g.remove((self.uri, RDF.type, PROV.Agent))

        # Special person properties
        if self.email is not None:
            g.add((self.uri, SDO.email, self.email))

        return g
