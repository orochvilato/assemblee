# -*- coding: utf-8 -*-
import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict
from datetime import datetime
import re
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="debug mode", action="store_true")
args = parser.parse_args()
debug = args.debug

_csscolors = {
    'NI': 'grey',
    'LR': 'blue',
    'MODEM': 'amber',
    'FI': 'deep-orange',
    'GDR': 'red',
    'LC': 'light-blue',
    'REM': 'purple',
    'NG': 'pink'}
svgcolors = {}



def setPalette(svgfile):
    css = ""
    svg = xmltodict.parse(open(svgfile,'r').read())
    for c in svg['svg']['rect']:
        id = c['@id']
        h = re.search(r';fill:([^;]+);',c['@style']).groups()[0][1:]
        svgcolors[id] = '#'+h
        hcolor = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
        css += '.coul'+id+' {\n  background-color: rgba(%d,%d,%d,1);\n}\n\n' % hcolor
        css += '.coul'+id+'-text {\n  color: rgba(%d,%d,%d,1);\n}\n\n' % hcolor
        css += '.coul'+id+'bg {\n  background-color: rgba(%d,%d,%d,0.33);\n}\n\n' % hcolor
        css += '.coul'+id+'bg-text {\n  color: rgba(%d,%d,%d,0.33);\n}\n\n' % hcolor
    open("dist/css/colors.css",'w').write(css)


setPalette('palette.svg')

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
    scrutins = dict( (s['uid'],s) for s in scrutins['scrutins']['scrutin'][::-1])
    return scrutins

import json

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




nbvotes = {}
groupes = {}
stats = {'fsp':{}, 'parite':{},'scrutins':{}}
for organe in organes.keys():
    org = organes[organe]
    if org['codeType'] == 'GP':
        if not org['viMoDe.dateFin']:
            groupes[org['uid']] = org
            org.update({'csscolor':'coul'+org['libelleAbrev'],'svgcolor':svgcolors.get(org['libelleAbrev'],'NI')})
        organes[org['uid']].update({'membres':{},'votes':{},'stats':{'fsp':{}, 'parite':{},'votes':{}}})

places = {}
for acteur in acteurs.keys():
    act = acteurs[acteur]
    act['contacts'] = []
    act['nomcomplet'] = act['etatCivil.ident.civ'] + ' ' + act['etatCivil.ident.prenom'] + ' ' + act['etatCivil.ident.nom']
    act['age'] = int((datetime.now() - datetime.strptime(act['etatCivil.infoNaissance.dateNais'],'%Y-%m-%d')).days / 365.25)
    for adr in act['adresses']:
        if 'valElec' in adr.keys():
            act['contacts'].append((adr['typeLibelle'],adr['valElec']))
    placeH = None
    for man in act['mandats']:
        if man['typeOrgane']=='ASSEMBLEE':
            placeH = man['mandature.placeHemicycle']
        if man['typeOrgane']=='GP':
            groupeRef = man['organes.organeRef']
            if man['infosQualite.codeQualite'] == u'Président':
                organes[man['organes.organeRef']]['president'] = act['uid']
            organes[man['organes.organeRef']]['membres'][act['uid']] = man['infosQualite.codeQualite']
            act['groupe'] = groupeRef

    if placeH:
        places[str(int(placeH))] = {'place':placeH,'acteur':acteur,'groupe':act['groupe']}
        act['place'] = placeH
    else:
        print act['uid']
    # initialisations
    act['stats'] = {'absenteisme':{}}
    act['votes'] = {}
    # stats
    fsp = act['profession.socProcINSEE.famSocPro'] or "Inconnu"
    ostats = organes[groupeRef]['stats']
    ostats['fsp'][fsp] = ostats['fsp'].get(fsp,0) + 1
    stats['fsp'][fsp] = stats['fsp'].get(fsp,0) + 1
    parite = 'Homme' if act['etatCivil.ident.civ']=='M.' else 'Femme'
    ostats['parite'][parite] = ostats['parite'].get(parite,0) + 1
    stats['parite'][parite] = stats['parite'].get(parite,0) + 1


# Hemicycle

hemicycle = xmltodict.parse(open('hemicycle.svg','r').read())
for i,a in enumerate(hemicycle['svg']['a']):
    if '@class' in a['path'].keys() and '@id' in a['path'].keys():
        place = places.get(a['path']['@id'][1:],None)
        if place:
            a['path']['@class'] += ' ' + place['groupe']
            a['title'] = {'#text':'%s (place %s)' % (acteurs[place['acteur']]['nomcomplet'], place['place']) }
            a['@href'] = 'acteurs/%s.html' % place['acteur']
            a['@target'] = "_parent"

open('dist/hemicycle.svg','w').write(xmltodict.unparse(hemicycle,pretty=True).encode('utf8'))

ttvot = 0
for s in scrutins.keys():
    scrutin = scrutins[s]
    #print scrutin['uid'],scrutin['dateScrutin']
    ttvot += int(scrutin['syntheseVote.nombreVotants'])
    scrutin['groupes'] = []
    svot = 0
    for grp in scrutin['ventilationVotes.organe.groupes']:
        scrutin['groupes'].append(grp['organeRef'])
        groupe = organes[grp['organeRef']]

        organes[grp['organeRef']]['votes'][scrutin['uid']] = {
                                                             'vote':grp['vote.positionMajoritaire'],
                                                             'pour':int(grp.get('vote.decompteVoix.pour',0)),
                                                             'contre':int(grp.get('vote.decompteVoix.contre',0)),
                                                             'abstention':int(grp.get('vote.decompteVoix.abstention',0)),
                                                             'nonVotant':int(grp.get('vote.decompteVoix.nonVotant',0))}

        positions = ['nonVotant','pour','contre','abstention']
        for pos in positions:
            if grp.get('vote.decompteNominatif.%ss.votant.acteurRef' % pos,None):
                votants = [ dict(acteurRef = grp['vote.decompteNominatif.%ss.votant.acteurRef' % pos],
                                 mandatRef = grp['vote.decompteNominatif.%ss.votant.mandatRef' % pos])]
            else:
                votants = grp.get('vote.decompteNominatif.%ss.votant' % pos,[])
            for v in votants:
                if pos != 'nonVotant':
                    svot += 1

                vote = { 'acteur_uid':v['acteurRef'],
                         'groupe_uid':grp['organeRef'],
                         'vote':pos,
                         'cause':v.get('causePositionVote',None)}
                scrutin['votants'] = scrutin.get('votants',[]) + [vote]
                acteur = acteurs.get(v['acteurRef'],None)
                if not acteur:
                    continue

                acteur['votes'][scrutin['uid']] = vote
                # stats
                acteur['stats'][pos] = acteur['stats'].get(pos,0) + 1

                organes[grp['organeRef']]['stats']['votes'][pos]= organes[grp['organeRef']]['stats']['votes'].get(pos,0) +1

    # Le détail n'est pas toujours cohérent
    scrutin['valide'] = (int(scrutin['syntheseVote.nombreVotants']) == svot)
    leg = scrutin['legislature']
    if scrutin['valide']:
        if leg not in stats['scrutins'].keys():
            stats['scrutins'][leg] = {'nb':0}
        stats['scrutins'][leg]['nb'] += 1


from jinja2 import Environment, PackageLoader, select_autoescape,FileSystemLoader
env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)



today = datetime.now().strftime('%d/%m/%Y %H:%M')

def format_date(date):
    d = datetime.strptime(date,'%Y-%m-%d')
    return d.strftime('%-d %B %Y').decode('utf8')

env.filters['fdate'] = format_date

def sort_scrutins(keys):
    # tri par legislature et date decroissante
    scruts = {}
    for k in keys:
        s  = scrutins[k]
        leg = s['legislature']
        if not leg in scruts.keys():
            scruts[leg] = []
        scruts[leg].append(s)

    return [ dict(leg=leg,
                  scrutins=sorted(scruts[leg],key=lambda k:k['dateScrutin'],reverse=True)) for leg in sorted(scruts.keys(),reverse=True)]


# Stats absenteisme (sur les scrutins cohérents)
for s in scrutins:
    scrutin = scrutins[s]
    leg = scrutin['legislature']
    if not scrutin['valide']:
        continue
    for vote in scrutin['votants']:
        acteur = acteurs.get(vote['acteur_uid'],None)

        if acteur:
            if not leg in acteur['stats']['absenteisme'].keys():
                acteur['stats']['absenteisme'][leg] = {'votes':0,'total':stats['scrutins'][leg]['nb']}
            acteur['stats']['absenteisme'][leg]['votes'] += 1

# classement absenteisme
#for leg in acteur['stats']['absenteisme'].keys():
#    acteur['stats']['absenteisme'][leg]['classement'] = [()]


for groupe in groupes:
    organes[groupe]['nbmembres'] = len(organes[groupe]['membres'].keys())
    open('dist/groupes/%s.html' % groupe,'w').write(env.get_template('groupetmpl.html').render(
            today=today,
            scrutins = sort_scrutins(organes[groupe]['votes'].keys()),
            acteurs = acteurs, groupe = organes[groupe]).encode('utf-8'))

open('dist/scrutins.html','w').write(env.get_template('scrutinstmpl.html').render(today=today,scrutins = sort_scrutins(scrutins.keys()), organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
open('dist/groupes.html','w').write(env.get_template('groupestmpl.html').render(today=today, stats=stats, organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
for s in scrutins.keys():
    open('dist/scrutins/%s.html' % s,'w').write(env.get_template('scrutintmpl.html').render(today=today, scrutin = scrutins[s], organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))


for act in acteurs:

    acteur = acteurs[act]
    scruts = sort_scrutins(acteur['votes'].keys())
    for leg in acteur['stats']['absenteisme'].keys():
        stat = acteur['stats']['absenteisme'][leg]
        stat['tx']= "%.2f" % (100*float(stat['total']-stat['votes'])/stat['total'])

    open('dist/acteurs/%s.html' % act,'w').write(env.get_template('acteurtmpl.html').render(
        scrutins=scruts,
        organes=organes,
        today=today,
        acteur = acteur,
        groupe = organes[acteur['groupe']]).encode('utf-8'))

open('dist/acteurs.html','w').write(env.get_template('acteurstmpl.html').render(today=today, stats=stats, acteurs = acteurs, groupes = groupes).encode('utf-8'))
