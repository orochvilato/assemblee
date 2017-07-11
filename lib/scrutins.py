# -*- coding: utf-8 -*-
from conf import data
import actorg

import json
import os

scrutins = []
def loadScrutins():
    for s in os.listdir('dist/json/'):
        if s[0:7]=='scrutin':
            scrutins.append(json.loads(open('dist/json/'+s,'r').read()))




def setScores():
    from collections import Counter
    for scrutin in scrutins:
        FIpos = [ p['position'] for p in scrutin['positions'] if p['position'] in ['pour','contre','abstention'] and p['uid'] in data['organes_abrev']['FI']['membres'].keys()]
        EMpos = [ p['position'] for p in scrutin['positions'] if  p['position'] in ['pour','contre','abstention'] and p['uid'] in data['organes_abrev']['REM']['membres'].keys()]


        fi = sorted(Counter(FIpos).items(),key=lambda p:p[1], reverse=True)[0][0]
        em = sorted(Counter(EMpos).items(),key=lambda p:p[1], reverse=True)[0][0]
        def eval_score(base,pos):

            if base==pos:
                score = 2
            elif pos in ('absent','nonVotant','abstention'):
                score = 1
            else:
                score = 0
            return score

        for i,p in enumerate(scrutin['positions']):
            p['fi'] = eval_score(fi,p['position'])
            p['em'] = eval_score(em,p['position'])


        open('dist/json/scrutin'+scrutin['numero']+'.json','w').write(json.dumps(scrutin))
#for scrutin in scrutins:


loadScrutins()
#setScores()
data['scrutins'] = sorted(scrutins,key=lambda s:int(s['numero']))
