from flask import Flask, render_template, request, url_for
import os

app = Flask(__name__)

# We have just one "song" in this scenario:
SONG_NAMES = {
    "Die With a Smile": "die_with_a_smile", 
    "Someone Like You": "Adele", 
    "Happy": "happy", 
    "Imperial March": "imperial", 
    "Mario Theme Song": "Mario", 
    "Vivaldi Spring": "spring", 
    "Uptown Funk": "uptown", 
    "Vivaldi Winter": "winter"
}

# Instrument overlays: Drums, Guitar, Keyboard, Keyboard2
INSTRUMENT_VIDEOS = {
    "None": "",
    "All": "instruments",
    "Drums": "instruments_drums",
    "Strings": "instruments_strings",
    "Keyboard": "instruments_piano",
    "Horns": "instruments_horns",
}

def get_song_file(song_name, character_name, energy_level=None):
    file_path = f"{SONG_NAMES[song_name]}/{SONG_NAMES[song_name]}_{character_name}.mp4"
    print(file_path)
    return file_path
    


def get_instrument_file(song_name, instrument_name):
    #return "Adele/adele_instrument_piano.webm"
    file_path = f"{SONG_NAMES[song_name]}/{SONG_NAMES[song_name]}_{INSTRUMENT_VIDEOS[instrument_name].webm}"
    print(file_path)
    return file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default to boy vocal + no instruments
    selected_song = "Die With a Smile"
    selected_character = "vocal_boy"
    selected_song_file = get_song_file(selected_song, selected_character)
    selected_instrument = "None"
    selected_instrument_file = None

    if request.method == 'POST':
        # If user clicks "Apply"
        if request.form.get('reset') == 'true':
            # Reset to defaults
            selected_character = "Boy Vocal"
            selected_instrument = "None"
        else:
            selected_song = request.form.get('song-choice') or selected_song
            selected_character = request.form.get('character-select') or selected_character
            selected_instrument = request.form.get('instruments') or selected_instrument
            
            selected_song_file = get_song_file(selected_song, selected_character)
            if selected_instrument == "None":
                selected_instrument_file = None
            else:
                selected_instrument_file = get_instrument_file(selected_song, selected_instrument)

    return render_template(
        'index.html',
        songs=SONG_NAMES.keys(),
        selected_character=selected_character,
        selected_instrument=selected_instrument,
        character_video_file=selected_song_file,
        instrument_video_file=selected_instrument_file
    )

if __name__ == '__main__':
    # Use the environment variable for the host and port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("DEBUG", "False") == "True", host='0.0.0.0', port=port)
