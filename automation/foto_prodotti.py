# -*- coding: utf-8 -*-
"""Foto prodotto mancanti con gemini_auto\img.py (soggetto auto dal nome/descrizione EN), colleg ate al catalogo + push.
Uso: python automation/foto_prodotti.py [--no-push] [id ...]   (senza id = tutti quelli senza foto). Account: env GEMINI_ACCOUNT=3"""
import csv, json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(R, '_data', 'catalogo.json')
OUT = os.path.join(R, 'assets', 'images', 'prodotti')
IMG = r'C:\Users\mirco\Desktop\gemini_auto\img.py'
EXTRA = ('ABSOLUTELY NO TEXT of any kind: no letters, no numbers, no words, no dates, no logos, no brand names. '
         'Labels, boxes and packaging must be completely blank. Language-neutral. Plain pure white #FFFFFF background, soft shadow, studio product photo.')

def sogg(p):
    en = p.get('tr', {}).get('en', {})
    return 'Italian Calabrian food product photo: %s. %s. Rustic, appetizing, centered.' % (en.get('nome') or p['nome'], (en.get('descrizione') or p.get('descrizione', ''))[:160])

def sh(*a):
    return subprocess.run(a, cwd=R, capture_output=True, text=True, encoding='utf-8', errors='replace')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    push = '--no-push' not in sys.argv
    d = json.load(open(CAT, encoding='utf-8-sig'))
    prod = d['prodotti']
    os.makedirs(OUT, exist_ok=True)
    todo = [p['id'] for p in prod if (p['id'] in args if args else not p.get('immagine'))]
    todo = [i for i in todo if args or not os.path.exists(os.path.join(OUT, i + '.webp'))]
    print('da generare:', len(todo), todo)
    if todo:
        lista = os.path.join(R, 'automation', 'tmp_lista.csv')
        with open(lista, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f, delimiter=';')
            for p in prod:
                if p['id'] in todo: w.writerow([p['id'], sogg(p), 'prodotto'])
        r = subprocess.run([sys.executable, IMG, '--lista', lista, '--out', OUT, '--extra', EXTRA], cwd=R, text=True, encoding='utf-8', errors='replace')
        print('img.py exit', r.returncode)
    ok = []
    for p in prod:
        f = os.path.join(OUT, p['id'] + '.webp')
        if os.path.exists(f) and (not p.get('immagine') or p['id'] in args):
            p['immagine'] = 'assets/images/prodotti/' + p['id'] + '.webp'; ok.append(p['id'])
    if not ok:
        print('nessuna foto da collegare'); return
    json.dump(d, open(CAT, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('collegate:', len(ok), ok)
    if push:
        sh('git', 'add', '-A', 'assets/images/prodotti', '_data/catalogo.json', 'automation/foto_prodotti.py')
        print(sh('git', 'commit', '-m', 'Foto prodotti: %d immagini' % len(ok)).stdout[-200:])
        sh('git', 'pull', '-q', '--rebase'); print(sh('git', 'push').stderr[-200:])

if __name__ == '__main__':
    main()
