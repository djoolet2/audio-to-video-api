from flask import Flask, request, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)

# Output folder
OUTPUT_FOLDER = "output_videos"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return "Flask API is running!"

@app.route("/generate_video", methods=["POST"])
def generate_video():
    data = request.json
    if not data or "audio_url" not in data or "image_url" not in data:
        return jsonify({"error": "Missing parameters: 'audio_url' and 'image_url'"}), 400

    audio_url = data["audio_url"]
    image_url = data["image_url"]

    # Generating unique filenames
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
    image_filename = f"image_{uuid.uuid4().hex}.jpg"
    output_filename = f"{OUTPUT_FOLDER}/video_{uuid.uuid4().hex}.mp4"

    # Download files using wget
    os.system(f"wget -O {audio_filename} {audio_url}")
    os.system(f"wget -O {image_filename} {image_url}")

    # Generate video using FFmpeg
    ffmpeg_command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_filename,
        "-i", audio_filename,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", "scale=1920:1080",
        output_filename
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        return jsonify({
            "message": "Video generated successfully",
            "video_url": f"{request.host_url}{output_filename}"
        })
    except subprocess.CalledProcessError:
        return jsonify({"error": "FFmpeg video generation failed"}), 500
    finally:
        # Cleanup
        os.remove(audio_filename)
        os.remove(image_filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
