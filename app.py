from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from redis import Redis
from rq import Queue

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())


app = Flask(__name__)

#Setting URI for database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
q = Queue(connection=Redis())

class word_counter(db.Model):
    url_name_db = db.Column('url_name_var', db.String(100), primary_key= True )
    word_count_db = db.Column(db.Integer)

def __init__(self, url_name_db, word_count_db):
    self.url_name_db = url_name_db
    self.word_count_db = word_count_db

# When form is not yet accessed
@app.route('/')
def func():
    return render_template("input.html")


# When form is accessed
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
         url_ = request.form['url']
         try:
             count = q.enqueue(count_words_at_url, url_)
             record = word_counter(url_, count)
             db.session.add(record)
             db.session.commit()
             return render_template("docfile.html", text=url_, number=count)
         except requests.exceptions.ConnectionError:
             return '<h3>Connection refused</h3>'


if __name__ == '__main__':
    db.create_all()
    app.run()
