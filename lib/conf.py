# -*- coding: utf-8 -*-
debug = False
axes = [(u'Assemblée',{'titre':u"Votes de l'Assemblée",'source':'assemblee','label':'libelle','key':'libelleAbrev',
        'item_field':'organes','item_compare':'$contains'}),
        ('Groupes',{'titre':u"Votes par Groupe parlementaire",'source':'groupes','label':'libelle','key':'uid',
                        'item_field':'groupe','item_compare':'$eq'}),
        ('Commissions',{'titre':u"Votes par Commission parlementaire",'source':'commissions','label':'libelle','key':'uid',
                        'item_field':'commissions','item_compare':'$contains'}),
        ('Région',{'titre':u"Votes par région",'source':'acteurs','label':'region','key':'region',
                        'item_field':'region','item_compare':'$eq'}),
        ('Type Région',{'titre':u"Votes par type de région",'source':'acteurs','label':'typeregion','key':'typeregion',
                'item_field':'typeregion','item_compare':'$eq'}),
        (u'Département',{'titre':u"Votes par département",'source':'acteurs','label':'departement','key':'departement',
                        'item_field':'departement','item_compare':'$eq','hidechart':True}),
        ('Ages',{'titre':u"Votes par age",'source':'acteurs','label':'classeage','key':'classeage',
                'item_field':'classeage','item_compare':'$eq'}),
        ('CSP',{'titre':u"Votes par Catégorie Socio-Professionelle",'source':'acteurs','label':'csp','key':'csp',
        'item_field':'csp','item_compare':'$eq'}),
        ('Sexe',{'titre':u"Votes par sexe",'source':'acteurs','label':'sexe','key':'sexe',
        'item_field':'sexe','item_compare':'$eq'}),
        

       ]


data = {}
