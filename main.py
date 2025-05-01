from flask import Flask, request, render_template_string, send_file
import pandas as pd
import re
import os

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FDF to CSV Converter</title>
</head>
<body>
    <h2>Upload an FDF file</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="fdf_file" accept=".fdf" required>
        <input type="submit" value="Convert">
    </form>
    {% if annotations and counts %}
        <p><a href="{{ annotations }}">Download Annotations CSV</a></p>
        <p><a href="{{ counts }}">Download Stamp Counts CSV</a></p>
    {% endif %}
</body>
</html>
'''

def extract_annotations(fdf_text):
    objects = re.findall(r'\d+ \d+ obj(.*?)endobj', fdf_text, re.DOTALL)
    annotations = []
    for obj in objects:
        subj = re.search(r'/Subj\((.*?)\)', obj)
        title = re.search(r'/T\((.*?)\)', obj)
        name = re.search(r'/Name\((.*?)\)', obj)
        entry = {
            "Subject": subj.group(1) if subj else "",
            "Title": title.group(1) if title else "",
            "Name": name.group(1) if name else ""
        }
        if any(entry.values()):
            annotations.append(entry)
    return pd.DataFrame(annotations)

@app.route("/", methods=["GET", "POST"])
def upload():
    annotations_path = counts_path = None
    if request.method == "POST":
        file = request.files["fdf_file"]
        content = file.read().decode("latin1")
        df = extract_annotations(content)

        # Save CSVs
        annotations_path = "annotations.csv"
        counts_path = "stamp_counts.csv"
        df.to_csv(annotations_path, index=False)
        df["Subject"].value_counts().reset_index().to_csv(counts_path, index=False, header=["Stamp Type", "Count"])

    return render_template_string(HTML_PAGE,
                                  annotations=annotations_path if annotations_path else None,
                                  counts=counts_path if counts_path else None)

@app.route("/annotations.csv")
def download_annotations():
    return send_file("annotations.csv", as_attachment=True)

@app.route("/stamp_counts.csv")
def download_counts():
    return send_file("stamp_counts.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
