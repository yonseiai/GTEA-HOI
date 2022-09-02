# %%

import tqdm
import os
import json

# %%


train_json_files = [f for f in os.listdir("train1") if f[-4:] == "json"]


# %%

labels = []

for json_file in tqdm.tqdm(train_json_files):
    with open(os.path.join("train1", json_file)) as file:
        data = json.loads(file.read())

    for a in data[0]["annotations"]:
        labels.append(a["label"])


# %%


unique_labels = list(set([l for l in labels if l[:2] != "v_"]))
# %%
len(unique_labels)


# %%

corrections = {
    "eating_utensilw": "eating_utensil",
    "han": "hand",
    "psn": "pan",
    "carro": "carrot",
    "trash_container": "trash_can",
    "pap": "pan",
    "bo": "bowl",
    "washing_liquid": "dish_soap",
}

for l in unique_labels:
    if l not in corrections:
        res = input(f"What is '{l}'?")

        if res != "":
            corrections[l] = res
            print(f"Updated corrections {l} = {res}")
        else:
            print("Is ok!")
# %%
corrections
# %%

for json_file in tqdm.tqdm(train_json_files):
    with open(os.path.join("train1", json_file), "r+") as file:
        data = json.loads(file.read())

        for a in data[0]["annotations"]:
            a["label"] = corrections.get(a["label"], a["label"])

        file.seek(0)
        file.write(json.dumps(data))
        file.truncate()


# %%
