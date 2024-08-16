import sys, unicodedata, re
from collections import *
import properties
from util import *

# we filteren alle echte onzin woorden
# zoals met uitheemse letters of cijfers
exceptions = "ångström blaséë bühne döner föhn einzelgänger röntgen fröbel tölt glühwein knäckebröd knödel köfte kür löss löyly müsli römer rösti rücksichtslos salonfähig schrödinger slöjd smörgåsbord smörrebröd tölt über açai alençonkant aperçu reçu cachaça commerçant curaçao façad façonn français garçon glaçure kemençe maçon Provença remplaçant déjà-vu ère voilà crèche scène bèta carrièr crème ampèr appèl après agnès barège-doek birème blèr blèt bohème bustières calèche carènediagram chèque clientèle cliëntèle concrète cortège crèpe deux-pièces dodenstèle elocipède encephalocèle escabèche èta excès siècle géomètres grège grès hazè hoofdcortège hoofdcortèges imitatie-suèdeleder kassières lettre-exprès liège meningomyelocèle merokèle misères mopè myelomeningocèle nègre oelèëbalang omphalocèle répète rivièra schrobbelèr sèvres snèkpersoneel solfège stèle stratagème suède tantième thèta velocipède vélocipède zèta enquête bêta apprêteerder apprêtuur arrêt gêne bête bêtise brûlée campêche chaîne flûte rôtisseur côte coûte crême crêpe contrôle croûton debâcle dendê-olie depêche dépôt hôtel dînatoire drôleforel eilandsglooiîng embête enquêtrice entraînement entrecôte extrêmes fête(e)r fraîche frêle geëmbêteerd gefêteerd gênant goût depôt guêpière île zône ragoût maître materiêle mêlé mêlee mêle même moê pâtés piqûre plaît prêt-à-porter protêt rêverie rhône thêta skûtsje suprême tête biná bodhrá buní colón córdoba empaná karkó lúss málaga politikós seú stobá stobá's tambú turrón yucatán smørrebrød brønsted Faerøer chòler hòfi doña doño mansaliña muña Niño piñata señor vicuña Māori".split(' ')
def is_normal_dutch_word(w):
	def char_valid(w, i):
		c = w[i]
		if c in 'abcdefghijklmnopqrstuvwxyzé': return True
		if c in 'ëïöüä': return i > 0 and w[i-1] in 'eaiouy'
		if c == '-': return w.count('-') == 1 and i != 0 and i != len(w)-1
		if c == "'": return i == len(w)-2 and w[-1] == 's'
		return False

	for e in [e for e in exceptions if e in w]:
		w = w.replace(e, 'e')

	return all(char_valid(w.lower(), i) for i in range(len(w)))

# we laden onze woordenboeken in, we nemen aan dat deze in UTF-8 complete notatie zijn, één woord per regel
# ook berekenen we alvast de 'puzzelnotatie'
def to_az(w):
    nfkd_form = unicodedata.normalize('NFKD', w.lower())
    return ''.join(c for c in nfkd_form if c in 'abcdefghijklmnopqrstuvwxyz')

words = defaultdict(lambda: {'anw':0, 'dvd':0, 'groeneboekje':0,'wiktionary':0,'iate':0, 'corpus':0,'generated':0})
def load_dict(filename):
	print("   ", filename)
	for w in open(filename).read().split('\n'):
		if w and is_normal_dutch_word(w):
			k = to_az(w)
			if not 'spelling' in words[k]: words[k]['spelling'] = set()
			words[k]['spelling'].add(w)
			words[k][filename.split('/')[-1]] = 1

print("Loading dictionaries")
load_dict('sources/groeneboekje')
load_dict('sources/anw')
load_dict('sources/dvd')
load_dict('sources/wiktionary')
load_dict('sources/iate')
load_dict('sources/corpus')
#load_dict('sources/generated')

for v in words.values():
	v['spelling'] = ','.join(v['spelling'])

# Dan hebben we een aantal eigenschappen die we kunnen afleiden uit de orignele spellings grafemen maar niet meer uit de az-representatie
# is_abbr is niet zuiver, maar goed genoeg voor nu
def is_abbr(w): return '.' in w or any(c.isupper() for c in w[1:]) or all(not c in 'aeuioy' for c in to_az(w))
def is_name(w): return w[0].isupper()
def has_symbols(w): return '-' in w or "'" in w
def has_diacretics(w): return w.lower().replace('-', '').replace("'", '') == to_az(w)
def is_perfect(w): return w == to_az(w)

def syllables(w):
	total = 0
	for part in re.split(r'(?=[A-Z])|[-, ]', w):
		part = part.lower()
		part = ''.join(['a' if part[i] == 'y' and is_y_vowel(part, i) else part[i] for i in range(len(part))])
		total += len(re.findall(r'[äëïöü]?[aeuioáéóíúàèùìòâêîôû]+', part))
	return total

print("Generating spellinginfo")
for label, f in (('is_abbr', is_abbr), ('is_proper_noun', is_name), ('has_symbols', has_symbols), ('has_diacretics', has_diacretics), ('is_perfect', is_perfect)):
	print('   ', label)
	for k, props in words.items():
		props[label] = '01'[all(f(w) for w in props['spelling'])]

print('   syllables')
for k, props in words.items():
	props['syllables'] = str(syllables(props['spelling'].split(',')[0]))

print("Loading additional properties")

# TODO, uit  dpw.csv, wiktionary, ANW:
# - IPA (incl. aantal lettergrepen, klemtoon), mogelijk missende genereren (phonetisaurus)
#	- aantal lettergrepen
#	- rijmuitgang
#	- klemtoon
#	- homoniemen (klink en schrijft hetzelfde)
#	- heterografen (schrijft hetzelfde, klinkt anders)
#	- heterografen (schrijft anders klinkt hetzelfde)
#	- IJ-spelling
#	- engels homofoon
# - woordsoort
# - synoniemen/antoniemen
# - woordontleding (mogelijke generatief)

print("storing result")
# sla een CSV'tje op en klaar!
f = open('words.csv', 'w')
f.write('word\t' + '\t'.join(k for k,_ in sorted(props.items())) + '\n')
for k, props in words.items():
	f.write(k + '\t' + '\t'.join(str(v) for _,v in sorted(props.items())) + '\n') 
f.close()
