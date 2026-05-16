from flask import Flask, render_template_string, redirect, url_for, flash, send_from_directory
import os, sys, subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES = {
    'PythonCarGame': 'PythonCarGame.py',
    'PythonSnakeGame': 'PythonSnakeGame.py',
    'bestgame': 'bestgame.py',
}

INDEX_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>PyGame Hub Browser</title>
  <style>
    body {font-family: Arial, sans-serif; background:#f4f4f8; margin:0;}
    .container {max-width:600px; margin:40px auto; padding:20px; background:white; border-radius:10px; box-shadow:0 4px 16px rgba(0,0,0,.12);}    
    h1 {text-align:center; color:#222;}
    .buttons {display:grid; gap:12px;}
    .btn {padding:14px; font-size:1rem; text-decoration:none; background:#2a9df4; color:white; text-align:center; border-radius:8px; display:block;}
    .btn:hover {background:#1c73c7;}
    .error {color:#c0392b; margin-bottom:12px;}
    .info {color:#555; text-align:center; margin-top:18px;}
  </style>
</head>
<body>
  <div class="container">
    <h1>PyGame Browser Hub</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="error">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <div class="buttons">
      <a class="btn" href="/car-game">Play Car Racing Game (Web)</a>
      {% for name, key in games.items() %}
        <a class="btn" href="{{ url_for('launch_game', game_key=name) }}">Play {{ name }}</a>
      {% endfor %}
    </div>
    <p class="info">Click a button to launch the game process on the server machine. Close this page anytime.</p>
  </div>
</body>
</html>
'''

LAUNCH_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Launching {{ game_name }} - PyGame Hub Browser</title>
  <style>
    body {font-family: Arial, sans-serif; background:#f4f4f8; margin:0; display:flex; align-items:center; justify-content:center; min-height:100vh;}
    .container {max-width:500px; padding:30px; background:white; border-radius:10px; box-shadow:0 4px 16px rgba(0,0,0,.12); text-align:center;}
    h1 {color:#222; margin-bottom:20px;}
    .status {color:#27ae60; font-size:1.2rem; margin:20px 0;}
    .btn {padding:12px 24px; font-size:1rem; text-decoration:none; background:#2a9df4; color:white; border-radius:8px; display:inline-block; margin-top:20px;}
    .btn:hover {background:#1c73c7;}
    .info {color:#555; margin-top:20px; font-size:0.9rem;}
  </style>
  <script>
    setTimeout(function() {
      window.close();
    }, 3000);
  </script>
</head>
<body>
  <div class="container">
    <h1>Launching {{ game_name }}</h1>
    <div class="status">{{ status_message }}</div>
    <p>The game should now be running on your desktop.</p>
    <a class="btn" href="{{ url_for('index') }}">Back to Game Hub</a>
    <p class="info">This tab will close automatically in 3 seconds, or you can close it manually.</p>
  </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML, games=GAMES)

@app.route('/car-game')
def car_game():
    return send_from_directory(BASE_DIR, 'PythonCarGame.html')

@app.route('/play/<game_key>')
def launch_game(game_key):
    if game_key not in GAMES:
        return render_template_string(LAUNCH_HTML, game_name="Unknown Game", status_message="Error: Invalid game selection")

    game_file = os.path.join(BASE_DIR, GAMES[game_key])
    if not os.path.exists(game_file):
        return render_template_string(LAUNCH_HTML, game_name=game_key, status_message=f"Error: Game file not found: {GAMES[game_key]}")

    try:
        subprocess.Popen([sys.executable, game_file], cwd=BASE_DIR)
        return render_template_string(LAUNCH_HTML, game_name=game_key, status_message="Game launched successfully!")
    except Exception as e:
        return render_template_string(LAUNCH_HTML, game_name=game_key, status_message=f"Error launching game: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
