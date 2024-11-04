from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict, BeforeValidator
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, PROV, OWL, RDF, RDFS, XSD
from typing_extensions import Annotated

from .exceptions import ProvWorkflowException
from .namespace import PROVWF, PWFS
from .utils import convert_to_uriref, convert_to_literal


class ProvReporter(BaseModel):
    """A base class for PROV reporting in semantic web applications.

    This class serves as a superclass for all PROV classes (Entity, Activity, Agent) and facilitates
    provenance logging. It should not be instantiated directly - use instead Entity, Activity,
    or their subclasses like Block & Workflow.

    Attributes:
        uri: A unique identifier for this instance. If not provided, a UUID-based URI will be generated.
        label: A human-readable label for this instance.
        named_graph_uri: The URI of the named graph this instance belongs to.
        class_uri: The URI of the specialized class this instance represents.
        version_uri: The version URI, derived from Git info if available.
        created: Timestamp of instance creation.

    Example:
        ```python
        # This class should not be used directly, but its subclasses work like this:
        class MySpecializedBlock(ProvReporter):
            class_uri = URIRef("http://example.org/MyBlock")

        block = MySpecializedBlock(label="My Block")
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    uri: Annotated[URIRef, BeforeValidator(convert_to_uriref)] = Field(
        default_factory=lambda: URIRef(PWFS + str(uuid.uuid1())),
        description="Unique identifier for this instance",
    )
    label: Optional[Annotated[Literal, BeforeValidator(convert_to_literal)]] = Field(
        default=None, description="Human-readable label"
    )
    named_graph_uri: Optional[Annotated[URIRef, BeforeValidator(convert_to_uriref)]] = (
        Field(default=None, description="URI of the named graph")
    )
    class_uri: Optional[Annotated[URIRef, BeforeValidator(convert_to_uriref)]] = Field(
        default=None, description="URI of the specialized class"
    )
    version_uri: Optional[URIRef] = Field(
        default=None, description="Version URI from Git or fallback"
    )
    created: Literal = Field(
        default_factory=lambda: Literal(
            datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
            datatype=XSD.dateTimeStamp,
        ),
        description="Timestamp of instance creation",
    )

    @model_validator(mode="after")
    def validate_class_specialization(self) -> ProvReporter:
        """Validate class specialization rules and setup version URI."""
        # Validate class specialization
        known_classes = ["Entity", "Activity", "Agent", "Workflow", "Block"]
        class_name = self.__class__.__name__

        if class_name in known_classes and self.class_uri is not None:
            raise ProvWorkflowException(
                "If a ProvWorkflow-defined class is used without specialisation, class_uri must not be set"
            )
        elif class_name not in known_classes and self.class_uri is None:
            raise ProvWorkflowException(
                "A specialised Block must have a class_uri instance variable supplied"
            )
        elif self.class_uri is not None and not str(self.class_uri).startswith("http"):
            raise ProvWorkflowException("If supplied, a class_uri must start with http")

        # Setup version URI
        git_info = os.getenv("INCLUDE_GIT_INFO")
        if git_info == "true":
            try:
                from .git_utils import get_version_uri

                uri_str = get_version_uri()
                if uri_str is not None:
                    self.version_uri = URIRef(uri_str)
            except ImportError:
                print(
                    "Git executable not found on system - git related functionality not available"
                )

        if self.version_uri is None:
            self.version_uri = self.uri

        return self

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        """Convert the instance to RDF graph format.

        Args:
            g: An existing graph to add statements to. If None, creates a new graph.

        Returns:
            The RDF graph containing this instance's statements.
        """
        if g is None:
            if self.named_graph_uri is not None:
                g = Graph(identifier=self.named_graph_uri)
            else:
                g = Graph()

        # Bind namespaces
        g.bind("prov", PROV)
        g.bind("provwf", PROVWF)
        g.bind("pwfs", PWFS)
        g.bind("owl", OWL)
        g.bind("dcterms", DCTERMS)

        # Add basic statements
        g.add((self.uri, RDF.type, PROVWF.ProvReporter))
        g.add((self.uri, DCTERMS.created, self.created))

        # Add label if present
        if self.label is not None:
            g.add((self.uri, RDFS.label, self.label))

        return g
