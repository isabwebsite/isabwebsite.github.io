#!/usr/bin/env python3
"""Offline checks for manuscript integrity, generated links and maintenance behavior."""
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
from pathlib import Path
import json, re, tempfile
from build import ROOT, Builder, inline, markdown, read_article

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.duplicates=[];self.refs=[];self.h1=0;self.refresh=False;self.errors=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='meta' and a.get('http-equiv')=='refresh':self.refresh=True
        if tag=='img' and not a.get('alt'):self.errors.append('Image without alternative text')
        for k in ['href','src']:
            if a.get(k):self.refs.append(a[k])

def main():
    dist=ROOT/'dist'
    if not dist.exists():raise SystemExit('先运行 python3 tools/build.py / Build first.')
    b=Builder('2026-11-06');errors=[];warnings=[]
    pages={p:Page(p.read_text(encoding='utf-8')) for p in dist.rglob('*.html')}
    links=0
    for p,page in pages.items():
        route='/'+str(p.relative_to(dist))
        if route.endswith('index.html'):route=route[:-10]
        if page.duplicates:errors.append(f'{route}: duplicate ids {page.duplicates}')
        if not page.refresh and page.h1!=1:errors.append(f'{route}: expected one h1, found {page.h1}')
        errors.extend(f'{route}: {e}' for e in page.errors)
        for ref in page.refs:
            u=urlsplit(urljoin('https://local.invalid'+route,ref))
            if u.hostname!='local.invalid':continue
            links+=1;target=dist/unquote(u.path).lstrip('/')
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(f'{route}: missing {ref}');continue
            if u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'{route}: missing anchor {ref}')
    for a in b.articles:
        for key in [x.strip() for x in a.get('related','').split(',') if x.strip()]:
            if not b.get(a['lang'],key):errors.append(f'{a["file"]}: missing related {key}')
    for key in b.editorial['starting_notes']+b.editorial['season_notes']:
        if not b.get('en',key):errors.append('Missing editorial selection '+key)
    for old,new in b.aliases.items():
        if not b.get('en',new):errors.append('Missing redirect target '+new)

    # Every originally imported file remains represented by a current source route.
    imported=json.loads((ROOT/'docs/import-record.json').read_text())
    if len(b.articles)<imported['markdown_files']:errors.append('Fewer source files than original import')
    baseline=ROOT/'docs/original-routes.json'
    if baseline.exists():
        for route in json.loads(baseline.read_text()):
            if not (dist/route.lstrip('/')/'index.html').is_file():errors.append('Missing original route '+route)

    # A single-language contribution must show up in the catalog without requiring a translation.
    fake=dict(b.articles[0],lang='zh',kind='resource',slug='maintenance-smoke',key='resource/maintenance-smoke')
    b.articles.append(fake);b.by_key[('zh',fake['key'])]=fake
    if not any(a['key']==fake['key'] for a in b.records('en')):errors.append('Single-language article omitted')
    # Markdown input never becomes executable HTML or JavaScript links.
    if '<script>' in inline('<script>alert(1)</script>'):errors.append('Raw HTML not escaped')
    try:inline('[bad](javascript:alert)');errors.append('Unsafe link accepted')
    except ValueError:pass
    for invalid in ['//external.example/x','javascript:alert(1)','data:text/plain,x']:
        try:inline('[bad]('+invalid+')');errors.append('Unsafe URL accepted: '+invalid)
        except ValueError:pass
    html,toc=markdown('## Title\n\n| Name | Value |\n| --- | --- |\n| A | B |\n\n- One\n- Two\n','en')
    if len(toc)!=1 or '<table>' not in html or html.count('<li>')!=2:errors.append('Markdown structures failed')
    # Canonical addresses follow the actual page route, including non-article pages.
    with tempfile.TemporaryDirectory() as folder:
        probe=Builder('2026-11-06','https://preview.example');probe.out=Path(folder)
        probe.write('/zh/notes/',probe.shell('Notes','<main id="main"><h1>Notes</h1></main>'))
        if 'href="https://preview.example/zh/notes/"' not in (probe.out/'zh/notes/index.html').read_text():errors.append('Canonical route mismatch')
    # Never publish local paths, personal account IDs or secrets with the website.
    patterns=[r'/Users/',r'(?i)[A-Za-z0-9._%+-]+@(?:gmail|outlook|hotmail|icloud|yahoo)\.com',r'(?i)NETLIFY_AUTH_TOKEN',r'(?i)sk-proj-[A-Za-z0-9_-]{10,}']
    leaks=[]
    for p in dist.rglob('*'):
        if p.suffix in ['.html','.js','.json','.css','.txt','.xml','.md'] and p.is_file():
            text=p.read_text(encoding='utf-8',errors='replace')
            if any(re.search(pattern,text) for pattern in patterns):leaks.append(str(p.relative_to(dist)))
    if leaks:errors.append('Personal/config data found in public output: '+', '.join(leaks[:10]))
    report={'article_files':len(b.articles)-1,'unique_notes':len({a['key'] for a in b.articles})-1,'html_pages':len(pages),'internal_references_checked':links,'errors':errors,'warnings':warnings,'external_links':'Not live-checked by this offline test','source_review':'Imported dates retained; only new resources rechecked in this revision'}
    (ROOT/'docs/check-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
