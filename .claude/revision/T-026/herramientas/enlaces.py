import re,os,sys,urllib.parse,glob
root=sys.argv[1]
files=glob.glob(root+'/entregables/**/*.md',recursive=True)+glob.glob(root+'/entregables/**/*.html',recursive=True)+[root+'/README.md',root+'/exportados/README.md']
pat_md=re.compile(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
pat_html=re.compile(r'(?:src|href)="([^"]+)"')
bad=0
for f in sorted(files):
    txt=open(f,encoding='utf-8',errors='ignore').read()
    for i,line in enumerate(txt.splitlines(),1):
        for m in list(pat_md.finditer(line))+list(pat_html.finditer(line)):
            u=m.group(1).strip('<>')
            if re.match(r'^(https?:|mailto:|#|data:|tel:)',u): continue
            p=urllib.parse.unquote(u.split('#')[0].split('?')[0])
            if not p: continue
            full=os.path.normpath(os.path.join(os.path.dirname(f),p))
            if not os.path.exists(full):
                bad+=1; print(f"{os.path.relpath(f,root)}:{i}: {u}")
print("ROTOS:",bad)
