"""Genera las páginas de los tableros de claude.ai (TV y celular) en herramientas/artefactos/."""
import json, re, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); os.chdir(HERE)
OUT=os.path.join(HERE,'artefactos'); os.makedirs(OUT,exist_ok=True)
SP='vendor/'
t=open('template.html',encoding='utf-8').read()
data=json.load(open(os.path.join(ROOT,'data.json'),encoding='utf-8'))
mob_css=open('mobile.css',encoding='utf-8').read()
libs=''.join('<script>'+open(SP+f).read().replace('</script','<\\/script')+'</script>\n' for f in ['react.production.min.js','react-dom.production.min.js','htm.umd.js'])
guard='''<div id="boot-err" hidden style="position:fixed;left:16px;right:16px;top:16px;z-index:99;padding:16px;border-radius:8px;background:#7F1D1D;color:#FFFFFF;font:600 15px/1.4 system-ui,sans-serif"></div>
<script>
window.addEventListener('error',function(e){var b=document.getElementById('boot-err');if(b){b.hidden=false;b.textContent='No se pudo iniciar el tablero: '+(e.message||'error desconocido');}});
</script>
'''
t=re.sub(r'<script src="https://cdnjs[^"]+react\.production\.min\.js"></script>\n<script src="https://cdnjs[^"]+react-dom\.production\.min\.js"></script>\n<script src="https://unpkg\.com/htm@3\.1\.1/dist/htm\.umd\.js"></script>\n', lambda m: guard+libs, t)
t=t.replace("ReactDOM.createRoot(document.getElementById('app')).render(html`<${App}/>`);",
 "try { ReactDOM.createRoot(document.getElementById('app')).render(html`<${App}/>`); } catch (e) { var b=document.getElementById('boot-err'); b.hidden=false; b.textContent='No se pudo iniciar el tablero: '+e.message; }")
t=t.replace('/*__DATA__*/', json.dumps(data,ensure_ascii=False)).replace('/*__LOGO__*/', open('logo.datauri').read().strip())
open(os.path.join(OUT,'tv.html'),'w',encoding='utf-8').write(t)
m=t.replace('</style>', mob_css+'\n</style>',1).replace('<title>Tablero Informativo Aranzazu</title>','<title>Tablero Aranzazu Móvil</title>')
for a,b in [("style=${{ transform: `scale(${scale})` }}",""),("const v = Math.max(0.05, Math.min(w / 1920, h / 1080));","const v = 1;"),
 ("const wake = () => { setActive(true); document.body.classList.remove('idle'); clearTimeout(t); t = setTimeout(() => { setActive(false); document.body.classList.add('idle'); }, 4000); };","const wake = () => { setActive(true); };")]:
    assert a in m, a; m=m.replace(a,b)
open(os.path.join(OUT,'movil.html'),'w',encoding='utf-8').write(m)
print('ok', len(t), len(m))
