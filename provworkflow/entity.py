from __future__ import annotations

from typing import Optional, List, Any

from pydantic import Field
from rdflib import Graph, Literal
from rdflib.namespace import DCAT, PROV, RDF

from .agent import Agent
from .namespace import PROVWF
from .prov_reporter import ProvReporter


class Entity(ProvReporter):
    """prov:Entity

    [... original docstring ...]
    """

    value: Optional[Any] = Field(
        default=None,
        description="Any Python object to be exchanged within the workflow",
    )
    was_used_by: List[Any] = Field(  # Type Any to avoid circular import with Activity
        default_factory=list, description="Activities that used this Entity"
    )
    was_generated_by: List[Any] = (
        Field(  # Type Any to avoid circular import with Activity
            default_factory=list, description="Activities that generated this Entity"
        )
    )
    was_attributed_to: Optional[Agent] = Field(
        default=None, description="Agent this Entity is attributed to"
    )
    was_revision_of: Optional[Entity] = Field(
        default=None, description="Entity this is a revision of"
    )
    external: Optional[bool] = Field(
        default=None, description="Whether this Entity exists outside the workflow"
    )

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        g.bind("dcat", DCAT)

        # Add in type
        g.add((self.uri, RDF.type, PROV.Entity))
        g.remove((self.uri, RDF.type, PROVWF.ProvReporter))

        if self.value is not None:
            g.add((self.uri, PROV.value, Literal(self.value)))

        for a in self.was_used_by:
            if a is not None:
                a.prov_to_graph(g)
                g.add((a.uri, PROV.used, self.uri))

        for a in self.was_generated_by:
            if a is not None:
                a.prov_to_graph(g)
                g.add((a.uri, PROV.generated, self.uri))

        if self.was_attributed_to is not None:
            self.was_attributed_to.prov_to_graph(g)
            g.add((self.uri, PROV.wasAttributedTo, self.was_attributed_to.uri))

        if self.was_revision_of is not None:
            self.was_revision_of.prov_to_graph(g)
            g.add((self.uri, PROV.wasRevisionOf, self.was_revision_of.uri))

        if self.external:
            g.add((self.uri, PROV.wasAttributedTo, Literal("Workflow")))

        return g


def convert_to_entity(v):
    """Convert input to Entity if needed."""
    if isinstance(v, Entity):
        return v
    elif isinstance(v, dict):
        return Entity(**v)
    elif isinstance(v, list):
        return [convert_to_entity(item) for item in v]
    else:
        raise ValueError(f"Invalid type for serves_datasets item: {type(v)}")
