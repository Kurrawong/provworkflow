from __future__ import annotations

from typing import Optional

from pydantic import Field, BeforeValidator
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import PROV, RDF
from typing_extensions import Annotated

from .entity import Entity
from .prov_reporter import PROVWF


def convert_to_error_literal(v):
    """Convert input to Literal with ERROR default."""
    if isinstance(v, str):
        return Literal(v)
    elif isinstance(v, Literal):
        return v
    elif v is None:
        return Literal("ERROR")
    return v


class ErrorEntity(Entity):
    """A prov:Entity specialised to communicate an error

    :param uri: A URI you assign to the Entity instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to ERROR
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional

    :param value: (prov:value) should be used to contain simple literal values when the Entity is entirely defined
        by that value.
    :type value: Literal, optional
    """

    label: Annotated[Literal, BeforeValidator(convert_to_error_literal)] = Field(
        default="ERROR", description="Text label for the error entity"
    )
    value: Annotated[Literal, BeforeValidator(convert_to_error_literal)] = Field(
        default="ERROR", description="Value describing the error"
    )
    class_uri: URIRef = Field(default=PROVWF.ErrorEntity, frozen=True)

    class Config:
        arbitrary_types_allowed = True

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        # Add in type
        g.add((self.uri, RDF.type, PROVWF.ErrorEntity))
        g.remove((self.uri, RDF.type, PROV.Entity))

        return g
