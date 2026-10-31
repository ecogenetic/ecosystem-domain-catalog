#!/usr/bin/env python3.14
"""Client for the public Ontology Validation service on ecosystem-server.

Reads ``ONTOLOGY_VALIDATION_SERVER`` (default ``http://localhost:3001``),
normalizes the base URL, and calls unauthenticated endpoints:

* ``GET  {base}/modeling/ontology/validation/metadata``
* ``POST {base}/modeling/ontology/validate``
* ``POST {base}/modeling/ontology/recommendations/apply``

When the remote server is unreachable, falls back to a local pyoxigraph /
rdflib syntax check and stamps ``validationSource: local-fallback``.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None

DEFAULT_SERVER = "http://localhost:3001"


def normalize_validation_server(raw: str | None = None) -> str:
    value = (raw if raw is not None else os.environ.get("ONTOLOGY_VALIDATION_SERVER", "")).strip()
    if not value:
        value = DEFAULT_SERVER
    # Fix common typos: http:localhost:3001 → http://localhost:3001
    value = re.sub(r"^(https?):(?!/)([^/])", r"\1://\2", value)
    if not value.startswith(("http://", "https://")):
        value = "http://" + value.lstrip("/")
    return value.rstrip("/")


def validation_server() -> str:
    return normalize_validation_server()


def _get(path: str, timeout: float = 30.0) -> dict[str, Any]:
    if httpx is None:
        raise RuntimeError("httpx is required for remote ontology validation")
    url = f"{validation_server()}{path}"
    resp = httpx.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, body: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    if httpx is None:
        raise RuntimeError("httpx is required for remote ontology validation")
    url = f"{validation_server()}{path}"
    resp = httpx.post(url, json=body, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_ontology_validation_metadata() -> dict[str, Any]:
    base = validation_server()
    try:
        data = _get("/modeling/ontology/validation/metadata")
        data["validationSource"] = "remote"
        data["validationServer"] = base
        return data
    except Exception as exc:
        return {
            "ok": False,
            "validationSource": "local-fallback",
            "validationServer": base,
            "error": str(exc),
            "serviceVersion": "local-fallback",
            "supportedFormats": ["ttl", "owl", "rdf"],
            "standards": {"RDF 1.2": {}, "OWL 2": {}, "SKOS": {}, "SHACL": {}, "BFO": {}},
            "rules": [],
        }


def validate_ontology(
    ontology_content: str = "",
    shapes_content: str | None = None,
    domain_id: str | None = None,
    industry_id: str | None = None,
    format: str | None = None,
    include_recommendations: bool = True,
) -> dict[str, Any]:
    base = validation_server()
    body: dict[str, Any] = {
        "includeRecommendations": include_recommendations,
    }
    if ontology_content:
        body["inputMode"] = "raw"
        body["content"] = ontology_content
        if format:
            body["format"] = format
    elif domain_id:
        body["inputMode"] = "catalog"
        body["domainId"] = domain_id
        if industry_id:
            body["industryId"] = industry_id
    else:
        return {
            "ok": False,
            "error": "ontology_content or domain_id is required",
            "validationSource": "local-fallback",
            "validationServer": base,
        }
    if shapes_content:
        body["shapesContent"] = shapes_content

    try:
        data = _post("/modeling/ontology/validate", body)
        data["validationSource"] = "remote"
        data["validationServer"] = base
        return data
    except Exception as exc:
        return _local_fallback(ontology_content or "", shapes_content, base, str(exc))


_STANDARD_PREFIX_MAP: dict[str, str] = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sh": "http://www.w3.org/ns/shacl#",
    "bfo": "http://purl.obolibrary.org/obo/BFO_",
}


def _ensure_turtle(content: str) -> str:
    """Convert RDF/XML or OWL/XML content to Turtle so TTL patches can be applied cleanly."""
    head = (content or "").lstrip()
    if not (
        head.startswith("<?xml")
        or head.startswith("<rdf:")
        or head.startswith("<owl:")
        or head.startswith("<Ontology")
        or head.startswith("<RDF")
    ):
        return content
    try:
        from agents.shared.rdf_parse import parse_rdf_graph

        g = parse_rdf_graph(data=content)
        ttl = g.serialize(format="turtle")
        return ttl if isinstance(ttl, str) else ttl.decode("utf-8")
    except Exception:
        return content


def _infer_default_ns(turtle: str) -> str:
    m = re.search(r"@?prefix\s+:\s*<([^>]+)>", turtle, re.I)
    if m:
        return m.group(1)
    m2 = re.search(r"<(https?://[^>]+)>", turtle)
    if m2:
        iri = m2.group(1)
        if "#" in iri:
            return iri.rsplit("#", 1)[0] + "#"
        return iri.rstrip("/") + "#"
    return "https://example.org/ontology#"


def _merge_ttl_patches(base_content: str, snippets: list[str]) -> str:
    """Merge Turtle snippets into base_content, hoisting @prefix declarations to the top
    and ensuring all standard prefixes used in the patched document are declared."""
    base_ttl = _ensure_turtle(base_content)
    declared: dict[str, str] = {}
    for m in re.finditer(r"@?prefix\s+(\w*):\s*<([^>]+)>", base_ttl, re.I):
        declared[m.group(1)] = m.group(2)

    extra_prefixes: dict[str, str] = {}
    body_blocks: list[str] = []
    for raw in snippets:
        lines: list[str] = []
        for line in raw.splitlines():
            pm = re.match(r"^\s*@?prefix\s+(\w*):\s*<([^>]+)>\s*\.?\s*$", line, re.I)
            if pm:
                pfx, uri = pm.group(1), pm.group(2)
                if pfx not in declared:
                    extra_prefixes[pfx] = uri
                    declared[pfx] = uri
            else:
                lines.append(line)
        cleaned = "\n".join(lines).strip()
        if cleaned and cleaned not in base_ttl:
            body_blocks.append(cleaned)

    combined = base_ttl.rstrip() + ("\n\n" + "\n\n".join(body_blocks) if body_blocks else "") + "\n"

    # Ensure default ':' prefix if ':something' is used
    if re.search(r"(?<![:\w]):[A-Za-z_]\w*", combined) and "" not in declared:
        ns = _infer_default_ns(base_ttl)
        extra_prefixes[""] = ns
        declared[""] = ns

    # Ensure standard prefixes (skos:, sh:, bfo:, owl:, rdfs:, xsd:) when used
    for pfx, uri in _STANDARD_PREFIX_MAP.items():
        if pfx not in declared and re.search(rf"(?<![:\w]){pfx}:[A-Za-z0-9_]", combined):
            extra_prefixes[pfx] = uri
            declared[pfx] = uri

    if extra_prefixes:
        header = "\n".join(f"@prefix {k}: <{v}> ." for k, v in extra_prefixes.items())
        combined = header + "\n" + combined
    return combined


def apply_ontology_recommendations(
    ontology_content: str,
    recommendations: list[dict[str, Any]] | None = None,
    shapes_content: str | None = None,
    custom_ttl: str | None = None,
) -> dict[str, Any]:
    base = validation_server()
    ttl_input = _ensure_turtle(ontology_content or "")
    body: dict[str, Any] = {"content": ttl_input}
    if shapes_content:
        body["shapesContent"] = shapes_content
    if recommendations:
        body["recommendations"] = recommendations
    if custom_ttl:
        body["customTtl"] = custom_ttl
    try:
        data = _post("/modeling/ontology/recommendations/apply", body)
        # If the server put SHACL shapes into shapesContent, also merge them into content
        # for single-file session ontologies when shapes_content was not separate
        patched_content = data.get("content") or ttl_input
        if not shapes_content and data.get("shapesContent"):
            patched_content = _merge_ttl_patches(patched_content, [str(data["shapesContent"])])
        else:
            patched_content = _merge_ttl_patches(patched_content, [])
        data["content"] = patched_content
        data["validationSource"] = "remote"
        data["validationServer"] = base
        return data
    except Exception as exc:
        snippets: list[str] = []
        applied: list[str] = []
        for rec in recommendations or []:
            ttl = (rec.get("suggestedTtl") or "").strip()
            if not ttl:
                continue
            snippets.append(ttl)
            applied.append(rec.get("id") or "rec")
        if custom_ttl and custom_ttl.strip():
            snippets.append(custom_ttl.strip())
            applied.append("custom-ttl")
        patched = _merge_ttl_patches(ttl_input, snippets)
        revalidated = _local_fallback(patched, shapes_content, base, str(exc))
        return {
            "ok": True,
            "content": patched,
            "shapesContent": shapes_content,
            "applied": applied,
            "validation": revalidated,
            "validationSource": "local-fallback",
            "validationServer": base,
        }


def _local_fallback(
    ontology_content: str,
    shapes_content: str | None,
    base: str,
    error: str,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []

    def add_issue(
        rule_id: str,
        aspect: str,
        severity: str,
        message: str,
        subject: str | None = None,
        hint: str | None = None,
    ) -> None:
        item: dict[str, Any] = {
            "ruleId": rule_id,
            "aspect": aspect,
            "severity": severity,
            "message": message,
        }
        if subject:
            item["subject"] = subject
        if hint:
            item["hint"] = hint
        issues.append(item)

    def add_rec(
        rec_id: str,
        rule_id: str,
        category: str,
        severity: str,
        title: str,
        rationale: str,
        suggested_ttl: str,
        subject: str | None = None,
        action_type: str = "add_triples",
    ) -> None:
        item: dict[str, Any] = {
            "id": rec_id,
            "ruleId": rule_id,
            "category": category,
            "severity": severity,
            "title": title,
            "rationale": rationale,
            "actionType": action_type,
            "suggestedTtl": suggested_ttl,
            "autoApplicable": bool(suggested_ttl.strip()),
        }
        if subject:
            item["subject"] = subject
        recommendations.append(item)

    text = ontology_content or ""
    if not text.strip():
        add_issue("SYN-009", "syntax", "error", "Empty ontology content", hint="Provide Turtle or RDF/XML.")
    else:
        if "VERSION" in text or "@version" in text.lower():
            features.append({"ruleId": "SYN-004", "detail": "VERSION"})
        if "<<" in text:
            features.append({"ruleId": "SYN-005", "detail": "triple-term"})
        if re.search(r"@[A-Za-z]{2,8}(?:-[A-Za-z0-9]+)*--(?:ltr|rtl)\b", text):
            features.append({"ruleId": "SYN-006", "detail": "directional-lang"})

        is_xml = text.lstrip().startswith("<")
        if not is_xml:
            declared = set(re.findall(r"@?prefix\s+(\w*):\s*<[^>]+>", text, re.I))
            declared.add("")
            builtin = {"rdf", "rdfs", "owl", "xsd", "skos", "sh", "bfo", "dc", "dcterms", "core"}
            for p in sorted(set(re.findall(r"(?<![:\w])(\w+):", text))):
                if p.lower() in {"http", "https", "urn"} or p in declared or p.lower() in builtin:
                    continue
                add_issue("SYN-001", "syntax", "error", f"Undeclared prefix '{p}:'", subject=f"{p}:")
                add_rec(
                    f"rec-prefix-{p}",
                    "SYN-001",
                    "syntax",
                    "error",
                    f"Declare @prefix {p}:",
                    f"Prefix '{p}:' is used without an @prefix declaration.",
                    f"@prefix {p}: <https://example.org/{p}#> .",
                    subject=f"{p}:",
                )

    classes: list[str] = []
    obj_props: list[str] = []
    data_props: list[str] = []
    roles: list[str] = []
    triple_count = 0

    try:
        from rdflib import RDF, RDFS, OWL
        from rdflib.namespace import SKOS
        from agents.shared.rdf_parse import parse_rdf_graph

        g = parse_rdf_graph(data=text)
        triple_count = len(g) if g is not None else 0
        features.append({"ruleId": "SYN-010", "detail": f"triples={triple_count}"})

        if triple_count == 0 and text.strip():
            add_issue(
                "SYN-007",
                "syntax",
                "error",
                "Parsed zero triples — check Turtle / RDF/XML syntax.",
            )

        ont_nodes = list(g.subjects(RDF.type, OWL.Ontology))
        if not ont_nodes and "owl:Ontology" not in text and "<owl:Ontology" not in text:
            add_issue(
                "OWL-001",
                "owl_skos",
                "error",
                "Missing owl:Ontology header",
                hint="Declare an ontology IRI typed as owl:Ontology with rdfs:label.",
            )
            add_rec(
                "rec-owl-header",
                "OWL-001",
                "owl_skos",
                "error",
                "Add owl:Ontology header",
                "Every ontology should declare its ontology IRI and label.",
                '@prefix owl: <http://www.w3.org/2002/07/owl#> .\n'
                '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
                '<https://example.org/ontology> a owl:Ontology ;\n'
                '    rdfs:label "Domain Ontology" ;\n'
                '    rdfs:comment "Ontology description." .',
            )
        elif ont_nodes:
            has_label = any(list(g.objects(o, RDFS.label)) for o in ont_nodes)
            if not has_label:
                add_issue("OWL-002", "owl_skos", "warning", "Ontology header missing rdfs:label")

        def local(iri: Any) -> str:
            s = str(iri)
            if "#" in s:
                return s.rsplit("#", 1)[-1]
            if "/" in s:
                return s.rsplit("/", 1)[-1]
            return s

        class_nodes = list(dict.fromkeys(g.subjects(RDF.type, OWL.Class)))
        for r in g.subjects(RDF.type, RDFS.Class):
            if r not in class_nodes:
                class_nodes.append(r)

        if not class_nodes:
            add_issue(
                "OWL-003",
                "owl_skos",
                "error",
                "No owl:Class (or rdfs:Class) declarations found",
                hint="Declare domain concepts as owl:Class with skos:prefLabel and skos:definition.",
            )

        for c in class_nodes:
            cname = local(c)
            if not cname or cname.startswith("N"):
                continue
            classes.append(cname)
            parents = [str(p) for p in g.objects(c, RDFS.subClassOf)]
            if any("BFO_0000023" in p or p.endswith("0000023") for p in parents) or cname.endswith("Role"):
                roles.append(cname)
            prefs = list(g.objects(c, SKOS.prefLabel)) or list(g.objects(c, RDFS.label))
            defs = list(g.objects(c, SKOS.definition)) or list(g.objects(c, RDFS.comment))
            alts = list(g.objects(c, SKOS.altLabel))
            human = re.sub(r"([a-z])([A-Z])", r"\1 \2", cname)
            if not prefs:
                add_issue("SKOS-001", "owl_skos", "warning", f"Class :{cname} missing skos:prefLabel", subject=cname)
                add_rec(
                    f"rec-pref-{cname}",
                    "SKOS-001",
                    "owl_skos",
                    "warning",
                    f"Add skos:prefLabel for :{cname}",
                    "Preferred labels are required for catalog indexing and UI display.",
                    f":{cname} skos:prefLabel \"{human}\" .",
                    subject=cname,
                )
            if not defs:
                add_issue("SKOS-002", "owl_skos", "warning", f"Class :{cname} missing skos:definition", subject=cname)
                add_rec(
                    f"rec-def-{cname}",
                    "SKOS-002",
                    "owl_skos",
                    "warning",
                    f"Add skos:definition for :{cname}",
                    "Definitions ground LLM prompts, mappings, and documentation.",
                    f":{cname} skos:definition \"{human} concept in this domain.\" .",
                    subject=cname,
                )
            if prefs and defs and not alts and not cname.endswith("Role"):
                add_issue("SKOS-003", "owl_skos", "suggestion", f"Class :{cname} has no skos:altLabel synonyms", subject=cname)
                add_rec(
                    f"rec-alt-{cname}",
                    "SKOS-003",
                    "owl_skos",
                    "suggestion",
                    f"Add skos:altLabel synonym for :{cname}",
                    "Synonyms improve cross-domain and schema matching.",
                    f":{cname} skos:altLabel \"{human} Record\" .",
                    subject=cname,
                )

        for p in dict.fromkeys(g.subjects(RDF.type, OWL.ObjectProperty)):
            pname = local(p)
            obj_props.append(pname)
            if not list(g.objects(p, RDFS.domain)):
                add_issue("OWL-004", "owl_skos", "warning", f"ObjectProperty :{pname} missing rdfs:domain", subject=pname)
                add_rec(
                    f"rec-dom-{pname}",
                    "OWL-004",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:domain for :{pname}",
                    "Object properties need rdfs:domain to bind relationships to a source class.",
                    f":{pname} rdfs:domain :{classes[0] if classes else 'Thing'} .",
                    subject=pname,
                )
            if not list(g.objects(p, RDFS.range)):
                add_issue("OWL-005", "owl_skos", "warning", f"ObjectProperty :{pname} missing rdfs:range", subject=pname)
                add_rec(
                    f"rec-rng-{pname}",
                    "OWL-005",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:range for :{pname}",
                    "Object properties need rdfs:range to bind relationships to a target class.",
                    f":{pname} rdfs:range :{classes[0] if classes else 'Thing'} .",
                    subject=pname,
                )

        for p in dict.fromkeys(g.subjects(RDF.type, OWL.DatatypeProperty)):
            pname = local(p)
            data_props.append(pname)
            if not list(g.objects(p, RDFS.domain)):
                add_issue("OWL-006", "owl_skos", "warning", f"DatatypeProperty :{pname} missing rdfs:domain", subject=pname)
                add_rec(
                    f"rec-ddom-{pname}",
                    "OWL-006",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:domain for :{pname}",
                    "Datatype properties should state which class carries the attribute.",
                    f":{pname} rdfs:domain :{classes[0] if classes else 'Thing'} .",
                    subject=pname,
                )
            if not list(g.objects(p, RDFS.range)):
                add_issue("OWL-007", "owl_skos", "warning", f"DatatypeProperty :{pname} missing rdfs:range", subject=pname)
                add_rec(
                    f"rec-drng-{pname}",
                    "OWL-007",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:range for :{pname}",
                    "Datatype properties should declare an XSD datatype (e.g. xsd:string).",
                    f":{pname} rdfs:range xsd:string .",
                    subject=pname,
                )

        combined_shapes = (shapes_content or "") + ("\n" + text if "NodeShape" in text else "")
        shape_count = len(re.findall(r"sh:NodeShape\b", combined_shapes))
        if shape_count == 0:
            target_cls = classes[0] if classes else "Entity"
            add_issue(
                "SHACL-001",
                "shacl",
                "warning",
                "No sh:NodeShape declarations found",
                hint="Add SHACL shapes to enforce required attributes and status lifecycles.",
            )
            add_rec(
                "rec-shacl-shape",
                "SHACL-001",
                "shacl",
                "warning",
                f"Add starter sh:NodeShape for :{target_cls}",
                "SHACL NodeShapes define cardinality and value constraints for your classes.",
                f"@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
                f"@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
                f":{target_cls}Shape a sh:NodeShape ;\n"
                f"    sh:targetClass :{target_cls} ;\n"
                f"    sh:property [\n"
                f"        sh:path :id ;\n"
                f"        sh:datatype xsd:string ;\n"
                f"        sh:minCount 1 ;\n"
                f"    ] .",
                subject=target_cls,
                action_type="add_shacl_shape",
            )

        if not roles:
            add_issue(
                "ROLE-001",
                "role_policy",
                "warning",
                "No BFO role class (rdfs:subClassOf bfo:0000023) found",
                hint="Role classes let generators derive access control and role policies.",
            )
            target_cls = classes[0] if classes else "Entity"
            add_rec(
                "rec-bfo-role",
                "ROLE-001",
                "role_policy",
                "warning",
                "Add a BFO role class",
                "Subclass bfo:0000023 with Bearer and Permissions in skos:definition.",
                f"@prefix bfo: <http://purl.obolibrary.org/obo/BFO_> .\n\n"
                f":OperatorRole a owl:Class ;\n"
                f"    rdfs:subClassOf bfo:0000023 ;\n"
                f"    skos:prefLabel \"Operator\" ;\n"
                f"    skos:definition \"Person role operating {target_cls}. Bearer: person. Permissions: {target_cls}:read, {target_cls}:write.\" .",
                subject="OperatorRole",
            )
    except Exception as parse_exc:
        add_issue(
            "SYN-002",
            "syntax",
            "error",
            f"RDF parse failed: {parse_exc}",
            hint="Fix syntax errors (unclosed tags/quotes/prefixes) and re-run validation.",
        )
        # Regex scan so broken RDF/TTL still gets actionable OWL/SKOS/SHACL diagnostics
        if "owl:Ontology" not in text and "<owl:Ontology" not in text:
            add_issue(
                "OWL-001",
                "owl_skos",
                "error",
                "Missing owl:Ontology header",
                hint="Declare an ontology IRI typed as owl:Ontology with rdfs:label.",
            )
            add_rec(
                "rec-owl-header",
                "OWL-001",
                "owl_skos",
                "error",
                "Add owl:Ontology header",
                "Every ontology should declare its ontology IRI and label.",
                '@prefix : <https://example.org/ontology#> .\n'
                '@prefix owl: <http://www.w3.org/2002/07/owl#> .\n'
                '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
                '@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n\n'
                '<https://example.org/ontology> a owl:Ontology ;\n'
                '    rdfs:label "Domain Ontology" ;\n'
                '    rdfs:comment "Ontology description." .',
            )
        regex_classes = re.findall(r":(\w+)\s+a\s+owl:Class\b", text)
        regex_classes += re.findall(
            r"(?:<owl:Class|<rdfs:Class)[^>]*?(?:rdf:about|rdf:ID)=[\"'](?:[^\"']*[#/])?(\w+)[\"']",
            text,
        )
        for cname in dict.fromkeys(regex_classes):
            classes.append(cname)
            human = re.sub(r"([a-z])([A-Z])", r"\1 \2", cname)
            if "skos:prefLabel" not in text:
                add_issue("SKOS-001", "owl_skos", "warning", f"Class :{cname} missing skos:prefLabel", subject=cname)
                add_rec(
                    f"rec-pref-{cname}",
                    "SKOS-001",
                    "owl_skos",
                    "warning",
                    f"Add skos:prefLabel for :{cname}",
                    "Preferred labels are required for catalog indexing and UI display.",
                    f":{cname} skos:prefLabel \"{human}\" .",
                    subject=cname,
                )
            if "skos:definition" not in text:
                add_issue("SKOS-002", "owl_skos", "warning", f"Class :{cname} missing skos:definition", subject=cname)
                add_rec(
                    f"rec-def-{cname}",
                    "SKOS-002",
                    "owl_skos",
                    "warning",
                    f"Add skos:definition for :{cname}",
                    "Definitions ground LLM prompts, mappings, and documentation.",
                    f":{cname} skos:definition \"{human} concept in this domain.\" .",
                    subject=cname,
                )
        for pname in dict.fromkeys(re.findall(r":(\w+)\s+a\s+owl:ObjectProperty\b", text)):
            obj_props.append(pname)
            if "rdfs:domain" not in text:
                add_issue("OWL-004", "owl_skos", "warning", f"ObjectProperty :{pname} missing rdfs:domain", subject=pname)
                add_rec(
                    f"rec-dom-{pname}",
                    "OWL-004",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:domain for :{pname}",
                    "Object properties need rdfs:domain.",
                    f":{pname} rdfs:domain :{classes[0] if classes else 'Thing'} .",
                    subject=pname,
                )
            if "rdfs:range" not in text:
                add_issue("OWL-005", "owl_skos", "warning", f"ObjectProperty :{pname} missing rdfs:range", subject=pname)
                add_rec(
                    f"rec-rng-{pname}",
                    "OWL-005",
                    "owl_skos",
                    "warning",
                    f"Add rdfs:range for :{pname}",
                    "Object properties need rdfs:range.",
                    f":{pname} rdfs:range :{classes[0] if classes else 'Thing'} .",
                    subject=pname,
                )
        if "NodeShape" not in text and not (shapes_content and "NodeShape" in shapes_content):
            target_cls = classes[0] if classes else "Entity"
            add_issue("SHACL-001", "shacl", "warning", "No sh:NodeShape declarations found")
            add_rec(
                "rec-shacl-shape",
                "SHACL-001",
                "shacl",
                "warning",
                f"Add starter sh:NodeShape for :{target_cls}",
                "SHACL NodeShapes define cardinality and value constraints.",
                f"@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
                f"@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
                f":{target_cls}Shape a sh:NodeShape ;\n"
                f"    sh:targetClass :{target_cls} .",
                subject=target_cls,
                action_type="add_shacl_shape",
            )

    errors = sum(1 for i in issues if i.get("severity") == "error")
    warnings = sum(1 for i in issues if i.get("severity") == "warning")
    suggestions = sum(1 for i in issues if i.get("severity") == "suggestion")
    info = sum(1 for i in issues if i.get("severity") == "info")
    shape_total = len(re.findall(r"sh:NodeShape\b", (shapes_content or "") + "\n" + text))
    return {
        "ok": errors == 0,
        "validationSource": "local-fallback",
        "validationServer": base,
        "remoteError": error,
        "serviceVersion": "local-fallback-1.0.0",
        "issues": issues,
        "recommendations": recommendations,
        "detectedFeatures": features,
        "validationSummary": {
            "tripleCount": triple_count,
            "classCount": len(classes),
            "objectPropertyCount": len(obj_props),
            "datatypePropertyCount": len(data_props),
            "shaclNodeShapeCount": shape_total,
            "bfoRoleCount": len(roles),
            "conforms": errors == 0,
            "rdfVersion": "1.2" if ("VERSION" in text or "<<" in text) else "1.1",
            "errors": errors,
            "warnings": warnings,
        },
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "info": info,
            "issueCount": len(issues),
            "recommendationCount": len(recommendations),
            "passed": errors == 0,
        },
    }


__all__ = [
    "normalize_validation_server",
    "validation_server",
    "get_ontology_validation_metadata",
    "validate_ontology",
    "apply_ontology_recommendations",
]
