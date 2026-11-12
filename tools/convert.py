"""シート「AMAKUMA英語ジム_レッスン教材」の値（タブ名→2次元配列）を、アプリ用の LESSONS（JSON）に変換する。
使い方: python3 convert.py rows.json > lessons.json
rows.json = {"レッスン": [[...],...], "単語": ..., "会話": ..., "問題": ..., "速攻英語": ..., "よくある間違い": ...}（各タブ、1行目は見出し）
"""
import json, sys

TYPE = {'聞く': 'listen', '読む': 'read', '文法': 'gram', '話す_音読': 'oral', '話す_質問': 'qa', '書く': 'write'}

def rows(tab, data):
    out = []
    for r in data.get(tab, [])[1:]:
        r = [str(c).strip() for c in r] + [''] * 20
        if not r[0] or r[0] == '記入例':
            continue
        out.append(r)
    return out

def split(s):
    return [x.strip() for x in s.split('/') if x.strip()]

def convert(data):
    warn = []
    lessons = []
    for r in rows('レッスン', data):
        lid, title, lv, cando, scene, gt, gtip, reuse, pre, uname = r[:10]
        if not title:
            continue
        L = {'id': lid, 'unit': lid.split('-')[0], 'unitName': uname, 'title': title, 'lv': lv or 'A1', 'cando': cando, 'scene': scene,
             'gTitle': gt, 'gTip': gtip, 'reuse': split(reuse),
             'preSkip': (pre == 'スキップ可') or (pre == '' and (lv or 'A1') == 'A1'),
             'words': [], 'dlg': [], 'qs': [], 'sk': None, 'errs': []}
        for w in rows('単語', data):
            if w[0] == lid and w[1]:
                L['words'].append([w[1], w[2], w[3]])
        d = [x for x in rows('会話', data) if x[0] == lid and x[3]]
        d.sort(key=lambda x: float(x[1] or 0))
        L['dlg'] = [[x[2] or '?', x[3], x[4], split(x[5])] for x in d]
        for q in rows('問題', data):
            if q[0] != lid or q[1] not in TYPE:
                continue
            t = TYPE[q[1]]
            item = {'type': t, 'prompt': q[2], 'en': q[3], 'ans': q[4], 'opts': [o for o in (q[4], q[5], q[6]) if o],
                    'why': {k: v for k, v in ((q[5], q[7]), (q[6], q[8])) if k and v},
                    'hint': q[9], 'conds': [c for c in (q[10], q[11]) if c], 'example': q[12]}
            need = {'listen': item['prompt'] and item['ans'] and len(item['opts']) >= 2,
                    'read': item['prompt'] and item['ans'] and len(item['opts']) >= 2,
                    'gram': '___' in item['en'] and item['ans'] and len(item['opts']) >= 2,
                    'oral': item['en'], 'qa': item['en'] and item['conds'],
                    'write': item['prompt'] and item['conds']}[t]
            if need:
                L['qs'].append(item)
            elif any(q[2:13]):
                warn.append(f'{lid} 問題（{q[1]}）: 必要な列が空いているため使いません')
        for s in rows('速攻英語', data):
            if s[0] == lid and s[1] and s[5]:
                L['sk'] = {'prompt': s[1], 'q': s[2], 'cards': split(s[3]),
                           'els': [{'name': n or '要素', 'pats': p} for n, p in ((s[4], s[5]), (s[6], s[7])) if p],
                           'bonus': {'name': s[8] or 'ボーナス', 'pats': s[9]} if s[9] else None,
                           'examples': [x for x in s[10:13] if x], 'natural': s[13],
                           'mode': s[14] if s[14] in ('話す', '書く', '両方') else '両方'}
        for e in rows('よくある間違い', data):
            if e[0] == lid and e[1] and e[2]:
                L['errs'].append({'wrong': e[1], 'right': e[2], 'why': e[3]})
        if len(L['words']) > 5:
            warn.append(f'{lid} 単語が{len(L["words"])}語あります（5語まで）')
        if not L['dlg']:
            warn.append(f'{lid} 会話がまだありません')
        if not L['sk']:
            warn.append(f'{lid} 速攻英語がまだありません')
        lessons.append(L)
    return lessons, warn

if __name__ == '__main__':
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    lessons, warn = convert(data)
    for w in warn:
        print('注意:', w, file=sys.stderr)
    print(json.dumps(lessons, ensure_ascii=False))
