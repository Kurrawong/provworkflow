from __future__ import annotations

from typing import List, Optional

from pydantic import Field, BeforeValidator
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCAT, PROV, RDF
from typing_extensions import Annotated

from .entity import Entity, convert_to_entity
from .utils import convert_to_literal


class DataService(Entity):
    """dcat:DataService

    :param uri: A URI you assign to the DataService instance. If None, a UUID-based URI will be created,
    defaults to None
    :type uri: Union[URIRef, str], optional

    :param label: A text label you assign, defaults to None
    :type label: str, optional

    :param named_graph_uri: A Named Graph URI you assign, defaults to None
    :type named_graph_uri: Union[URIRef, str], optional

    :param access_uri: (dcat:accessURL) should be used to contain links used to access the content of the Entity, e.g. a
        Google Cloud Services API call or an S3 Bucket link.
    :type access_uri: str, optional

    :param service_parameters: (provwf:serviceParameters) should be used to contain any parameters used for web
        services accessed via access_uri that are not contained within the URI itself.
    :type service_parameters: str, optional

    :param was_used_by: The inverse of prov:used: this indicates which Activities prov:used this Entity
    :type was_used_by: Activity, optional

    :param was_generated_by: Generation is the completion of production of a new entity by an activity. This entity
        did not exist before generation and becomes available for usage after this generation.
    :type was_generated_by: Activity, optional

    :param was_attributed_to: An Agent that this Entity is ascribed to (created by). Note "this Entity" refers to this
    occurence of use of the DataService, not the DataService in general, so it's the Agent that specified DataService
     use at this time, with these parameters.
    :type was_attributed_to: Agent, optional

    :param serves_datasets: Dataset Entities that this DataServise provides access to.
    This is a form of dcat:distribution
    :type serves_datasets: Entity, optional

    :param external: Whether this Entity exists outside the workflow
    :type external: bool, optional
    """

    value: Optional[Annotated[Literal, BeforeValidator(convert_to_literal)]] = Field(
        default=None, description="Value as a Literal"
    )
    access_uri: Optional[Annotated[Literal, BeforeValidator(convert_to_literal)]] = (
        Field(default=None, description="URI for accessing the service")
    )
    service_parameters: Optional[
        Annotated[Literal, BeforeValidator(convert_to_literal)]
    ] = Field(default=None, description="Parameters for the service")
    serves_datasets: Annotated[List[Entity], BeforeValidator(convert_to_entity)] = (
        Field(default_factory=list, description="Datasets served by this service")
    )
    class_uri: URIRef = Field(default=DCAT.DataService, frozen=True)

    class Config:
        arbitrary_types_allowed = True

    def prov_to_graph(self, g: Optional[Graph] = None) -> Graph:
        g = super().prov_to_graph(g)

        g.bind("dcat", DCAT)

        # Add in type
        g.add((self.uri, RDF.type, DCAT.DataService))
        g.remove((self.uri, RDF.type, PROV.Entity))

        # Add served datasets
        for dataset in self.serves_datasets:
            dataset.prov_to_graph(g)
            g.add((self.uri, DCAT.servesDataset, dataset.uri))

        return g
