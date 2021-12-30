# %%

import os
import sys
import json
import shutil
import tarfile
from tqdm import tqdm


def is_modified(data):
    for item in data:
        for annon in item["annotations"]:
            coor = annon["coordinates"]

            # We're just gonna assume that if the coordiantes are the default
            # auto generated ones, this file has not been modified
            if coor["x"] == 100 or coor["y"] == 100:
                return False

    return True


# %%


def main(source_dir, out_file):
    archive = tarfile.TarFile(out_file, mode="w")
    json_files = [f for f in os.listdir(source_dir) if f[-4:] == "json"]
    items = []

    for json_file in tqdm(json_files):
        with open(os.path.join(source_dir, json_file), "r") as h:
            data = json.loads(h.read())

            if is_modified(data):
                items.append(data)

                # Add the jpg to the archive
                jpg_file = json_file[:-4] + "jpg"
                archive.add(os.path.join(source_dir, jpg_file))

    annotations_file = "annotations.json"

    with open(annotations_file, "w") as h:
        h.write(json.dumps(items))

    archive.add(annotations_file)
    archive.close()

    print(f"Wrote {len(items)} annotations to {out_file}")


if __name__ == "__main__":
    source_dir = sys.argv[1]
    out_file = sys.argv[2]

    assert os.path.exists(source_dir), f"Source dir {source_dir} does not exist"

    main(source_dir, out_file)

# %%
