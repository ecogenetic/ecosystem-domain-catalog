export type CollectionInfo = {
  name: string;
  entity?: string;
  count?: number;
  infrastructure?: boolean;
};

export type MappedEntity = {
  entity: string;
  collection?: string;
  catalogIri?: string;
  catalogDomain?: string;
  prefLabel?: string;
  joins?: { field: string; targetEntity: string; targetCollection?: string }[];
};

export type QueryResult = {
  ok?: boolean;
  result?: number;
  query?: string;
  plan?: {
    targetClass?: string;
    collection?: string;
    filters?: { entity: string; field: string; op: string; value: unknown }[];
    joins?: { from: string; to: string; field: string }[];
  };
  error?: string;
  llm?: { used?: boolean };
};

export const DATA_EXAMPLES = [
  'how many customers do i have',
  'how many active customers',
  'how many orders in the last month',
  'how many orders have customers',
  'how many orders have customers that are active that ordered in the last month',
];
