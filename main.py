import string
import random
import sqlite3
from flask import Flask, render_template, request, redirect


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'shortener.db'


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
    conn.close()


def store_url(long_url, short_alias):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('INSERT INTO urls (long_url, short_alias) VALUES (?, ?)', (long_url, short_alias))
    conn.commit()
    conn.close()


def get_long_url(short_alias):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT long_url FROM urls WHERE short_alias = ?', (short_alias,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['url']
        short_alias = generate_short_alias()
        store_url(long_url, short_alias)
        return render_template('index.html', short_url=request.host_url + short_alias)
    return render_template('index.html')


@app.route('/<short_alias>')
def redirect_to_long_url(short_alias):
    long_url = get_long_url(short_alias)
    if long_url:
        return redirect(long_url)
    return 'URL not found.'


if __name__ == '__main__':
    create_database()
    app.run()
