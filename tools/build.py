#!/usr/bin/env python3
"""Dependency-free static journal builder. Markdown files are the only article source."""
from pathlib import Path
from datetime import datetime, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from html import escape
from urllib.parse import urlsplit, quote
import argparse, json, re, shutil, tempfile, math, os

ROOT=Path(__file__).resolve().parents[1]
def today_string():
    try:return datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
    except ZoneInfoNotFoundError:return date.today().isoformat()

LANGS={'zh':'简体中文','en':'English','es':'Español','ar':'العربية','hi':'हिन्दी','ko':'한국어','vi':'Tiếng Việt','fr':'Français','bn':'বাংলা','pt':'Português','sw':'Kiswahili'}
CATS={'study':('学习有办法','Study a little better'),'food':('吃饭与买菜','Food & groceries'),'home':('安顿日常','Make yourself at home'),'move':('出门与通勤','Getting around'),'weekend':('给自己放个假','A little time off'),'care':('需要帮助时','Find support'),'events':('城市的热闹','Around town')}
WORDS={
'home':('首页','Home'),'all':('全部笔记','All notes'),'about':('关于这本小刊','About this journal'),'recent':('最近更新','Fresh pages'),
'read':('读这篇笔记','Read the note'),'source':('打开原网站','Visit the resource'),'contents':('这篇会讲什么','In this note'),'quick':('先看这几句','The short version'),
'login':('需要账号吗','Do I need an account?'),'cost':('费用与免费范围','What does it cost?'),'checked':('资料核对','Sources checked'),'edited':('文字整理','Edited'),
'author':('ISAB 编辑组 · 公开资料整理','ISAB editors · Based on published sources'),'more':('接着翻一篇','Keep reading'),'past':('往期回顾','Past edition'),
'current':('查看这一期日程','Check this edition'),'future':('日程待公布','Dates to be announced'),'back':('回到全部笔记','Back to all notes'),
'print':('打印 / 保存 PDF','Print / save PDF'),'share':('复制链接','Copy link'),'copied':('链接已复制','Link copied'),'shareError':('暂时无法复制，可复制浏览器中的网址。','Copy the address from your browser instead.'),
'search':('想找点什么？','What would help today?'),'placeholder':('试试：做饭、论文、公交、租房…','Try groceries, papers, buses, rent…'),
'found':('篇笔记','notes'),'empty':('还没找到，换个词试试，或查看全部笔记。','No match yet. Try another word or browse all notes.'),
'skip':('跳到正文','Skip to content'),'guide':('生活与学习笔记','Notes for everyday life'),'credits':('照片与资料来源','Photos & sources'),
'screen':('展开原网页参考截图','View the reference screenshot'),'screenshotNote':('截图是当时的页面，当前界面可能不同。','This records an earlier page; the current interface may differ.'),
'pastNote':('这一期已经结束，以下保留为往期参考。下一期日期请查看主办方，不沿用旧日程。','This edition has ended. The notes below are an archive; check the organizer for the next dates.'),
}
def tr(key,lang): return WORDS[key][0 if lang=='zh' else 1]
def cat(key,lang): return CATS[key][0 if lang=='zh' else 1]
def safe_url(url):
    return url.startswith(('/', '#')) and not url.startswith('//') or urlsplit(url).scheme in ('https','http')
def inline(text):
    tokens=[]
    def token(value): tokens.append(value);return '\x00'+str(len(tokens)-1)+'\x00'
    def link(m):
        label,url=m.groups()
        if not safe_url(url): raise ValueError('Unsupported link: '+url)
        ext=' target="_blank" rel="noopener noreferrer"' if url.startswith(('https:','http:')) else ''
        return token('<a href="'+escape(url,quote=True)+'"'+ext+'>'+escape(label)+'</a>')
    text=re.sub(r'\[([^\]]+)\]\(([^\s]+)\)',link,text)
    text=escape(text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    return re.sub('\x00(\d+)\x00',lambda m:tokens[int(m[1])],text)

def markdown(body,lang):
    lines=body.splitlines(); out=[]; headings=[]; i=0; anchor=0
    while i<len(lines):
        s=lines[i].strip()
        if not s:i+=1;continue
        h=re.match(r'^(#{2,4}) (.+)',s)
        if h:
            anchor+=1;ident='section-'+str(anchor);level=len(h[1]);headings.append((ident,h[2],level))
            out.append(f'<h{level} id="{ident}">{inline(h[2])}</h{level}>');i+=1;continue
        im=re.fullmatch(r'!\[([^\]]*)\]\(([^\s]+)\)',s)
        if im:
            alt,src=im.groups()
            if not src.startswith('/assets/'):raise ValueError('Images must use /assets/: '+src)
            fig=f'<figure><a href="{escape(src)}" target="_blank" rel="noopener"><img src="{escape(src)}" alt="{escape(alt)}" loading="lazy" width="1280" height="720"></a><figcaption>{escape(alt)}</figcaption></figure>'
            out.append(f'<details class="reference-image"><summary>{tr("screen",lang)}</summary>{fig}<p>{tr("screenshotNote",lang)}</p></details>' if '/journal/' in src else fig);i+=1;continue
        if s.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|\-]+\|$',lines[i+1].strip()):
            split=lambda x:[c.strip() for c in x.strip().strip('|').split('|')]
            cols=split(s);i+=2;rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):rows.append(split(lines[i]));i+=1
            if any(len(row)!=len(cols) for row in rows):raise ValueError('Uneven Markdown table')
            out.append('<div class="table-wrap" role="region" tabindex="0" aria-label="'+('数据表，可横向滚动' if lang=='zh' else 'Data table, scroll horizontally')+'"><table><thead><tr>'+''.join('<th scope="col">'+inline(c)+'</th>' for c in cols)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+inline(c)+'</th>') if j==0 else '<td>'+inline(c)+'</td>' for j,c in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>');continue
        if s.startswith('> '):
            parts=[]
            while i<len(lines) and lines[i].strip().startswith('> '):parts.append(lines[i].strip()[2:]);i+=1
            out.append('<aside class="editor-note">'+inline(' '.join(parts))+'</aside>');continue
        if re.match(r'^(?:- |\d+\. )',s):
            ordered=bool(re.match(r'^\d+\. ',s));items=[];pattern=r'^\d+\. ' if ordered else r'^- '
            while i<len(lines) and re.match(pattern,lines[i].strip()):items.append(re.sub(pattern,'',lines[i].strip()));i+=1
            tag='ol' if ordered else 'ul';out.append('<'+tag+'>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</'+tag+'>');continue
        parts=[s];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#{2,4} |!\[|> |\||- |\d+\. )',lines[i].strip()):parts.append(lines[i].strip());i+=1
        out.append('<p>'+inline(' '.join(parts))+'</p>')
    return '\n'.join(out),headings

def read_article(path):
    raw=path.read_text(encoding='utf-8')
    if not raw.startswith('---\n'):raise ValueError(str(path)+': missing metadata')
    metadata,body=raw[4:].split('\n---\n',1);m={}
    for line in metadata.splitlines():
        if not line.strip() or line.startswith('#'):continue
        key,value=line.split(':',1)
        if key in m:raise ValueError('Duplicate field '+key)
        m[key]=value.strip()
    for key in ['lang','kind','slug','category','title','summary','takeaway','edited','checked']:
        if not m.get(key):raise ValueError(str(path)+': missing '+key)
    if m['lang'] not in LANGS or m['category'] not in CATS:raise ValueError('Unknown language/category: '+str(path))
    if not re.fullmatch('[a-z0-9-]+',m['slug']) or not re.fullmatch('[a-z]+',m['kind']):raise ValueError('Invalid article path')
    for k in ['edited','checked','event_end']:
        if m.get(k):date.fromisoformat(m[k])
    if m.get('url') and not m['url'].startswith('https://'):raise ValueError('Resource URL must use HTTPS')
    for k in ['cover']:
        if m.get(k) and not (ROOT/m[k].lstrip('/')).is_file():raise ValueError('Missing cover '+m[k])
    expected=ROOT/'content'/m['lang']/m['kind']/(m['slug']+'.md')
    if path.resolve()!=expected.resolve():raise ValueError('Article metadata must match file location: '+str(expected.relative_to(ROOT)))
    m['key']=m['kind']+'/'+m['slug'];m['path']='/'+m['lang']+'/guides/'+m['key']+'/'
    m['body']=body.strip();m['html'],m['headings']=markdown(body,m['lang']);m['file']=str(path.relative_to(ROOT))
    plain=re.sub(r'\]\([^)]*\)','',body);cn=len(re.findall(r'[\u4e00-\u9fff]',plain))
    m['minutes']=max(1,math.ceil(cn/400 if cn>100 else len(plain.split())/220))
    return m

class Builder:
 def __init__(self,today,public_url=''):
    self.today=today;self.public_url=public_url.rstrip('/');self.articles=[read_article(p) for p in sorted((ROOT/'content').rglob('*.md'))]
    self.by_key={(a['lang'],a['key']):a for a in self.articles}
    if len(self.by_key)!=len(self.articles):raise ValueError('Duplicate language/article route')
    self.aliases=json.loads((ROOT/'theme/aliases.json').read_text());self.editorial=json.loads((ROOT/'theme/editorial.json').read_text());self.routes=set();self.out=None
 def records(self,lang):
    keys=sorted({a['key'] for a in self.articles})
    return [self.get(lang,key) for key in keys]
 def get(self,lang,key):
    return (self.by_key.get((lang,key)) or self.by_key.get(('en',key))
            or self.by_key.get(('zh',key)) or next((a for a in self.articles if a['key']==key),None))
 def past(self,a):return a.get('event_status')=='past' or bool(a.get('event_end') and a['event_end']<self.today)
 def event_badge(self,a,lang):
    if a['kind']!='event':return ''
    label=tr('past' if self.past(a) else ('current' if a.get('event_end') else 'future'),lang)
    return f'<span class="status-tag" data-event-end="{a.get("event_end","")}" data-event-state="{a.get("event_status","")}">{label}</span>'
 def write(self,path,html):
    dest=self.out/path.strip('/')
    if path.endswith('/') or path=='/':dest=dest/'index.html'
    if self.public_url:
        html=re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="'+escape(self.public_url+path)+'">', html)
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html,encoding='utf-8');self.routes.add(path)
 def shell(self,title,body,lang='zh',active='',description='',article=None):
    zh=lang=='zh';home='/'+lang+'/';current=article['path'] if article else home
    options=[]
    for code,name in LANGS.items():
        target=self.get(code,article['key'])['path'] if article else '/'+code+'/'
        if article and (code,article['key']) not in self.by_key:target='/'+code+'/'
        options.append(f'<option value="{target}"'+(' selected' if code==lang else '')+'>'+name+'</option>')
    seo=f'<link rel="canonical" href="{escape(self.public_url+current)}">' if self.public_url else '<meta name="robots" content="noindex,nofollow">'
    return f'''<!doctype html><html lang="{lang}"{' dir="rtl"' if lang=='ar' else ''}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · ISAB</title><meta name="description" content="{escape(description or tr('guide',lang))}"><meta name="theme-color" content="#f7f3eb">{seo}<link rel="icon" href="/assets/isab.svg"><link rel="stylesheet" href="/theme.css"><script defer src="/journal.js"></script></head><body data-lang="{lang}" data-today="{self.today}"><a class="skip" href="#main">{tr('skip',lang)}</a><header class="site-header"><a class="brand" href="{home}" aria-label="ISAB {tr('home',lang)}"><strong>ISAB<span>↗</span></strong><span class="brand-caption">{tr('guide',lang)}<small>THE EVERYDAY JOURNAL</small></span></a><nav aria-label="{'主导航' if zh else 'Main navigation'}"><a href="{home}" {'aria-current="page"' if active=='home' else ''}>{tr('home',lang)}</a><a href="/{lang}/notes/" {'aria-current="page"' if active=='notes' else ''}>{tr('all',lang)}</a><a href="/{lang}/about/" {'aria-current="page"' if active=='about' else ''}>{tr('about',lang)}</a></nav><label class="language"><span class="sr-only">{'选择语言' if zh else 'Language'}</span><select id="language">{''.join(options)}</select></label></header>{body}<footer class="site-footer"><div><a class="footer-logo" href="{home}">ISAB ↗</a><p>{'把有用的经验，一届一届传下去。' if zh else 'Useful little things, passed from one group of students to the next.'}</p><small>{'学生独立整理的生活与学习笔记。' if zh else 'Independently edited notes for student life.'}</small></div><div><a href="/{lang}/notes/">{tr('all',lang)}</a><a href="/{lang}/about/#sources">{tr('credits',lang)}</a><a href="/directory/">{'其他语言' if zh else 'More languages'}</a></div><span class="footer-place">IOWA CITY<br>LIFE · LEARNING · LITTLE DISCOVERIES</span></footer></body></html>'''
 def card(self,a,lang,style=''):
    i=self.articles.index(a);theme=['sand','rose','plum'][i%3]
    cover=a.get('cover','');photo=cover and '/journal/' not in '/'+cover
    art=f'<img src="/{escape(cover.lstrip("/"))}" alt="{escape(a.get("cover_alt",a["title"]))}" loading="lazy" width="640" height="420">' if photo else f'<span class="cover-number">{escape(a.get("site",cat(a["category"],lang)))}</span><span class="cover-word">{escape(cat(a["category"],lang))}</span><span class="cover-arrow" aria-hidden="true">↗</span>'
    fallback='<span class="language-tag">'+LANGS[a['lang']]+'</span>' if a['lang']!=lang else ''
    return f'''<article class="note-card {style}" lang="{a["lang"]}" dir="{"rtl" if a["lang"]=="ar" else "ltr"}"><a class="card-art {theme}" href="{a["path"]}" tabindex="-1" aria-hidden="true">{art}</a><div class="card-copy"><p class="eyebrow">{escape(cat(a["category"],lang))} {fallback} {self.event_badge(a,lang)}</p><h3><a href="{a["path"]}">{escape(a["title"])}</a></h3><p>{escape(a["summary"])}</p><div class="card-meta"><span>{a["minutes"]} {'分钟' if lang=='zh' else 'min read'}</span><time datetime="{a["edited"]}">{a["edited"]}</time><span aria-hidden="true">↗</span></div></div></article>'''
 def home(self,lang):
    zh=lang=='zh';records=self.records(lang);new=sorted(records,key=lambda a:(a['edited'],a['key']),reverse=True)
    featured=new[:3]
    language_notice='' if lang in ['zh','en'] else f'<p class="language-notice">{LANGS[lang]}: existing weekend and seasonal notes are available in this language. Other articles open in an available language, clearly marked.</p>'
    topics=''.join(f'<a href="/{lang}/notes/?topic={key}"><span>{cat(key,lang)}</span><span aria-hidden="true">↗</span></a>' for key in ['study','food','home','move','weekend','care'])
    paths=self.editorial['starting_notes']
    reading=''.join(f'<a class="reading-row" href="{a["path"]}"><span class="row-number">0{i+1}</span><span><small>{cat(a["category"],lang)}</small><strong>{escape(a["title"])}</strong></span><span aria-hidden="true">↗</span></a>' for i,k in enumerate(paths) if (a:=self.get(lang,k)))
    season=[self.get(lang,key) for key in self.editorial['season_notes']];season=[a for a in season if a]
    resources=''.join(f'<a class="resource-row" href="{a["path"]}"><strong>{escape(a["site"])}</strong><span>{escape(a.get("cost",a["summary"]))}</span><span aria-hidden="true">↗</span></a>' for a in [r for r in new if r['kind']=='resource'][:3])
    body=f'''<main id="main"><div class="edition"><span>ISAB · IOWA CITY</span><span>{'同学整理，日常慢慢用。' if zh else 'Student notes. Everyday discoveries.'}</span><time datetime="{self.today}">{self.today}</time></div>{language_notice}<section class="hero"><div class="hero-copy"><p class="eyebrow">A LITTLE HELP FOR EVERYDAY LIFE</p><h1>{'把日子<br>过顺一点。' if zh else 'A little help.<br>A better day.'}</h1><p class="hero-intro">{'一顿饭怎么做，一篇论文怎么找，一个周末怎么过。把值得用的网站和小方法，留在这里，慢慢翻。' if zh else 'A meal to make, a paper to find, a weekend to enjoy. Good websites and small ideas, collected for life here.'}</p><a class="button primary" href="#latest">{'翻开最近的笔记' if zh else 'Open the latest notes'} <span aria-hidden="true">↗</span></a><p class="hero-byline">{'由 ISAB 编辑组独立整理' if zh else 'Independently put together by ISAB editors'}</p></div><figure class="hero-photo"><img src="/assets/downtown-iowa-city.jpg" alt="{'2021 年 Iowa City 的 Clinton Street 沿街店铺' if zh else 'Clinton Street storefronts in Iowa City in 2021'}" width="1195" height="596" fetchpriority="high"><div class="photo-label"><span>01 / LOCAL LIFE</span><b>{'从这里，开始熟悉一座城。' if zh else 'Make a place feel a little more familiar.'}</b></div><figcaption>Clinton Street, Iowa City · 2021 · <a href="/{lang}/about/#sources">{'照片来源' if zh else 'Photo credit'}</a></figcaption></figure></section><nav class="topic-nav" aria-label="{'按日常主题阅读' if zh else 'Explore by topic'}">{topics}</nav><section id="latest" class="section"><div class="section-head"><div><p class="eyebrow">NEW IN THE JOURNAL</p><h2>{tr('recent',lang)}</h2></div><a class="text-link" href="/{lang}/notes/">{tr('all',lang)} ↗</a></div><div class="cards-three">{''.join(self.card(a,lang) for a in featured)}</div></section><section class="section reading-section"><div class="reading-intro"><p class="eyebrow">A GOOD PLACE TO START</p><h2>{'今天，先解决<br>一件小事。' if zh else 'One small thing<br>at a time.'}</h2><p>{'不用一次读完。找到眼下需要的那一篇，做完一件事，再回来翻下一页。' if zh else 'No need to read everything. Find the note you need, try one useful thing, and come back for the next.'}</p></div><div class="reading-list">{reading}</div></section><section class="section season-section"><div class="section-head"><div><p class="eyebrow">FOR THE SEASON</p><h2>{escape(self.editorial['season_title_zh' if zh else 'season_title_en'])}</h2></div><a class="text-link" href="/{lang}/notes/?topic=weekend">{'留点时间给自己' if zh else 'Make a little time'} ↗</a></div><div class="season-grid">{''.join(self.card(a,lang,'season-card') for a in season)}</div></section><section class="section resources-section"><div><p class="eyebrow">BOOKMARK-WORTHY</p><h2>{'值得留下的网站' if zh else 'Worth a bookmark'}</h2><p>{'先看看能帮什么，再决定要不要注册。' if zh else 'See what it helps with before creating an account.'}</p></div><div>{resources}</div></section><section class="closing-note"><p>{'这里的笔记，会跟着大家的生活慢慢长大。' if zh else 'A journal that grows with the people who use it.'}</p><a href="/{lang}/about/">{'认识这本小刊' if zh else 'Meet the journal'} ↗</a></section></main>'''
    self.write('/'+lang+'/',self.shell(tr('guide',lang),body,lang,'home'))
    if lang=='zh':self.write('/',self.shell(tr('guide',lang),body,lang,'home'))
 def article(self,a):
    lang=a['lang'];zh=lang=='zh';key=a['key'];toc=''.join(f'<a href="#{ident}">{escape(label)}</a>' for ident,label,level in a['headings'] if level==2)
    facts=''.join(f'<div><dt>{tr(k,lang)}</dt><dd>{escape(a[k])}</dd></div>' for k in ['login','cost'] if a.get(k))
    resource=f'<a class="button primary resource-button" href="{escape(a["url"])}" target="_blank" rel="noopener noreferrer">{tr("source",lang)} · {escape(a.get("site",""))} ↗</a>' if a.get('url') else ''
    event=f'<aside class="event-notice" data-event-notice data-event-end="{a.get("event_end","")}" data-event-state="{a.get("event_status","")}"'+('' if self.past(a) else ' hidden')+f'>{tr("pastNote",lang)}</aside>' if a['kind']=='event' else ''
    cover=''
    if a.get('cover') and ('(/'+a['cover'].lstrip('/')+')') not in a['body']:
        src='/'+a['cover'].lstrip('/');fig=f'<figure class="article-cover"><a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="{escape(a.get("cover_alt",a["title"]))}" width="1195" height="700" loading="lazy"></a><figcaption>{escape(a.get("cover_caption",a.get("cover_alt","")))}</figcaption></figure>'
        cover=f'<details class="reference-image"><summary>{tr("screen",lang)}</summary>{fig}<p>{tr("screenshotNote",lang)}</p></details>' if '/journal/' in src else fig
    related_keys=[k.strip() for k in a.get('related','').split(',') if k.strip()]
    related=[self.get(lang,k) for k in related_keys if self.get(lang,k)]
    related+=[r for r in self.records(lang) if r['category']==a['category'] and r['key']!=key and r not in related]
    related=related[:3]
    body=f'''<main id="main" class="article-page"><div class="article-breadcrumb"><a href="/{lang}/notes/">{tr('all',lang)}</a><span>/</span><a href="/{lang}/notes/?topic={a['category']}">{cat(a['category'],lang)}</a></div><header class="article-header"><p class="eyebrow">{cat(a['category'],lang)} {self.event_badge(a,lang)}</p><h1>{escape(a['title'])}</h1><p class="article-deck">{escape(a['summary'])}</p><div class="article-meta"><span>{tr('author',lang)}</span><span>{a['minutes']} {'分钟阅读' if zh else 'min read'}</span><span>{tr('edited',lang)} {a['edited']}</span></div></header><div class="article-layout"><aside class="article-sidebar"><p>{tr('contents',lang)}</p><nav aria-label="{tr('contents',lang)}">{toc}</nav><a class="back-link" href="/{lang}/notes/">← {tr('back',lang)}</a></aside><article class="prose"><section class="quick-take"><p class="eyebrow">{tr('quick',lang)}</p><p class="takeaway">{escape(a['takeaway'])}</p>{'<dl class="resource-facts">'+facts+'</dl>' if facts else ''}{resource}<p class="checked-date">{tr('checked',lang)} <time datetime="{a['checked']}">{a['checked']}</time></p></section>{event}<details class="mobile-toc"><summary>{tr('contents',lang)}</summary><nav>{toc}</nav></details>{cover}{a['html']}<div class="article-end"><p>{'这篇笔记依据公开资料整理。需要预约、申请或购买时，请在资源提供方的网站确认当前条件。' if zh else 'Compiled from published sources. Check current terms with the provider before booking, applying or buying.'}</p><p>{tr('checked',lang)} {a['checked']} · {tr('edited',lang)} {a['edited']}</p><div class="article-actions"><button type="button" data-copy-url>{tr('share',lang)}</button><button type="button" data-print>{tr('print',lang)}</button></div><p id="copy-status" role="status"></p></div></article></div><section class="section related"><div class="section-head"><h2>{tr('more',lang)}</h2><a href="/{lang}/notes/">{tr('all',lang)} ↗</a></div><div class="cards-three">{''.join(self.card(r,lang) for r in related)}</div></section></main>'''
    self.write(a['path'],self.shell(a['title'],body,lang,'notes',a['summary'],a))
 def catalog(self,lang,category='',kind='',path=None):
    zh=lang=='zh';records=[a for a in self.records(lang) if (not category or a['category']==category) and (not kind or a['kind']==kind)]
    records.sort(key=lambda a:(self.past(a),-date.fromisoformat(a['edited']).toordinal(),a['title']))
    chips='<button type="button" data-topic="all" aria-pressed="true">'+('全部' if zh else 'All')+'</button>'+''.join(f'<button type="button" data-topic="{k}" aria-pressed="false">{cat(k,lang)}</button>' for k in CATS)
    items=''
    for a in records:
        hay=' '.join([a['title'],a['summary'],a.get('tags',''),re.sub(r'\s+',' ',a['body'])]).casefold()
        items+=f'<div class="catalog-item" data-category="{a["category"]}" data-search="{escape(hay,quote=True)}">{self.card(a,lang,"compact")}</div>'
    notice='' if lang in ['zh','en'] else '<p class="language-notice">Seasonal and weekend notes retain existing translations. Other notes open in an available language, clearly marked.</p>'
    title=cat(category,lang) if category else tr('all',lang)
    body=f'''<main id="main" class="catalog-page"><header class="catalog-head"><p class="eyebrow">THE NOTEBOOK</p><h1>{title}</h1><p>{'按眼下的需要找一篇。读完，也许今天就能用上。' if zh else 'Find a note for what you need right now. Try something useful today.'}</p></header>{notice}<section class="catalog-tools" aria-label="{'查找笔记' if zh else 'Find a note'}"><form role="search" id="search-form"><label for="search">{tr('search',lang)}</label><div class="search-input"><input id="search" type="search" placeholder="{tr('placeholder',lang)}" autocomplete="off"><button type="submit">{'查找' if zh else 'Find'} ↗</button></div></form><div class="filter-chips" aria-label="{'主题' if zh else 'Topic'}">{chips}</div><p class="results-count" id="results-count" role="status">{len(records)} {tr('found',lang)}</p></section><div class="catalog-grid">{items}</div><p class="empty-state" id="empty-state" hidden>{tr('empty',lang)}</p></main>'''
    self.write(path or '/'+lang+'/notes/',self.shell(title,body,lang,'notes'))
 def about(self,lang):
    zh=lang=='zh';photos=json.loads((ROOT/'theme/photos.json').read_text())['photos'];credits=''.join(f'<li><a href="{escape(p["source"])}" target="_blank" rel="noopener noreferrer">{escape(p["caption"].get(lang,p["caption"]["en"]))}</a> · {escape(p["author"])} · <a href="{escape(p["licenseUrl"])}">{escape(p["license"])}</a></li>' for p in photos.values())
    text='''<p>这本小刊由 ISAB 编辑组独立整理，写给正在熟悉 Iowa City、也想把日常过得轻松一点的同学。</p><p>这里会留下值得用的网站、找到资料的小方法、一顿饭的灵感，以及周末能去走走的地方。文章可以链接学校、图书馆、商家和社区资源；介绍来自同学的整理，具体服务由对应机构提供。</p><h2>经验可以分享，来源也要说清楚。</h2><p>目前的文章以公开资料整理为主，不把网页浏览写成亲身体验。每篇分别显示文字编辑日期和资料核对日期；调整排版或改一句话，不代表所有价格、时间和条件重新查过。</p><h2>读者不用注册。</h2><p>阅读笔记和搜索不需要账号。文中的原网站可能有自己的登录、预约或收费条件，我们把已知范围写在笔记开头。本站没有读者账户、投稿表单或在线 AI 问答，也不要求提供个人资料。</p><h2>一起让笔记变得更好。</h2><p>如果发现链接失效、价格过时，或有一条自己的生活经验想分享，可以先记下文章链接、变化内容、来源和日期。社团统一联系方式准备好后，会放在这里。</p><h2>关于语言</h2><p>新增笔记优先维护中英文。原有周末与四季笔记保留其他九种语言；缺少对应译文时，明确标注英文，不把英文回退当成已经翻译。</p>''' if zh else '''<p>An independent journal by ISAB editors, for students making a life in and around Iowa City.</p><p>We collect useful websites, small study habits, food ideas and places to spend a free afternoon. Links may lead to libraries, schools, businesses or community services. We write the notes; the linked providers run their own services.</p><h2>Good notes show where they come from.</h2><p>Current articles are based on published sources, not invented first-person experiences. Editing dates and source-check dates are separate. A design update does not mean every price or opening hour has been checked again.</p><h2>No account needed to read.</h2><p>You can read and search without signing in. Linked resources may have their own accounts, eligibility and prices; we explain the known conditions near the start. This site has no reader accounts, submission forms or live AI chat.</p><h2>A journal we can keep improving.</h2><p>Found an old price or a broken link? Keep the article link, what changed, the source and the date. A shared contact route will be added when the student group has one ready.</p><h2>About the languages</h2><p>New articles are maintained in English and Chinese first. Existing weekend and seasonal notes retain nine other languages. Where a translation is unavailable, the English article is clearly marked.</p>'''
    body=f'<main id="main" class="about-page"><p class="eyebrow">ABOUT THE JOURNAL</p><h1>{"把有用的小事，<br>留给下一个人。" if zh else "Small things worth<br>passing on."}</h1><div class="prose">{text}<h2 id="sources">{tr("credits",lang)}</h2><p>{"地点照片来自 Wikimedia Commons，保留各自署名与许可，经过网页缩放和裁切。历史照片均标明年份。第三方网页截图保留原权利，仅作阅读参考，来源与采集记录随图片保存。" if zh else "Place photos come from Wikimedia Commons, with their original credits and licenses, resized and cropped for the web. Historic photos retain their dates. Third-party screenshots retain their original rights and are used as reading references."}</p><ul class="credit-list">{credits}</ul><p><a href="/assets/journal/SOURCES.json">{"网页截图来源记录" if zh else "Screenshot source records"}</a></p></div></main>'
    self.write('/'+lang+'/about/',self.shell(tr('about',lang),body,lang,'about'))
 def build(self):
    with tempfile.TemporaryDirectory(prefix='.build-',dir=ROOT) as temp:
      self.out=Path(temp);shutil.copytree(ROOT/'assets',self.out/'assets')
      for src,name in [('theme/styles.css','theme.css'),('theme/site.js','journal.js')]:shutil.copyfile(ROOT/src,self.out/name)
      for a in self.articles:self.article(a)
      for lang in LANGS:
        self.home(lang);self.catalog(lang);self.about(lang)
        for category in CATS:self.catalog(lang,category=category,path=f'/{lang}/topics/{category}/')
        for old,kind in [('journal','journal'),('practical','practical'),('transport','ride'),('life','note')]:self.catalog(lang,kind=kind,path=f'/{lang}/topics/{old}/')
        # Old untranslated pages resolve explicitly to their English article.
        for a in self.records(lang):
          if a['lang']!=lang:self.redirect(f'/{lang}/guides/{a["key"]}/',a['path'],lang)
        for old,new in self.aliases.items():
          a=self.get(lang,new)
          if a:self.redirect(f'/{lang}/guides/{old}/',a['path'],lang)
      language_list=''.join(f'<li><a href="/{code}/">{name}</a></li>' for code,name in LANGS.items())
      self.write('/directory/',self.shell('Languages',f'<main id="main" class="about-page"><h1>Choose your language</h1><ul class="language-directory">{language_list}</ul></main>','en'))
      self.write('/404.html',self.shell('找不到这页 / Page not found','<main id="main" class="about-page"><h1>这页可能搬家了。</h1><p>This page may have moved. Find the note in the journal.</p><a class="button primary" href="/zh/notes/">查看全部笔记 / Browse notes ↗</a></main>'))
      (self.out/'legacy-routes.json').write_text(json.dumps(self.aliases,ensure_ascii=False))
      # URL metadata is generated only for an explicitly chosen public address.
      if self.public_url:
        xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(self.public_url+p)+'</loc></url>' for p in sorted(self.routes) if p.endswith('/'))+'</urlset>'
        (self.out/'sitemap.xml').write_text(xml);(self.out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+self.public_url+'/sitemap.xml\n')
      else:(self.out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
      (self.out/'build-info.json').write_text(json.dumps({'built_for':'public' if self.public_url else 'local-preview','date':self.today,'articles':len(self.articles),'routes':len(self.routes)},indent=2))
      target=ROOT/'dist'
      if target.exists():shutil.rmtree(target)
      shutil.copytree(self.out,target)
    manifest={'date':self.today,'articles':len(self.articles),'unique_articles':len({a['key'] for a in self.articles}),'routes':len(self.routes),'languages':list(LANGS),'source_files':[{k:a[k] for k in ['file','path','lang','key','checked','edited']} for a in self.articles]}
    (ROOT/'docs/build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    index=['# 文章索引','','此索引由文稿自动生成。同一篇可有多个语言版本；请改对应文稿，不要修改网页输出。','']
    for category,names in CATS.items():
        index+=['## '+names[0],'','| 标题 | 中文文稿 | 英文文稿 |','| --- | --- | --- |']
        for a in self.records('zh'):
            if a['category']!=category:continue
            links=[]
            for code in ['zh','en']:
                translated=self.by_key.get((code,a['key']))
                links.append('[打开](../'+translated['file']+')' if translated else '暂无')
            index.append('| '+a['title'].replace('|','／')+' | '+' | '.join(links)+' |')
        index.append('')
    (ROOT/'docs/文章索引.md').write_text('\n'.join(index),encoding='utf-8')
    print(f'Built {len(self.articles)} article files / {manifest["unique_articles"]} unique notes; {len(self.routes)} routes. '+('Public build.' if self.public_url else 'Local preview only; indexing disabled.'))
 def redirect(self,path,target,lang):
    self.write(path,'<!doctype html><html lang="'+lang+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url='+target+'"><link rel="icon" href="/assets/isab.svg"><title>ISAB · Note moved</title><p><a href="'+target+'">继续阅读 / Continue reading</a></p></html>')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--today',default=today_string());parser.add_argument('--public-url',default='');args=parser.parse_args()
    date.fromisoformat(args.today)
    if args.public_url:
      u=urlsplit(args.public_url)
      if u.scheme!='https' or not u.netloc or u.query or u.fragment or u.path not in ('','/') or u.username:raise ValueError('--public-url must be an HTTPS site root; subpath hosting is not configured.')
    Builder(args.today,args.public_url).build()
if __name__=='__main__':main()
