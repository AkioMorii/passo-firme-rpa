"""Gera figura BPMN simplificada e um arquivo BPMN 2.0 editável/importável."""
from __future__ import annotations
import shlex
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

nodes = {
    "start": ("startEvent", "Início"),
    "listar": ("task", "Buscar relatos via GET /relatos"),
    "fila": ("exclusiveGateway", "Há relatos novos?"),
    "validar": ("task", "Validar foto, GPS, classe e confiança"),
    "dados": ("exclusiveGateway", "Dados válidos?"),
    "duplicidade": ("exclusiveGateway", "Duplicado em 25 m / 48 h?"),
    "confianca": ("exclusiveGateway", "Confiança >= 0,65?"),
    "priorizar": ("task", "Calcular prioridade"),
    "consultar": ("task", "Consultar POST /assistente"),
    "recusa": ("exclusiveGateway", "Assistente recusou?"),
    "encaminhar": ("task", "PATCH: encaminhado + canal simulado"),
    "revisar": ("task", "PATCH: revisão humana"),
    "descartar": ("task", "PATCH: descartado"),
    "auditar": ("task", "Auditar resultado e tratar erros"),
    "end": ("endEvent", "Fim do lote"),
}

edges = [
    ("start", "listar", ""), ("listar", "fila", ""),
    ("fila", "end", "Não"), ("fila", "validar", "Sim"),
    ("validar", "dados", ""), ("dados", "revisar", "Não"),
    ("dados", "duplicidade", "Sim"), ("duplicidade", "descartar", "Sim"),
    ("duplicidade", "confianca", "Não"), ("confianca", "revisar", "Não"),
    ("confianca", "priorizar", "Sim"), ("priorizar", "consultar", ""),
    ("consultar", "recusa", ""), ("recusa", "revisar", "Sim"),
    ("recusa", "encaminhar", "Não"), ("encaminhar", "auditar", ""),
    ("revisar", "auditar", ""), ("descartar", "auditar", ""),
    ("auditar", "fila", "Próximo"),
]

style = '''digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.55", nodesep="0.5", ranksep="0.58", splines=polyline,
         fontname="DejaVu Sans", fontsize=15, label="Passo Firme | Fluxo de triagem (BPMN simplificado)", labelloc=t,
         dpi=170];
  node [fontname="DejaVu Sans", fontsize=11, color="#203449", fontcolor="#18354B", penwidth=1.7];
  edge [fontname="DejaVu Sans", fontsize=10, color="#526477", fontcolor="#526477", arrowsize=0.7];
'''
for key, (kind, label) in nodes.items():
    if kind == "startEvent":
        attrs = 'shape=circle, width=0.58, height=0.58, fixedsize=true, style="filled", fillcolor="#DFF7EE", color="#078E69", label=""'
    elif kind == "endEvent":
        attrs = 'shape=doublecircle, width=0.58, height=0.58, fixedsize=true, style="filled", fillcolor="#FFE5E2", color="#BE423D", label=""'
    elif kind == "exclusiveGateway":
        short_label = label.replace(' em ', '\\nem ').replace(' / ', '\\n/ ')
        attrs = f'shape=diamond, width=2.15, height=1.05, style="filled", fillcolor="#FEF2D8", color="#C77E18", label="{short_label}"'
    else:
        attrs = f'shape=box, style="rounded,filled", fillcolor="#EAF2FA", color="#286496", margin="0.20,0.14", label="{label}"'
    style += f'  {key} [{attrs}];\n'
for i, (a, b, label) in enumerate(edges):
    opts = f' [label="{label}", id="Flow_{i+1}"]' if label else f' [id="Flow_{i+1}"]'
    if a == "auditar" and b == "fila":
        opts = ' [label="Próximo", constraint=false, minlen=1]'
    style += f'  {a} -> {b}{opts};\n'
style += '''  {rank=same; revisar; descartar}
  note [shape=note, fontsize=10, color="#9BA8B6", fillcolor="#F5F8FB", style=filled,
    label="HTTP: até 3 tentativas em erros temporários.\\nFalha definitiva: auditoria e próximo item.\\nDados fictícios; sem acionamento real do SP156."];
  note -> auditar [style=dotted, arrowhead=none, constraint=false];
}
'''
dot_path = DOCS / "fluxo-rpa.dot"
dot_path.write_text(style, encoding="utf-8")
subprocess.run(["dot", "-Tpng", str(dot_path), "-o", str(ASSETS / "fluxo-bpmn.png")], check=True)
subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(ASSETS / "fluxo-bpmn.svg")], check=True)

# BPMN 2.0 com elementos e DI: geometricamente aproximado a partir do Graphviz.
plain = subprocess.check_output(["dot", "-Tplain", str(dot_path)], text=True)
parsed = {}
height = 20
for line in plain.splitlines():
    if not (line.startswith("graph ") or any(line.startswith(f"node {k} ") for k in nodes)):
        continue
    split = shlex.split(line)
    if not split:
        continue
    if split[0] == "graph":
        height = float(split[3])
    if split[0] == "node" and split[1] in nodes:
        _, nid, x, y, w, h = split[:6]
        parsed[nid] = (float(x), float(y), float(w), float(h))

ns = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
}
for k, url in ns.items():
    ET.register_namespace(k, url)

def Q(prefix, tag):
    return f"{{{ns[prefix]}}}{tag}"

def bpmn_id(k):
    return "Start_1" if k == "start" else "End_1" if k == "end" else f"Activity_{k}" if nodes[k][0] == "task" else f"Gateway_{k}"

root = ET.Element(Q("bpmn", "definitions"), {
    "id": "Definitions_PassoFirme", "targetNamespace": "https://passofirme.example/rpa",
    "exporter": "Passo Firme RPA", "exporterVersion": "1.0",
})
proc = ET.SubElement(root, Q("bpmn", "process"), {"id": "Process_Triagem", "name": "Triagem automática de relatos de calçada", "isExecutable": "false"})
for key, (kind, label) in nodes.items():
    ele = ET.SubElement(proc, Q("bpmn", kind), {"id": bpmn_id(key), "name": label})
    if kind == "startEvent" or kind == "endEvent":
        continue
for index, (a, b, label) in enumerate(edges, 1):
    attrs = {"id": f"Flow_{index}", "sourceRef": bpmn_id(a), "targetRef": bpmn_id(b)}
    if label:
        attrs["name"] = label
    ET.SubElement(proc, Q("bpmn", "sequenceFlow"), attrs)
for key in nodes:
    el = next(x for x in list(proc) if x.get("id") == bpmn_id(key))
    for index, (a, b, _) in enumerate(edges, 1):
        if b == key:
            ET.SubElement(el, Q("bpmn", "incoming")).text = f"Flow_{index}"
        if a == key:
            ET.SubElement(el, Q("bpmn", "outgoing")).text = f"Flow_{index}"

plane = ET.SubElement(ET.SubElement(root, Q("bpmndi", "BPMNDiagram"), {"id": "BPMNDiagram_1"}),
                     Q("bpmndi", "BPMNPlane"), {"id": "BPMNPlane_1", "bpmnElement": "Process_Triagem"})
for key in nodes:
    x, y, w, h = parsed[key]
    ET.SubElement(ET.SubElement(plane, Q("bpmndi", "BPMNShape"),
                                {"id": f"Shape_{key}", "bpmnElement": bpmn_id(key)}),
                  Q("dc", "Bounds"), {"x": str((x-w/2)*96+50), "y": str((height-y-h/2)*96+50), "width": str(w*96), "height": str(h*96)})
for index, (a, b, _) in enumerate(edges, 1):
    edge = ET.SubElement(plane, Q("bpmndi", "BPMNEdge"),
                         {"id": f"Edge_{index}", "bpmnElement": f"Flow_{index}"})
    x1, y1, _, _ = parsed[a]; x2, y2, _, _ = parsed[b]
    for x, y in [(x1, y1), (x2, y2)]:
        ET.SubElement(edge, Q("di", "waypoint"), {"x": str(x*96+50), "y": str((height-y)*96+50)})
ET.indent(root, space="  ")
ET.ElementTree(root).write(DOCS / "fluxo-rpa.bpmn", encoding="utf-8", xml_declaration=True)
print("Fluxograma BPMN (PNG/SVG + XML) salvo.")
