"""Diagrama BPMN ilustrativo em SVG/PNG e arquivo BPMN 2.0 (não executável)."""
from pathlib import Path
import subprocess, shlex
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
N={
 'ini':('startEvent','Início'),
 'listar':('task','GET /relatos\n(status=recebido)'),
 'prox':('exclusiveGateway','Há relato?'),
 'validar':('task','Validar GPS e\ndetecção'),
 'valido':('exclusiveGateway','Válido?'),
 'duplicado':('exclusiveGateway','Duplicado?\n25m/48h'),
 'confianca':('exclusiveGateway','Confiança\n>= 0,65?'),
 'priorizar':('task','Prioridade 1-5'),
 'consultar':('task','POST /assistente'),
 'fundamento':('exclusiveGateway','Responsável e\nfonte válidos?'),
 'def_revisao':('task','Definir\nrevisao_humana'),
 'def_descartar':('task','Definir\ndescartado'),
 'def_encaminhar':('task','Definir\nencaminhado'),
 'decidir':('exclusiveGateway','Aplicar?'),
 'status':('exclusiveGateway','Qual status?'),
 'triagem':('task','PATCH:\nem_triagem'),
 'encaminhar':('task','PATCH:\nencaminhado'),
 'revisao':('task','PATCH:\nrevisao_humana'),
 'descartar':('task','PATCH:\ndescartado'),
 'planejar':('task','Dry-run:\nsem PATCH'),
 'auditar':('task','Log de auditoria\n+ próximo item'),
 'fim':('endEvent','Fim'),
}
E=[
 ('ini','listar',''),('listar','prox',''),('prox','fim','não'),('prox','validar','sim'),
 ('validar','valido',''),('valido','def_revisao','não'),('valido','duplicado','sim'),
 ('duplicado','def_descartar','sim'),('duplicado','confianca','não'),
 ('confianca','def_revisao','não'),('confianca','priorizar','sim'),
 ('priorizar','consultar',''),('consultar','fundamento',''),
 ('fundamento','def_revisao','não'),('fundamento','def_encaminhar','sim'),
 ('def_revisao','decidir',''),('def_descartar','decidir',''),('def_encaminhar','decidir',''),
 ('decidir','status','sim'),('decidir','planejar','não'),
 ('status','triagem','encaminhar'),('status','revisao','revisão'),('status','descartar','descartar'),
 ('triagem','encaminhar',''),('encaminhar','auditar',''),
 ('revisao','auditar',''),('descartar','auditar',''),('planejar','auditar',''),
 ('auditar','prox','próximo'),
]
# Os destinos são decididos antes da escolha entre executar PATCH e apenas simular.
DOT='''digraph BPMN {
 graph [rankdir=TB, bgcolor="white", pad="0.35", nodesep="0.43", ranksep="0.5", splines=ortho,
       fontname="DejaVu Sans", fontsize=18, label="PASSO FIRME | Triagem automatizada (BPMN simplificado)", labelloc=t, labelfontcolor="#163149"];
 node [fontname="DejaVu Sans", fontsize=11.0, fontcolor="#153249", color="#385B74", penwidth=1.4];
 edge [fontname="DejaVu Sans", fontsize=9.5, color="#5B7180", fontcolor="#5B7180", arrowsize=0.65];
'''
for id,(tipo,rotulo) in N.items():
 if tipo=='startEvent': attrs='shape=circle, width=0.48, height=0.48, fixedsize=true, label="", style=filled, fillcolor="#DFF6E8", color="#0A8A60"'
 elif tipo=='endEvent': attrs='shape=doublecircle, width=0.5, height=0.5, fixedsize=true, label="", style=filled, fillcolor="#FFE7E3", color="#B5433B"'
 elif tipo=='exclusiveGateway': attrs=f'shape=diamond, style=filled, fillcolor="#FFF5E0", color="#C28320", width=1.8, height=0.75, label="{rotulo}"'
 else: attrs=f'shape=box, style="rounded,filled", fillcolor="#E9F1F8", color="#27618A", margin="0.18,0.13", label="{rotulo}"'
 DOT+=f' {id} [{attrs}];\n'
for a,b,label in E:
 attrs=[]
 if label: attrs.append(f'label="{label}"')
 if a=='auditar' and b=='prox': attrs+=['constraint=false','minlen=1','style=dashed','color="#508E7F"']
 DOT+=f' {a} -> {b}'+(' ['+', '.join(attrs)+']' if attrs else '')+';\n'
DOT+='''
 {rank=same; revisao; descartar; planejar}
 notas [shape=note, style=filled, fillcolor="#F6F9FC", color="#B2C1C9", fontsize=9,
  label="Fluxo com repetição por lote, decisão e exceções.\\nGateway 'Aplicar?' protege o banco no modo dry-run.\\nFalhas HTTP: tentativas com espera, registro em auditoria; item seguinte.\\nNão cria chamados oficiais SP156."];
 notas -> auditar [style=dotted, arrowhead=none, constraint=false];
}
'''
(rootdot:=ROOT/'docs/fluxo-bpmn-atualizado.dot').write_text(DOT,encoding='utf-8')
for ext in ('png','svg'):
 subprocess.run(['dot',f'-T{ext}',str(rootdot),'-o',str(ROOT/f'assets/fluxo-bpmn-atualizado.{ext}')],check=True)
plain=subprocess.check_output(['dot','-Tplain',str(rootdot)],text=True)
parsed={}; height=20
for l in plain.splitlines():
 if l.startswith('graph '): height=float(shlex.split(l)[3])
 for id in N:
  if l.startswith(f'node {id} '):
   s=l.split(); parsed[id]=tuple(float(x) for x in s[2:6]); break
ns={'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL','bpmndi':'http://www.omg.org/spec/BPMN/20100524/DI','dc':'http://www.omg.org/spec/DD/20100524/DC','di':'http://www.omg.org/spec/DD/20100524/DI'}
for p,u in ns.items():ET.register_namespace(p,u)
q=lambda pre,tag: f'{{{ns[pre]}}}{tag}'
ID=lambda id: 'Start_1' if id=='ini' else 'End_1' if id=='fim' else ('Gateway_' if N[id][0]=='exclusiveGateway' else 'Activity_')+id
r=ET.Element(q('bpmn','definitions'),{'id':'Definitions_PassoFirme_v0','targetNamespace':'https://passofirme.local/rpa'})
proc=ET.SubElement(r,q('bpmn','process'),{'id':'Process_Triagem_v0','isExecutable':'false','name':'Triagem automatizada - API v0'})
for id,(tipo,rotulo) in N.items():ET.SubElement(proc,q('bpmn',tipo),{'id':ID(id),'name':rotulo.replace('\n',' ')})
for n,(a,b,label) in enumerate(E,1):
 attrs={'id':f'Flow_{n}','sourceRef':ID(a),'targetRef':ID(b)}
 if label:attrs['name']=label
 ET.SubElement(proc,q('bpmn','sequenceFlow'),attrs)
for id in N:
 e=next(x for x in list(proc) if x.get('id')==ID(id))
 for n,(a,b,_) in enumerate(E,1):
  if b==id:ET.SubElement(e,q('bpmn','incoming')).text=f'Flow_{n}'
  if a==id:ET.SubElement(e,q('bpmn','outgoing')).text=f'Flow_{n}'
plane=ET.SubElement(ET.SubElement(r,q('bpmndi','BPMNDiagram'),{'id':'Diagram_1'}),q('bpmndi','BPMNPlane'),{'id':'Plane_1','bpmnElement':'Process_Triagem_v0'})
for id,(x,y,w,h) in parsed.items():
 el=ET.SubElement(plane,q('bpmndi','BPMNShape'),{'id':f'Shape_{id}','bpmnElement':ID(id)})
 ET.SubElement(el,q('dc','Bounds'),{'x':f'{(x-w/2)*85+30:.2f}','y':f'{(height-y-h/2)*85+30:.2f}','width':f'{w*85:.2f}','height':f'{h*85:.2f}'})
for n,(a,b,_) in enumerate(E,1):
 el=ET.SubElement(plane,q('bpmndi','BPMNEdge'),{'id':f'Edge_{n}','bpmnElement':f'Flow_{n}'})
 for id in (a,b):
  x,y,_,_=parsed[id];ET.SubElement(el,q('di','waypoint'),{'x':f'{x*85+30:.2f}','y':f'{(height-y)*85+30:.2f}'})
ET.indent(r,space='  ')
ET.ElementTree(r).write(ROOT/'docs/fluxo-bpmn-atualizado.bpmn',encoding='utf-8',xml_declaration=True)
print('gerado',ROOT/'assets/fluxo-bpmn-atualizado.png')
