import typing as t
import torch
from torchvision.transforms import Normalize


class UnNormalize(Normalize):
    def __init__(
        self,
        mean: t.Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: t.Tuple[float, float, float] = (0.229, 0.224, 0.225),
    ):
        m = torch.tensor(mean)
        std = torch.tensor(std)
        std_inv = 1 / (std + 1e-7)
        m_inv = -m * std_inv

        super().__init__(
            mean=m_inv,
            std=std_inv,
        )
