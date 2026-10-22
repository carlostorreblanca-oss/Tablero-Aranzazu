import json, re
import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); os.chdir(HERE)
SP='vendor/'
t=open('template.html',encoding='utf-8').read()
data=json.load(open(os.path.join(ROOT,'data.json'),encoding='utf-8'))
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
web_redirect='<script>try{if(Math.min(screen.width,innerWidth)<760&&!/[?&]tv/.test(location.search))location.replace("movil.html")}catch(e){}</script>\n'
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(t)
print('ok', len(t))
# Envoltura HTML completa para publicar fuera de claude.ai (GitHub Pages)
HEAD='<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
for fn in ('index.html',):
    p=os.path.join(ROOT,fn); s=open(p,encoding='utf-8').read()
    open(p,'w',encoding='utf-8').write(HEAD+s+'\n</html>\n')
