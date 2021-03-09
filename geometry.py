from typing import Tuple, List

import numpy as np


def sphere(center: Tuple[int, int, int] = (0, 0, 0), radius: int = 1, fill: bool = True, num=100) -> List[Tuple[int, int, int]]:
    theta = np.linspace(0, 2 * np.pi, num)
    phi = np.linspace(0, np.pi, num)
    xc, yc, zc = center
    x = xc + radius * np.outer(np.cos(theta), np.sin(phi))
    y = yc + radius * np.outer(np.sin(theta), np.sin(phi))
    z = zc + radius * np.outer(np.ones(np.size(theta)), np.cos(phi))
    x = np.rint(x).astype(int).ravel()
    y = np.rint(y).astype(int).ravel()
    z = np.rint(z).astype(int).ravel()
    return list(set(zip(x, y, z)))


def unzip(coord: List[Tuple[int, int, int]]):
    return map(list, zip(*coord))


if __name__ == "__main__":
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    # sphere 1
    X1, Y1, Z1 = unzip(sphere(center=(0, 0, 0), radius=30))
    # sphere 2
    X2, Y2, Z2 = unzip(sphere(center=(10, 30, 20), radius=15))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X1, Y1, Z1, marker='.', color='b', alpha=0.1)
    ax.scatter(X2, Y2, Z2, marker='.', color='r', alpha=0.1)

    plt.savefig("2 spheres.png")
    plt.close()
