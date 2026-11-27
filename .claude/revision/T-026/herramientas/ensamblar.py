"""Ensambla HALLAZGOS.md a partir de hallazgos/*.md y comprueba capturas y estados (T-026)."""
import re, os, sys, collections
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
orden=["S01","S02","S03-04","S05","S06-restauracion","S06","S09","S10","S11","S12","S13","TRANSVERSAL"]
frag={o:open(f"{B}/hallazgos/{o}.md",encoding="utf-8").read() for o in orden}
cont=collections.OrderedDict(); problemas=[]; filas=[]
for o in orden:
    sem={"S06-restauracion":"S06","TRANSVERSAL":"Transversal"}.get(o,o)
    for m in re.finditer(r"^### (H-\d{3}) · (\w+) · (.+?)$(.*?)(?=^### |^## |\Z)", frag[o], re.S|re.M):
        hid,sev,tit,cuerpo=m.groups()
        e=re.search(r"\*\*Estado:\*\*\s*([^\n]+)",cuerpo); est=e.group(1).strip() if e else "?"
        tipo="Cerrado" if est.startswith("Cerrado") else ("Pendiente" if est.lower().startswith("pendiente") else "?")
        if tipo=="?": problemas.append(f"{hid}: estado no reconocido «{est[:40]}»")
        a=f"{B}/capturas/{hid}_antes.png"; d=f"{B}/capturas/{hid}_despues.png"
        if not os.path.exists(a) or os.path.getsize(a)<2000: problemas.append(f"{hid}: falta captura antes")
        if tipo=="Cerrado" and (not os.path.exists(d) or os.path.getsize(d)<2000): problemas.append(f"{hid}: Cerrado sin captura después")
        c=cont.setdefault(sem,{"Cerrado":0,"Pendiente":0,"ids_p":[]}); c[tipo]=c.get(tipo,0)+1
        if tipo=="Pendiente": c["ids_p"].append(hid)
        filas.append((hid,sem,sev,tit.strip(),tipo))
ids=[f[0] for f in filas]; dup=[i for i in set(ids) if ids.count(i)>1]
if dup: problemas.append(f"IDs duplicados: {dup}")
if "--comprobar" in sys.argv:
    for k,v in cont.items(): print(k, v)
    print("TOTAL", len(filas), "cerrados", sum(v["Cerrado"] for v in cont.values()), "pendientes", sum(v["Pendiente"] for v in cont.values()))
    print("PROBLEMAS:", problemas or "ninguno"); sys.exit(1 if problemas else 0)
cab=open(f"{B}/herramientas/cabecera_hallazgos.md",encoding="utf-8").read()
idx=["| ID | Semana | Severidad | Hallazgo | Estado |","| --- | --- | --- | --- | --- |"]+[f"| [{h}](#{h.lower()}) | {s} | {sv} | {t} | {e} |" for h,s,sv,t,e in filas]
out=cab.replace("{{INDICE}}","\n".join(idx)).replace("{{TOTALES}}",f"{len(filas)} hallazgos: {sum(1 for f in filas if f[4]=='Cerrado')} cerrados y {sum(1 for f in filas if f[4]=='Pendiente')} pendientes justificados")
cuerpo="\n\n".join(re.sub(r"\]\(\.\./capturas/","](capturas/",re.sub(r"\]\(\.\./requisitos/","](requisitos/",frag[o])).strip() for o in orden)
open(f"{B}/HALLAZGOS.md","w",encoding="utf-8").write(out+"\n\n"+cuerpo+"\n")
print("HALLAZGOS.md escrito:",len(filas))
