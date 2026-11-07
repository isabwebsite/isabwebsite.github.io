"""One-time import from the verified public snapshot. Never used by the normal build."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'work/site-review-2026-11-06/published-public-files'
TODAY = '2026-11-06'
def data(name): return json.loads((SOURCE/name).read_text().split('=',1)[1].strip().removesuffix(';'))
def loc(value, lang): return value.get(lang,value.get('en','')) if isinstance(value,dict) else value
def links(values): return '\n'.join('- ['+x.get('label',x.get('title','Source'))+']('+x['url']+')' for x in values or [])
def image(path, caption): return '\n\n!['+caption.replace(']','')+'](/'+path.lstrip('/')+')\n\n'
def write(meta, body):
    p=ROOT/'content'/meta['lang']/meta['kind']/(meta['slug']+'.md')
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): raise RuntimeError('Refusing to overwrite editable article: '+str(p))
    p.write_text('---\n'+'\n'.join(k+': '+str(v).replace('\n',' ') for k,v in meta.items() if v is not None)+'\n---\n\n'+body.strip()+'\n')

# Editorial changes affect titles and summaries, not source verification dates.
titles={
'counseling-support':('想找人聊聊，可以从哪里开始？','When you need someone to talk to'),
'health-insurance':('选保险前，先看懂自己要付的钱','Before choosing insurance, understand your costs'),
'using-healthcare':('第一次看病，预约和账单怎么走？','Your first appointment, from booking to the bill'),
'theatre-live-shows':('给自己留一个看戏的晚上','Make an evening of going to the theatre'),
'movie-nights':('今晚看电影，先选片还是选影院？','A movie night, from the film to the seats'),
'campus-sports':('想动一动，找到适合自己的运动','Find a way to move that fits your week'),
'outdoor-active':('出门走走，三个公园慢慢选','Three parks for a change of pace'),
'student-support':('生活卡住的时候，去哪里找帮助？','Where to start when everyday life gets difficult'),
'aldi-shopping-notes':('第一次去 ALDI，带上这两样东西','Your first ALDI trip: two things to bring'),
'costco-shopping-gas-notes':('去 Costco 前，先想好怎么吃完、怎么带回家','Before Costco, think about storage and the trip home'),
'bike-ebike-scooter-notes':('不买车，也能把日常安排好','Getting around without buying a car'),
'bike-library-notes':('先借一辆自行车，看看合不合适','Borrow a bike before deciding to keep it'),
'parking-permit-notes':('买停车许可前，先对上自己的时间表','Match a parking permit to your actual schedule'),
'campus-parking-lots':('车停哪里，才方便每天往返？','Where to park for your everyday trip'),
'banking-notes':('准备去 Chase 开户？先把问题带上','Questions to take to a Chase appointment'),
'wells-fargo-notes':('在 Wells Fargo 开户，先问清月费','Before a Wells Fargo account, ask about monthly fees'),
'utilities-notes':('搬进新家，水电到底由谁来开？','Moving in: who sets up the utilities?'),
'library-resources':('找到一篇论文以后，怎样真正读到它？','You found a paper. How do you read it?'),
'study-spaces':('今天想安静学，还是找个地方一起讨论？','A quiet seat or a room to work together?'),
'zillow-search':('Zillow 上房子很多，怎么留下三个候选？','Turn a crowded Zillow map into three possibilities'),
'apartments-search':('看公寓页面时，别漏掉这些小字','Read the details behind an apartment listing'),
}
takeaways={
'aldi-shopping-notes':('带购物袋和一枚 quarter，先按几顿饭买。出发前看好回程，买完不用拎着大包临时找车。','Bring bags and a quarter, shop for a few meals, and plan the trip home before filling your cart.'),
'library-resources':('先从图书馆入口找全文；打不开时，再看校外访问和馆际互借。不要一看到付费按钮就急着购买。','Start with library access, then check remote access and interlibrary loan before paying for a paper.'),
'study-spaces':('先想清楚今天要独自专注还是一起讨论，再选座位或预约房间。不同图书馆的预约方式并不相同。','Choose between quiet work and conversation first. Room-booking systems differ between libraries.'),
'zillow-search':('先确认价格对应整套还是单间，再记下具体单元、全部月费和入住日。留下三四个能用同一标准比较的候选。','Check what the price covers, then compare the exact unit, full monthly cost and move-in date.'),
'costco-shopping-gas-notes':('先算会员费、冰箱空间和回程。大包装只有在吃得完、带得回时，才真的适合这一趟采购。','Consider membership, fridge space and transport. A bulk purchase only works if you can use it and get it home.'),
}
category_map={'practicalHealth':'care','practicalArts':'weekend','practicalSports':'weekend','practicalShopping':'food','practicalNoCar':'move','practicalDriving':'move','practicalSetup':'home','practicalStudy':'study'}
cost_map={
'food':('购物、餐饮或会员费用按文中项目分别核对。','Check the costs of shopping, meals or membership for each option.'),
'home':('费用依房源、账户或服务而定，先看具体条件。','Costs depend on the property, account or service. Check the specific terms.'),
'move':('票价、许可或借用费用见正文与来源。','See the notes and sources for fares, permits or borrowing costs.'),
'study':('部分资源有使用资格，预约和借阅条件见正文。','Some resources have eligibility or booking conditions; see the notes.'),
'care':('费用与使用资格依服务和保险而定。','Costs and eligibility depend on the service and insurance.'),
'weekend':('场次、门票或租借费用分别查看。','Check tickets, individual sessions and rental charges separately.'),
'events':('入场、报名和现场消费分别查看主办方说明。','Check admission, registration and purchases with the organizer.'),
}
photodata=data('photos.js')
(ROOT/'theme/photos.json').write_text(json.dumps(photodata,ensure_ascii=False,indent=2))
content=data('content.js'); aliases={}; count=0
for filename,kind in [('practical.js','practical'),('journal.js','journal')]:
 for a in data(filename)['entries']:
  for lang in ['zh','en']:
   i=0 if lang=='zh' else 1; t=a[lang]; category=category_map.get(a.get('category'),'home')
   title=titles.get(a['id'],(a['zh']['title'],a['en']['title']))[i]
   meta={'lang':lang,'kind':kind,'slug':a['id'],'category':category,'title':title,'summary':t['summary'],'takeaway':takeaways.get(a['id'],(a['zh']['summary'],a['en']['summary']))[i],'edited':TODAY,'checked':a['checked'],'site':a['site'],'url':a['url'],'cost':cost_map[category][i],'login':('阅读此笔记无需登录；预约、申请或个人服务可能需要账号。' if lang=='zh' else 'No login to read this note. Booking, applications or personal services may need an account.'),'tags':', '.join(a.get('tags',[])),'cover':a.get('cover',''),'cover_alt':t.get('coverAlt',title),'cover_caption':t.get('coverCaption',''),'related':', '.join('practical/'+x for x in a.get('relatedNoteIds',[]))}
   body=t.get('intro','')+'\n\n'
   for s in t['sections']:
    body+='## '+s['title']+'\n\n'+s.get('body','')+'\n\n'
    if s.get('image'):body+=image(s['image'],s.get('caption',s['title']))
    if s.get('table'):
     table=s['table'];body+=table.get('caption','')+'\n\n'
     body+='| '+' | '.join(table['columns'])+' |\n| '+' | '.join('---' for _ in table['columns'])+' |\n'
     body+='\n'.join('| '+' | '.join(str(c).replace('|','／') for c in row)+' |' for row in table['rows'])+'\n\n'
    if s.get('links'):body+=links(s['links'])+'\n\n'
   if t.get('endnote'):body+='> '+t['endnote']+'\n\n'
   allsources=a.get('sources',[]) or [{'label':a['site'],'url':a['url']}]
   body+=('## 来源与实用链接' if lang=='zh' else '## Sources & useful links')+'\n\n'+links(allsources)
   write(meta,body);count+=1

for a in content['food']:
 if a.get('noteId'): aliases['place/'+a['id']]='practical/'+a['noteId'];continue
 for lang in ['zh','en']:
  t=a[lang];i=lang=='en';category='food'
  meta={'lang':lang,'kind':'place','slug':a['id'],'category':category,'title':a['name'],'summary':t['why'],'takeaway':t.get('firstOrder',t.get('firstShop',t['why'])),'edited':a['checked'],'checked':a['checked'],'site':a['name'],'url':a.get('menu',(a.get('sources') or [{}])[0].get('url','')),'cost':'菜单价格与最终结账金额可能不同。' if lang=='zh' else 'Menu prices may differ from the final total.','login':'阅读笔记无需登录；线上下单按商家要求。' if lang=='zh' else 'No login to read; online ordering follows the merchant’s requirements.','tags':', '.join(a.get('countries',[]))+', '+a.get('cuisine',''),'address':a['address']}
  body='## '+('去哪里' if lang=='zh' else 'Where to go')+'\n\n'+a['address']+'\n\n'
  body+='## '+('点什么，买什么' if lang=='zh' else 'What to order or shop for')+'\n\n'+t.get('firstOrder',t.get('firstShop',''))+'\n\n'
  if t.get('tip'):body+='## '+('出发前看一眼' if lang=='zh' else 'Before heading out')+'\n\n'+t['tip']+'\n\n'
  body+=('## 来源与菜单' if lang=='zh' else '## Sources & menu')+'\n\n'+links(a.get('sources',[]))
  write(meta,body);count+=1

for a in content['transport']:
 if a.get('noteId'): aliases['ride/'+a['id']]='practical/'+a['noteId'];continue
 for lang in ['zh','en']:
  i=lang=='en';meta={'lang':lang,'kind':'ride','slug':a['id'],'category':'move','title':loc(a['title'],lang),'summary':loc(a['summary'],lang),'takeaway':loc(a['quick'],lang),'edited':a['checked'],'checked':a['checked'],'url':a['sources'][0]['url'],'site':'出行资源' if lang=='zh' else 'Transport resources','cost':cost_map['move'][i],'login':'阅读笔记无需登录；订车与 App 功能按运营方要求。' if lang=='zh' else 'No login to read; bookings and app features follow provider requirements.'}
  body='## '+('把这一趟安排好' if lang=='zh' else 'Plan the trip')+'\n\n'+'\n'.join(str(n+1)+'. '+x for n,x in enumerate(loc(a['steps'],lang)))+'\n\n'
  body+='## '+('还有这些小事' if lang=='zh' else 'A few more things')+'\n\n'+'\n'.join('- '+x for x in loc(a['tips'],lang))+'\n\n'+('## 来源与链接' if lang=='zh' else '## Sources & links')+'\n\n'+links(a['sources'])
  write(meta,body);count+=1

for a in content['life']:
 for lang in a['title']:
  t=loc(a['title'],lang);photo=photodata['photos'].get(photodata['notes'].get(a['id']),{});zh=lang=='zh'
  meta={'lang':lang,'kind':'note','slug':a['id'],'category':'weekend','title':t,'summary':loc(a['summary'],lang),'takeaway':loc(a['summary'],lang),'edited':a['checked'],'checked':a['checked'],'url':loc(a['links'],lang)[0]['url'],'site':'出行与四季' if zh else 'Weekends & seasons','cover':photo.get('path',''),'cover_alt':loc(photo.get('alt',{}),lang),'cover_caption':loc(photo.get('caption',{}),lang)}
  if a['id']=='winter-clothing' and lang in ['en','zh']:meta['title']='起风的日子，出门前多准备一点' if zh else 'A few things to have ready before winter'
  body=loc(a['body'],lang)+'\n\n'+('## 出发前的小准备' if zh else '## Before you go')+'\n\n'+'\n'.join('- '+x for x in loc(a['steps'],lang))+'\n\n'+('## 来源与链接' if zh else '## Sources & links')+'\n\n'+links(loc(a['links'],lang))
  write(meta,body);count+=1

ends={'iowa-city-book-festival':'2026-10-25','iowa-city-farmers-market':'2026-10-31','iowa-city-holiday-markets':'2026-12-05','day-party':'2026-04-25','iowa-city-pride':'2026-06-20','downtown-block-party':'2026-06-27','iowa-city-jazz-festival':'2026-07-05','friday-night-concert-series':'2026-09-30'}
for a in data('events.js')['entries']:
 for lang in ['zh','en']:
  t=a[lang];i=lang=='en';meta={'lang':lang,'kind':'event','slug':a['id'],'category':'events','title':a['name'],'summary':t['summary'],'takeaway':t['title'],'edited':a['checked'],'checked':a['checked'],'site':a['name'],'url':a['url'],'cover':a.get('cover',''),'cover_alt':t.get('screenshotCaption',a['name']),'cover_caption':t.get('screenshotCaption',''),'cost':cost_map['events'][i],'login':'是否需报名，打开所选场次确认。' if lang=='zh' else 'Check the selected session for registration requirements.','event_end':ends.get(a['id'],''),'event_status':'past' if a['id']=='iowa-arts-festival' else '', 'event_label':t['season'],'tags':', '.join(a.get('tags',[]))}
  body='## '+('这一期的时间与地点' if lang=='zh' else 'Dates and places for this edition')+'\n\n'+t['season']+'\n\n'+t['where']+'\n\n'
  body+='## '+('怎么逛' if lang=='zh' else 'An idea for your visit')+'\n\n'+t['plan']+'\n\n'+t['details']+'\n\n'+('## 主办方与日程' if lang=='zh' else '## Organizer & program')+'\n\n'+links(a.get('sources',[]))
  write(meta,body);count+=1
(ROOT/'theme/aliases.json').write_text(json.dumps(aliases,ensure_ascii=False,indent=2))
(ROOT/'docs/import-record.json').write_text(json.dumps({'imported_on':TODAY,'source_deploy':'6ad93e88171202cdb1b2f0fe','markdown_files':count,'aliases':aliases,'note':'One-time data extraction. Future edits must use content/*.md; do not rerun this importer.'},ensure_ascii=False,indent=2))
print('Imported',count,'Markdown files;',len(aliases),'legacy aliases.')
