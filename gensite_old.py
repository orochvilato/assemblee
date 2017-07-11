# -*- coding: utf-8 -*-
import requests
from zipfile import ZipFile
from cStringIO import StringIO
import xmltodict
from datetime import datetime
import re
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

from lib.tools import cmdline_args,normalize,format_date


debug = cmdline_args.debug

# déclaration hatvp
from lib.hatvp import declarations

from collections import OrderedDict

from lib.actorg import statsCSP, gplabels, svgcolors



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

    open('json/acteurs.json','w').write(json.dumps(acteurs))
    open('json/organes.json','w').write(json.dumps(organes))

    scrutins = loadScrutins()
    open('json/scrutins.json','w').write(json.dumps(scrutins))
else:
    organes = json.loads(open('json/organes.json','r').read())
    acteurs = json.loads(open('json/acteurs.json','r').read())
    scrutins = json.loads(open('json/scrutins.json','r').read())


from lib.deputywatch import deputywatch



nbvotes = {}
groupes = {}

for organe in organes.keys():
    org = organes[organe]
    if not org['viMoDe.dateFin']:
        if org['codeType'] == 'GP':
            gplabels.append(org['libelleAbrev'])
            groupes[org['uid']] = org
            #print org['uid'],org['libelle']
            org.update({'csscolor':'coul'+org['libelleAbrev'],'svgcolor':svgcolors.get(org['libelleAbrev'],'NI')})

gplabels.sort()
for organe in organes.keys():
    org = organes[organe]
    organes[org['uid']].update({'membres':{},'votes':{},'qualites':{},'stats':
        {'fsp':OrderedDict(list((c,0) for c in statsCSP.keys())),
         'pctgp':OrderedDict(list((c,0) for c in sorted(gplabels))), 'parite':{},'votes':{}}})

stats = {'fsp':OrderedDict(list((c,0) for c in statsCSP.keys())), 'parite':{},'scrutins':{}, 'mandats':{},
         'pctgp':OrderedDict(list((c,0) for c in sorted(gplabels)))}

commstats = {'fsp':OrderedDict(list((c,0) for c in statsCSP.keys())), 'parite':{},'scrutins':{}, 'mandats':{},
         'pctgp':OrderedDict(list((c,0) for c in sorted(gplabels)))}

places = {}
rangs = {u'Président':1,
         u'Vice-Président':2,
         u'Questeur':3,
         u"Président d'âge":4,
         u"Secrétaire d'âge":5,
         u"Secrétaire":6,
         u'Membre apparenté':10}


correctionPlaces = {
'PA720606':'67',
'PA719850':'385',
'PA721824':'196',
'PA720822':'66',
'PA1198':'509',
'PA720798':'60',
'PA719922':'362',
'PA720614':'58',
'PA721262':'373',
'PA721036':'357',
'PA346876':'123',
'PA721880':'307',
'PA721718':'341',
'PA721678':'47',
'PA719890':'549',
'PA719770':'419',
'PA721398':'350',
'PA722150':'537',
'PA610667':'597',
'PA223837':'82',
'PA720622':'288',
'PA719388':'318',
'PA719640':'256',
'PA429893':'517',
'PA332747':'494',
'PA718736':'201',
'PA606212':'59',
'PA720468':'57',
'PA720664':'56',
'PA719608':'68',
'PA588884':'618',
'PA721600':'441',
'PA720746':'267',
'PA724827':'306',
'PA722070':'466'}


from confiance import voteconf
from etaturgence import voteurg
votec = {'pour':[],'contre':[],'abstention':[],'nonVotant':[]}
voteu = {'pour':[],'contre':[],'abstention':[],'nonVotant':[]}
voteugp = {}
votecgp = {}
totalc = {'pour':0,'contre':0,'abstention':0,'nonVotant':0}
totalu = {'pour':0,'contre':0,'abstention':0,'nonVotant':0}

for acteur in acteurs.keys():
    act = acteurs[acteur]
    act['contacts'] = []
    act['nomcomplet'] = act['etatCivil.ident.civ'] + ' ' + act['etatCivil.ident.prenom'] + ' ' + act['etatCivil.ident.nom']
    act['age'] = int((datetime.now() - datetime.strptime(act['etatCivil.infoNaissance.dateNais'],'%Y-%m-%d')).days / 365.25)
    if not act['profession.socProcINSEE.famSocPro'] in statsCSP.keys():
        act['profession.socProcINSEE.famSocPro'] = u"Autres (y compris inconnu et sans profession déclarée)"

    for adr in act['adresses']:
        if 'valElec' in adr.keys():
            act['contacts'].append((adr['typeLibelle'],adr['valElec']))
    placeH = None
    comm = 0
    fonctions =  {}

    for man in act['mandats']:

        organeRef = man['organes.organeRef']
        if man['typeOrgane']=='ASSEMBLEE':
            placeH = man['mandature.placeHemicycle']
        if man['typeOrgane']=='GP':

            act['groupe'] = organeRef
        #if man['infosQualite.codeQualite'] == u'Président':
        #    organes[man['organes.organeRef']]['president'] = act['uid']
        if not act['uid'] in organes[man['organes.organeRef']]['membres'].keys():
            fsp = act['profession.socProcINSEE.famSocPro']
            ostats = organes[organeRef]['stats']
            ostats['fsp'][fsp] = ostats['fsp'].get(fsp,0) + 1

            parite = 'Homme' if act['etatCivil.ident.civ']=='M.' else 'Femme'
            ostats['parite'][parite] = ostats['parite'].get(parite,0) + 1
            if man['typeOrgane'] == 'ASSEMBLEE':
                stats['parite'][parite] = stats['parite'].get(parite,0) + 1
                stats['fsp'][fsp] = stats['fsp'].get(fsp,0) + 1

            if man['typeOrgane'] in ('COMPER','CONFPT'):
                comm += 1
                commstats['fsp'][fsp] += 1
                commstats['parite'][parite] = commstats['parite'].get(parite,0) + 1


        qua = man['infosQualite.codeQualite']
        fonctions[organeRef] = dict(qualite=qua,debut=format_date(man['dateDebut']),organe=organeRef)
        qua_norm = normalize(qua)

        organes[man['organes.organeRef']]['qualites'][qua_norm] = organes[man['organes.organeRef']]['qualites'].get(qua_norm,[]) + [act['uid']]
        organes[man['organes.organeRef']]['membres'][act['uid']] = (act['uid'],qua,rangs.get(qua,3 if qua.lower()!='membre' else 8))

    act['fonctions'] = fonctions.values()
    if not placeH:
        placeH = correctionPlaces[act['uid']]
    if placeH:
        places[str(int(placeH))] = {'place':placeH,'acteur':acteur,'groupe':act['groupe']}
        act['place'] = placeH
    else:
        print act['nomcomplet']+";"+act['uid']
    # initialisations
    act['stats'] = {'absenteisme':{}}
    act['votes'] = {}
    # stats
    stats['pctgp'][organes[act['groupe']]['libelleAbrev']] += 1
    commstats['pctgp'][organes[act['groupe']]['libelleAbrev']] += comm

    norm_nom = normalize(act['nomcomplet'])
    # déclarations hatvp
    act['hatvp'] = declarations.get(norm_nom,[])

    # deputywatch
    act['deputywatch'] = deputywatch.get(norm_nom,None)
    if act['deputywatch']:
        print act['nomcomplet']

    if norm_nom in voteconf:
        gp = act['groupe']
        if not gp in votecgp.keys():
            votecgp[gp] = {'pour':[],'contre':[],'abstention':[],'nonVotant':[]}

        votecgp[gp][voteconf[norm_nom]].append(act['uid'])
        votec[voteconf[norm_nom]].append("%d" % int(placeH))
        totalc[voteconf[norm_nom]] += 1

    else:
        print "pb :" + norm_nom

    gp = act['groupe']
    if not gp in voteugp.keys():
        voteugp[gp] = {'pour':[],'contre':[],'abstention':[],'nonVotant':[]}

    if norm_nom in voteurg:
        voteugp[gp][voteurg[norm_nom]].append(act['uid'])
        voteu[voteurg[norm_nom]].append("%d" % int(placeH))
        totalu[voteurg[norm_nom]] += 1
    else:
        voteugp[gp]['nonVotant'].append(act['uid'])
        totalu['nonVotant'] += 1



totalu_sum = sum(totalu.values())
totalc_sum = sum(totalc.values())
totalu = OrderedDict(sorted({'pour': int(float(100*totalu['pour'])/(totalu_sum-totalu['nonVotant'])),
          'contre':int(float(100*totalu['contre'])/(totalu_sum-totalu['nonVotant'])),
          'abstention': int(float(100*totalu['abstention'])/(totalu_sum-totalu['nonVotant'])),
          'votant':100-int(float(100*totalu['nonVotant'])/totalu_sum)
          }.items(), key=lambda t:t[1], reverse=True))
totalc = OrderedDict(sorted({'pour': int(float(100*totalc['pour'])/(totalc_sum-totalc['nonVotant'])),
          'contre':int(float(100*totalc['contre'])/(totalc_sum-totalc['nonVotant'])),
          'abstention': int(float(100*totalc['abstention'])/(totalc_sum-totalc['nonVotant'])),
          'votant':100-int(float(100*totalc['nonVotant'])/totalc_sum)
          }.items(), key=lambda t:t[1], reverse=True))
# Vote confiance
for gp in votecgp.keys():
    pour = len(votecgp[gp]['pour'])
    contre = len(votecgp[gp]['contre'])
    abstention = len(votecgp[gp]['abstention'])
    nonVotant = len(votecgp[gp]['nonVotant'])
    #print groupes[gp]['libelle'],pour,contre,abstention,nonVotant
    total = pour+contre+abstention
    votecgp[gp]['stats'] = {'pour': int(float(100*pour)/total),
                            'contre':int(float(100*contre)/total),
                            'abstention': int(float(100*abstention)/total),
                            'votant':100-int(float(100*nonVotant)/(total+nonVotant))
                            }
    votecgp[gp]['stats'] = OrderedDict(sorted(votecgp[gp]['stats'].items(), key=lambda t:t[1], reverse=True))


for gp in voteugp.keys():
    pour = len(voteugp[gp]['pour'])
    contre = len(voteugp[gp]['contre'])
    abstention = len(voteugp[gp]['abstention'])
    nonVotant = len(voteugp[gp]['nonVotant'])

    total = pour+contre+abstention
    voteugp[gp]['stats'] = {'pour': int(float(100*pour)/total),
                            'contre':int(float(100*contre)/total),
                            'abstention': int(float(100*abstention)/total),
                            'votant':100-int(float(100*nonVotant)/(total+nonVotant))
                            }
    voteugp[gp]['stats'] = OrderedDict(sorted(voteugp[gp]['stats'].items(), key=lambda t:t[1], reverse=True))


css = ""
vcoul = {'pour':'green','contre':'red','abstention':'white' }
for v in votec:
    if v in vcoul.keys():
        css = css + ' ,'.join([ '#p%s' % d for d in votec[v]]) + ' { fill:'+vcoul[v]+'; stroke-width:0 } '


# Hemicycle

hemicycle = xmltodict.parse(open('hemicycle-test.svg','r').read())
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

totalcomm = sum(commstats['pctgp'].values())

for k in statsCSP.keys():
    stats['fsp'][k] = round(100*float(stats['fsp'][k])/len(acteurs.keys()),2)
    commstats['fsp'][k] = round(100*float(commstats['fsp'][k])/totalcomm,2)

coulgp = []


for k in stats['pctgp'].keys():
    stats['pctgp'][k] = round(100*float(stats['pctgp'][k])/len(acteurs.keys()),2)
    commstats['pctgp'][k] = round(100*float(commstats['pctgp'][k])/totalcomm,2)
    coulgp.append(svgcolors[k])




def statsOrgane(organe):
    # Stats repartition des groupes dans les organes
    ostats = organes[organe]['stats']
    for m in organes[organe]['membres']:
        ostats['pctgp'][groupes[acteurs[m]['groupe']]['libelleAbrev']] += 1

    for gp in ostats['pctgp'].keys():
        ostats['pctgp'][gp] = round(100*float(ostats['pctgp'][gp]) / organes[organe]['nbmembres'],2)

    for k in statsCSP.keys():
        organes[organe]['stats']['fsp'][k] = 100*float(organes[organe]['stats']['fsp'][k])/organes[organe]['nbmembres']


for organe in organes:
    organes[organe]['nbmembres'] = len(organes[organe]['membres'].keys())
    organes[organe]['membres_sort'] = sorted(organes[organe]['membres'].values(),key=lambda x:(x[2],acteurs[x[0]]['etatCivil.ident.nom'],acteurs[x[0]]['etatCivil.ident.prenom']))
    if organes[organe]['nbmembres']>0:
        statsOrgane(organe)
        if organes[organe]['codeType'] != 'GP':
            print organes[organe]['libelle']
            open('dist/commissions/%s.html' % organe,'w').write(env.get_template('organetmpl.html').render(
                today=today,
                csp=statsCSP,
                acteurs = acteurs,
                groupes= groupes,
                stats= stats,
                coulgp = coulgp,
                organe = organes[organe]).encode('utf-8'))
        else:
            open('dist/groupes/%s.html' % organe,'w').write(env.get_template('groupetmpl.html').render(
                today=today,
                csp=statsCSP,
                scrutins = sort_scrutins(organes[organe]['votes'].keys()),
                acteurs = acteurs, groupe = organes[organe]).encode('utf-8'))


open('dist/scrutins.html','w').write(env.get_template('scrutinstmpl.html').render(today=today,scrutins = sort_scrutins(scrutins.keys()), organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))


open('dist/commissions.html','w').write(env.get_template('organestmpl.html').render(
    today=today,
    commstats = commstats,
    stats=stats,
    csp=statsCSP,
    organes = organes,
    acteurs = acteurs,
    coulgp = coulgp,
    commissions = dict((k,v) for k,v in organes.iteritems() if v['nbmembres']>0 and v['codeType'] in ['CONFPT','COMPER'])).encode('utf-8'))
open('dist/groupes.html','w').write(env.get_template('groupestmpl.html').render(today=today, coulgp=coulgp, stats=stats, csp=statsCSP,organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))
for s in scrutins.keys():
    open('dist/scrutins/%s.html' % s,'w').write(env.get_template('scrutintmpl.html').render(today=today, scrutin = scrutins[s], organes = organes, acteurs = acteurs, groupes = groupes).encode('utf-8'))

count = 0
for act in acteurs:
    acteur = acteurs[act]
    if acteur['hatvp']:
        count += 1

    #if groupes[acteur['groupe']]['libelleAbrev']=='NI':
    #    print acteur['nomcomplet'],acteur.get('place','NA')
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
open('dist/hatvp.html','w').write(env.get_template('hatvptmpl.html').render(today=today, stats=stats, acteurs = acteurs, groupes = groupes).encode('utf-8'))
open('dist/voteconfiance.html','w').write(env.get_template('voteconfiancetmpl.html').render(total=totalc,titre=u"Scrutin n°1 : Confiance au gouvernement",today=today, votegp = votecgp, css = css,stats=stats, acteurs = acteurs, groupes = groupes).encode('utf-8'))
open('dist/voteurgence.html','w').write(env.get_template('voteconfiancetmpl.html').render(total=totalu,titre=u"Scrutin n°2 : Etat d'Urgence",today=today, votegp = voteugp, css = css,stats=stats, acteurs = acteurs, groupes = groupes).encode('utf-8'))
