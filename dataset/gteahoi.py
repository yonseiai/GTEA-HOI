import os
import json
import typing as t
import cv2
import torch
from torch.utils.data import Dataset
import albumentations as A
import albumentations.pytorch.transforms as Apyt
from dataset import labels


class GTEA_HOI(Dataset):
    image_dir: str
    items: t.List[dict]

    def __init__(
        self,
        image_dir: str,
        annotations: str,
        transforms: t.List[A.BasicTransform] = [
            A.Flip(p=0.5),
            A.ColorJitter(),
            A.FancyPCA(),
        ],
        normalize: bool = True,
    ):
        super().__init__()

        self.image_dir = image_dir
        self.transforms = A.Compose(
            [*transforms, A.Normalize(), Apyt.ToTensorV2()]
            if normalize
            else [*transforms, Apyt.ToTensorV2()],
            bbox_params=A.BboxParams(format="yolo", label_fields=["objects"]),
        )

        with open(annotations) as h:
            self.items = json.loads(h.read())

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx: int):
        item = self.items[idx]
        img = self.read_image(os.path.join(self.image_dir, item["image"]))
        t = self.transforms(image=img, bboxes=item["boxes"], objects=item["objects"])

        return t["image"], {
            "boxes": torch.FloatTensor(t["bboxes"]),
            "objects": torch.LongTensor(t["objects"]),
            "actions": torch.LongTensor(item["actions"]),
        }

    def read_image(self, img_path: str):
        return cv2.cvtColor(
            cv2.imread(img_path),
            cv2.COLOR_BGR2RGB,
        )
