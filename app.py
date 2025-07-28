import os
import subprocess
from flask import Flask, render_template, request, send_file, redirect, flash
from pathlib import Path
from flask import after_this_request

app = Flask(__name__)
app.secret_key = "tajny_kluc"
TMP_FOLDER = "downloads"
os.makedirs(TMP_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        if not url.startswith("http"):
            flash("Neplatná URL adresa.", "danger")
            return redirect("/")

        try:
            # Cesta k dočasnému súboru
            output_template = os.path.join(TMP_FOLDER, "%(title)s.%(ext)s")
            command = [
                "yt-dlp",
                "-o", output_template,
                "-f", "best",
                url
            ]
            subprocess.run(command, check=True)

            # Získaj najnovší súbor
            files = sorted(Path(TMP_FOLDER).glob("*"), key=os.path.getctime, reverse=True)
            latest_file = files[0] if files else None

            if latest_file:
                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(latest_file)
                    except Exception as e:
                        app.logger.error(f"Chyba pri mazani suboru: {e}")
                    return response

            return send_file(str(latest_file), as_attachment=True)

            flash("Nepodarilo sa získať súbor.", "danger")
            return redirect("/")

        except subprocess.CalledProcessError as e:
            flash("Chyba pri sťahovaní videa.", "danger")
            return redirect("/")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
