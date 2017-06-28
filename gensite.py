# -*- coding: utf-8 -*-
import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict


def loadXMLZip(url):

    zip = StringIO(requests.get(url).content)

    with ZipFile(zip,'r') as z:
        name = z.namelist()[0]
        with z.open(name,'r') as f:
            xml = f.read()

    return xmltodict.parse(xml)
def getVal(v):
    return None if isinstance(v,dict) else v

import collections
def flatten(elt):
    if isinstance(elt,dict):
        update = []
        for k,v in elt.iteritems():
            if isinstance(v, collections.MutableMapping):
                update.append((k,v))
            elif isinstance(v,list):
                flatten(v)
        for (k,v) in update:
            flatten(v)
            if '@xsi:nil' in v.keys():
                elt[k] = None
                continue
            if len(v.keys()) == 1 and k == v.keys()[0]+'s':
                elt[k] = v.values()[0]
                continue
            for _k,_v in v.iteritems():
                elt[ k + '.' + _k ] = _v
            del elt[k]
        if '@xsi:type' in elt.keys():
            elt['type'] = elt['@xsi:type']
            del elt['@xsi:type']
        if 'uid.#text' in elt.keys():
            elt['uid'] = elt['uid.#text']
            del elt['uid.#text']
    elif isinstance(elt,list):
        for e in elt:
            flatten(e)


def loadDeputes():
    url = "http://data.assemblee-nationale.fr/static/openData/repository/AMO/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.xml.zip"
    url = "http://data.assemblee-nationale.fr/static/openData/repository/AMO/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml.zip"
    deputes = loadXMLZip(url)
    #deputes = xmltodict.parse(open('AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml','r').read())

    flatten(deputes['export']['organes']['organe'])
    flatten(deputes['export']['acteurs']['acteur'])
    organes = dict( (o['uid'],o) for o in deputes['export']['organes']['organe'])
    acteurs = dict( (a['uid'],a) for a in deputes['export']['acteurs']['acteur'])
    return organes,acteurs

def loadScrutins():
    url = "http://data.assemblee-nationale.fr/static/openData/repository/LOI/scrutins/Scrutins_XIV.xml.zip"
    scrutins = loadXMLZip(url)
    #scrutins = xmltodict.parse(open('Scrutins_XIV.xml','r').read())

    flatten(scrutins['scrutins']['scrutin'])

    return scrutins['scrutins']['scrutin']

import json
debug = False
if not debug:
    organes,acteurs = loadDeputes()

    open('acteurs.json','w').write(json.dumps(acteurs))
    open('organes.json','w').write(json.dumps(organes))

    scrutins = loadScrutins()
    open('scrutins.json','w').write(json.dumps(scrutins))
else:
    organes = json.loads(open('organes.json','r').read())
    acteurs = json.loads(open('acteurs.json','r').read())
    scrutins = json.loads(open('scrutins.json','r').read())


scrutins = scrutins[::-1]
groupes = {}
for scrutin in scrutins:
    for grp in scrutin['ventilationVotes.organe.groupes']:
        groupe = organes[grp['organeRef']]
        if not grp['organeRef'] in groupes.keys():
            groupes[grp['organeRef']] = {'uid':grp['organeRef'],
                                         'votes':{},
                                         }

        groupes[grp['organeRef']]['votes'][scrutin['uid']] = { 'scrutin_uid':scrutin['uid'],
                                                             'vote':grp['vote.positionMajoritaire'],
                                                             'pour':int(grp.get('vote.decompteVoix.pour',0)),
                                                             'contre':int(grp.get('vote.decompteVoix.contre',0)),
                                                             'abstention':int(grp.get('vote.decompteVoix.abstention',0)),
                                                             'nonVotant':int(grp.get('vote.decompteVoix.nonVotant',0))}

        positions = ['nonVotant','pour','contre','abstention']
        for pos in positions:
            for v in grp.get('vote.decompteNominatif.%ss.votant' % pos,[]):
                vote = { 'scrutin_uid':scrutin['uid'],
                         'acteur_uid':v['acteurRef'],
                         'groupe_uid':grp['organeRef'],
                         'vote':pos,
                         'cause':v.get('causePositionVote',None)}
                scrutin['votants'] = scrutin.get('votants',[]) + [vote]

                acteur = acteurs.get(v['acteurRef'],None)
                if not acteur:
                    continue
                if not 'votes' in acteur.keys():
                    acteur['votes'] = {}
                acteur['votes'][scrutin['uid']] = vote


    #if scrutin['sort.code']==u'adopté':
        #print scrutin['uid'],scrutin['objet.libelle'].encode('utf8')


from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
from datetime import datetime
today = datetime.now().strftime('%d/%m/%Y %H:%M')
open('dist/scrutins.html','w').write(env.get_template('scrutinstmpl.html').render(today=today,scrutins = scrutins, organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
for scrutin in scrutins:
    open('dist/scrutins/%s.html' % scrutin['uid'],'w').write(env.get_template('scrutintmpl.html').render(today=today, scrutin = scrutin, organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))

#for acteur in acteurs.values():
#    print acteur['etatCivil.ident.civ'],acteur['etatCivil.ident.nom'].encode('utf8'),acteur['etatCivil.ident.prenom'].encode('utf8'),organes[acteur['mandats'][0]['organes.organeRef']]['libelle'].encode('utf8')