from collections import Counter
import re
import unicodedata
import functools
import csv

VOWELS = set('aeuioáéóíúàèùìòäëïöüâêîôûAEUIOÄËÜÏÖ')
VOWELS_DASH = set('aeuioáéóíúàèùìòäëïöüâêîôûAEUIOÄËÜÏÖ-')

def normalize_vowels(w):
    nfkd_form = unicodedata.normalize('NFKD', w.lower())
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def to_az(w):
    nfkd_form = unicodedata.normalize('NFKD', w.lower())
    return ''.join(c for c in nfkd_form if c in 'abcdefghijklmnopqrstuvwxyz')

def is_y_vowel(word, i):
    # exceptions first
    if i >= 2 and word[i-2:i+1] == 'boy': return False
    for m in re.finditer(r'bosyaws|canyon|fasyong|[Kk]enya|kufiyyah|yard|pinyin|sannyasin', word):
        if m.start() < i < m.end(): return False
    for m in re.finditer(r'(?<!g)eye', word):
        if m.start() < i < m.end(): return True
    # general rule
    if (i == 0 or word[i-1] in VOWELS_DASH) and (i < len(word)-1 and word[i+1] in VOWELS):
        return False
    return True

scrabble_scores = {'e':1,'n':1,'a':1,'o':1,'i':1,'d':2,'r':2,'s':2,'t':2,'g':3,'k':3,'l':3,'m':3,'b':3,'p':3,'u':4,'f':4,'h':4,'j':4,'v':4,'z':4,'c':5,'w':5,'x':8,'y':8,'q':10}

def is_lipo(s,w): return len(set(w) - set(s)) == 0 and w != ''

def mapstr(f,t,w,strict=True):
    if strict and not is_lipo(f, w):
        return ''
    ft = {x:y for x,y in zip(f,t)}
    return ''.join(ft[c] if c in ft else c for c in w)

def iso(w):
    if w == '': return 1
    c = set(Counter(w).values())
    return list(c)[0] if len(c) == 1 else None


def load_dict(filename):
    return {w for w in open(filename).read().split('\n') if w}

@functools.cache
def is_vowel(w, i):
    return w[i] in 'aeuioĳ{' or (w[i] == 'y' and is_y_vowel(w, i))

def are_vowel(w): return [is_vowel(w,i) for i,c in enumerate(w)]

@functools.cache
def vowels(w): return ''.join(c for i,c in enumerate(w) if is_vowel(w,i))

def r90(w): return mapstr('onuehiwxz', 'ozcmihexn', w)
def r180(w): return mapstr('abdeghijlmnoprsuwxyz', 'egbabyirlwuodjsnmxhz', w)[::-1]
def r270(w): return mapstr('ozcmihexn', 'onuehiwxz', w)[::-1]

def best_run(w, f, minimum = None):
    best, run = 0, 0
    for i in range(len(w)):
        if f(w, i):
            run += 1
        else:
            best = max(best, run)
            run = 0
    return None if minimum and minimum >= max(best, run) else max(best, run)

def group_n(w, n): return [w[i:i+n] for i in range(0, len(w), n)]

