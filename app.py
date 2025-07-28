import os
import subprocess
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "123asc_454_xsac_323456"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        if not url.startswith("http"):
            flash("Neplatná URL adresa.", "danger")
            return redirect(url_for("index"))

        try:
            command = [
                "yt-dlp",
                "-o", f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
                "-f", "best",
                url
            ]
            subprocess.run(command, check=True)

            # Získame najnovší súbor
            files = sorted(os.listdir(DOWNLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_FOLDER, x)), reverse=True)
            latest_file = files[0] if files else None

            if latest_file:
                return redirect(url_for("download_file", filename=latest_file))

        except subprocess.CalledProcessError:
            flash("Chyba pri sťahovaní videa.", "danger")
            return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
