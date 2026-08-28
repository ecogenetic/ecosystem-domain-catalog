#!/usr/bin/env python3.14
"""Compile OWL + SHACL (or introspected schema) into a PhysicalModel."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

from agents.data_agent.introspect import entity_from_collection
from agents.shared.catalog_index import local_name
from agents.shared.paths import CATALOG_ROOT, source_dir
from agents.shared.rdf_parse import parse_rdf_graph

BFO_ROLE = URIRef("http://purl.obolibrary.org/obo/BFO_0000023")
SH = Namespace("http://www.w3.org/ns/shacl#")


def camel_to_snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return s.replace("-", "_").lower()


def pluralize_table(name: str) -> str:
    lower = name.lower()
    if lower.endswith("s"):
        return lower
    if lower.endswith("y") and len(lower) > 1 and lower[-2] not in "aeiou":
        return lower[:-1] + "ies"
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return lower + "es"
    return lower + "s"


def class_to_table(class_local: str) -> str:
    """Singular snake_case table name so introspect entity matches OWL local name."""
    return camel_to_snake(class_local)


def property_to_column(prop_local: str) -> str:
    return camel_to_snake(prop_local)


def xsd_to_sql(xsd_iri: str) -> str:
    iri = (xsd_iri or "").lower()
    if "datetime" in iri or "date" in iri:
        return "TIMESTAMPTZ"
    if "decimal" in iri or "double" in iri or "float" in iri:
        return "NUMERIC"
    if "integer" in iri or "int" in iri:
        return "INTEGER"
    if "boolean" in iri:
        return "BOOLEAN"
    return "TEXT"


def xsd_to_bson(xsd_iri: str) -> str:
    iri = (xsd_iri or "").lower()
    if "datetime" in iri or "date" in iri:
        return "date"
    if "decimal" in iri or "double" in iri or "float" in iri:
        return "decimal"
    if "integer" in iri or "int" in iri:
        return "int"
    if "boolean" in iri:
        return "bool"
    return "string"


def _is_role_class(g: Graph, cls: URIRef) -> bool:
    iri = str(cls)
    loc = local_name(iri)
    if loc.endswith("Role") or iri.endswith("Role"):
        return True
    for parent in g.objects(cls, RDFS.subClassOf):
        if parent == BFO_ROLE:
            return True
    return False


def _lit(g: Graph, subj: URIRef, pred: URIRef) -> str:
    vals = list(g.objects(subj, pred))
    if not vals:
        return ""
    v = vals[0]
    return str(v) if isinstance(v, Literal) else str(v)


def _extract_shacl(g: Graph) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for shape in g.subjects(RDF.type, SH.NodeShape):
        targets = [str(t) for t in g.objects(shape, SH.targetClass)]
        for prop in g.objects(shape, SH.property):
            constraint: dict[str, Any] = {}
            paths = [str(p) for p in g.objects(prop, SH.path)]
            if paths:
                constraint["pathIri"] = paths[0]
                constraint["path"] = local_name(paths[0])
            for mc in g.objects(prop, SH.minCount):
                try:
                    constraint["minCount"] = int(mc)
                except (TypeError, ValueError):
                    pass
            for dt in g.objects(prop, SH.datatype):
                constraint["datatype"] = str(dt)
            classes = [str(c) for c in g.objects(prop, SH["class"])]
            if classes:
                constraint["classIri"] = classes[0]
                constraint["classLocal"] = local_name(classes[0])
            values: list[str] = []
            for item in g.objects(prop, SH["in"]):
                for val in g.items(item):
                    if isinstance(val, Literal):
                        values.append(str(val))
            if values:
                constraint["in"] = values
            if not constraint:
                continue
            for t in targets:
                out.setdefault(t, []).append(constraint)
    return out


def _load_ontology_graphs(
    domain_id: str | None = None,
    industry: str | None = None,
    turtle: str | None = None,
) -> Graph:
    g = Graph()
    if turtle:
        g += parse_rdf_graph(data=turtle)
        return g
    if not domain_id:
        raise ValueError("domainId or turtle is required")
    base = CATALOG_ROOT / "domains" / domain_id
    ont_path = base / "ontology.ttl"
    shapes_path = base / "shapes.ttl"
    if ont_path.exists():
        g += parse_rdf_graph(path=ont_path)
    if shapes_path.exists():
        g += parse_rdf_graph(path=shapes_path)
    if industry:
        overlay = base / "industries" / industry / "overlay.ttl"
        if overlay.exists():
            g += parse_rdf_graph(path=overlay)
    return g


def compile_physical_model(
    domain_id: str | None = None,
    industry: str | None = None,
    turtle: str | None = None,
) -> dict[str, Any]:
    g = _load_ontology_graphs(domain_id=domain_id, industry=industry, turtle=turtle)
    shacl = _extract_shacl(g)
    tables: list[dict[str, Any]] = []
    class_by_iri: dict[str, str] = {}

    for subj in g.subjects(RDF.type, OWL.Class):
        if not isinstance(subj, URIRef):
            continue
        iri = str(subj)
        if iri.startswith("http://www.w3.org/") or iri.startswith("http://purl.org/"):
            continue
        if _is_role_class(g, subj):
            continue
        cls_local = local_name(iri)
        if not cls_local:
            continue
        table_name = class_to_table(cls_local)
        entity = cls_local
        class_by_iri[iri] = entity
        pk_col = f"{camel_to_snake(cls_local)}_id"
        columns: list[dict[str, Any]] = [
            {
                "name": pk_col,
                "sqlType": "TEXT",
                "bsonType": "string",
                "primaryKey": True,
                "nullable": False,
                "propertyIri": None,
                "kind": "pk",
            }
        ]
        tables.append(
            {
                "entity": entity,
                "table": table_name,
                "classIri": iri,
                "columns": columns,
            }
        )

    table_by_entity = {t["entity"]: t for t in tables}
    table_by_class_iri = {t["classIri"]: t for t in tables}

    for ptype, kind in ((OWL.DatatypeProperty, "datatype"), (OWL.ObjectProperty, "object")):
        for subj in g.subjects(RDF.type, ptype):
            if not isinstance(subj, URIRef):
                continue
            prop_iri = str(subj)
            prop_local = local_name(prop_iri)
            if not prop_local:
                continue
            domains = [str(d) for d in g.objects(subj, RDFS.domain) if isinstance(d, URIRef)]
            ranges = [str(r) for r in g.objects(subj, RDFS.range) if isinstance(r, URIRef)]
            for dom in domains:
                dom_local = class_by_iri.get(dom) or local_name(dom)
                tbl = table_by_entity.get(dom_local) or table_by_class_iri.get(dom)
                if not tbl:
                    continue
                col_name = property_to_column(prop_local)
                if any(c["name"] == col_name for c in tbl["columns"]):
                    continue
                if kind == "object":
                    range_iri = ranges[0] if ranges else ""
                    range_local = class_by_iri.get(range_iri) or local_name(range_iri)
                    target_tbl = table_by_entity.get(range_local)
                    fk_col = f"{camel_to_snake(range_local)}_id" if range_local else col_name
                    if any(c["name"] == fk_col for c in tbl["columns"]):
                        fk_col = col_name
                    col: dict[str, Any] = {
                        "name": fk_col,
                        "sqlType": "TEXT",
                        "bsonType": "string",
                        "primaryKey": False,
                        "nullable": True,
                        "propertyIri": prop_iri,
                        "kind": "fk",
                        "refEntity": range_local,
                        "refTable": target_tbl["table"] if target_tbl else class_to_table(range_local),
                        "refClassIri": range_iri,
                    }
                else:
                    range_iri = ranges[0] if ranges else str(XSD.string)
                    col = {
                        "name": col_name,
                        "sqlType": xsd_to_sql(range_iri),
                        "bsonType": xsd_to_bson(range_iri),
                        "primaryKey": False,
                        "nullable": True,
                        "propertyIri": prop_iri,
                        "kind": "column",
                    }
                tbl["columns"].append(col)

    for class_iri, constraints in shacl.items():
        tbl = table_by_class_iri.get(class_iri)
        if not tbl:
            continue
        for c in constraints:
            path = c.get("path") or local_name(c.get("pathIri") or "")
            if not path:
                continue
            col_name = property_to_column(path)
            if c.get("classIri") or c.get("classLocal"):
                range_local = c.get("classLocal") or local_name(c.get("classIri") or "")
                fk_col = f"{camel_to_snake(range_local)}_id"
                existing = next((x for x in tbl["columns"] if x["name"] in {col_name, fk_col}), None)
                if existing is None:
                    target_tbl = table_by_entity.get(range_local)
                    tbl["columns"].append(
                        {
                            "name": fk_col,
                            "sqlType": "TEXT",
                            "bsonType": "string",
                            "primaryKey": False,
                            "nullable": not (c.get("minCount", 0) >= 1),
                            "propertyIri": c.get("pathIri"),
                            "kind": "fk",
                            "refEntity": range_local,
                            "refTable": target_tbl["table"] if target_tbl else class_to_table(range_local),
                            "refClassIri": c.get("classIri"),
                        }
                    )
                    existing = tbl["columns"][-1]
                else:
                    existing["nullable"] = not (c.get("minCount", 0) >= 1)
            else:
                existing = next((x for x in tbl["columns"] if x["name"] == col_name), None)
                if existing is None:
                    dt = c.get("datatype") or str(XSD.string)
                    tbl["columns"].append(
                        {
                            "name": col_name,
                            "sqlType": xsd_to_sql(dt),
                            "bsonType": xsd_to_bson(dt),
                            "primaryKey": False,
                            "nullable": not (c.get("minCount", 0) >= 1),
                            "propertyIri": c.get("pathIri"),
                            "kind": "column",
                        }
                    )
                    existing = tbl["columns"][-1]
                if existing:
                    if c.get("minCount", 0) >= 1:
                        existing["nullable"] = False
                    if c.get("in"):
                        existing["enum"] = c["in"]
                    if c.get("datatype"):
                        existing["sqlType"] = xsd_to_sql(c["datatype"])
                        existing["bsonType"] = xsd_to_bson(c["datatype"])

    model = {
        "ok": True,
        "domainId": domain_id,
        "industryId": industry,
        "tables": tables,
        "tableCount": len(tables),
    }
    return model


def physical_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Invert an introspected schema into a PhysicalModel."""
    tables: list[dict[str, Any]] = []
    for coll in schema.get("collections") or []:
        if coll.get("infrastructure"):
            continue
        entity = coll.get("entity") or entity_from_collection(coll["name"])
        pk_col = f"{camel_to_snake(entity)}_id"
        columns: list[dict[str, Any]] = [
            {
                "name": pk_col,
                "sqlType": "TEXT",
                "bsonType": "string",
                "primaryKey": True,
                "nullable": False,
                "propertyIri": None,
                "kind": "pk",
            }
        ]
        for field in coll.get("fields") or []:
            fname = field["name"]
            if fname in {"_id", "__v", "id"}:
                continue
            if field.get("ref"):
                ref_entity = field["ref"]
                fk_col = fname if fname.endswith("_id") or fname.endswith("Id") else f"{camel_to_snake(ref_entity)}_id"
                columns.append(
                    {
                        "name": fname if fname != fk_col else fk_col,
                        "sqlType": "TEXT",
                        "bsonType": "string",
                        "primaryKey": False,
                        "nullable": True,
                        "propertyIri": None,
                        "kind": "fk",
                        "refEntity": ref_entity,
                        "refTable": class_to_table(ref_entity),
                    }
                )
            else:
                types = field.get("types") or ["string"]
                sql = "TEXT"
                bson = "string"
                if any("int" in str(t).lower() or "float" in str(t).lower() for t in types):
                    sql = "NUMERIC"
                    bson = "decimal"
                if any("date" in str(t).lower() for t in types):
                    sql = "TIMESTAMPTZ"
                    bson = "date"
                if any("bool" in str(t).lower() for t in types):
                    sql = "BOOLEAN"
                    bson = "bool"
                columns.append(
                    {
                        "name": fname,
                        "sqlType": sql,
                        "bsonType": bson,
                        "primaryKey": False,
                        "nullable": True,
                        "propertyIri": None,
                        "kind": "column",
                    }
                )
        enums = coll.get("enumsFromLookups") or {}
        for col in columns:
            if col["name"] in enums:
                col["enum"] = enums[col["name"]]
        tables.append({"entity": entity, "table": coll["name"], "classIri": None, "columns": columns})
    return {"ok": True, "domainId": None, "industryId": None, "tables": tables, "tableCount": len(tables)}


def save_physical_model(source_id: str, model: dict[str, Any]) -> Path:
    dest = source_dir(source_id) / "physical.model.json"
    dest.write_text(json.dumps(model, indent=2), encoding="utf-8")
    return dest
