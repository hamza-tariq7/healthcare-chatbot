"""Deterministic notebook helpers; catalog normalization is not RxNorm."""
import re
import pandas as pd


def format_mode0_pdf(hits):
    if hits is None or hits.empty:
        return '(No matching document passages found.)'
    blocks = []
    for _, row in hits.iterrows():
        if 'score' in row and float(row['score']) <= 0:
            continue
        quote = str(row.get('text', '')).strip()
        if quote:
            blocks.append(
                f"DOC={row.get('doc_id', 'UNKNOWN')} | page={row.get('page', '?')} | "
                f"chunk={row.get('chunk_id', '?')}\nQUOTE: {quote}"
            )
    return '\n\n---\n\n'.join(blocks) or '(No matching document passages found.)'


def normalize_catalog_term(user_term, catalog):
    """Resolve whole catalog-name phrases without inventing brand aliases."""
    text = str(user_term or '').strip()
    ingredients, brands = [], []
    for _, row in catalog.iterrows():
        generic = str(row.get('generic_name', '')).strip()
        if not generic or generic.lower() == 'nan':
            continue
        for column in ['generic_name', 'brand_name']:
            value = row.get(column, '')
            if pd.isna(value):
                continue
            term = str(value).strip()
            if term and re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.I):
                if generic not in ingredients:
                    ingredients.append(generic)
                if column == 'brand_name' and term not in brands:
                    brands.append(term)
    return {'input': text, 'rxcui': None, 'rxnorm_name': None,
            'ingredients': ingredients, 'brand_aliases': brands,
            'normalization_source': 'synthetic_catalog'}


def chunk_text(text, chunk_size=900, overlap=150):
    """Character chunks with actual overlap and a finite final chunk."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError('Require chunk_size > overlap >= 0.')
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
