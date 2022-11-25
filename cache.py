import sys
import properties
import util
from collections import *
import re, csv

# words is assumed to be a purely ^[a-z]*$ affair
# in the future a CSV may be provided that maps such simplified
# words back to their original spellings and source as metadata
if __name__ == "__main__":
    words = load_csv_dict(sys.argv[1])
    out = {}
    for f,_ in properties.functions.values():
        print(f.__name__)
        out |= f(words)

    # ^rotaties_[a-z]+\t([a-z]* ){2,}
    with open('wordcache', 'w') as f:
        f.write('\n'.join(' '.join(k) + '\t' + ' '.join(v) for k,v in out.items()))

# we have 3 types of labels
# - singular labels apply to a word when it is part of that set
# - dual labels with associated _repr function require a (label, repr(w)) lookup.
# - dual labels with an integer value require a lookup in each of such labels

# therefor we also create 3 associated caches in which we do our lookups
# - label -> set cache
# - label -> (repr(w) -> list)
# - label -> (w -> int)
# the last 2 groups are harmonized

# this again represents 3 types of visualisations too and different search functionality.

WordCache = namedtuple('WordCache', ('words', 'bool_cache', 'group_cache', 'flat_cache'))

def load_csv_dict(filename):
    out = {}
    with open(filename, newline='') as csvfile:
        keys = next(csvfile).split('\t')
        for line in csvfile:
            row = {k:v.strip() for k,v in zip(keys, line.split('\t'))}
            out[row['word']] = row
    return out

def load_cache(all_words_file, cache_file = 'wordcache'):
    print('loading words')
    words = load_csv_dict(all_words_file)

    print('loading primary cache')
    bool_cache = {}
    group_cache = defaultdict(dict)
    for line in open(cache_file):
        if not line or line.endswith('\t'): continue
        label,content = line[:-1].split('\t')
        parts = tuple(label.split(' '))
        content = content.split(' ')

        if len(parts) == 1:
            bool_cache[parts[0]] = set(content)
        elif len(parts) == 2:
            group_cache[parts[0]][parts[1]] = content

    print('creating secondary cache')
    # label[0] -> Counter(word -> amount of instances)
    flat_cache = dict()
    for label in group_cache.keys(): flat_cache[label] = Counter()
    for label, group in group_cache.items():
        for sub_group in group.values():
            flat_cache[label].update(sub_group)

    return WordCache(words, bool_cache, group_cache, flat_cache)

# Get the value of each word property for word w
def get_properties(cache, w):
    out = dict()
    for k,v in cache.bool_cache.items():
        out[k] = w in v

    F = properties.functions
    for k,v in cache.group_cache.items():
        wkey = F[k][1](w) if k in F and F[k][1] else w
        out[k] = v[wkey] if wkey in v else []

    return out
