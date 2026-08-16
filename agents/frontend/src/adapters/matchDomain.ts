import { catalogApi } from './catalogApi';
import type { ClassDomainMatch } from './sessionOntology';
import type { CatalogMatch } from '../contracts/catalog';

const MATCH_CAP = 40;

export async function proposeClassMatches(
  classes: CatalogMatch[],
  domainId: string,
): Promise<ClassDomainMatch[]> {
  const slice = classes.slice(0, MATCH_CAP);
  const results: ClassDomainMatch[] = [];
  for (const cls of slice) {
    const query = (cls.prefLabel || cls.localName || '').trim();
    if (!query) {
      results.push({ classIri: cls.iri, status: 'none' });
      continue;
    }
    try {
      const found = await catalogApi.search({
        query,
        domain: domainId,
        limit: 5,
        includeOntology: false,
        useLlm: false,
      });
      const alts = (found.matches || [])
        .filter((m) => m.iri && m.iri !== cls.iri)
        .slice(0, 5)
        .map((m) => ({
          iri: m.iri,
          prefLabel: m.prefLabel || m.localName,
          domainId: m.domainId,
          definition: m.definition,
        }));
      const top = alts[0];
      results.push({
        classIri: cls.iri,
        catalogIri: top?.iri,
        catalogLabel: top?.prefLabel,
        catalogDomain: top?.domainId || domainId,
        catalogDefinition: top?.definition,
        alternatives: alts,
        status: top ? 'proposed' : 'none',
      });
    } catch {
      results.push({ classIri: cls.iri, status: 'none' });
    }
  }
  return results;
}
