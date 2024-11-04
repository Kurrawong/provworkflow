from __future__ import annotations

from typing import Union, Optional

from pydantic import Field, BeforeValidator, model_validator
from rdflib import Graph, URIRef
from rdflib.namespace import PROV, RDF
from typing_extensions import Annotated

from .prov_reporter import ProvReporter, PROVWF
from .utils import convert_to_uriref


class Agent(ProvReporter):
    """prov:Agent

    :param uri: A URI you assign to the Agent instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to None
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional
    """

    acted_on_behalf_of: Optional[
        Union[Agent, Annotated[URIRef, BeforeValidator(convert_to_uriref)]]
    ] = Field(default=None, description="The agent this agent acted on behalf of")

    @model_validator(mode="after")
    def validate_acted_on_behalf_of(self) -> Agent:
        """Convert URIRef to Agent if needed."""
        if isinstance(self.acted_on_behalf_of, URIRef):
            self.acted_on_behalf_of = Agent(uri=self.acted_on_behalf_of)
        return self

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        # Add in type
        g.add((self.uri, RDF.type, PROV.Agent))
        g.remove((self.uri, RDF.type, PROVWF.ProvReporter))

        # Special Agent properties
        if self.acted_on_behalf_of is not None:
            self.acted_on_behalf_of.prov_to_graph(g)
            g.add((self.uri, PROV.actedOnBehalfOf, self.acted_on_behalf_of.uri))

        return g
