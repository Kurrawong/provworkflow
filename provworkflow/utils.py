from typing import Union, Optional

from rdflib import URIRef, Literal


def convert_to_uriref(v: Optional[Union[str, URIRef]]) -> Optional[URIRef]:
    """Convert string to URIRef if needed."""
    if v is None:
        return None
    return URIRef(v) if isinstance(v, str) else v


def convert_to_literal(v: Optional[Union[str, Literal]]) -> Optional[Literal]:
    """Convert string to Literal if needed."""
    if v is None:
        return None
    return Literal(v) if isinstance(v, str) else v
