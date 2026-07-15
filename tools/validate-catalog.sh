#!/usr/bin/env bash
# validate-catalog.sh — structural validator for ecosystem-domain-catalog.
# Enforces the contract in AGENTS.md. Exit 0 = catalog valid.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

fail() { echo "FAIL: $1"; ERRORS=$((ERRORS + 1)); }
note() { echo "  ok: $1"; }

command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 2; }

# ---------- manifest parsing ----------
DOMAIN_IDS=$(python3 -c "
import json,sys
try:
    m=json.load(open('$ROOT/index.json'))
    for d in m['domains']: print(d['id'])
except Exception as e:
    print('MANIFEST_ERROR:'+str(e),file=sys.stderr); sys.exit(1)
") || { fail "index.json does not parse"; echo "Validation FAILED (1 error)"; exit 1; }

INDUSTRY_IDS=$(python3 -c "
import json,sys
try:
    m=json.load(open('$ROOT/industries.json'))
    for i in m['industries']: print(i['id'])
except Exception as e:
    print('MANIFEST_ERROR:'+str(e),file=sys.stderr); sys.exit(1)
") || { fail "industries.json does not parse"; echo "Validation FAILED (1 error)"; exit 1; }

# ---------- manifest field completeness ----------
python3 - "$ROOT" <<'PYEOF'
import json, sys, re
root = sys.argv[1]
required = ["id","acronym","name","description","icon","chips","entities",
            "capability","benefit","workflow","statefulEntity","industries",
            "hasDescription","hasOntology","hasShapes","version"]
semver = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
m = json.load(open(f"{root}/index.json"))
bad = 0
for d in m["domains"]:
    did = d.get("id", "?")
    for f in required:
        if f not in d or d[f] in ("", None) or (isinstance(d[f], list) and f in ("chips","entities") and len(d[f]) == 0):
            print(f"FAIL: index.json domain '{did}' missing/empty field '{f}'")
            bad += 1
    ver = d.get("version", "")
    if ver and not semver.match(str(ver)):
        print(f"FAIL: index.json domain '{did}' version '{ver}' must match MAJOR.MINOR.PATCH")
        bad += 1
    inds = d.get("industries")
    if not isinstance(inds, list) or len(inds) < 1:
        print(f"FAIL: index.json domain '{did}' must list at least one industry")
        bad += 1
    ents = d.get("entities") or []
    if len(ents) != len(set(ents)):
        print(f"FAIL: index.json domain '{did}' has duplicate entities")
        bad += 1
sys.exit(1 if bad else 0)
PYEOF
[ $? -ne 0 ] && ERRORS=$((ERRORS + 1))

# ---------- placeholder rejection (authored content only) ----------
PLACEHOLDERS=$(grep -rlE 'TODO|TBD\b|PLACEHOLDER|FIXME' "$ROOT/domains" "$ROOT/industries" 2>/dev/null || true)
if [ -n "$PLACEHOLDERS" ]; then
    fail "placeholder markers found in: $PLACEHOLDERS"
fi

# ---------- per-domain checks ----------
for id in $DOMAIN_IDS; do
    DIR="$ROOT/domains/$id"
    if [ ! -d "$DIR" ]; then fail "domain '$id' in manifest but domains/$id/ missing"; continue; fi

    DESC="$DIR/description.md"; ONT="$DIR/ontology.ttl"; SHP="$DIR/shapes.ttl"
    for f in "$DESC" "$ONT" "$SHP"; do
        [ -s "$f" ] || fail "domain '$id': missing or empty $(basename "$f")"
    done
    [ -s "$DESC" ] && [ -s "$ONT" ] && [ -s "$SHP" ] || continue

    # description.md — all seven sections, each with content before the next section
    for section in "## Concepts" "## Taxonomy" "## Relationships" "## Attributes" "## Lifecycle" "## Roles" "## Primary workflow"; do
        grep -q "^$section" "$DESC" || fail "domain '$id': description.md missing section '$section'"
    done
    python3 - "$DESC" "$id" <<'PYEOF'
import sys, re
text = open(sys.argv[1]).read()
dom = sys.argv[2]
sections = re.split(r"^## ", text, flags=re.M)[1:]
bad = 0
for s in sections:
    lines = s.strip().split("\n")
    title = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    if not body:
        print(f"FAIL: domain '{dom}': description.md section '{title}' is empty")
        bad += 1
sys.exit(1 if bad else 0)
PYEOF
    [ $? -ne 0 ] && ERRORS=$((ERRORS + 1))

    # every manifest entity present as a class in ontology.ttl and as a concept bullet in description.md
    ENTITIES=$(python3 -c "
import json
m=json.load(open('$ROOT/index.json'))
d=[x for x in m['domains'] if x['id']=='$id'][0]
print('\n'.join(d['entities']))
")
    for e in $ENTITIES; do
        grep -q ":$e a owl:Class" "$ONT" || fail "domain '$id': entity '$e' not declared as owl:Class in ontology.ttl"
        grep -q "\*\*$e\*\*" "$DESC" || fail "domain '$id': entity '$e' has no **$e** concept bullet in description.md"
    done

    # namespace
    grep -q "@prefix : <https://ecosystemcode.com/ontology/$id#>" "$ONT" || fail "domain '$id': ontology.ttl namespace prefix incorrect"

    # >= 4 object properties with domain and range
    OPROPS=$(grep -c "a owl:ObjectProperty" "$ONT")
    [ "$OPROPS" -ge 4 ] || fail "domain '$id': only $OPROPS object properties (minimum 4)"
    DOMAINS_N=$(grep -c "rdfs:domain" "$ONT"); RANGES_N=$(grep -c "rdfs:range" "$ONT")
    [ "$DOMAINS_N" -ge "$OPROPS" ] || fail "domain '$id': object properties lack rdfs:domain declarations"
    [ "$RANGES_N" -ge "$OPROPS" ] || fail "domain '$id': object properties lack rdfs:range declarations"

    # SKOS: every class carries prefLabel and definition
    CLASSES_N=$(grep -c "a owl:Class" "$ONT")
    PREF_N=$(grep -c "skos:prefLabel" "$ONT")
    DEF_N=$(grep -c "skos:definition" "$ONT")
    [ "$PREF_N" -ge "$CLASSES_N" ] || fail "domain '$id': $CLASSES_N classes but only $PREF_N skos:prefLabel"
    [ "$DEF_N" -ge "$CLASSES_N" ] || fail "domain '$id': $CLASSES_N classes but only $DEF_N skos:definition"

    # role class under BFO branch
    grep -q "rdfs:subClassOf bfo:0000023" "$ONT" || fail "domain '$id': no role class under bfo:0000023"

    # shapes.ttl minimums
    grep -q "a sh:NodeShape" "$SHP" || fail "domain '$id': shapes.ttl has no sh:NodeShape"
    grep -q "sh:minCount" "$SHP" || fail "domain '$id': shapes.ttl has no sh:minCount constraint"
    grep -q "sh:in" "$SHP" || fail "domain '$id': shapes.ttl does not constrain lifecycle states with sh:in"

    # overlay folders must be registered in the manifest industries[] and vice versa
    MANIFEST_INDUSTRIES=$(python3 -c "
import json
m=json.load(open('$ROOT/index.json'))
d=[x for x in m['domains'] if x['id']=='$id'][0]
print('\n'.join(d.get('industries',[])))
")
    if [ -d "$DIR/industries" ]; then
        for ov in "$DIR/industries"/*/; do
            [ -d "$ov" ] || continue
            ovid=$(basename "$ov")
            echo "$MANIFEST_INDUSTRIES" | grep -qx "$ovid" || fail "domain '$id': overlay folder '$ovid' not in manifest industries[]"
            [ -s "$ov/overlay.md" ]  || fail "domain '$id': overlay '$ovid' missing overlay.md"
            [ -s "$ov/overlay.ttl" ] || fail "domain '$id': overlay '$ovid' missing overlay.ttl"
            echo "$INDUSTRY_IDS" | grep -qx "$ovid" || fail "domain '$id': overlay industry '$ovid' not registered in industries.json"
        done
    fi
    for mi in $MANIFEST_INDUSTRIES; do
        [ -d "$DIR/industries/$mi" ] || fail "domain '$id': manifest lists industry '$mi' but no overlay folder exists"
    done
done

# ---------- folders without manifest entries ----------
for d in "$ROOT/domains"/*/; do
    [ -d "$d" ] || continue
    id=$(basename "$d")
    echo "$DOMAIN_IDS" | grep -qx "$id" || fail "domains/$id/ exists but has no index.json entry"
done

# ---------- industries ----------
for iid in $INDUSTRY_IDS; do
    IDIR="$ROOT/industries/$iid"
    [ -d "$IDIR" ] || { fail "industry '$iid' in registry but industries/$iid/ missing"; continue; }
    [ -s "$IDIR/industry.md" ] || fail "industry '$iid': missing industry.md"
    [ -s "$IDIR/common.ttl" ]  || fail "industry '$iid': missing common.ttl"
done
for d in "$ROOT/industries"/*/; do
    [ -d "$d" ] || continue
    iid=$(basename "$d")
    echo "$INDUSTRY_IDS" | grep -qx "$iid" || fail "industries/$iid/ exists but has no industries.json entry"
done

echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "Validation FAILED ($ERRORS error(s))"
    exit 1
fi
COUNT=$(echo "$DOMAIN_IDS" | wc -l | tr -d ' ')
echo "Validation PASSED — $COUNT domains, $(echo "$INDUSTRY_IDS" | wc -l | tr -d ' ') industries."
exit 0
