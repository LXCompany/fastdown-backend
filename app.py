from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    is_audio = data.get('isAudioOnly', False)
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if is_audio:
        format_selector = 'bestaudio/best'
    else:
        format_selector = 'best[ext=mp4]/best'

    # Configuramos yt-dlp con clientes simulados para saltar el bloqueo de bot de YouTube
    ydl_opts = {
        'format': format_selector,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'web']
            }
        },
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            direct_url = info.get('url')
            if not direct_url and 'formats' in info:
                formats = info['formats']
                if not is_audio:
                    mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
                    if mp4_formats:
                        direct_url = mp4_formats[-1].get('url')
                
                if not direct_url:
                    direct_url = formats[0].get('url')

            if not direct_url:
                return jsonify({'error': 'Could not extract media URL'}), 500
                
            return jsonify({'success': True, 'url': direct_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
