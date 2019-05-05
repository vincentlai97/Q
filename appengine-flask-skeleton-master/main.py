"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, render_template, request, session
import json
import urllib
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    # Initialise score if not yet initialised
    if 'games_won' in session:
        session['games_won'] = session['games_won']
    else:
        session['games_won'] = 0
    if 'games_lost' in session:
        session['games_lost'] = session['games_lost']
    else:
        session['games_lost'] = 0
    return render_template('index.html')


@app.route('/new_game', methods=['POST'])
def new_game():
    # Generate random word
    url = "http://randomword.setgetgo.com/get.php"
    session['answer'] = urllib.urlopen(url).read().upper()
    
    # Set word_state to blank of the same length
    session['word_state'] = ''
    for count in range(len(session['answer'])):
        session['word_state'] += '_'
    
    # Set number of bad guesses to 0
    session['bad_guesses'] = 0
    
    response = {
        'word_length' : len(session['answer'])
    }
    return json.dumps(response)


@app.route('/check_letter', methods=['POST'])
def check_letter():
    # Get JSON
    jsondata = request.data
    # Get actual value
    data = json.loads(jsondata)
    letter = data['guess']
    
    # Check if letter is correct
    correct = False
    for count in range(len(session['answer'])):
        if session['answer'][count] == letter:
            session['word_state'] = session['word_state'][:count] + letter + session['word_state'][count+1:]
            correct = True
    # If not increase bad_guesses
    if correct == False:
        session['bad_guesses'] += 1
    
    # If bad_guesses is more than 7, send lose state
    if session['bad_guesses'] > 7:
        response = {
            'game_state' : 'LOSE',
            'word_state' : session['word_state'],
            'answer' : session['answer']
        }
        session['games_lost'] += 1
        return json.dumps(response)
    
    # If word_state is all filled with letters, send win state
    correct = True
    for count in range(len(session['word_state'])):
        if session['word_state'][count] == '_':
            correct = False
            break
    if correct:
        response = {
            'game_state' : 'WIN',
            'word_state' : session['word_state']
        }
        session['games_won'] += 1
        return json.dumps(response)
    
    response = {
        'game_state' : 'ONGOING',
        'word_state' : session['word_state'],
        'bad_guesses' : session['bad_guesses']
    }
    return json.dumps(response)


@app.route('/score', methods=['GET', 'DELETE'])
def score():
    # return score
    if request.method == 'DELETE':
        session['games_won'] = 0
        session['games_lost'] = 0
    response = {
        'games_won' : session['games_won'],
        'games_lost' : session['games_lost']
    }
    return json.dumps(response)
        

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


app.secret_key = 'DansGame-69420'