# -*- coding: utf-8 -*-
import pdfminer.high_level
import pdfminer.layout
import sys
from io import BytesIO
from tools import strip_accents
import cStringIO, codecs
import json
from tools import cmdline_args,normalize,flatten
debug = cmdline_args.debug


votes = {'Pour':'pour',
         'Contre':'contre',
         'Abstention': 'abstention',
         'Non-votant(s)': 'nonVotant'
        }

import actorg
from conf import data

#from actorg import acteurs,acteurs_ids,organes,groupes


def parseVotePDF(path):
    # Create a PDF interpreter object.
    laparams = pdfminer.layout.LAParams(word_margin=0.4, char_margin=3)
    # Open a PDF file.
    fp = open(path, 'rb')
    # Create a PDF parser object associated with the file object.
    txtfp = BytesIO()

    pdfminer.high_level.extract_text_to_fp(fp, outfp=txtfp,codec='utf-8',laparams = laparams)
    r = txtfp.getvalue().decode('utf8')

    import re
    pages = re.split(r'Page \d+ sur \d+[ \n\r\x0c]+',r)
    synthese,pages = pages[0],strip_accents(''.join(pages[1:]))
    pages = re.split(r'Mises au point', pages)+['']
    pages, miseaupoint = pages[0],pages[1:]
    pages = ''.join(re.split(r'[\w ,:]+\(\d+\) *\n',pages))
    pages = re.split(r'([\w\-\(\)]+) : (\d+)',pages)[1:]
    positions = [pages[x:x+3] for x in xrange(0, len(pages), 3)]

    synthese = synthese.replace('\n',' ').replace('  ',' ')
    noscrutin = re.search(r'Analyse du scrutin[ n]+. *(\d)',synthese).groups()[0]
    datestr = re.search(r's.ance du \w+ (\d+ [^ ]+ \d+)',synthese).groups()[0]

    import locale
    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
    from datetime import datetime
    date = datetime.strptime(datestr,"%d %B %Y")

    libelle = re.search(r'Scrutin public sur (.*). Demand. par :',synthese)
    if libelle:
        libelle = libelle.groups()[0]
    else:
        libelle = re.search(r'Scrutin public sur (.*). Synth',synthese).groups()[0]

    scrutin = { 'numero':noscrutin,'libelle':libelle,'date':date.strftime('%d/%m/%Y'),'positions':[]}
    exprimes = []
    for pos,nb,act in positions:
         act = act.replace(' et ',',').replace(' et',',').replace('\net',',').replace('\n','').replace(' ','').replace(u'\u0153','oe')
         act = re.sub(r'\([^\)]+\)',r'',act).split(',')
         if int(nb) != len(act):
             print "probleme"
         for a in act:
             act = data['acteurs_ids'][normalize(a)]
             exprimes.append(act['uid'])
             scrutin['positions'].append({'uid':act['uid'],
                                          'nom':act['nomcomplet'],
                                          'commissions': act['commissions'],
                                          'organes': act['organes'],
                                          'groupe': act['groupe'],
                                          'classeage':act['classeage'],
                                          'region':act['region'],
                                          'departement':act['departement'],
                                          'csp':act['csp'],
                                          'sexe':act['sexe'],
                                          'position':votes[pos]})

    for uid in list(set(data['acteurs_uid'].keys())-set(exprimes)):
        act = data['acteurs_uid'][uid]
        scrutin['positions'].append({'uid':'uid',
                                     'nom':act['nomcomplet'],
                                     'commissions': act['commissions'],
                                     'organes': act['organes'],
                                     'groupe': act['groupe'],
                                     'classeage':act['classeage'],
                                     'region':act['region'],
                                     'departement':act['departement'],
                                     'csp':act['csp'],
                                     'sexe':act['sexe'],
                                     'position':'absent'})

    return scrutin

#r = parseVotePDF('pdfs/scrutin2017_07_04.pdf')
r = parseVotePDF('pdfs/scrutin02.pdf')
open('dist/json/scrutin%s.json' % r['numero'], 'w').write(json.dumps(r))
