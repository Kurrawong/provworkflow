from __future__ import annotations

from typing import List, Optional

from pydantic import Field, model_validator
from rdflib import URIRef, Graph, Literal
from rdflib.namespace import OWL, PROV, RDF, RDFS, XSD

from . import ProvWorkflowException
from .activity import Activity
from .block import Block
from .namespace import PROVWF


class WorkflowException(Exception):
    pass


class Workflow(Activity):
    """A Workflow is a specialised prov:Activity that contains 1+ Blocks (also specialised Activity instances).

    For its Semantic Web definition, see https://data.kurrawong.ai/def/provworkflow/Workflow (not available
    yet).

    You cannot set the _used_ or _generated_ properties of a Workflow as you can for other Activities as these are
    calculated automatically, based on the _used_ & _generated_ properties of the Blocks the Workflow contains.

    You can either set the (list of) the Workflow's Blocks at creation time or afterwards. The order is unimportant as
    Block ordering is understood using Blocks' startedAtTime property.

    :param uri: A URI you assign to the Workflow instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to None
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional

    :param was_associated_with: An Agent that ran this Workflow (prov:wasAssociatedWith), defaults to None
    :type was_associated_with: Agent, optional

    :param blocks: A list of Blocks that were run by this Workflow
    :type blocks: List[Block], optional
    """

    blocks: List[Block] = Field(
        default_factory=list, description="Blocks that were run by this workflow"
    )

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def validate_blocks(self) -> Workflow:
        """Ensure workflow has at least one block when converting to graph."""
        # We don't validate here because blocks might be added after creation
        return self

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        if not self.blocks:
            raise ProvWorkflowException(
                "A Workflow must have at least one Block within it"
            )

        if g is None:
            if self.named_graph_uri is not None:
                g = Graph(identifier=URIRef(self.named_graph_uri))
            else:
                g = Graph()

        # Add in type
        g.add((self.uri, RDF.type, PROVWF.Workflow))
        g.remove((self.uri, RDF.type, PROV.Activity))

        # Add in type for specialized workflows
        if self.__class__.__name__ != "Workflow":
            g.add((self.uri, RDFS.subClassOf, PROVWF.Block))
            g.add((self.uri, RDF.type, self.class_uri))
            g.remove((self.uri, RDF.type, PROV.Activity))

        # Soft typing using the version_uri
        if self.version_uri is not None:
            g.add(
                (
                    self.uri,
                    OWL.versionIRI,
                    Literal(str(self.version_uri), datatype=XSD.anyURI),
                )
            )

        # Add the prov graph of each block to this Workflow's prov graph
        for block in self.blocks:
            block.prov_to_graph(g)
            # Associate this Block with this Workflow
            g.add((self.uri, PROVWF.hadBlock, block.uri))

        # Build all the details for the Workflow itself
        g = super().prov_to_graph(g)

        # Attach external Block inputs and outputs to the Workflow
        all_inputs = [o for o in g.objects(subject=None, predicate=PROV.used)]
        all_outputs = [o for o in g.objects(subject=None, predicate=PROV.generated)]

        for i in [x for x in all_inputs if x not in all_outputs]:
            g.add((self.uri, PROV.used, i))

        for o in [x for x in all_outputs if x not in all_inputs]:
            g.add((self.uri, PROV.generated, o))

        # Add back in any externals
        for s in g.subjects(predicate=PROV.wasAttributedTo, object=Literal("Workflow")):
            g.add((self.uri, PROV.generated, s))
            g.remove((s, PROV.generated, Literal("")))

        return g
