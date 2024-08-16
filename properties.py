from collections import *
from itertools import *
from util import *
import re, csv

def geordend(w): return sorted(w) == list(w)

def zelfkeerwoord(w): return w[::-1] == w

def zelfhalfslag(w): return r180(w) == w
def zelfkwartslag(w): return r270(w) == w

def vierkant(w):
	# 1 & 2 are trivial and always true
	# 3 5 7 13 are prime and so can't be rectangled, 4 6 8 9 have unique solutions
	# 10 is 5x2, too tall
	# 12 has 2 solutions, we simply pick 3x4 as the correct form
	if len(w) == 4 and re.match(r'^.(.)\1.$', w): return True
	if len(w) == 6 and re.match(r'^.(.)(.)\1\2.$', w): return True
	if len(w) == 8 and re.match(r'^.(.)\1(.)\1\2\2.$', w): return True
	if len(w) == 9 and re.match(r'^.(.)(.)\1.(.)\2\3.$', w): return True
	if len(w) ==12 and re.match(r'^.(.)(.)\1\1\1\2\2\2\1\2.^', w): return True
	if len(w) ==16 and re.match(r'^.(.)(.)(.)\1.(.)(.)\2\4.(.)\3\5\6.$', w): return True
	if len(w) ==25 and re.match(r'^.(.)(.)(.)(.)\1.(.)(.)(.)\2\5.(.)(.)\3\6\8.(.)\4\7\9\10.$', w): return True
	return False

def isogram(w): return iso(w)
def klinkerisogram(w): return len(set(vowels(w))) == 5 and iso(vowels(w))

def alipo(w): return is_lipo('a', vowels(w)) and 'a' in w
def elipo(w): return is_lipo('e', vowels(w)) and 'e' in w
def olipo(w): return is_lipo('o', vowels(w)) and 'o' in w
def ulipo(w): return is_lipo('u', vowels(w)) and 'u' in w
def ilipo(w): return is_lipo('i', vowels(w)) and 'i' in w and not 'ij' in w
def ijlipo(w): return is_lipo('ĳ{', vowels(w)) and ('ĳ' in w or '{' in w)

def qwertylipo(w): return is_lipo('qwertyuiop', w)
def asdflipo(w): return is_lipo('asdfghjkl', w)
def horizontalipo(w): return is_lipo('bcdehikox', w)
def verticalipo(w): return is_lipo('ahimotuvwxy', w)
def stoklooslipo(w): return is_lipo('acemnorsuvwxz', w)
def rekenmachinelipo(w): return is_lipo('odizehsglb', w)
def muzieklipo(w): return is_lipo('abcdefg', w)

def klinkerstapel(w): return best_run(w, is_vowel, 4)
def medeklinkerstapel(w): return best_run(w, lambda w,i: not is_vowel(w, i), 6)

#UNARY_FUNCTIONS = [is_ordered, is_palindrome, is_rot180_sym, is_rot270_sym, is_transposable, is_1_isogram, is_2_isogram, is_3_isogram, is_vowel_isogram, is_a_lipo, is_e_lipo, is_o_lipo, is_u_lipo, is_i_lipo, is_ij_lipo, is_toprow_lipo, is_midrow_lipo, is_horizontal_lipo, is_vertical_lipo, is_baseline_lipo, is_number_lipo, is_music_lipo, is_rot90_valid, is_rot180_valid, is_rot270_valid, vowel_heap, consonant_heap]
UNARY_FUNCTIONS = [geordend, zelfkeerwoord, zelfhalfslag, zelfkwartslag, vierkant, isogram, klinkerisogram, alipo, elipo, olipo, ulipo, ilipo, ijlipo, qwertylipo, asdflipo, horizontalipo, verticalipo, stoklooslipo, rekenmachinelipo, muzieklipo, klinkerstapel, medeklinkerstapel]

# convert unary functions to correct format automatically
def simple_properties(words):
	out = defaultdict(list)
	for f in UNARY_FUNCTIONS:
		print('   ', f.__name__)
		t = type(f(''))
		# a bool is an attribute that can be expressed as a set of words
		if t is bool:
			out[(f.__name__,)] = [w for w in words if f(w)]
		else:
			for w in words:
				if fw := f(w):
					out[(f.__name__, str(fw))].append(w)
	return out

def _remove_singles(out): return {k:v for k,v in out.items() if len(v) > 1}

def _group_property(words, name, repr):
	out = defaultdict(list)
	for w in words:
		out[(name, repr(w))].append(w)
	return _remove_singles(out)

def anagrams_repr(w): return ''.join(sorted(w))
def anagrams(words): return _group_property(words, 'anagrammen', anagrams_repr)

def reversable_repr(w): return min(w, w[::-1])
def reversable(words): return _group_property(words, 'keerwoord', reversable_repr)

def rotations_repr(w): return min(w[i:] + w[:i] for i in range(len(w)))
def rotations(words): return _group_property(words, 'rotaties', rotations_repr)

def alfa_rotations_repr(w): return ''.join(chr((ord(c)-ord(w[0]))%26+ord('a')) for c in w)
def alfa_rotations(words): return _group_property(words, 'alfarotaties', alfa_rotations_repr)

def atbash_repr(w): return min(alfa_rotations_repr(w), alfa_rotations_repr(''.join(chr(25-(ord(c)-ord('a'))+ord('a')) for c in w)))
def atbash(words): return _group_property(words, 'alfaomkering', atbash_repr)

def zipper_repr(w): return w
def zipper(words):
	out = dict()
	for w in words:
		for n in range(2,4):
			parts = [w[i::2] for i in range(n)]
			if all(p in words for p in parts):
				out[('rits', w)] = parts
	return out

def _stable_parts(words, name, f):
	out = dict()
	for w in words:
		parts = list(f(w))
		if all(p in words for p in parts):
			out[(name, w)] = parts
	return out

def prefix_stability_repr(w): return w
def prefix_stability(words): return _stable_parts(words, 'prefixstabiel', lambda w: [w[:i] for i in range(2, len(w)+1)])

def suffix_stability_repr(w): return w
def suffix_stability(words): return _stable_parts(words, 'suffixstabiel', lambda w: [w[i:] for i in range(0, len(w)-1)])

# lots of bullshit in the shape of
# megamegamegamegaposter I need a blacklist...
def hypograms(words):
	out = defaultdict(list)
	for w in words:
		for n in range(1, 6):
			k = max(len(list(v)) for _,v in groupby(group_n(w, n)))
			if k >= 5-n and k > 1:
				out[('hypogram', f'{n}{k}')].append(w)
	return out

functions = {
	'simpel': (simple_properties, None), 
	'anagrammen': (anagrams, anagrams_repr), 
	'keerwoord': (reversable, reversable_repr), 
	'rotaties': (rotations, rotations_repr), 
	'alfarotaties': (alfa_rotations, alfa_rotations_repr), 
	'alfaomkering': (atbash, atbash_repr), 
	'rits': (zipper, zipper_repr), 
	'prefixstabiel': (prefix_stability, prefix_stability_repr), 
	'suffixstabiel': (suffix_stability, suffix_stability_repr), 
	'hypogram': (hypograms, None),
}
