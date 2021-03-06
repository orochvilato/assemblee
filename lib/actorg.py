# -*- coding: utf-8 -*-

import json
import xmltodict
import re
from datetime import datetime
from tools import cmdline_args, normalize, loadXMLZip,format_date, flatten
debug = cmdline_args.debug

from conf import data,axes

data['commissions_uid'] = commissions = {}
data['acteurs_uid'] = acteurs = {}
data['organes_uid'] = organes = {}
data['groupes_uid'] = groupes = {}
data['gplabels'] = gplabels = []
data['svgcolors'] = svgcolors = {}

from collections import OrderedDict

from hatvp import declarations
from deputywatch import deputywatch

data['statsCSP'] = statsCSP = OrderedDict((
(u"Agriculteurs exploitants", 1.1),
(u"Artisans, commerçants et chefs d'entreprise",3.6),
(u"Cadres et professions intellectuelles supérieures",9.4),
(u"Professions Intermédiaires",13.8),
(u"Employés",15.9),
(u"Ouvriers",12.3),
(u"Retraités",24.9),
(u"Autres (y compris inconnu et sans profession déclarée)",19)
))

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



def loadActOrg():
    url = "http://data.assemblee-nationale.fr/static/openData/repository/AMO/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.xml.zip"
    url = "http://data.assemblee-nationale.fr/static/openData/repository/AMO/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml.zip"
    deputes = loadXMLZip(url)
    #deputes = xmltodict.parse(open('AMO10_deputes_actifs_mandats_actifs_organes_XIV.xml','r').read())

    flatten(deputes['export']['organes']['organe'])
    flatten(deputes['export']['acteurs']['acteur'])
    organes.update(dict( (o['uid'],o) for o in deputes['export']['organes']['organe']))
    acteurs.update(dict( (a['uid'],a) for a in deputes['export']['acteurs']['acteur']))

if not debug:
    loadActOrg()
    open('json/acteurs.json','w').write(json.dumps(acteurs))
    open('json/organes.json','w').write(json.dumps(organes))
else:
    acteurs.update(json.loads(open('json/acteurs.json','r').read()))
    organes.update(json.loads(open('json/organes.json','r').read()))



# MAJ Organes

for organe in organes.keys():
    org = organes[organe]
    org.update({'membres':{},'votes':{},'qualites':{},'stats':{}})
    if not org['viMoDe.dateFin']:
        if org['codeType'] == 'GP':
            gplabels.append(org['libelleAbrev'])
            groupes[org['uid']] = org
            org.update({'csscolor':'coul'+org['libelleAbrev'],'svgcolor':svgcolors.get(org['libelleAbrev'],'NI')})

# MAJ acteurs
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



for acteur in acteurs.keys():
    act = acteurs[acteur]
    act['sexe'] = 'Homme' if act['etatCivil.ident.civ']=='M.' else 'Femme'
    act['contacts'] = []
    act['commissions'] = []
    act['nomcomplet'] = act['etatCivil.ident.civ'] + ' ' + act['etatCivil.ident.prenom'] + ' ' + act['etatCivil.ident.nom']
    act['id'] = normalize(act['nomcomplet'])
    act['age'] = int((datetime.now() - datetime.strptime(act['etatCivil.infoNaissance.dateNais'],'%Y-%m-%d')).days / 365.25)
    act['classeage'] = '%d-%d ans' % ((act['age']/10)*10,(1+(act['age']/10))*10)
    if not act['profession.socProcINSEE.famSocPro'] in statsCSP.keys():
        act['profession.socProcINSEE.famSocPro'] = u"Autres (y compris inconnu et sans profession déclarée)"

    act['csp'] = act['profession.socProcINSEE.famSocPro']
    for adr in act['adresses']:
        if 'valElec' in adr.keys():
            act['contacts'].append((adr['typeLibelle'],adr['valElec']))
    placeH = None

    fonctions =  {}
    act_commissions = {}

    for man in act['mandats']:
        organeRef = man['organes.organeRef']
        if man['typeOrgane']=='ASSEMBLEE':
            placeH = man['mandature.placeHemicycle']
            if not 'region' in act.keys():
                act['region'] = man['election.lieu.region']
                act['typeregion'] = man['election.lieu.regionType']
                act['departement'] = man['election.lieu.departement']
                act['circo'] = man['election.lieu.numCirco']

        if man['typeOrgane']=='GP':
            act['groupe'] = organeRef
        if man['typeOrgane'] in ['CONFPT','COMPER']:
            act_commissions[organeRef] = 1
        qua = man['infosQualite.codeQualite']
        fonctions[organeRef] = dict(qualite=qua,debut=format_date(man['dateDebut']),organe=organeRef)
        qua_norm = normalize(qua)

        organes[man['organes.organeRef']]['qualites'][qua_norm] = organes[man['organes.organeRef']]['qualites'].get(qua_norm,[]) + [act['uid']]
        organes[man['organes.organeRef']]['membres'][act['uid']] = (act['uid'],qua,rangs.get(qua,3 if qua.lower()!='membre' else 8))

    act['fonctions'] = fonctions.values()
    act['commissions'] = act_commissions.keys()
    act['organes'] = [ organes[o]['libelleAbrev'] for o in fonctions.keys()]

    if not placeH:
        placeH = correctionPlaces[act['uid']]
    if placeH:
        places[str(int(placeH))] = {'place':placeH,'acteur':acteur,'groupe':act['groupe']}
        act['place'] = placeH
    else:
        print act['nomcomplet']+";"+act['uid']

    # initialisations

    #act['votes'] = {}

    # déclarations hatvp
    act['hatvp'] = declarations.get(act['id'],[])

    # deputywatch
    act['deputywatch'] = deputywatch.get(act['id'],None)



for organe in organes:
    org = organes[organe]
    org['nbmembres'] = len(org['membres'].keys())
    org['membres_sort'] = sorted(org['membres'].values(),key=lambda x:(x[2],acteurs[x[0]]['etatCivil.ident.nom'],acteurs[x[0]]['etatCivil.ident.prenom']))
    if org['nbmembres']>0 and org['codeType'] in ['CONFPT','COMPER']:
        commissions[org['uid']] = org

data['acteurs_ids'] = dict((normalize(act['nomcomplet']),act) for act in acteurs.values())
data['groupes'] = groupes.values()
data['acteurs'] = acteurs.values()
data['organes'] = organes.values()
data['commissions'] = commissions.values()
data['organes_abrev'] = dict((org['libelleAbrev'],org) for org in organes.values())
data['assemblee'] = [ data['organes_abrev']['AN'] ]
