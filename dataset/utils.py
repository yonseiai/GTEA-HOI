import typing as t
import io
import torch
import matplotlib.pyplot as plt
from torch import Tensor
from PIL import Image
from torchvision.ops import box_convert
from dataset import labels

_obj_map = {v: k for k, v in labels.objects.items()}
_act_map = {v: k for k, v in labels.actions.items()}


def plot_hoi(
    img: t.Union[Tensor, Image.Image],
    boxes: t.Union[t.List, Tensor],
    objects: t.Union[t.List, Tensor],
    actions: t.Optional[t.Union[t.List, Tensor]] = None,
    figure_size: t.Optional[t.Tuple[float, float]] = (16, 10),
) -> Image.Image:
    plt.ioff()

    if isinstance(img, Tensor):
        # if the img is a tensor, convert it to a PIL image first
        img = Image.fromarray(img.permute(1, 2, 0).numpy())

    if actions is None:
        # if no actions are provided, just set them all to noop
        actions = [0 for _ in objects]

    if len(boxes) > 0:
        # convert boxes to absolute xyxy coordinates
        w, h = img.width, img.height
        boxes = box_convert(boxes, "cxcywh", "xyxy") * torch.tensor([w, h, w, h])

    plt.figure(figsize=figure_size)
    plt.imshow(img)

    ax = plt.gca()

    for obj, action, box in zip(objects, actions, boxes):
        xmin, ymin, xmax, ymax = box
        is_action = action != labels.actions["noop"]
        color = "green" if is_action else "white"

        ax.add_patch(
            plt.Rectangle(
                (xmin, ymin),
                xmax - xmin,
                ymax - ymin,
                fill=False,
                color=color,
                linewidth=3,
            )
        )

        label = _obj_map.get(int(obj), "n/a")

        if is_action:
            label += " ← " + _act_map.get(int(action), "n/a")

        ax.text(
            xmin,
            ymin,
            label,
            fontsize=15,
            color="white" if is_action else "black",
            bbox={"facecolor": color, "alpha": 0.5},
        )

    plt.axis("off")

    # save to buffer before opening as a PIL image again
    buf = io.BytesIO()
    plt.savefig(buf)

    plt.close()
    buf.seek(0)

    return Image.open(buf)
