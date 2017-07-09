# -*- coding: utf-8 -*-
debug = False
axes = [(u'Assemblée',{'source':'assemblee','label':'libelle','key':'libelleAbrev',
        'item_field':'organes','item_compare':'$contains'}),
        ('Groupes',{'source':'groupes','label':'libelle','key':'uid',
                        'item_field':'groupe','item_compare':'$eq'}),
        ('Commissions',{'source':'commissions','label':'libelle','key':'uid',
                        'item_field':'commissions','item_compare':'$contains'}),
        ('Region',{'source':'acteurs','label':'region','key':'region',
                        'item_field':'region','item_compare':'$eq'}),
        (u'Département',{'source':'acteurs','label':'departement','key':'departement',
                        'item_field':'departement','item_compare':'$eq'}),

        ('Ages',{'source':'acteurs','label':'classeage','key':'classeage',
                'item_field':'classeage','item_compare':'$eq'}),
        ('CSP',{'source':'acteurs','label':'csp','key':'csp',
        'item_field':'csp','item_compare':'$eq'}),
        ('Sexe',{'source':'acteurs','label':'sexe','key':'sexe',
        'item_field':'sexe','item_compare':'$eq'}),

       ]


data = {}
