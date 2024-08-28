from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

def parse_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Store playlists and tracks
        playlists = []
        for playlist in root.findall('.//NODE'):
            playlist_name = playlist.get('Name')  
            if playlist_name:
                playlist_tracks = []

                for track in playlist.findall('.//TRACK'):
                    location = track.get('Location')  
                    if location:
                        playlist_tracks.append(location)

                playlists.append({
                    'playlist_name': playlist_name,
                    'tracks': playlist_tracks
                })

       
        if not any(playlist['tracks'] for playlist in playlists):
            global_tracks = []
            for track in root.findall('.//TRACK'):
                location = track.get('Location')
                if location:
                    global_tracks.append(location)

            # Add global tracks to a separate category
            playlists.append({
                'playlist_name': "Global Tracks",
                'tracks': global_tracks
            })

        return playlists
    except Exception as e:
        return str(e)
    

@app.route('/get_playlists', methods=['POST'])
def upload_or_parse():
    # Check if a file is uploaded
    if 'xml_file' in request.files:
        file = request.files['xml_file']
        if file.filename.endswith('.xml'):
            file_path = os.path.join('/tmp', file.filename)
            file.save(file_path)
            playlists = parse_xml(file_path)
            return jsonify(playlists)
        else:
            return jsonify({'error': 'Only XML files are allowed.'}), 400

    # Check if a file path is provided in the form data
    elif 'xml_path' in request.form:
        xml_path = request.form['xml_path']
        if os.path.exists(xml_path) and xml_path.endswith('.xml'):
            playlists = parse_xml(xml_path)
            return jsonify(playlists)
        else:
            return jsonify({'error': 'Invalid file path or file is not an XML.'}), 400

    # If no file or xml_path is provided
    return jsonify({'error': 'No file uploaded or path provided.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
