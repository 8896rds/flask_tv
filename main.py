import sqlite3
from pathlib import Path
import cloudscraper
from re import findall as re_findall
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testsecretkeyforflask'

this_folder = Path(__file__).parent.resolve()

m3u_file = this_folder / 'static/tv.m3u'

#create DB connection
def get_db_connection():
    database_file = this_folder/'tv_database.db'
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    return conn

# Get data from DB for particular id
def get_post(url_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM tv WHERE id = ?',
                        (url_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

# Add new record to a M3U file
def write_file(name, url,group):
    with open(m3u_file,'a+') as f:
        f.write('\n#EXTINF:-1, group-id="{}" tvg-logo="",{}\n'.format(group,name))
        f.write(url)
        f.write('\n')

#this method is used to update single url
def update_file(name, url):

    #open existing file
    indx = 0
    with open(m3u_file,'r') as f:
        data = f.readlines()

        for idx,text in enumerate(data):
            if name in text:
                indx = idx

    #checking if entry was found, then update the url in next line
    if indx != 0 and indx != len(data):
        indx+=1
        data[indx] = url

    # writing file
    with open(m3u_file,'w+') as f:
        f.writelines(data)

# this method is used to delete single url
def delete_url_file(name):

    # open existing file
    indx = 0
    with open(m3u_file, 'r') as f:
        data = f.readlines()

        for idx, text in enumerate(data):
            if name in text:
                indx = idx

    # checking if entry was found, then update the url in next line
    if indx != 0 and indx != len(data):
        del data[indx]
        del data[indx]

    # writing file
    with open(m3u_file, 'w+') as f:
        f.writelines(data)

# Index Page
@app.route('/')
def index():
    conn = get_db_connection()
    urls = conn.execute('SELECT * FROM tv').fetchall()
    conn.close()
    return render_template('index.html', urls=urls)

# Single Entry Page
@app.route('/<int:url_id>', methods=('GET', 'POST'))
def url(url_id):
    url = get_post(url_id)
    #check if method is get or post
    if request.method == 'POST':
        form = request.form
        conn = get_db_connection()
        if form['action'] == 'delete':
            conn.execute('delete from tv where id=?',(url_id,))
            conn.commit()
            delete_url_file(url[1])
        elif form['action'] == 'update':
            if not form['link']:
                flash('Link is required!')
            else:
                conn.execute('update tv set link = ? where id = ?',
                             (form['link'],url_id))

                update_file(url[1],form['link'])

                flash('Link Updated')

        conn.close()
        return redirect(url_for('index'))

    return render_template('url.html', url=url)

#Create New Entry Page
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        form = request.form

        if not form['link']:
            flash('Link is required!')
        else:

            conn = get_db_connection()
            write_file(form['name'], form['link'], form['group'])
            conn.execute('INSERT INTO tv (channel_name, link, channel_group) VALUES (?, ?, ?)',
                         (form['name'], form['link'], form['group']))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

if __name__ == "__main__":
    app.run(debug=True)