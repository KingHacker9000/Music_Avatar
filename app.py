from flask import Flask, render_template, request, url_for, redirect
import os
from CloudDBHelper import CloudDB
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize the database
connection_string = f"{os.environ.get('SQLite_Connection')}apikey={os.environ.get('SQLite_apikey')}"
db = CloudDB(connection_string, db_name='AvatarInteractions')

# We have just one "song" in this scenario:
SONG_NAMES = {
    "Die With a Smile": "die_with_a_smile", 
    "Someone Like You": "Adele", 
    "Happy": "happy", 
    "Imperial March": "imperial", 
    "Mario Theme Song": "Mario", 
    "Vivaldi Spring": "spring", 
    "Uptown Funk": "uptown", 
    "Vivaldi Winter": "winter",
    "Moonlight": "moonlight"
}

# Instrument overlays: Drums, Guitar, Keyboard, Keyboard2
INSTRUMENT_VIDEOS = {
    "None": "",
    "All": "instruments",
    "Drums": "instruments_drums",
    "Strings": "instruments_strings",
    "Piano": "instruments_piano",
    "Horns": "instruments_horns",
    "Synth": "instruments_synth"
}

def get_song_file(song_name, character_name, energy_level=None):
    file_path = f"{SONG_NAMES[song_name]}/{SONG_NAMES[song_name]}_{character_name}.mp4"
    return file_path
    

def get_instrument_file(song_name, instrument_name):
    #return "Adele/adele_instrument_piano.webm"
    file_path = f"{SONG_NAMES[song_name]}/{SONG_NAMES[song_name]}_{INSTRUMENT_VIDEOS[instrument_name]}.webm"
    return file_path

def get_captions_file(song_name):
    #return "Adele/adele_captions.webm"
    file_path = f"{SONG_NAMES[song_name]}/{SONG_NAMES[song_name]}_captions.webm"
    return file_path

@app.route('/<user_id>', methods=['GET', 'POST'])
def user_index(user_id):
    # Default to boy vocal + no instruments
    selected_song = "Die With a Smile"
    selected_character = "vocal_boy"
    selected_song_file = get_song_file(selected_song, selected_character)
    selected_instrument = "None"
    selected_instrument_file = None
    selected_captions = "off"
    selected_captions_file = None

    if request.method == 'POST':
        # If user clicks "Apply"
        if request.form.get('reset') == 'true':
            # Reset to defaults
            selected_character = "vocal_boy"
            selected_instrument = "None"
        else:
            selected_song = request.form.get('song-choice') or selected_song
            selected_character = request.form.get('character-select') or selected_character
            selected_instrument = request.form.get('instruments') or selected_instrument
            selected_captions = request.form.get('captions') or selected_captions

            selected_song_file = get_song_file(selected_song, selected_character)
            if selected_instrument == "None":
                selected_instrument_file = None
            else:
                selected_instrument_file = get_instrument_file(selected_song, selected_instrument)

            if selected_captions == "on" and selected_song in ["Happy", "Die With a Smile", "Someone Like You", "Uptown Funk"]:
                selected_captions_file = get_captions_file(selected_song)
            else:
                selected_captions_file = None

            if user_id != "-1":
                # Log the interaction to the database
                print(f"Logging interaction for user {user_id}")
                old_song = request.form.get('old_song_choice') or ""
                old_character = request.form.get('old_character_select') or ""
                old_instrument = request.form.get('old_instruments') or ""
                old_captions = request.form.get('old_captions') or ""
                if old_song != "":
                    print(f"Old: {old_song} {old_character} {old_instrument} {old_captions}")
                    print(f"New: {selected_song} {selected_character} {selected_instrument} {selected_captions}")
                    db.add_interaction(user_id, (old_song, old_character, old_instrument, old_captions), (selected_song, selected_character, selected_instrument, selected_captions))


    return render_template(
        'index.html',
        songs=SONG_NAMES.keys(),
        selected_song=selected_song,
        selected_character=selected_character,
        selected_instrument=selected_instrument,
        selected_captions=selected_captions,
        character_video_file=selected_song_file,
        instrument_video_file=selected_instrument_file,
        captions_video_file=selected_captions_file,
        user_id=user_id
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('user_index', user_id='-1'))

if __name__ == '__main__':
    # Use the environment variable for the host and port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("DEBUG", "False") == "True", host='0.0.0.0', port=port)
