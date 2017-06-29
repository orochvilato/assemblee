# -*- coding: utf-8 -*-
import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict
from datetime import datetime

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

grpcolors = {
    'NI': 'grey',
    'LR': 'blue',
    'MODEM': 'amber',
    'FI': 'deep-orange',
    'GDR': 'red',
    'LC': 'light-blue',
    'REM': 'purple',
    'NG': 'pink'}

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




nbvotes = {}
groupes = {}
stats = {'fsp':{}, 'parite':{}}
for organe in organes.keys():
    org = organes[organe]
    if org['codeType'] == 'GP':
        if not org['viMoDe.dateFin']:
            groupes[org['uid']] = org
        organes[org['uid']].update({'membres':{},'votes':{},'stats':{'fsp':{}, 'parite':{},'votes':{}}})

places = {}
for acteur in acteurs.keys():
    act = acteurs[acteur]
    act['contacts'] = []
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
            places[str(int(placeH)) if placeH else ''] = groupeRef

    # initialisations
    act['stats'] = {}
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

        a['path']['@class'] += ' '+places.get(a['path']['@id'][1:],'')
        hemicycle['svg']['path'].append(a['path'])
        del hemicycle['svg']['a'][i]

open('dist/hemicycle.svg','w').write(xmltodict.unparse(hemicycle).encode('utf8'))



for s in scrutins.keys():
    scrutin = scrutins[s]
    print scrutin['uid'],scrutin['dateScrutin']
    scrutin['groupes'] = []
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
        absents_uid = [ act['uid'] for act in acteurs.values()]
        for pos in positions:
            if grp.get('vote.decompteNominatif.%ss.votant.acteurRef' % pos,None):
                votants = [ dict(acteurRef = grp['vote.decompteNominatif.%ss.votant.acteurRef' % pos],
                                 mandatRef = grp['vote.decompteNominatif.%ss.votant.mandatRef' % pos])]
            else:
                votants = grp.get('vote.decompteNominatif.%ss.votant' % pos,[])
            for v in votants:
                nbvotes[v['acteurRef']] = nbvotes.get(v['acteurRef'],0) + 1
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
                absents_uid.remove(v['acteurRef'])
                organes[grp['organeRef']]['stats']['votes'][pos]= organes[grp['organeRef']]['stats']['votes'].get(pos,0) +1
        continue
        for absent in absents_uid:
            acteurs[absent]['votes'][scrutin['uid']]={'vote':'absent'}
            acteurs[absent]['absent'] = acteurs[absent].get('absent',0) + 1
            group = organes[acteurs[absent]['groupe']]
            if datetime.strptime(group['viMoDe.dateDebut'],'%Y-%m-%d')<datetime.strptime(scrutin['dateScrutin'],'%Y-%m-%d'):
                group['stats']['absent'] = group['stats'].get('absent',0) +1
    #if scrutin['sort.code']==u'adopté':
        #print scrutin['uid'],scrutin['objet.libelle'].encode('utf8')



#print [(k,v) for (k,v) in sorted([ (k,v) for k,v in nbvotes.iteritems()],key=lambda t:t[1]) if k in acteurs.keys()]

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

def count_scrutins():
    counts = {}
    for k in scrutins.keys():
        s  = scrutins[k]
        leg = s['legislature']
        if not leg in counts.keys():
            counts[leg] = dict(nb=0)
        counts[leg]['nb'] += 1
    return counts

stats_scrutins = count_scrutins()
print stats_scrutins
for groupe in groupes:
    organes[groupe]['nbmembres'] = len(organes[groupe]['membres'].keys())
    open('dist/groupes/%s.html' % groupe,'w').write(env.get_template('groupetmpl.html').render(
            today=today,
            scrutins = sort_scrutins(organes[groupe]['votes'].keys()),
            color=grpcolors.get(organes[groupe]['libelleAbrev'],'NI'),acteurs = acteurs, groupe = organes[groupe]).encode('utf-8'))
open('dist/scrutins.html','w').write(env.get_template('scrutinstmpl.html').render(today=today,scrutins = sort_scrutins(scrutins.keys()), organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
open('dist/groupes.html','w').write(env.get_template('groupestmpl.html').render(today=today, colors=grpcolors,stats=stats, organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
for s in scrutins.keys():
    open('dist/scrutins/%s.html' % s,'w').write(env.get_template('scrutintmpl.html').render(today=today, scrutin = scrutins[s], organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))


for act in acteurs:
    print act
    acteur = acteurs[act]
    scruts = sort_scrutins(acteur['votes'].keys())
    acteur['absenteisme']= dict((leg['leg'],dict(
                                 tx="%.2f" % (100*(1-float(len(leg['scrutins']))/stats_scrutins[leg['leg']]['nb'])),nb=(stats_scrutins[leg['leg']]['nb']-len(leg['scrutins'])))) for leg in scruts )

    open('dist/acteurs/%s.html' % act,'w').write(env.get_template('acteurtmpl.html').render(
        scrutins=scruts,
        organes=organes,
        today=today,
        color=grpcolors.get(organes[acteur['groupe']]['libelleAbrev'],'NI'),
        acteur = acteur,
        groupe = organes[acteur['groupe']]).encode('utf-8'))

open('dist/acteurs.html','w').write(env.get_template('acteurstmpl.html').render(today=today, colors=grpcolors,stats=stats, acteurs = acteurs, groupes = groupes).encode('utf-8'))

for groupe in groupes:
    organes[groupe]['nbmembres'] = len(organes[groupe]['membres'].keys())
    open('dist/groupes/%s.html' % groupe,'w').write(env.get_template('groupetmpl.html').render(
            today=today,
            scrutins = sort_scrutins(organes[groupe]['votes'].keys()),
            color=grpcolors.get(organes[groupe]['libelleAbrev'],'NI'),acteurs = acteurs, groupe = organes[groupe]).encode('utf-8'))
