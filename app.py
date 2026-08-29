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

    ydl_opts = {
        'format': 'bestaudio/best' if is_audio else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url') or (info.get('formats')[0].get('url') if info.get('formats') else None)
            
            if not direct_url:
                return jsonify({'error': 'Could not extract media URL'}), 500
                
            return jsonify({'success': True, 'url': direct_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
    
