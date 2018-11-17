"""
Maxtree without Union-by-rank

Reference:
    A fair comparison of many max-tree computation algorithms
    (Extended version of the paper submitted to ISMM 2013)
"""

import numpy as np
import scipy as scp
import scipy.misc
import maxtree 

def find_pixel_parent(parents, index):
    """
    Given an image containing pixel's parent and a pixel id,
    returns the id of its parent id.

    The parent is also named as root.
    """

    root = parents[index]

    # Assign the root of the given pixel to the root of its parent.
    if (root != index):
        parents[index] = find_pixel_parent(parents, root)

    return parents[index]

def canonize(image, parents, nodes_order):
    """
    Makes sure all nodes of a max tree are valid.
    """

    for pi in nodes_order:
        root = parents[pi]

        if image[root] == image[parents[root]]:
            parents[pi] = parents[root]

def get_4_neighbors(width, height, resolution, pi, pixel_row):
    """
    For a given image width, height and pixel index, return the index
    of direct neighbor pixels using 4 connection.
    """

    top_pi = pi - width 
    bottom_pi = pi + width
    left_pi = pi - 1
    right_pi = pi + 1

    neighbors = []

    if top_pi >= 0:
        neighbors.append(top_pi)
    if bottom_pi < resolution:
        neighbors.append(bottom_pi) 

    # For right and left pixels, we need to check if we moved to 
    # the next row or not.
    if left_pi % width == pixel_row:
        neighbors.append(left_pi) 
    if right_pi % width == pixel_row:
        neighbors.append(right_pi)

    return neighbors

def get_8_neighbors(width, height, resolution, pi, pixel_row):
    """
    For a given image width, height and pixel index, return the index
    of direct neighbor pixels using 8 connection.
    """

    neighbors = get_4_neighbors(width, height, resolution, pi, pixel_row)

    top_left_pi = pi - width  - 1
    top_right_pi = top_left_pi + 2
    bottom_left_pi = pi + width - 1
    bottom_right_pi = bottom_left_pi + 2

    if top_left_pi >= 0 and (top_left_pi % width) == pixel_row - 1:
        neighbors.append(top_left_pi)

    if top_right_pi >= 0 and (top_right_pi % width) == pixel_row - 1:
        neighbors.append(top_right_pi)

    if bottom_left_pi < resolution and (bottom_left_pi % width) == pixel_row + 1:
        neighbors.append(bottom_left_pi)

    if bottom_right_pi < resolution and (bottom_right_pi % width) == pixel_row + 1:
        neighbors.append(bottom_right_pi)

    return neighbors

def maxtree_berger(image, connection8=True):
    """
    Union-find based max-tree algorithm as proposed by Berger et al.

    Arguments:
    image is supposed to be a numpy array.

    Returns:
    """

    (width, height) = (image.shape[0], image.shape[1])

    flatten_image = image.flatten()
    resolution = flatten_image.shape[0]

    # Unique value telling if a pixel is defined in the max tree or not.
    undefined_node = resolution + 2

    # We generate an extra vector of pixels that order nodes downard.
    # This vector allow to traverse the tree both upward and downard
    # without having to sort childrens of each node.
    # Initially, we sort pixel by increasing value and add indices in it.
    sorted_pixels = flatten_image.argsort()

    # We store in the parent node of each pixel in an image.
    # To do so we use the index of the pixel (x + y * width).
    parents = np.full(
        shape=(resolution, 1), 
        fill_value=undefined_node, 
        dtype=np.uint32)

    # zparents make root finding much faster.
    zparents = parents.copy()

    # We go through sorted pixels in the reverse order.
    for pi in reversed(sorted_pixels):
        # Make a node.
        # By default, a pixel is its own parent.
        parents[pi] = pi
        zparents[pi] = pi

        # Find the row of this pixel.
        pixel_row = pi % width;

        # We need to go through neighbors that already have a parent.
        if connection8:
            neighbors = get_8_neighbors(width, height, resolution, pi, pixel_row)
        else:
            neighbors = get_4_neighbors(width, height, resolution, pi, pixel_row)

        # Filter neighbors.
        neighbors = [n for n in neighbors if parents[n] != undefined_node]

        # Merge nodes together.
        for nei_pi in neighbors:
            nei_root = find_pixel_parent(zparents, nei_pi)

            if nei_root != pi:
                zparents[nei_root] = parents[nei_root] = pi

    canonize(flatten_image, parents, sorted_pixels)

    parents = np.reshape(parents, image.shape)
    return (parents, sorted_pixels)

if __name__ == '__main__':
    img1 = maxtree.image_read(filename="examples/images/cameraman.jpg")
    result = maxtree_berger(img1)

    print(result[0].shape)
    print(result[1].shape)
    print(result[0])
    print(result[1])

