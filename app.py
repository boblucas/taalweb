from flask import Flask, redirect, request, render_template
from werkzeug.routing import BaseConverter
from urllib.parse import quote
from cache import *
from search import *

class ListConverter(BaseConverter):
    def to_python(self, value): return value.split('+')
    def to_url(self, values): return '+'.join(value for value in values)

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter

cache = load_cache('words.csv', 'wordcache_small')

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

    return render_template('search.html', prop=query, words=search(cache, query) if query else [])

