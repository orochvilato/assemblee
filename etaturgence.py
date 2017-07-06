# -*- coding: utf-8 -*-
#

vote = {'pour':"""Mme Bérangère Abba, M. Damien Adam, Mme Aude Amadou, M. François André,
M. Pieyre-Alexandre Anglade, M. Gabriel Attal, Mme Laetitia Avia, M. Xavier Batut,
Mme Aurore Bergé, M. Hervé Berville, M. Éric Bothorel, M. Florent Boudié, Mme Pascale
Boyer, Mme Yaël Braun-Pivet, Mme Émilie Cariou, Mme Samantha Cazebonne, M. Anthony
Cellier, Mme Fannette Charvier, M. Guillaume Chiche, Mme Bérangère Couillard,
Mme Yolaine de Courson, M. Dominique Da Silva, Mme Jennifer De Temmerman,
Mme Typhanie Degois, M. Frédéric Descrozaille, M. Benjamin Dirx, M. Jean-Baptiste
Djebbari, Mme Jacqueline Dubois, Mme Christelle Dubos, Mme Coralie Dubost, Mme Nicole
Dubré-Chirat, M. Christophe Euzet, Mme Valéria Faure-Muntian, M. Jean-Michel Fauvergue,
Mme Albane Gaillot, Mme Anne Genetet, M. Raphaël Gérard, M. Fabien Gouttefarde,
Mme Olivia Gregoire, M. Pierre Henriet, Mme Danièle Hérin, M. Dimitri Houbron, M. Sacha
Houlié, Mme Caroline Janvier, M. Christophe Jerretie, M. François Jolivet, M. Hubert JulienLaferriere,
Mme Catherine Kamowski, M. Guillaume Kasbarian, Mme Fadila Khattabi,
M. Rodrigue Kokouendo, Mme Annaïg Le Meur, Mme Marie Lebec, Mme Marion Lenne,
Mme Monique Limon, M. Sylvain Maillard, M. Jacques Maire, M. Jacques Marilossian,
M. Denis Masséglia, M. Jean François Mbaye, M. Thomas Mesnier, Mme Monica Michel,
M. Jean-Michel Mis, Mme Sandrine Mörch, Mme Naïma Moutchou, Mme Isabelle MullerQuoy,
Mme Cécile Muschotti, M. Mickaël Nogal, Mme Claire O'Petit, Mme Valérie Oppelt,
M. Didier Paris, Mme Zivka Park, M. Patrice Perrot, M. Pierre Person, Mme Michèle Peyron,
M. Damien Pichereau, M. Bruno Questel, M. Rémy Rebeyrotte, M. Hugues Renson,
Mme Stéphanie Rist, Mme Marie-Pierre Rixain, Mme Laëtitia Romeiro Dias, Mme Laurianne
Rossi, M. Pacôme Rupin, M. Bruno Studer, M. Stéphane Testé, M. Vincent Thiébaut,
Mme Valérie Thomas, M. Alain Tourret, M. Manuel Valls, Mme Annie Vidal, M. Cédric
Villani,M. Guillaume Vuilletet,
M. Thibault Bazin, Mme Valérie Beauvais, Mme Émilie Bonnivard, M. Jean-Yves Bony,
M. Xavier Breton, M. Éric Ciotti, M. Vincent Descoeur, M. Fabien Di Filippo, M. Pierre-Henri
Dumont, M. Jean-Jacques Ferrara, M. Nicolas Forissier, M. Guillaume Larrivé,
Mme Constance Le Grip, M. Gilles Lurton, M. Maxime Minot, M. Alain Ramadier,
M. Frédéric Reiss, M. Martial Saddier,M. Patrice Verchère,
M. Erwan Balanant, M. Philippe Bolo, Mme Isabelle Florennes, M. Philippe MichelKleisbauer,
Mme Maud Petit, Mme Michèle de Vaucouleurs, Mme Laurence Vichnievsky,
M. Sylvain Waserman,
Mme Sophie Auconie, M. Pierre-Yves Bournazel, M. Meyer Habib, M. Yves Jégo, M. Napole
Polutele,Mme Maina Sage,
Mme Delphine Batho, M. Christophe Bouillon, M. Luc Carvounas, Mme Marietta Karamanli,
M. Serge Letchimy,M. Boris Vallaud,
M. Bruno Bilde, M. Sébastien Chenu, Mme Marine Le Pen, Mme Emmanuelle Ménard,
M. Ludovic Pajot""",
"contre":"""Mme Clémentine Autain, M. Ugo Bernalicis, M. Éric Coquerel, M. Alexis Corbière,
Mme Caroline Fiat, M. Bastien Lachaud, Mme Danièle Obono, M. Loïc Prud'homme,
M. Adrien Quatennens, Mme Sabine Rubin,Mme Bénédicte Taurine,M. Jean-Paul Dufrègne,M. Stéphane Peu"""
}

# Gestion du vote de confiance (trop pressé)
from lib.tools import normalize

votec = dict((k,normalize(v.decode('utf8').replace('\n','')).split(',')) for k,v in vote.iteritems())
voteurg = {}
for k in votec:
    for d in votec[k]:
        voteurg[d] = k
