import re
import pandas as pd
import argparse
import os

def extract_annotations(fdf_path):
    # Read FDF content
    with open(fdf_path, "r", encoding="latin1") as file:
        content = file.read()

    # Find all object blocks
    objects = re.findall(r'\d+ \d+ obj(.*?)endobj', content, re.DOTALL)

    # Extract relevant fields
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

def main():
    parser = argparse.ArgumentParser(description="Extract annotations from FDF file into CSV.")
    parser.add_argument("fdf_file", help="Path to the .fdf file")

    args = parser.parse_args()
    fdf_path = args.fdf_file
    base = os.path.splitext(fdf_path)[0]

    # Extract and export data
    df = extract_annotations(fdf_path)
    annotations_csv = base + "_annotations.csv"
    summary_csv = base + "_stamp_counts.csv"

    df.to_csv(annotations_csv, index=False)

    stamp_counts = df["Subject"].value_counts().reset_index()
    stamp_counts.columns = ["Stamp Type", "Count"]
    stamp_counts.to_csv(summary_csv, index=False)

    print(f"Saved:\n- {annotations_csv}\n- {summary_csv}")

if __name__ == "__main__":
    main()
