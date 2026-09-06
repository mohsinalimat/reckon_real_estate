from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import hashlib, json, re
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
REF = Path(r'C:/Users/User/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.1/skills/artifact-template-system-design/assets/reference.docx')
OUT = ROOT / 'docs/Reckon_Real_Estate_Implementation_and_User_Manual.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
def q(x): return '{%s}%s' % (W,x)
def text(el): return ''.join(el.itertext()) if False else ''.join(el.xpath('.//w:t/text()',namespaces=NS))
def replace_text(el, value):
    props = deepcopy(el.find(q('pPr')))
    runs = el.findall(q('r'))
    rp = deepcopy(runs[0].find(q('rPr'))) if runs else None
    for c in list(el): el.remove(c)
    if props is not None: el.append(props)
    run = E.SubElement(el,q('r'))
    if rp is not None: run.append(rp)
    t=E.SubElement(run,q('t')); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); t.text=value
    return el
def xml(el): return E.tostring(el,encoding='UTF-8',xml_declaration=True,standalone=True)

with ZipFile(REF) as z: parts={n:z.read(n) for n in z.namelist()}
inventory={'reference_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'parts':{n:hashlib.sha256(b).hexdigest() for n,b in parts.items()}}
(WORK/'template_inventory.json').write_text(json.dumps(inventory,indent=2))
doc=E.fromstring(parts['word/document.xml']); body=doc.find(q('body'))
paras=body.findall(q('p')); tables=body.findall(q('tbl'))
normal=deepcopy(paras[22]); heading=deepcopy(paras[21]); sub=deepcopy(paras[35]); caption=deepcopy(paras[33])
table_proto=deepcopy(tables[5]); sect=deepcopy(body.find(q('sectPr')))
# Preserve the exact cover components and their positioning.
cover=[]
for el in body:
    if el is paras[21]: break
    cover.append(deepcopy(el))
for el in cover:
    if el.tag==q('p'):
        if text(el)=='System Name': replace_text(el,'Reckon Real Estate')
        elif text(el)=='Title of Proposal': replace_text(el,'User Manual')
    elif el.tag==q('tbl'):
        for p in el.xpath('.//w:p',namespaces=NS):
            t=text(p)
            mappings={'[Draft / Proposed / Approved]':'Reference edition 1.0','OWNER':'AUDIENCE','[Team Name]':'Implementation and operations','[Month, DD, YYYY]':'5 September 2026','Authors':'Purpose','[Name(s)]':'Step by step setup and user reference','Reviewers':'Readers','[Reviewer names, roles, or groups]':'Administrators, sales, accounts, construction and service teams','Related docs':'Verification','[Link to related docs]':'Checked against source code; live site acceptance testing required','Scope':'Coverage','[One-sentence description of what this design covers]':'Property, sales, collections, construction, land, handover and after sales'}
            if t in mappings: replace_text(p,mappings[t])
for el in list(body): body.remove(el)
for el in cover: body.append(el)

def p(value,proto=normal):
    el=replace_text(deepcopy(proto),value)
    pp=el.find(q('pPr'))
    if pp is None: pp=E.Element(q('pPr'));el.insert(0,pp)
    for name in ['numPr','pageBreakBefore']:
        node=pp.find(q(name))
        if node is not None:pp.remove(node)
    # The copied prose may carry a footnote reference; replace_text removes it.
    body.append(el);return el
def page_heading(value,index):
    el=p(value,heading);pp=el.find(q('pPr'));E.SubElement(pp,q('pageBreakBefore'))
    # Explicit bookmarks make chapters addressable while retaining source styles.
    bm=E.SubElement(el,q('bookmarkStart'));bm.set(q('id'),str(100+index));bm.set(q('name'),'manual_'+str(index))
    be=E.SubElement(el,q('bookmarkEnd'));be.set(q('id'),str(100+index))
def table(lines):
    rows=[[c.strip() for c in s.strip('|').split('|')] for s in lines]
    rows=[r for r in rows if not all(re.fullmatch('[-: ]+',c) for c in r)]
    t=deepcopy(table_proto)
    proto_rows=t.findall(q('tr'))
    for r in proto_rows:t.remove(r)
    cols=len(rows[0]); widths=([3000,7224] if cols==2 else [3000]*cols)
    grid=t.find(q('tblGrid'))
    for c in list(grid):grid.remove(c)
    for width in widths:E.SubElement(grid,q('gridCol')).set(q('w'),str(width))
    for i,values in enumerate(rows):
        row=deepcopy(proto_rows[0 if i==0 else 1+(i-1)%2])
        cells=row.findall(q('tc'))
        for c in cells:row.remove(c)
        trp=row.find(q('trPr'))
        if trp is None:trp=E.Element(q('trPr'));row.insert(0,trp)
        E.SubElement(trp,q('cantSplit'))
        if i==0 and trp.find(q('tblHeader')) is None:E.SubElement(trp,q('tblHeader'))
        for j,value in enumerate(values):
            cell=deepcopy(cells[min(j,len(cells)-1)])
            cp=cell.find(q('tcPr'));tw=cp.find(q('tcW'))
            if tw is not None:tw.set(q('w'),str(widths[j]))
            cps=cell.findall(q('p'));cp0=replace_text(cps[0],value)
            for c in cps[1:]:cell.remove(c)
            row.append(cell)
        t.append(row)
    body.append(t)
    p('')

lines=(ROOT/'docs/reckon-real-estate-user-manual.md').read_text(encoding='utf-8').splitlines()
i=0;chapter=0
while i<len(lines):
    line=lines[i]
    if not line.strip(): i+=1;continue
    if line.startswith('# '):page_heading(line[2:],chapter);chapter+=1
    elif line.startswith('## '):p(line[3:],sub)
    elif line.startswith('|'):
        group=[]
        while i<len(lines) and lines[i].startswith('|'):group.append(lines[i]);i+=1
        table(group);continue
    elif line.startswith('SS'):
        el=p('Screenshot placeholder '+line,caption)
        pp=el.find(q('pPr'));sp=pp.find(q('spacing'))
        if sp is not None:sp.set(q('after'),'100')
    elif line.startswith('CODE '):
        el=p(line[5:]);r=el.find(q('r'));rp=r.find(q('rPr'))
        if rp is None:rp=E.SubElement(r,q('rPr'))
        rf=rp.find(q('rFonts'))
        if rf is None:rf=E.SubElement(rp,q('rFonts'))
        rf.set(q('ascii'),'Consolas');rf.set(q('hAnsi'),'Consolas')
        sz=rp.find(q('sz'))
        if sz is None:sz=E.SubElement(rp,q('sz'))
        sz.set(q('val'),'18')
    else:p(line)
    i+=1
body.append(sect)
parts['word/document.xml']=xml(doc)
for name,data in list(parts.items()):
    if re.fullmatch(r'word/footer\d+\.xml',name):
        f=E.fromstring(data)
        for para in f.xpath('.//w:p',namespaces=NS):
            if '[Organization Name]' in text(para):
                replace_text(para,'Reckon Real Estate | User Manual | ')
                field=E.SubElement(para,q('fldSimple'));field.set(q('instr'),'PAGE')
                r=E.SubElement(field,q('r'));E.SubElement(r,q('t')).text='1'
        parts[name]=xml(f)
OUT.parent.mkdir(exist_ok=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
allowed={'word/document.xml'}|{n for n in parts if re.fullmatch(r'word/footer\d+\.xml',n)}
assert all(hashlib.sha256(parts[n]).hexdigest()==h for n,h in inventory['parts'].items() if n not in allowed)
assert E.tostring(sect)==E.tostring(E.fromstring(parts['word/document.xml']).find('w:body/w:sectPr',NS))
assert hashlib.sha256(REF.read_bytes()).hexdigest()==inventory['reference_sha256']
print(OUT)
print('Chapters including navigation:',chapter,'Preserved package parts:',len(parts)-len(allowed))
