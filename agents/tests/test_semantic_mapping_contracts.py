#!/usr/bin/env python3.14
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parents[2]
CRM = Namespace("https://ecosystemcode.com/ontology/crm#")
CVM = Namespace("https://ecosystemcode.com/ontology/cvm#")
LEGACY_CRM = Namespace("https://example.com/legacy/crm#")
LEGACY_CVM = Namespace("https://example.com/legacy/cvm#")


def _graph(relative: str) -> Graph:
    return Graph().parse(ROOT / relative, format="turtle")


def test_crm_child_foreign_keys_use_child_to_parent_properties():
    ontology = _graph("domains/crm/ontology.ttl")
    mapping = _graph("domains/crm/mappings/generic-mapping.ttl")

    assert (CRM.memberOfCampaign, RDF.type, OWL.ObjectProperty) in ontology
    assert (CRM.memberOfCampaign, OWL.inverseOf, CRM.hasCampaignMember) in ontology
    assert (CRM.partOfOpportunity, RDF.type, OWL.ObjectProperty) in ontology
    assert (CRM.partOfOpportunity, OWL.inverseOf, CRM.hasOpportunityLine) in ontology

    assert (LEGACY_CRM.campaign_member_campaign_ref, RDFS.subPropertyOf, CRM.memberOfCampaign) in mapping
    assert (LEGACY_CRM.campaign_member_campaign_ref, RDFS.domain, LEGACY_CRM.campaign_members_table) in mapping
    assert (LEGACY_CRM.campaign_member_campaign_ref, RDFS.range, LEGACY_CRM.campaigns_table) in mapping
    assert (LEGACY_CRM.opportunity_line_opportunity_ref, RDFS.subPropertyOf, CRM.partOfOpportunity) in mapping
    assert (LEGACY_CRM.opportunity_line_opportunity_ref, RDFS.domain, LEGACY_CRM.opportunity_lines_table) in mapping
    assert (LEGACY_CRM.opportunity_line_opportunity_ref, RDFS.range, LEGACY_CRM.opportunities_table) in mapping


def test_cvm_segment_foreign_keys_match_property_domains():
    mapping = _graph("domains/cvm/mappings/generic-mapping.ttl")
    assert (LEGACY_CVM.campaign_segment_id, RDFS.subPropertyOf, CVM.targetsSegment) in mapping
    assert (LEGACY_CVM.offer_segment_id, RDFS.subPropertyOf, CVM.targetedAtSegment) in mapping
