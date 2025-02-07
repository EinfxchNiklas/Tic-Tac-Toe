# http://192.168.178.163:5000/
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import webbrowser
import socket

app = Flask(__name__)
socketio = SocketIO(app)

# Initialisiere das Spielfeld und den aktuellen Spieler
game_state = [None] * 9  # 3x3 Tic-Tac-Toe-Feld
current_player = 'X'  # Der erste Spieler ist 'X'
game_over = False  # Überprüft, ob das Spiel vorbei ist

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('make_move')
def handle_move(data):
    global current_player, game_over  # Zugriff auf die globalen Variablen
    index = int(data['index'])  # Der Index, der geklickt wurde

    if game_over:  # Falls das Spiel schon vorbei ist, keine Züge mehr erlauben
        return

    # Überprüfe, ob das Feld leer ist, bevor der Zug gemacht wird
    if game_state[index] is None:
        game_state[index] = current_player
        print(f'Updated game state: {game_state}')

        # Überprüfe, ob jemand gewonnen hat
        winner = check_winner(game_state)
        if winner:
            game_over = True
            emit('game_over', {'winner': winner}, broadcast=True)

        # Wechsel den Spieler
        current_player = 'O' if current_player == 'X' else 'X'

        # Sende das aktualisierte Spielfeld an alle verbundenen Clients
        emit('update_board', game_state, broadcast=True)

@socketio.on('reset_game')
def reset_game():
    global current_player, game_over  # Zugriff auf die globalen Variablen
    # Setze das Spielfeld zurück
    game_state[:] = [None] * 9
    current_player = 'X'  # Starte immer mit 'X'
    game_over = False  # Das Spiel ist wieder am Laufen
    # Sende das zurückgesetzte Spielfeld an alle Clients
    emit('update_board', game_state, broadcast=True)
    emit('game_over', {'winner': None}, broadcast=True)

def check_winner(board):
    # Diese Funktion überprüft, ob jemand gewonnen hat
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontale Gewinnlinien
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertikale Gewinnlinien
        [0, 4, 8], [2, 4, 6]              # Diagonale Gewinnlinien
    ]
    for combo in winning_combinations:
        if board[combo[0]] is not None and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]  # Gibt den Gewinner (X oder O) zurück
    return None  # Kein Gewinner

if __name__ == '__main__':
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    url = f"http://{local_ip}:5000"
    
    print(f"Server läuft! Öffne {url} in deinem Browser.")
    webbrowser.open(url)
    
    socketio.run(app, host='0.0.0.0', port=5000)