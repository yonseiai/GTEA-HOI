# %%

import os
import re
import sys
import json
import tarfile
from tqdm import tqdm
from dataset import labels


def is_modified(data):
    for item in data:
        for annon in item["annotations"]:
            coor = annon["coordinates"]

            # We're just gonna assume that if the coordiantes are the default
            # auto generated ones, this file has not been modified
            if coor["x"] == 100 or coor["y"] == 100:
                return False

    return True


def process_item(item):
    regex_obj = re.compile(f"_({'|'.join(labels.objects.keys())})")
    regex_verb = re.compile("_verb-(\w+)_")
    boxes = []
    objects = []
    actions = []
    w, h = 640, 480

    for a in item["annotations"]:
        coors = a["coordinates"]

        boxes.append(
            [
                coors["x"] / w,
                coors["y"] / h,
                coors["width"] / w,
                coors["height"] / h,
            ]
        )

        # if a label annotation is prefixed with v_ it is the target of the image action
        if a["label"][:2] == "v_":
            objects.append(labels.objects.get(a["label"][2:]))

            # unfortunately the verb label is contained in the filename of the image
            # which needs to be cleaned up before assignment
            action = regex_obj.sub("", regex_verb.search(item["image"]).group(1))
            actions.append(labels.actions.get(action, "noop"))
        else:
            objects.append(labels.objects.get(a["label"]))
            actions.append(labels.actions["noop"])

    return {
        "image": item["image"],
        "boxes": boxes,
        "objects": objects,
        "actions": actions,
    }


# %%


def main(source_dir, out_file):
    archive = tarfile.TarFile(out_file, mode="w")
    json_files = [f for f in os.listdir(source_dir) if f[-4:] == "json"]
    items = []

    for json_file in tqdm(json_files):
        with open(os.path.join(source_dir, json_file), "r") as h:
            data = json.loads(h.read())

            if is_modified(data):
                items.extend([process_item(item) for item in data])

                # Add the jpg to the archive
                jpg_file = json_file[:-4] + "jpg"
                archive.add(os.path.join(source_dir, jpg_file))

    annotations_file = "annotations.json"

    with open(annotations_file, "w") as h:
        h.write(json.dumps(items))

    archive.add(annotations_file)
    archive.close()

    print(f"Wrote {len(items)} annotated images to {out_file}")


# %%
if __name__ == "__main__":
    source_dir = sys.argv[1]
    out_file = sys.argv[2]

    assert os.path.exists(source_dir), f"Source dir {source_dir} does not exist"

    main(source_dir, out_file)

# %%
