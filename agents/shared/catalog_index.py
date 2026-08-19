#!/usr/bin/env python3.14
"""Catalog graph processing: extract → transform → load → validate → heal."""

from __future__ import annotations

import hashlib
import json
import pickle
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

from agents.shared.paths import CATALOG_ROOT, GRAPH_PATH, INDEX_DB, ensure_data_dir
from agents.shared.rdf_parse import parse_rdf_graph

NS_BASE = "https://ecosystemcode.com/ontology/"
STOPWORDS = {
    "a", "an", "the", "for", "of", "to", "and", "or", "my", "me", "in", "on",
    "with", "that", "this", "is", "are", "be", "ontology", "ontologies",
}
STUB_MARKERS = ("legacy:Entity", ":CoreEntity")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def tokenize(text: str) -> list[str]:
    parts = re.findall(r"[a-z0-9]+", text.lower())
    return [p for p in parts if p not in STOPWORDS and len(p) > 1]


def split_camel(name: str) -> list[str]:
    parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return tokenize(parts)


def is_stub_mapping(text: str) -> bool:
    return all(marker in text for marker in STUB_MARKERS)


def local_name(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def domain_from_iri(iri: str) -> tuple[str | None, str | None]:
    if not iri.startswith(NS_BASE):
        return None, None
    rest = iri[len(NS_BASE) :]
    if rest.startswith("industry/"):
        ind = rest.split("#", 1)[0].split("/", 1)[-1]
        return None, ind
    if rest.startswith("core"):
        return "core", None
    body = rest.split("#", 1)[0]
    parts = body.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0] or None, None


@dataclass
class IndexDoc:
    iri: str
    kind: str
    domain_id: str | None = None
    industry_id: str | None = None
    pref_label: str = ""
    alt_labels: list[str] = field(default_factory=list)
    definition: str = ""
    ontology_iri: str = ""
    local_name: str = ""
    source_path: str = ""
    core_alignment: dict[str, Any] = field(default_factory=dict)
    lifecycle_states: list[str] = field(default_factory=list)
    mappings: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        return {
            "iri": self.iri,
            "kind": self.kind,
            "domain_id": self.domain_id,
            "industry_id": self.industry_id,
            "pref_label": self.pref_label,
            "alt_labels": json.dumps(self.alt_labels),
            "definition": self.definition,
            "ontology_iri": self.ontology_iri,
            "local_name": self.local_name or local_name(self.iri),
            "source_path": self.source_path,
            "extra": json.dumps(
                {
                    "coreAlignment": self.core_alignment,
                    "lifecycleStates": self.lifecycle_states,
                    "mappings": self.mappings,
                    **self.extra,
                }
            ),
        }


class CatalogIndex:
    def __init__(self, catalog_root: Path | None = None, db_path: Path | None = None) -> None:
        self.root = Path(catalog_root or CATALOG_ROOT)
        self.db_path = Path(db_path or INDEX_DB)
        self.graph_path = GRAPH_PATH
        self.nx = nx.MultiDiGraph()
        self.quarantined: list[str] = []
        self.warnings: list[str] = []
        self._conn: sqlite3.Connection | None = None
        self._manifest: dict[str, Any] = {}
        self._industries: dict[str, Any] = {}
        self._false_friends: set[str] = set()

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            ensure_data_dir()
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        conn = self._conn
        assert conn is not None
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                mtime REAL NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS docs (
                iri TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                domain_id TEXT,
                industry_id TEXT,
                pref_label TEXT,
                alt_labels TEXT,
                definition TEXT,
                ontology_iri TEXT,
                local_name TEXT,
                source_path TEXT,
                extra TEXT
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
                iri, pref_label, alt_labels, definition, domain_id, local_name, industry_id
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """
        )
        conn.commit()

    def rebuild(self, incremental: bool = False) -> dict[str, Any]:
        self.warnings = []
        self.quarantined = []
        conn = self.connect()
        if not incremental:
            conn.execute("DELETE FROM docs")
            conn.execute("DELETE FROM docs_fts")
            conn.execute("DELETE FROM files")
            self.nx = nx.MultiDiGraph()
        self._load_manifests()
        sources = list(self._iter_sources())
        changed = []
        for path, kind in sources:
            rel = str(path.relative_to(self.root))
            digest = sha256_file(path)
            mtime = path.stat().st_mtime
            row = conn.execute("SELECT sha256, status FROM files WHERE path=?", (rel,)).fetchone()
            if incremental and row and row["sha256"] == digest and row["status"] == "ok":
                continue
            if incremental and row:
                conn.execute("DELETE FROM docs WHERE source_path=?", (rel,))
            try:
                self._ingest(path, kind)
                conn.execute(
                    "INSERT OR REPLACE INTO files(path, sha256, mtime, status) VALUES (?,?,?,?)",
                    (rel, digest, mtime, "ok"),
                )
                changed.append(rel)
            except Exception as exc:  # noqa: BLE001
                self.quarantined.append(rel)
                self.warnings.append(f"quarantine {rel}: {exc}")
                conn.execute(
                    "INSERT OR REPLACE INTO files(path, sha256, mtime, status) VALUES (?,?,?,?)",
                    (rel, digest, mtime, "quarantined"),
                )
        self._refresh_fts()
        self._apply_alignments()
        health = self.validate()
        self._save_graph()
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('health', ?)",
            (json.dumps(health),),
        )
        conn.commit()
        counts = self._counts()
        return {**counts, "changed": changed, "warnings": self.warnings, "quarantined": self.quarantined, **health}

    def heal_index(self, paths: list[str] | None = None) -> dict[str, Any]:
        conn = self.connect()
        if paths:
            for p in paths:
                conn.execute("DELETE FROM files WHERE path=?", (p,))
        else:
            conn.execute("DELETE FROM files WHERE status != 'ok'")
        conn.commit()
        result = self.rebuild(incremental=True)
        still = [p for p in self.quarantined]
        return {"ok": True, "rebuilt": True, "stillQuarantined": still, "warnings": self.warnings, **result}

    def health(self) -> dict[str, Any]:
        conn = self.connect()
        stale: list[str] = []
        for row in conn.execute("SELECT path, sha256 FROM files WHERE status='ok'"):
            path = self.root / row["path"]
            if not path.exists() or sha256_file(path) != row["sha256"]:
                stale.append(row["path"])
        quarantined = [r["path"] for r in conn.execute("SELECT path FROM files WHERE status='quarantined'")]
        base = self.validate()
        ok = base.get("ok", False) and not stale
        return {
            "ok": ok,
            "staleFiles": stale,
            "quarantined": quarantined,
            **base,
        }

    def validate(self) -> dict[str, Any]:
        conn = self.connect()
        self._load_manifests()
        domain_ids = [d["id"] for d in self._manifest.get("domains", [])]
        indexed_domains = {
            r["domain_id"]
            for r in conn.execute("SELECT DISTINCT domain_id FROM docs WHERE domain_id IS NOT NULL")
        }
        missing_domains = [d for d in domain_ids if d not in indexed_domains]
        collisions = self._homonyms()
        stub_count = conn.execute(
            "SELECT COUNT(*) AS c FROM docs WHERE kind='mapping' AND extra LIKE '%\"isStub\": true%'"
        ).fetchone()["c"]
        overlay_gaps = []
        for d in self._manifest.get("domains", []):
            for ind in d.get("industries") or []:
                overlay = self.root / "domains" / d["id"] / "industries" / ind / "overlay.ttl"
                if not overlay.exists():
                    overlay_gaps.append(f"{d['id']}/{ind}")
        ok = not missing_domains and stub_count == 0
        return {
            "ok": ok,
            "missingDomains": missing_domains,
            "collisions": collisions,
            "stubMappingsIndexed": stub_count,
            "overlayGaps": overlay_gaps,
            "warnings": self.warnings,
        }

    def search(
        self,
        query: str,
        industry: str | None = None,
        domain: str | None = None,
        include_ontology: bool = False,
        limit: int = 12,
    ) -> dict[str, Any]:
        self.connect()
        terms = tokenize(query)
        validated = self.validate_text(query, industry=industry, domain=domain)
        hits = self._fts_search(query, industry, domain, limit * 4)
        hits = _merge_rows(hits, self._exact_name_hits(terms, industry, domain))
        if not hits:
            hits = self._token_fallback(terms, industry, domain, limit * 4)
        scored = self._rank(hits, terms, industry, domain, query)
        if not scored:
            expanded = self._expand_from_terms(terms)
            scored = self._rank(expanded, terms, industry, domain, query)
        matches = scored[:limit]
        payload = {
            "ok": True,
            "query": query,
            "validatedTerms": validated["terms"],
            "matches": matches,
            "mappings": self._mappings_for(matches),
        }
        want_ontology = include_ontology or "ontology" in query.lower()
        if want_ontology and matches:
            payload["ontology"] = self.get_ontology(
                matches[0].get("domainId") or "",
                matches[0].get("industryId"),
            )
        return payload

    def validate_text(self, text: str, industry: str | None = None, domain: str | None = None) -> dict[str, Any]:
        conn = self.connect()
        terms_out = []
        for token in tokenize(text):
            rows = conn.execute(
                """
                SELECT iri, domain_id, pref_label, kind FROM docs
                WHERE lower(local_name)=? OR lower(pref_label)=?
                   OR lower(alt_labels) LIKE ?
                """,
                (token, token, f'%"{token}"%'),
            ).fetchall()
            extra = conn.execute(
                """
                SELECT iri, domain_id, pref_label, kind FROM docs
                WHERE lower(local_name) LIKE ? OR lower(pref_label) LIKE ?
                """,
                (f"%{token}%", f"%{token}%"),
            ).fetchall()
            seen = {r["iri"] for r in rows}
            for r in extra:
                if r["iri"] not in seen:
                    rows.append(r)
                    seen.add(r["iri"])
            if industry:
                rows = [r for r in rows if r["domain_id"] == industry or True]
            iris = []
            domains = set()
            for r in rows:
                if domain and r["domain_id"] not in (domain, "core", None):
                    if r["domain_id"] != domain:
                        continue
                iris.append(r["iri"])
                if r["domain_id"]:
                    domains.add(r["domain_id"])
            if not iris:
                status = "unknown"
            elif len(domains) > 1:
                status = "homonym"
            else:
                status = "matched"
            terms_out.append(
                {
                    "token": token,
                    "iri": iris[0] if len(iris) == 1 else None,
                    "iris": iris[:8],
                    "status": status,
                }
            )
        return {"ok": True, "terms": terms_out}

    def get_concept(self, iri: str) -> dict[str, Any]:
        doc = self._doc(iri)
        if not doc:
            return {"ok": False, "error": "not_found", "iri": iri}
        neighbors = self.expand_graph(iri, depth=1)
        return {"ok": True, **doc, "neighbors": neighbors}

    def get_ontology(self, domain_id: str, industry: str | None = None) -> dict[str, Any]:
        if industry:
            path = self.root / "domains" / domain_id / "industries" / industry / "overlay.ttl"
            ontology_iri = f"{NS_BASE}{domain_id}/{industry}"
        else:
            path = self.root / "domains" / domain_id / "ontology.ttl"
            ontology_iri = f"{NS_BASE}{domain_id}"
        turtle = path.read_text(encoding="utf-8") if path.exists() else ""
        conn = self.connect()
        classes = [
            dict(r)
            for r in conn.execute(
                """
                SELECT iri, pref_label, definition, domain_id, industry_id
                FROM docs WHERE kind IN ('class','overlay_class') AND domain_id=?
                  AND (? IS NULL OR industry_id=? OR industry_id IS NULL)
                LIMIT 80
                """,
                (domain_id, industry, industry),
            )
        ]
        return {
            "ok": True,
            "ontologyIri": ontology_iri,
            "domainId": domain_id,
            "industryId": industry,
            "turtle": turtle,
            "classes": [self._row_to_match(c) for c in classes],
        }

    def expand_graph(
        self,
        iri: str,
        depth: int = 1,
        rels: list[str] | None = None,
    ) -> dict[str, Any]:
        allowed = set(rels or ["subClassOf", "equivalentClass", "mapping", "alignment", "objectProperty"])
        if not self.nx.nodes:
            self._load_graph()
        nodes = {iri}
        edges: list[dict[str, str]] = []
        frontier = {iri}
        for _ in range(max(1, depth)):
            nxt = set()
            for node in frontier:
                if node not in self.nx:
                    continue
                for _, dest, data in self.nx.out_edges(node, data=True):
                    if not self._edge_allowed(data, allowed):
                        continue
                    nxt.add(dest)
                    edges.append({"from": node, "to": dest, "rel": str(data.get("rel") or "")})
                for src, _, data in self.nx.in_edges(node, data=True):
                    if not self._edge_allowed(data, allowed):
                        continue
                    nxt.add(src)
                    edges.append({"from": src, "to": node, "rel": str(data.get("rel") or "")})
            nodes |= nxt
            frontier = nxt
        node_docs = []
        for n in nodes:
            doc = self._doc(n)
            if doc:
                node_docs.append(doc)
            else:
                node_docs.append({"iri": n, "kind": "unknown"})
        return {"ok": True, "nodes": node_docs, "edges": edges}

    def _edge_allowed(self, data: dict[str, Any], allowed: set[str]) -> bool:
        rel = str(data.get("rel") or "")
        edge_kind = str(data.get("edgeKind") or "")
        if edge_kind == "objectProperty":
            return "objectProperty" in allowed
        if rel in {"domain", "range"}:
            return False
        return rel in allowed

    def list_domains(self) -> dict[str, Any]:
        self._load_manifests()
        return {"ok": True, "domains": self._manifest.get("domains", [])}

    def list_industries(self) -> dict[str, Any]:
        self._load_manifests()
        return {"ok": True, "industries": self._industries.get("industries", [])}

    def get_mappings_for_concept(self, iri: str) -> dict[str, Any]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT iri, pref_label, extra, source_path FROM docs WHERE kind='mapping'"
        ).fetchall()
        mappings = []
        for row in rows:
            extra = json.loads(row["extra"] or "{}")
            for m in extra.get("mappings") or []:
                if m.get("target_iri") == iri or m.get("source_iri") == iri or row["iri"] == iri:
                    if m.get("isStub"):
                        continue
                    mappings.append({**m, "source_path": row["source_path"]})
            if iri in (row["iri"],) or iri in json.dumps(extra):
                for m in extra.get("mappings") or []:
                    if not m.get("isStub"):
                        mappings.append({**m, "source_path": row["source_path"]})
        # also from extra on the class doc
        doc = self._doc(iri)
        if doc:
            for m in (doc.get("coreAlignment") and []) or []:
                pass
            extra = doc.get("mappings") or []
            mappings.extend(extra)
        uniq = []
        seen = set()
        for m in mappings:
            key = (m.get("source_iri"), m.get("target_iri"), m.get("predicate"))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(m)
        return {"ok": True, "iri": iri, "mappings": uniq}

    def get_alignments(self, iri: str) -> dict[str, Any]:
        doc = self._doc(iri)
        alignment = (doc or {}).get("coreAlignment") or {"relation": "none"}
        local = local_name(iri).lower()
        false_friend = local in self._false_friends or (
            local == "account" and (doc or {}).get("domainId") in {"crm", "fin"}
        )
        return {
            "ok": True,
            "iri": iri,
            "alignment": alignment if alignment else {"relation": "none"},
            "falseFriend": bool(false_friend),
        }

    def validate_iris(self, iris: list[str]) -> dict[str, Any]:
        conn = self.connect()
        valid = []
        invalid = []
        for iri in iris:
            row = conn.execute("SELECT iri, kind FROM docs WHERE iri=?", (iri,)).fetchone()
            if row:
                valid.append({"iri": row["iri"], "kind": row["kind"]})
            else:
                invalid.append(iri)
        return {"ok": True, "valid": valid, "invalid": invalid}

    def diagnose_failure(self, error: str, last_tool: str, last_args: dict[str, Any]) -> dict[str, Any]:
        err = (error or "").lower()
        if "stale" in err or "missing" in err or last_tool in {"search_catalog", "rebuild_index"}:
            return {
                "ok": True,
                "cause": "index_gap",
                "suggestedTool": "heal_index",
                "suggestedArgs": {},
            }
        if "not_found" in err or "unknown" in err:
            return {
                "ok": True,
                "cause": "empty_search",
                "suggestedTool": "expand_graph",
                "suggestedArgs": last_args if "iri" in last_args else {"iri": last_args.get("iri", "")},
            }
        if "iri" in err or "invalid" in err:
            return {
                "ok": True,
                "cause": "invalid_iri",
                "suggestedTool": "validate_iris",
                "suggestedArgs": {"iris": last_args.get("iris") or []},
            }
        return {
            "ok": True,
            "cause": "unknown",
            "suggestedTool": "index_health",
            "suggestedArgs": {},
        }

    # --- internals ---

    def _load_manifests(self) -> None:
        self._manifest = json.loads((self.root / "index.json").read_text(encoding="utf-8"))
        self._industries = json.loads((self.root / "industries.json").read_text(encoding="utf-8"))
        alignments = (self.root / "core" / "alignments.ttl").read_text(encoding="utf-8")
        self._false_friends = set()
        if "false-friend" in alignments.lower() or "false friend" in alignments.lower():
            self._false_friends.add("account")

    def _iter_sources(self) -> Iterable[tuple[Path, str]]:
        yield self.root / "index.json", "manifest"
        yield self.root / "industries.json", "industries"
        core_ont = self.root / "core" / "ontology.ttl"
        if core_ont.exists():
            yield core_ont, "core"
        alignments = self.root / "core" / "alignments.ttl"
        if alignments.exists():
            yield alignments, "alignments"
        for industry in (self.root / "industries").iterdir() if (self.root / "industries").exists() else []:
            if not industry.is_dir():
                continue
            common = industry / "common.ttl"
            md = industry / "industry.md"
            if common.exists():
                yield common, "industry"
            if md.exists():
                yield md, "industry_md"
        domains_dir = self.root / "domains"
        for domain in sorted(p for p in domains_dir.iterdir() if p.is_dir()):
            for name, kind in (
                ("ontology.ttl", "ontology"),
                ("description.md", "description"),
                ("shapes.ttl", "shapes"),
            ):
                path = domain / name
                if path.exists():
                    yield path, kind
            mappings = domain / "mappings"
            if mappings.exists():
                for ttl in mappings.glob("*.ttl"):
                    text = ttl.read_text(encoding="utf-8", errors="replace")
                    if is_stub_mapping(text):
                        continue
                    yield ttl, "mapping"
            industries = domain / "industries"
            if industries.exists():
                for ind in industries.iterdir():
                    if not ind.is_dir():
                        continue
                    overlay = ind / "overlay.ttl"
                    overlay_md = ind / "overlay.md"
                    if overlay.exists():
                        yield overlay, "overlay"
                    if overlay_md.exists():
                        yield overlay_md, "overlay_md"
                    ind_map = ind / "mappings"
                    if ind_map.exists():
                        for ttl in ind_map.glob("*.ttl"):
                            text = ttl.read_text(encoding="utf-8", errors="replace")
                            if is_stub_mapping(text):
                                continue
                            yield ttl, "mapping"

    def _ingest(self, path: Path, kind: str) -> None:
        rel = str(path.relative_to(self.root))
        if kind in {"ontology", "overlay", "core", "industry", "mapping", "alignments", "shapes"}:
            self._ingest_ttl(path, kind, rel)
        elif kind in {"description", "overlay_md", "industry_md"}:
            self._ingest_markdown(path, kind, rel)
        elif kind == "manifest":
            pass

    def _ingest_ttl(self, path: Path, kind: str, rel: str) -> None:
        g = parse_rdf_graph(path=path)
        ontology_iri = ""
        for s in g.subjects(RDF.type, OWL.Ontology):
            ontology_iri = str(s)
            break
        domain_id, industry_id = domain_from_iri(ontology_iri or str(path))
        if kind == "overlay":
            parts = Path(rel).parts
            if "domains" in parts and "industries" in parts:
                domain_id = parts[parts.index("domains") + 1]
                industry_id = parts[parts.index("industries") + 1]
        if kind in {"ontology", "shapes", "mapping"} and domain_id is None:
            parts = Path(rel).parts
            if "domains" in parts:
                domain_id = parts[parts.index("domains") + 1]

        states_by_class: dict[str, list[str]] = {}
        shapes_by_class: dict[str, list[dict[str, Any]]] = {}
        if kind == "shapes":
            shapes_by_class = self._extract_shacl(g)
            self._apply_shapes_to_docs(shapes_by_class)
            return

        if kind == "mapping":
            self._ingest_mapping(g, rel, domain_id, industry_id, ontology_iri)
            return
        if kind == "alignments":
            self._ingest_alignment_graph(g)
            return

        class_kind = "overlay_class" if kind == "overlay" else "class"
        if kind == "industry":
            class_kind = "industry_class"

        for subj in g.subjects(RDF.type, OWL.Class):
            iri = str(subj)
            if iri.startswith("http://www.w3.org/") or iri.startswith("http://purl.org/"):
                continue
            pref = _lit(g, subj, SKOS.prefLabel) or _lit(g, subj, RDFS.label) or local_name(iri)
            alts = _lits(g, subj, SKOS.altLabel)
            definition = _lit(g, subj, SKOS.definition) or _lit(g, subj, RDFS.comment)
            d_id, i_id = domain_from_iri(iri)
            doc = IndexDoc(
                iri=iri,
                kind="role" if iri.endswith("Role") or local_name(iri).endswith("Role") else class_kind,
                domain_id=d_id or domain_id,
                industry_id=i_id or industry_id,
                pref_label=pref,
                alt_labels=alts,
                definition=definition,
                ontology_iri=ontology_iri,
                local_name=local_name(iri),
                source_path=rel,
                lifecycle_states=states_by_class.get(iri, []),
            )
            self._upsert_doc(doc)
            self.nx.add_node(iri, kind=doc.kind, domain=doc.domain_id)
            for parent in g.objects(subj, RDFS.subClassOf):
                if isinstance(parent, URIRef):
                    self.nx.add_edge(iri, str(parent), rel="subClassOf")

        for ptype, pkind in ((OWL.ObjectProperty, "object_property"), (OWL.DatatypeProperty, "datatype_property")):
            for subj in g.subjects(RDF.type, ptype):
                iri = str(subj)
                pref = _lit(g, subj, SKOS.prefLabel) or _lit(g, subj, RDFS.label) or local_name(iri)
                d_id, i_id = domain_from_iri(iri)
                domains = [str(x) for x in g.objects(subj, RDFS.domain)]
                ranges = [str(x) for x in g.objects(subj, RDFS.range)]
                prop_local = local_name(iri)
                doc = IndexDoc(
                    iri=iri,
                    kind=pkind,
                    domain_id=d_id or domain_id,
                    industry_id=i_id or industry_id,
                    pref_label=pref,
                    alt_labels=_lits(g, subj, SKOS.altLabel),
                    definition=_lit(g, subj, SKOS.definition) or _lit(g, subj, RDFS.comment),
                    ontology_iri=ontology_iri,
                    local_name=prop_local,
                    source_path=rel,
                    extra={"domain": domains, "range": ranges},
                )
                self._upsert_doc(doc)
                for d in domains:
                    self.nx.add_edge(iri, d, rel="domain")
                for r in ranges:
                    self.nx.add_edge(iri, r, rel="range")
                if pkind == "object_property":
                    for d in domains:
                        for r in ranges:
                            if r.startswith("http://www.w3.org/2001/XMLSchema"):
                                continue
                            self.nx.add_edge(d, r, rel=prop_local, edgeKind="objectProperty")

        for s, o in g.subject_objects(OWL.equivalentClass):
            self.nx.add_edge(str(s), str(o), rel="equivalentClass")

    def _extract_shacl(self, g: Graph) -> dict[str, list[dict[str, Any]]]:
        from rdflib.namespace import Namespace

        SH = Namespace("http://www.w3.org/ns/shacl#")
        out: dict[str, list[dict[str, Any]]] = {}
        for shape in g.subjects(RDF.type, SH.NodeShape):
            targets = [str(t) for t in g.objects(shape, SH.targetClass)]
            for prop in g.objects(shape, SH.property):
                constraint: dict[str, Any] = {}
                paths = [str(p) for p in g.objects(prop, SH.path)]
                if paths:
                    constraint["path"] = local_name(paths[0])
                    constraint["pathIri"] = paths[0]
                for mc in g.objects(prop, SH.minCount):
                    try:
                        constraint["minCount"] = int(mc)
                    except (TypeError, ValueError):
                        pass
                classes = [str(c) for c in g.objects(prop, SH["class"])]
                if classes:
                    constraint["class"] = classes[0]
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

    def _apply_shapes_to_docs(self, shapes_by_class: dict[str, list[dict[str, Any]]]) -> None:
        conn = self.connect()
        for class_iri, shapes in shapes_by_class.items():
            row = conn.execute("SELECT extra FROM docs WHERE iri=?", (class_iri,)).fetchone()
            if not row:
                continue
            extra = json.loads(row["extra"] or "{}")
            extra["shapes"] = shapes
            enums: list[str] = []
            for s in shapes:
                for v in s.get("in") or []:
                    if v not in enums:
                        enums.append(v)
            if enums:
                extra["lifecycleStates"] = enums
            conn.execute("UPDATE docs SET extra=? WHERE iri=?", (json.dumps(extra), class_iri))
        conn.commit()

    def _extract_shacl_states(self, g: Graph) -> dict[str, list[str]]:
        """Backward-compatible lifecycle-only extract."""
        shapes = self._extract_shacl(g)
        out: dict[str, list[str]] = {}
        for iri, constraints in shapes.items():
            values: list[str] = []
            for c in constraints:
                for v in c.get("in") or []:
                    if v not in values:
                        values.append(v)
            if values:
                out[iri] = values
        return out

    def _ingest_mapping(self, g: Graph, rel: str, domain_id: str | None, industry_id: str | None, ontology_iri: str) -> None:
        mappings: list[dict[str, Any]] = []
        for s, o in g.subject_objects(OWL.equivalentClass):
            mappings.append(
                {
                    "source_iri": str(s),
                    "target_iri": str(o),
                    "predicate": "owl:equivalentClass",
                    "isStub": False,
                }
            )
            self.nx.add_edge(str(s), str(o), rel="mapping")
        for s, o in g.subject_objects(RDFS.subPropertyOf):
            mappings.append(
                {
                    "source_iri": str(s),
                    "target_iri": str(o),
                    "predicate": "rdfs:subPropertyOf",
                    "isStub": False,
                }
            )
            self.nx.add_edge(str(s), str(o), rel="mapping")
        if not mappings:
            return
        iri = f"{NS_BASE}mapping/{rel.replace('/', ':')}"
        doc = IndexDoc(
            iri=iri,
            kind="mapping",
            domain_id=domain_id,
            industry_id=industry_id,
            pref_label=Path(rel).name,
            definition=f"Source mapping {rel}",
            ontology_iri=ontology_iri,
            local_name=Path(rel).stem,
            source_path=rel,
            mappings=mappings,
        )
        self._upsert_doc(doc)
        conn = self.connect()
        for m in mappings:
            target = m["target_iri"]
            row = conn.execute("SELECT extra FROM docs WHERE iri=?", (target,)).fetchone()
            if not row:
                continue
            extra = json.loads(row["extra"] or "{}")
            extra.setdefault("mappings", []).append(m)
            conn.execute("UPDATE docs SET extra=? WHERE iri=?", (json.dumps(extra), target))

    def _ingest_alignment_graph(self, g: Graph) -> None:
        conn = self.connect()
        for s, o in g.subject_objects(OWL.equivalentClass):
            self._set_alignment(conn, str(s), str(o), "equivalentClass")
            self.nx.add_edge(str(s), str(o), rel="alignment")
        for s, o in g.subject_objects(RDFS.subClassOf):
            if str(s).startswith(NS_BASE) and "core#" in str(o):
                self._set_alignment(conn, str(s), str(o), "subClassOf")
                self.nx.add_edge(str(s), str(o), rel="alignment")

    def _set_alignment(self, conn: sqlite3.Connection, src: str, core: str, rel: str) -> None:
        row = conn.execute("SELECT extra FROM docs WHERE iri=?", (src,)).fetchone()
        extra = json.loads(row["extra"]) if row else {}
        extra["coreAlignment"] = {"iri": core, "relation": rel}
        if row:
            conn.execute("UPDATE docs SET extra=? WHERE iri=?", (json.dumps(extra), src))

    def _apply_alignments(self) -> None:
        path = self.root / "core" / "alignments.ttl"
        if path.exists():
            try:
                g = parse_rdf_graph(path=path)
                self._ingest_alignment_graph(g)
            except Exception as exc:  # noqa: BLE001
                self.warnings.append(f"alignments: {exc}")

    def _ingest_markdown(self, path: Path, kind: str, rel: str) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        parts = Path(rel).parts
        domain_id = parts[parts.index("domains") + 1] if "domains" in parts else None
        industry_id = parts[parts.index("industries") + 1] if "industries" in parts else None
        iri = f"{NS_BASE}text/{rel.replace('/', ':')}"
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else path.stem
        doc = IndexDoc(
            iri=iri,
            kind="description",
            domain_id=domain_id,
            industry_id=industry_id,
            pref_label=title,
            definition=text[:2000],
            local_name=path.stem,
            source_path=rel,
        )
        self._upsert_doc(doc)

    def _upsert_doc(self, doc: IndexDoc) -> None:
        conn = self.connect()
        row = doc.to_row()
        conn.execute(
            """
            INSERT OR REPLACE INTO docs(
                iri, kind, domain_id, industry_id, pref_label, alt_labels,
                definition, ontology_iri, local_name, source_path, extra
            ) VALUES (:iri,:kind,:domain_id,:industry_id,:pref_label,:alt_labels,
                      :definition,:ontology_iri,:local_name,:source_path,:extra)
            """,
            row,
        )

    def _refresh_fts(self) -> None:
        conn = self.connect()
        conn.execute("DELETE FROM docs_fts")
        conn.execute(
            """
            INSERT INTO docs_fts(iri, pref_label, alt_labels, definition, domain_id, local_name, industry_id)
            SELECT iri, pref_label, alt_labels, definition, domain_id, local_name, industry_id FROM docs
            """
        )

    def _counts(self) -> dict[str, Any]:
        conn = self.connect()
        docs = conn.execute("SELECT COUNT(*) AS c FROM docs").fetchone()["c"]
        domains = conn.execute(
            "SELECT COUNT(DISTINCT domain_id) AS c FROM docs WHERE domain_id IS NOT NULL AND domain_id != 'core'"
        ).fetchone()["c"]
        overlays = conn.execute("SELECT COUNT(*) AS c FROM docs WHERE kind='overlay_class'").fetchone()["c"]
        mappings = conn.execute("SELECT COUNT(*) AS c FROM docs WHERE kind='mapping'").fetchone()["c"]
        return {"ok": True, "docs": docs, "domains": domains, "overlays": overlays, "mappings": mappings}

    def _homonyms(self) -> dict[str, list[str]]:
        conn = self.connect()
        collisions: dict[str, list[str]] = {}
        rows = conn.execute(
            """
            SELECT lower(local_name) AS n, domain_id FROM docs
            WHERE kind IN ('class','overlay_class') AND local_name IS NOT NULL
            """
        ).fetchall()
        buckets: dict[str, set[str]] = {}
        for r in rows:
            if r["n"] and r["domain_id"]:
                buckets.setdefault(r["n"], set()).add(r["domain_id"])
        for name, domains in buckets.items():
            if len(domains) > 1:
                collisions[name] = sorted(domains)
        return {k: v for k, v in list(collisions.items())[:40]}

    def _fts_search(
        self, query: str, industry: str | None, domain: str | None, limit: int
    ) -> list[sqlite3.Row]:
        conn = self.connect()
        tokens = tokenize(query)
        if not tokens:
            return []
        match = " OR ".join(t.replace('"', "") for t in tokens)
        sql = "SELECT docs.* FROM docs_fts JOIN docs ON docs.iri = docs_fts.iri WHERE docs_fts MATCH ?"
        params: list[Any] = [match]
        if domain:
            sql += " AND (docs.domain_id=? OR docs.kind='mapping')"
            params.append(domain)
        if industry:
            sql += " AND (docs.industry_id=? OR docs.industry_id IS NULL)"
            params.append(industry)
        sql += " LIMIT ?"
        params.append(limit)
        try:
            return list(conn.execute(sql, params).fetchall())
        except sqlite3.OperationalError:
            return []

    def _token_fallback(
        self, tokens: list[str], industry: str | None, domain: str | None, limit: int
    ) -> list[sqlite3.Row]:
        conn = self.connect()
        hits: dict[str, sqlite3.Row] = {}
        for token in tokens:
            rows = conn.execute(
                """
                SELECT * FROM docs
                WHERE lower(local_name) LIKE ? OR lower(pref_label) LIKE ?
                   OR lower(alt_labels) LIKE ? OR lower(definition) LIKE ?
                LIMIT 50
                """,
                (f"%{token}%", f"%{token}%", f"%{token}%", f"%{token}%"),
            ).fetchall()
            for r in rows:
                if domain and r["domain_id"] not in (domain, "core", None) and r["kind"] != "mapping":
                    continue
                if industry and r["industry_id"] not in (industry, None):
                    # keep domain-level classes when industry filter is set
                    if r["industry_id"] not in (industry, None):
                        continue
                hits[r["iri"]] = r
        return list(hits.values())[:limit]

    def _expand_from_terms(self, tokens: list[str]) -> list[sqlite3.Row]:
        return self._token_fallback(tokens, None, None, 40)

    def _exact_name_hits(self, tokens: list[str], industry: str | None, domain: str | None) -> list[sqlite3.Row]:
        conn = self.connect()
        hits: list[sqlite3.Row] = []
        for token in tokens:
            rows = conn.execute(
                """
                SELECT * FROM docs
                WHERE kind IN ('class','overlay_class')
                  AND (lower(local_name)=? OR lower(pref_label)=?)
                """,
                (token, token),
            ).fetchall()
            for r in rows:
                if domain and r["domain_id"] not in (domain, "core", None):
                    continue
                hits.append(r)
        return hits

    def _rank(
        self,
        rows: list[sqlite3.Row],
        tokens: list[str],
        industry: str | None,
        domain: str | None,
        query: str,
    ) -> list[dict[str, Any]]:
        q = query.lower()
        scored: list[tuple[float, dict[str, Any]]] = []
        industries = {i["id"]: i["label"].lower() for i in self._industries.get("industries", [])} if self._industries else {}
        if not industries:
            try:
                self._load_manifests()
                industries = {i["id"]: i["label"].lower() for i in self._industries.get("industries", [])}
            except Exception:
                industries = {}
        for row in rows:
            if row["kind"] in {"description", "mapping"} and row["kind"] == "description":
                continue
            doc = self._row_to_match(row)
            score = 0.0
            reason = []
            name = (doc.get("localName") or "").lower()
            pref = (doc.get("prefLabel") or "").lower()
            alts = [a.lower() for a in doc.get("altLabels") or []]
            blob = " ".join([name, pref, *alts, (doc.get("definition") or "").lower()])
            for t in tokens:
                if t == name or t == pref.replace(" ", ""):
                    score += 25
                    reason.append(f"exact:{t}")
                elif pref == t or name.replace(" ", "") == t:
                    score += 25
                    reason.append(f"exact-label:{t}")
                elif t in pref.split() or t in name:
                    score += 5
                    reason.append(f"label:{t}")
                elif any(t in a for a in alts):
                    score += 7
                    reason.append(f"alt:{t}")
                elif t in blob:
                    score += 1.5
            if domain and doc.get("domainId") == domain:
                score += 6
                reason.append("domain-filter")
            if industry and doc.get("industryId") == industry:
                score += 8
                reason.append("industry-filter")
            for ind_id, label in industries.items():
                if ind_id in tokens or any(p in q for p in label.split()):
                    if doc.get("industryId") == ind_id:
                        score += 6
                        reason.append(f"industry:{ind_id}")
                    if doc.get("domainId") == ind_id:
                        score += 2
            if "card" in tokens and doc.get("domainId") == "card":
                score += 6
                reason.append("domain:card")
            if "credit card" in q and ("credit card" in " ".join(alts) or "credit card" in pref or "retailcreditcard" in name):
                score += 20
                reason.append("phrase:credit-card")
            if any(t in {"phone", "phones", "mobile"} for t in tokens):
                if doc.get("domainId") in {"pim", "ecom", "cvm", "crm", "sub"}:
                    score += 3
                if "product" in name or "product" in pref:
                    score += 4
                if doc.get("industryId") == "telco" or "telco" in tokens:
                    score += 3
            if any(t in {"customer", "customers", "client"} for t in tokens):
                if "customer" in name or "customer" in pref:
                    score += 5
            if doc.get("kind") in {"class", "overlay_class"}:
                score += 6
            if doc.get("kind") in {"object_property", "datatype_property"}:
                score -= 4
            if doc.get("kind") == "role":
                score -= 2
            doc["score"] = round(score, 3)
            doc["reason"] = reason
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: (-x[0], x[1].get("iri", "")))
        # Personalized PageRank boost from top seeds
        if self.nx.nodes and scored:
            seeds = [d["iri"] for _, d in scored[:5] if d.get("iri") in self.nx]
            if seeds:
                personal = {n: (1 / len(seeds) if n in seeds else 0.0) for n in self.nx.nodes}
                try:
                    ppr = nx.pagerank(self.nx, personalization=personal, max_iter=50)
                    boosted = []
                    for score, doc in scored:
                        boost = ppr.get(doc.get("iri"), 0) * 3
                        doc["score"] = round(score + boost, 3)
                        boosted.append((doc["score"], doc))
                    boosted.sort(key=lambda x: -x[0])
                    scored = boosted
                except Exception:
                    pass
        return [d for _, d in scored]

    def _row_to_match(self, row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        if isinstance(row, sqlite3.Row):
            data = dict(row)
        else:
            data = row
        extra = json.loads(data.get("extra") or "{}") if isinstance(data.get("extra"), str) else (data.get("extra") or {})
        alts = data.get("alt_labels") or data.get("altLabels") or "[]"
        if isinstance(alts, str):
            try:
                alts = json.loads(alts)
            except json.JSONDecodeError:
                alts = [alts]
        return {
            "iri": data.get("iri"),
            "kind": data.get("kind"),
            "domainId": data.get("domain_id") or data.get("domainId"),
            "industryId": data.get("industry_id") or data.get("industryId"),
            "prefLabel": data.get("pref_label") or data.get("prefLabel") or "",
            "altLabels": alts or [],
            "definition": data.get("definition") or "",
            "ontologyIri": data.get("ontology_iri") or data.get("ontologyIri") or "",
            "localName": data.get("local_name") or data.get("localName") or local_name(data.get("iri") or ""),
            "coreAlignment": extra.get("coreAlignment") or {"relation": "none"},
            "lifecycleStates": extra.get("lifecycleStates") or [],
            "shapes": extra.get("shapes") or [],
            "mappings": extra.get("mappings") or [],
            "sourcePath": data.get("source_path") or data.get("sourcePath"),
        }

    def _doc(self, iri: str) -> dict[str, Any] | None:
        conn = self.connect()
        row = conn.execute("SELECT * FROM docs WHERE iri=?", (iri,)).fetchone()
        if not row:
            return None
        return self._row_to_match(row)

    def _mappings_for(self, matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for m in matches:
            out.extend(m.get("mappings") or [])
            got = self.get_mappings_for_concept(m.get("iri") or "")
            out.extend(got.get("mappings") or [])
        uniq = []
        seen = set()
        for m in out:
            key = (m.get("source_iri"), m.get("target_iri"))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(m)
        return uniq[:30]

    def _save_graph(self) -> None:
        ensure_data_dir()
        with self.graph_path.open("wb") as fh:
            pickle.dump(self.nx, fh)

    def _load_graph(self) -> None:
        if self.graph_path.exists():
            with self.graph_path.open("rb") as fh:
                self.nx = pickle.load(fh)


def _merge_rows(*groups: list) -> list:
    seen: dict[str, Any] = {}
    for group in groups:
        for row in group:
            seen[row["iri"]] = row
    return list(seen.values())


def _lit(g: Graph, subj, pred) -> str:
    for val in g.objects(subj, pred):
        return str(val)
    return ""


def _lits(g: Graph, subj, pred) -> list[str]:
    return [str(v) for v in g.objects(subj, pred)]


_SKIP_IRI = ("http://www.w3.org/", "http://purl.org/")
_PREVIEW_BYTES = 2_000_000
_PREVIEW_NODE_CAP = 1000


def _preview_class_terms(g: Graph) -> list[URIRef]:
    """owl:Class, rdfs:Class, and both ends of rdfs:subClassOf (IES and similar RDFS ontologies)."""
    found: list[URIRef] = []
    seen: set[str] = set()

    def add(term: object) -> None:
        if not isinstance(term, URIRef):
            return
        iri = str(term)
        if iri.startswith(_SKIP_IRI) or iri in seen:
            return
        seen.add(iri)
        found.append(term)

    for class_type in (OWL.Class, RDFS.Class):
        for subj in g.subjects(RDF.type, class_type):
            add(subj)
    for subj, obj in g.subject_objects(RDFS.subClassOf):
        add(subj)
        add(obj)
    return found


def preview_ontology_text(turtle: str = "") -> dict[str, Any]:
    """Parse Turtle or RDF/XML in memory. Never writes to the catalog index or disk."""
    text = (turtle or "").strip()
    if not text:
        return {"ok": False, "error": "empty"}
    if len(text.encode("utf-8")) > _PREVIEW_BYTES:
        return {"ok": False, "error": "too_large", "detail": "Maximum size is 2 MB."}
    try:
        g = parse_rdf_graph(data=text)
    except Exception as exc:  # noqa: BLE001 — parse errors are returned to the caller
        return {"ok": False, "error": "parse_failed", "detail": str(exc)[:400]}

    ontology_iri = ""
    for s in g.subjects(RDF.type, OWL.Ontology):
        ontology_iri = str(s)
        break

    terms = _preview_class_terms(g)
    nodes: list[dict[str, Any]] = []
    for subj in terms[:_PREVIEW_NODE_CAP]:
        iri = str(subj)
        nodes.append(
            {
                "iri": iri,
                "kind": "class",
                "prefLabel": _lit(g, subj, SKOS.prefLabel) or _lit(g, subj, RDFS.label) or local_name(iri),
                "altLabels": _lits(g, subj, SKOS.altLabel),
                "definition": _lit(g, subj, SKOS.definition) or _lit(g, subj, RDFS.comment),
                "localName": local_name(iri),
                "ontologyIri": ontology_iri,
            }
        )

    keep = {n["iri"] for n in nodes}
    edges: list[dict[str, str]] = []

    def _add_edge(frm: str, to: str, rel: str) -> None:
        if frm in keep and to in keep:
            edges.append({"from": frm, "to": to, "rel": rel})

    for iri in keep:
        subj = URIRef(iri)
        for parent in g.objects(subj, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                _add_edge(iri, str(parent), "subClassOf")
        for eq in g.objects(subj, OWL.equivalentClass):
            if isinstance(eq, URIRef):
                _add_edge(iri, str(eq), "equivalentClass")

    for subj in g.subjects(RDF.type, OWL.ObjectProperty):
        if not isinstance(subj, URIRef):
            continue
        rel = local_name(str(subj)) or "link"
        domains = [str(x) for x in g.objects(subj, RDFS.domain) if isinstance(x, URIRef)]
        ranges = [str(x) for x in g.objects(subj, RDFS.range) if isinstance(x, URIRef)]
        for d in domains:
            for r in ranges:
                _add_edge(d, r, rel)

    return {
        "ok": True,
        "ontologyIri": ontology_iri,
        "nodes": nodes,
        "edges": edges,
        "classes": nodes,
        "classCount": len(nodes),
        "truncated": len(terms) > _PREVIEW_NODE_CAP,
        "stored": False,
    }


_INDEX: CatalogIndex | None = None


def get_index() -> CatalogIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = CatalogIndex()
        db = INDEX_DB
        if not db.exists() or db.stat().st_size < 1000:
            _INDEX.rebuild(incremental=False)
        else:
            _INDEX.connect()
            _INDEX._load_graph()
            _INDEX._load_manifests()
    return _INDEX
