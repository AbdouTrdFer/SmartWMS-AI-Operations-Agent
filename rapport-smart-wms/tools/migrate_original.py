"""One-time, auditable PDF-to-LaTeX migration. Does not inspect application code."""
from pathlib import Path
import json
import re
import shutil
import sys
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4_Organise_Professionnel.pdf'

def clean(text):
    text = text.replace('\u00ad', '').replace('\uf0b7', '•')
    text = re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '-', text)
    return re.sub(r'\s+', ' ', text).strip()

def tex(text):
    text = clean(text)
    text = text.replace('L’assessment', 'L’analyse des besoins')
    text = text.replace('données maître', 'données de référence')
    text = text.replace('supporte des objets', 'prend en charge des objets')
    text = text.replace('use cases', 'cas d’usage').replace('use case', 'cas d’usage')
    text = text.replace('—', ' : ').replace('→', '§ARROW§')
    for a,b in [('&',r'\&'),('%',r'\%'),('#',r'\#'),('_',r'\_')]: text=text.replace(a,b)
    text = text.replace('§ARROW§',r'\(\rightarrow\)')
    text = re.sub(r'\[(\d+)\][–-]\[(\d+)\]',lambda m:r'\cite{'+','.join('ref'+str(n) for n in range(int(m[1]),int(m[2])+1))+'}',text)
    text = re.sub(r'\[(\d+)\]',lambda m:r'\cite{ref'+m[1]+'}',text)
    return text

TABLES = [
 ('sat',[(7,0)],'Domaines d’intervention de SAT et liens avec le stage',[.23,.33,.44]),
 ('perimetre',[(9,0)],'Périmètre et limites du stage',[.5,.5]),
 ('livrables',[(9,1),(10,0)],'Livrables et résultats attendus',[.32,.68]),
 ('socle',[(15,0),(16,0)],'Socle fonctionnel commun aux trois solutions étudiées',[.27,.13,.13,.13,.34]),
 ('comparaison',[(16,1),(17,0)],'Différenciateurs observés dans le benchmark',[.2,.27,.26,.27]),
 ('problemes',[(19,0)],'Problèmes, contraintes et orientations par domaine',[.18,.29,.25,.28]),
 ('reception',[(19,1),(20,0)],'Cas d’usage de réception',[.13,.36,.18,.33]),
 ('stockage',[(20,1)],'Cas d’usage de stockage et d’inventaire',[.13,.36,.18,.33]),
 ('expedition',[(20,2),(21,0)],'Cas d’usage de commandes et d’expédition',[.13,.36,.18,.33]),
 ('yard',[(21,1)],'Cas d’usage de gestion de la cour et des quais',[.13,.36,.18,.33]),
 ('ressources',[(21,2),(22,0)],'Cas d’usage des ressources et infrastructures',[.16,.33,.18,.33]),
 ('transversal',[(22,1)],'Familles de cas d’usage transversaux',[.22,.22,.36,.20]),
 ('classification',[(23,0)],'Classification et conditions d’activation par domaine',[.17,.23,.22,.22,.16]),
 ('responsabilites',[(28,0)],'Responsabilités des blocs de l’architecture fonctionnelle',[.23,.40,.37]),
 ('activation',[(30,0)],'Conditions d’activation des capacités Smart et Optional',[.22,.14,.35,.29]),
]

FIGURES = {
 5:('fil_conducteur','Fil conducteur de la transformation vers le Smart WMS.'),
 6:('sat','Positionnement de SAT, synthèse du document de présentation cité dans le rapport initial.'),
 12:('marche','Paysage concurrentiel reproduit du support de benchmark fourni pendant le stage. Attribution et millésime à confirmer.'),
 13:('manhattan','Lecture fonctionnelle de Manhattan Active : plateforme et exécution unifiée. Synthèse du benchmark.'),
 14:('sap','Lecture fonctionnelle de SAP EWM : processus et objets métier. Synthèse du benchmark.'),
 15:('oracle','Orchestration des commandes et des tâches dans Oracle WMS. Reconstruction fonctionnelle du benchmark.'),
 16:('comparaison','Apports complémentaires des trois solutions à la conception du Smart WMS.'),
 18:('scan_plan_act','Démarche SCAN, PLAN et ACT appliquée au stage de conception.'),
 23:('classification','Classification des capacités et vérification de leurs conditions d’activation.'),
 26:('architecture','Architecture fonctionnelle détaillée du Smart WMS.'),
 27:('architecture_detail','Systèmes externes, cœur opérationnel, tâches et données.'),
 29:('support_detail','Ressources, intelligence et appareils de terrain.'),
 30:('activation','Socle commun et activation des capacités selon les besoins, les données et l’infrastructure.'),
}

def main():
    archive=ROOT/'archive'/'version_abregee'
    if not archive.exists():
        archive.mkdir(parents=True)
        for name in ['main.tex','config','chapters','bibliography','README.md','CORRECTIONS.md']:
            p=ROOT/name
            if p.is_dir(): shutil.copytree(p,archive/name)
            elif p.exists(): shutil.copy2(p,archive/name)
        shutil.copy2(ROOT/'build'/'Rapport_Stage_FERHAN_Abdelali_Smart_WMS_Revu.pdf',archive/'apercu_14_pages.pdf')
    for name in ['tables','figures/revision','audit/migration','chapters/revision']:
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    d=pymupdf.open(SOURCE)
    detected={i+1:p.find_tables().tables for i,p in enumerate(d)}
    table_starts={}; exclusions={}; manifest={'source':SOURCE.name,'sections':[],'tables':[],'figures':[],'paragraphs':[]}
    for name,locations,caption,widths in TABLES:
        rows=[]
        for n,(page,idx) in enumerate(locations):
            t=detected[page][idx]
            data=[[clean(c or '') for c in row] for row in t.extract()]
            exclusions.setdefault(page,[]).append(t.bbox)
            if n and name=='comparaison':
                rows[-1]=[clean(a+' '+b) for a,b in zip(rows[-1],data[-1])]
            else: rows.extend(data if n==0 or name=='livrables' else data[1:])
        if name=='livrables': rows.insert(0,['Livrable','Contenu attendu'])
        table_starts[locations[0]]=(name,caption)
        spec='@{}'+''.join('P{'+f'{w:.3f}'+r'\TableWidth}' for w in widths)+'@{}'
        lines=[r'\begingroup',r'\small\setlength{\tabcolsep}{4pt}',r'\setlength{\TableWidth}{\dimexpr\linewidth-'+str(8*(len(widths)-1))+r'pt\relax}',r'\begin{longtable}{'+spec+'}',r'\caption{'+tex(caption)+r'}\label{tab:'+name+r'}\\',r'\toprule']
        header=' & '.join(r'\textbf{'+tex(c)+'}' for c in rows[0])+r' \\'
        lines += [header,r'\midrule\endfirsthead',r'\multicolumn{'+str(len(widths))+r'}{l}{\small\itshape Tableau \thetable{} (suite)}\\',r'\toprule',header,r'\midrule\endhead',r'\midrule\multicolumn{'+str(len(widths))+r'}{r}{\small\itshape Suite à la page suivante}\\\endfoot',r'\bottomrule\endlastfoot']
        lines += [' & '.join(tex(c).removeprefix('• ') for c in row)+r' \\[3pt]' for row in rows[1:]]
        lines += [r'\end{longtable}',r'\endgroup']
        (ROOT/'tables'/f'{name}.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        manifest['tables'].append({'id':name,'source_pages':[x[0] for x in locations],'rows':len(rows)-1,'cells':rows})
    events=[]
    for pi in range(3,30):
        page=pi+1; p=d[pi]; local=[]
        for idx,t in enumerate(detected[page]):
            if (page,idx) in table_starts:
                name,caption=table_starts[(page,idx)]
                local.append((t.bbox[1],{'kind':'table','id':name,'page':page}))
        for b in p.get_text('dict')['blocks']:
            if b['type']==1:
                if page in FIGURES:
                    name,caption=FIGURES[page]
                    local.append((b['bbox'][1],{'kind':'figure','id':name,'caption':caption,'page':page}))
                    manifest['figures'].append({'id':name,'source_page':page})
                    if name=='marche':
                        (ROOT/'figures/revision/marche.png').write_bytes(b['image'])
                continue
            text=clean('\n'.join(''.join(s['text'] for s in l['spans']) for l in b['lines']))
            if not text or text.startswith(('RAPPORT DE STAGE','Page ','CHAPITRE','Figure ','Tableau ','Références ')) or re.match(r'^\[\d+\]',text): continue
            center=(b['bbox'][1]+b['bbox'][3])/2
            if any(box[1]-1<=center<=box[3]+1 for box in exclusions.get(page,[])): continue
            if text=='Domaines d’intervention particulièrement liés au stage': continue
            kind='paragraph'
            if re.match(r'^[1-4]\.\d+ ',text): kind='section'
            elif re.match(r'^[1-4]\. ',text): kind='chapter'
            elif text=='Introduction générale': kind='intro'
            elif text.startswith('Problématique directrice'): kind='problem';text=text.removeprefix('Problématique directrice').strip()
            elif text=='Question centrale du stage':continue
            elif text.startswith('•'):kind='item';text=text.removeprefix('•').strip()
            local.append((b['bbox'][1],{'kind':kind,'text':text,'page':page}))
        events.extend(e for y,e in sorted(local,key=lambda x:x[0]))
    # Rejoin paragraphs split by a source page break or a centered explanatory block.
    merged=[]
    for e in events:
        if merged and e['kind']=='paragraph' and merged[-1]['kind']=='paragraph' and not re.search(r'[.!?:;»]$',merged[-1]['text']):
            merged[-1]['text']+=' '+e['text']
        else: merged.append(e)
    out={0:[]};chapter=0; inlist=False
    for e in merged:
        kind=e['kind']; text=e.get('text','')
        if kind!='item' and inlist:out[chapter].append(r'\end{itemize}');inlist=False
        if kind=='intro':out[0]+=[r'\chapter*{Introduction générale}',r'\addcontentsline{toc}{chapter}{Introduction générale}',r'\markboth{Introduction générale}{}']
        elif kind=='chapter':
            chapter=int(text[0]);out[chapter]=[r'\chapter{'+tex(text[3:])+'}',r'\label{chap:'+str(chapter)+'}']
        elif kind=='section':
            sid,title=text.split(' ',1)
            out[chapter]+=[f'% Original : page {e["page"]}, section {sid}',r'\section{'+tex(title)+'}',r'\label{sec:'+sid+'}']
            manifest['sections'].append({'id':sid,'title':title,'source_page':e['page']})
        elif kind=='table':out[chapter].append(r'\input{tables/'+e['id']+'}')
        elif kind=='figure':
            name=e['id']
            if name=='architecture':out[chapter].append(r'\input{figures/revision/architecture_pages}')
            elif name in ('architecture_detail','support_detail'):out[chapter].append(r'\input{figures/revision/'+name+'_page}')
            else:out[chapter].append(r'\reportfigure{'+name+'}{'+tex(e['caption'])+'}')
        elif kind=='problem':out[chapter].append(r'\begin{problematique}'+tex(text)+r'\end{problematique}')
        elif kind=='item':
            if not inlist:out[chapter].append(r'\begin{itemize}');inlist=True
            out[chapter].append(r'\item '+tex(text))
        else:
            out[chapter].append(tex(text)+'\n')
            manifest['paragraphs'].append({'chapter':chapter,'source_page':e['page'],'text':text})
    for i,lines in out.items():
        if '--refresh-chapter4' in sys.argv and i!=4: continue
        (ROOT/'chapters/revision'/f'{i:02d}.tex').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    (ROOT/'audit/migration/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Migrated',len(manifest['sections']),'sections,',len(manifest['paragraphs']),'paragraphs,',len(TABLES),'tables and',len(manifest['figures']),'figures.')

if __name__=='__main__':main()
