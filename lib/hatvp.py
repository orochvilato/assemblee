# -*- coding: utf-8 -*-
import requests
import csv
import json
from cStringIO import StringIO
from tools import normalize

from tools import cmdline_args
debug = cmdline_args.debug

types_doc = {
 'dia': u'Déclaration d’intérêts et d’activités',
 'diam': u'Déclaration de modification substantielle des intérêts et des activités',
 'di': u'Déclaration d’intérêts',
 'dim': u'Déclaration de modification substantielle des intérêts',
 'dsp': u'Déclaration de situation patrimoniale',
 'dspm': u'Déclaration de modification substantielle de situation patrimoniale',
 'dspfm': u'Déclaration de modification substantielle de situation patrimoniale',
 'appreciation': u'Appréciation de la HATVP'
}

if not debug:
    r = requests.get('http://www.hatvp.fr/files/open-data/liste.csv')
    f = StringIO(r.content)
    csv = csv.DictReader(f, delimiter=';', quotechar='"')
    declarations = {}
    for row in csv:
        drow = dict((k,v.decode('utf8') if isinstance(v,basestring) else v) for k,v in row.iteritems())
        id = normalize(drow['civilite']+' '+drow['prenom']+' '+drow['nom'])
        drow['docurl'] = 'http://www.hatvp.fr/livraison/dossiers/'+drow['nom_fichier']
        drow['typedoc'] = types_doc[drow['type_document']]
        declarations[id] = declarations.get(id,[])+ [drow]

    open('json/hatvp.json','w').write(json.dumps(declarations))

else:
    declarations = json.loads(open('json/hatvp.json','r').read())
