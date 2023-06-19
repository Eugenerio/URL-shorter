import string
import random
import sqlite3
from flask import Flask, render_template, request, redirect
import validators
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'shortener.db'


def get_url_preview(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('title').get_text()
    description = soup.find('meta', attrs={'name': 'description'})
    description = description['content'] if description else ''

    return title, description


def store_url(long_url, short_alias):
    if not validators.url(long_url):
        return 'Invalid URL'

    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('INSERT INTO urls (long_url, short_alias) VALUES (?, ?)', (long_url, short_alias))
    conn.commit()
    c.execute('INSERT INTO history (long_url, short_alias) VALUES (?, ?)', (long_url, short_alias))
    conn.commit()
    conn.close()


def generate_short_alias():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=7))


def create_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 long_url TEXT,
                 short_alias TEXT UNIQUE)''')
    conn.commit()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 long_url TEXT,
                 short_alias TEXT,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


def get_long_url(short_alias):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT long_url FROM urls WHERE short_alias = ?', (short_alias,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


@app.route('/clean-history', methods=['POST'])
def clean_history():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('DELETE FROM history')
    conn.commit()
    conn.close()
    return redirect('/', code=302)


def get_history():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT * FROM history ORDER BY timestamp DESC')
    result = c.fetchall()
    conn.close()
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['url']
        short_alias = generate_short_alias()
        store_url(long_url, short_alias)
        return render_template('index.html', short_url=request.host_url + short_alias, history=get_history())

    return render_template('index.html', history=get_history(), short_url=None, clean_history_button=True)


@app.route('/url-preview', methods=['POST'])
def url_preview():
    url = request.form['url']
    title, description = get_url_preview(url)
    return render_template('url_preview.html', title=title, description=description)


@app.route('/<short_alias>')
def redirect_to_long_url(short_alias):
    long_url = get_long_url(short_alias)
    if long_url:
        return redirect(long_url)
    return 'URL not found.'


if __name__ == '__main__':
    create_database()
    app.run()
