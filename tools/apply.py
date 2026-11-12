"""convert.py の出力（lessons.json）をアプリの LESSONS に入れる。使い方: python3 apply.py lessons.json ../amakuma-gym.html"""
import json,re,sys
les=json.load(open(sys.argv[1],encoding='utf-8'));p=sys.argv[2];s=open(p,encoding='utf-8').read()
new='const LESSONS='+json.dumps(les,ensure_ascii=False)+'; /* LESSONS_DATA */'
s2,n=re.subn(r'const LESSONS=.*?; /\* LESSONS_DATA \*/',lambda m:new,s,count=1)
assert n==1;open(p,'w',encoding='utf-8').write(s2);print('lessons:',len(les))
