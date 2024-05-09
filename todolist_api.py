# RESTful API
from flask import Flask, render_template, redirect, g, request, url_for, jsonify, Response
import sqlite3
import urllib
import json

DATABASE = 'todolist.db'

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/api/items/<email>")  # default method is GET
def get_items(email):
    email = urllib.parse.unquote(email)
    db = get_db()
    cur = db.execute('SELECT what_to_do, due_date, status FROM entries WHERE useremail="'+email+'"')
    entries = cur.fetchall()
    tdlist = [dict(what_to_do=row[0], due_date=row[1], status=row[2])
              for row in entries]
    response = Response(json.dumps(tdlist),  mimetype='application/json')
    return response


@app.route("/api/items/", methods=['POST'])
def add_item():
    db = get_db()
    db.execute('insert into entries (what_to_do, due_date, useremail) values (?, ?, ?)',
               [request.json['what_to_do'], request.json['due_date'], request.json['useremail']])
    db.commit()
    return jsonify({"result": True})


@app.route("/api/items/<email>/<item>", methods=['DELETE'])
def delete_item(email,item):
    email, item = urllib.parse.unquote(email), urllib.parse.unquote(item)
    db = get_db()
    db.execute("DELETE FROM entries WHERE useremail='"+email+"' AND what_to_do='"+item+"'")
    db.commit()
    return jsonify({"result": True})


@app.route("/api/items/<email>/<item>", methods=['PUT'])
def update_item(email,item):
    # we do not need the body so just ignore it
    email, item = urllib.parse.unquote(email), urllib.parse.unquote(item)
    db = get_db()
    db.execute("UPDATE entries SET status='done' WHERE useremail='"+email+"' AND what_to_do='"+item+"'")
    db.commit()
    return jsonify({"result": True})


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001)
