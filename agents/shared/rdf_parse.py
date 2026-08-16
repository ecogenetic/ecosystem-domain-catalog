#!/usr/bin/env python3.14
"""Parse RDF 1.1 and RDF 1.2 into an rdflib Graph for catalog preview and ingest.

Oxigraph reads Turtle 1.2 (VERSION / @version, annotations, triple terms,
dirLangString). RDFLib 7.x still parses Turtle 1.1 only, so asserted triples are
copied into rdflib and triple terms are dropped (no TripleTerm type in 7.6).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import XSD

try:
    import pyoxigraph as ox
except ImportError:  # pragma: no cover — declared in pyproject.toml
    ox = None


def _guess_ox_format(text: str):
    head = text.lstrip()
    if head.startswith("<?xml") or head.startswith("<rdf:") or head.startswith("<RDF"):
        return ox.RdfFormat.RDF_XML
    return ox.RdfFormat.TURTLE


def _ox_term(term: Any):
    if ox is None:
        return None
    if isinstance(term, ox.NamedNode):
        return URIRef(term.value)
    if isinstance(term, ox.BlankNode):
        return BNode(term.value)
    if isinstance(term, ox.Literal):
        if term.language:
            return Literal(term.value, lang=term.language)
        datatype = term.datatype.value if term.datatype else None
        if datatype in {None, str(XSD.string)}:
            return Literal(term.value)
        return Literal(term.value, datatype=URIRef(datatype))
    return None


def parse_rdf_graph(*, data: str | None = None, path: Path | None = None) -> Graph:
    """Parse Turtle 1.2 / Turtle 1.1 / RDF/XML / TriG into an rdflib Graph."""
    if path is not None and data is None:
        data = path.read_text(encoding="utf-8")
    text = data or ""
    ox_error: Exception | None = None
    if ox is not None:
        try:
            g = Graph()
            fmt = _guess_ox_format(text)
            for quad in ox.parse(text.encode("utf-8"), format=fmt):
                subj = _ox_term(quad.subject)
                pred = _ox_term(quad.predicate)
                obj = _ox_term(quad.object)
                if subj is None or pred is None or obj is None:
                    continue
                g.add((subj, pred, obj))
            return g
        except Exception as exc:  # noqa: BLE001 — try RDFLib Turtle 1.1 next
            ox_error = exc
    g = Graph()
    head = text.lstrip()
    fmt = "xml" if head.startswith("<?xml") or head.startswith("<rdf:") or head.startswith("<RDF") else "turtle"
    try:
        g.parse(data=text, format=fmt)
        return g
    except Exception as exc:
        raise ox_error or exc
