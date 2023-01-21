import sys
import os
import pandas as pd

indir = sys.argv[1]
outfile = sys.argv[2]

rows = []

for filename in os.listdir(indir):
    rel_type = filename
    with open(f'{indir}/{filename}', encoding="utf-8") as infile:
        content = infile.read()

    for item in content.split("\n\n"):
        rows.append((item.replace("[Texto]:", "").strip(), rel_type))

df = pd.DataFrame(rows, columns=["generated_text", "relation_type"])
df.to_csv(outfile, encoding="utf-8", index=False)

