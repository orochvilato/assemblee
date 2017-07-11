# -*- coding: utf-8 -*-
import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict
from datetime import datetime
import re
import json
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

from lib.tools import cmdline_args,normalize,format_date

debug = cmdline_args.debug
from lib.conf import data,axes
from lib import scrutins


axejson = {'noms':[],'defs':{}}
for axe,defs in axes:
    axe_items = [ (s[defs['key']],s[defs['label']]) for s in data[defs['source']] ]
    axejson['noms'].append(axe)
    axejson['defs'][axe] = {'titre':defs['titre'],'hidechart':defs.get('hidechart',False),'field':defs['item_field'], 'compare':defs['item_compare'], 'items':sorted(list(set(axe_items)),key=lambda item:item[1])}

open('dist/json/axes.json','w').write(json.dumps(axejson))


today = datetime.now().strftime('%d/%m/%Y %H:%M')

from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

open('dist/voteaxes.html','w').write(env.get_template('voteaxestmpl.html').render(today=today,scrutins = data['scrutins']).encode('utf-8'))
