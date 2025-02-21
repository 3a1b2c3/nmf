import torch
import math
from typing import Tuple

def signed_clip(v, eps=torch.finfo(torch.float32).eps):
    return v.sign() * v.abs().clip(min=eps)

def normalize(v, ord=2, eps=torch.finfo(torch.float32).eps):
    if ord == 2:
        return v / (v**2).sum(axis=-1, keepdim=True).clip(min=eps).sqrt()
    else:
        return v / (torch.linalg.norm(v, dim=-1, keepdim=True, ord=ord)+1e-8)

def inv_sigmoid(v):
    a = (v / (1-v))
    if type(a) == float:
        return math.log(a)
    else:
        return a.log()

def inv_activation(a, activation):
    if activation == 'exp':
        if type(a) == float:
            return math.log(a)
        else:
            return a.log()
    elif activation == 'sigmoid':
        return inv_sigmoid(a)
    else:
        raise Exception(f"inv_activation does not support {activation}")

def expand_bits(v):                                                                                                                                                                                                
    v = (v * 0x00010001) & 0xFF0000FF                                                                                                                                                                              
    v = (v * 0x00000101) & 0x0F00F00F                                                                                                                                                                              
    v = (v * 0x00000011) & 0xC30C30C3                                                                                                                                                                              
    v = (v * 0x00000005) & 0x49249249                                                                                                                                                                              
    return v                                                                                                                                                                                                       

def morton3D(xyz):                                                                                                                                                                                                 
    exyz = expand_bits(xyz)                                                                                                                                                                                        
    return (exyz[..., 0] | (exyz[..., 1] << 1) | (exyz[..., 2] << 2)).long()

def unravel_index(
    indices: torch.LongTensor,
    shape: Tuple[int, ...],
) -> torch.LongTensor:
    r"""Converts flat indices into unraveled coordinates in a target shape.

    This is a `torch` implementation of `numpy.unravel_index`.

    Args:
        indices: A tensor of indices, (*, N).
        shape: The targeted shape, (D,).

    Returns:
        unravel coordinates, (*, N, D).
    """

    shape = torch.tensor(shape)
    indices = indices % shape.prod()  # prevent out-of-bounds indices

    coord = torch.zeros(indices.size() + shape.size(), dtype=int)

    for i, dim in enumerate(reversed(shape)):
        coord[..., i] = indices % dim
        indices = indices // dim

    return coord.flip(-1)
