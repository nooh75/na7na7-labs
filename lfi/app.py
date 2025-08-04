from flask import Flask, request, render_template, session
import os

app = Flask(__name__)
app.secret_key = 'vulnkey'  # For sessions

UPLOAD_FOLDER = 'uploads'
SESSION_FOLDER = 'sess'
LOG_FOLDER = 'logs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SESSION_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('home.html')

# Local File Inclusion / Remote File Inclusion
@app.route('/vuln')
def vuln():
    page = request.args.get('page')
    if not page:
        return "No page specified."
    try:
        with open(page, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

# File Upload
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)
        return f"File uploaded: {path}"
    return '''
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

# Simulated log injection
@app.route('/logme')
def logme():
    ua = request.headers.get('User-Agent')
    with open(os.path.join(LOG_FOLDER, 'access.log'), 'a') as f:
        f.write(ua + '\n')
    return "User-Agent logged."

# Simulated session injection
@app.route('/setsession')
def setsession():
    payload = request.args.get('payload', '')
    sid = 'sess_' + os.urandom(4).hex()
    with open(os.path.join(SESSION_FOLDER, sid), 'w') as f:
        f.write(payload)
    return f"Session saved as: {SESSION_FOLDER}/{sid}"

# RCE endpoint
@app.route('/rce')
def rce():
    cmd = request.args.get('cmd')
    if not cmd:
        return "No command"
    return os.popen(cmd).read()

if __name__ == '__main__':
    app.run(debug=True)
