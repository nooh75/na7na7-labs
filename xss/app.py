from flask import Flask, request, render_template, redirect
import sqlite3
import os

app = Flask(__name__)

# إعداد قاعدة البيانات
if not os.path.exists("db.db"):
    conn = sqlite3.connect("db.db")
    conn.execute("CREATE TABLE comments (msg TEXT)")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template("home.html")

# Reflected XSS
@app.route('/reflected', methods=['GET', 'POST'])
def reflected():
    data = ''
    if request.method == 'POST':
        data = request.form['search']  # ⚠️ XSS هنا
    return render_template("reflected.html", data=data)

# Stored XSS
@app.route('/stored', methods=['GET', 'POST'])
def stored():
    conn = sqlite3.connect("db.db")
    if request.method == 'POST':
        msg = request.form['msg']
        conn.execute("INSERT INTO comments (msg) VALUES (?)", (msg,))
        conn.commit()
    comments = conn.execute("SELECT msg FROM comments").fetchall()
    conn.close()
    return render_template("stored.html", comments=comments)

# DOM-Based XSS
@app.route('/dom')
def dom():
    return render_template("dom.html")

# Query string XSS
@app.route('/result')
def result():
    name = request.args.get('name', '')
    return render_template("result.html", name=name)


@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    return {"result": f"You searched for: {query}"}  # no encoding (⚠️ XSS in JSON viewer)


@app.route('/csp')
def csp():
    resp = app.make_response(render_template("csp.html"))
    # سياسة تمنع inline scripts
    resp.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self';"
    return resp

@app.route('/iframe')
def iframe():
    return render_template("iframe.html")


@app.route('/blind', methods=['GET', 'POST'])
def blind():
    if request.method == 'POST':
        payload = request.form['data']
        conn = sqlite3.connect("db.db")
        conn.execute("INSERT INTO comments (msg) VALUES (?)", (payload,))
        conn.commit()
        conn.close()
        return "Thanks for submitting!"
    return render_template("blind_submit.html")

@app.route('/blind-admin')
def blind_admin():
    conn = sqlite3.connect("db.db")
    rows = conn.execute("SELECT msg FROM comments").fetchall()
    conn.close()
    html = "<h2>Admin Panel</h2>"
    for r in rows:
        html += f"<div>{r[0]}</div>"
    return html


if __name__ == '__main__':
    app.run(debug=True)

