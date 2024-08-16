from flask import Flask, redirect, request, render_template, jsonify
from werkzeug.routing import BaseConverter
from urllib.parse import quote
from cache import *
from search import *

class ListConverter(BaseConverter):
    def to_python(self, value): return value.split('+')
    def to_url(self, values): return '+'.join(value for value in values)

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter

cache = load_cache('words.csv', 'wordcache')
#cache = load_cache('/home/bob/programming/wordsquares/dicts/words_small', 'wordcache')

@app.route("/")
def home_page():
    return render_template('index.html')

@app.route("/vragen")
def questions():
    return render_template('vragen.html')

@app.route('/woord')
@app.route('/woord/<word>')
def word_page(word = ''):
    if not word:
        return render_template('woord.html', word='', props=None, facts=None)
    if not word in cache.words:
        return render_template('woord.html', word=word, props=None, facts=None)
    return render_template('woord.html', word=word, props=get_properties(cache, word), facts=cache.words[word])

@app.route('/zoek')
@app.route('/zoek/<query>')
def search_page(query=''):
    if not query and (query := request.args.get('zoekopdracht', default = '', type = str)):
        return redirect(f"/zoek/{quote(query)}", code=302)

    return render_template('livesearch.html', prop=query, words=search(cache, query) if query else [])

@app.route('/api/zoek/<query>/<order>')
def search_api(query, order):
    results = list(search(cache, query))

    if not order or order == 'alphabetical':
        results = sorted(results)
    elif order == 'reverse_alphabetical':
        results = sorted(results, reverse=True)
    elif order == 'length':
        results = sorted(results, key=len)
    elif order == 'reverse_length':
        results = sorted(results, key=len, reverse=True)
    
    results = results[:1000]
    return jsonify(list(results))

# url_for('static', filename='style.css')