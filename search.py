from lark import Transformer, Lark, Token
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken

SEARCH_DSL = Lark(r'''
all: value
?value: bracketed | num_op | label

bracketed: "(" value (set_op value?)* ")"
// Hoe groot is de groep waar in een woord voorkomt
num_op: label comparison number
label: /[A-Za-z0-9_]+/

set_op: /[&|]/
comparison: /[<>=]/
number: /[0-9]+/

%import common.WS
%ignore WS''', start="all", parser="lalr")

def get_comp_f(op, n):
    if op == '=': return lambda w: len(w) == n
    if op == '<': return lambda w: len(w) < n
    if op == '>': return lambda w: len(w) > n

def load_label(cache, label):
    if label in cache.bool_cache:
        return cache.bool_cache[label]
    if label in cache.flat_cache:
        return set(cache.flat_cache[label].keys())
    if label.count('_') == 1:
        a,b = label.split('_')
        if a in cache.group_cache and b in cache.group_cache[a]:
            return set(cache.group_cache[a][b])
    return {}

def reduce_query(cache, tree):
    print(tree)
    # a value is always has a singular resolvable 
    state = []
    for child in tree.children:
        if child.data.value == 'bracketed':
            state.append(reduce_query(cache, child))
        elif child.data.value == 'label':
            state.append(load_label(cache, child.children[0].value))
        elif child.data.value == 'num_op':
            label = child.children[0].children[0].value
            op = child.children[1].children[0].value
            n = int(child.children[2].children[0].value)
            fop = get_comp_f(op, n)
            if label == 'n':
                state.append({w for w in cache.words if fop(w)})
            else:
                state.append(set(sum([group for group in cache.group_cache[label].values() if fop(group)], [])))
        else:
            state.append(child.children[0].value)

    result = set(state[0])
    for op,v in zip(state[1::2], state[2::2]):
        if op == '&': result &= v
        if op == '|': result |= v
    return result

def search(cache, query):
    return reduce_query(cache, SEARCH_DSL.parse(f'({query})').children[0])

