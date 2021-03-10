import itertools
from typing import Tuple, List

import numpy as np


def sphere(center: Tuple[int, int, int] = (0, 0, 0), radius: int = 1, fill: bool = True, n=100) -> List[Tuple[int, int, int]]:
    theta = np.linspace(0, 2 * np.pi, n)
    phi = np.linspace(0, np.pi, n)
    xc, yc, zc = center
    if fill:
        x = [xc + rho * np.outer(np.cos(theta), np.sin(phi)) for rho in range(radius)]
        y = [yc + rho * np.outer(np.sin(theta), np.sin(phi)) for rho in range(radius)]
        z = [zc + rho * np.outer(np.ones(np.size(theta)), np.cos(phi)) for rho in range(radius)]
    else:
        x = xc + radius * np.outer(np.cos(theta), np.sin(phi))
        y = yc + radius * np.outer(np.sin(theta), np.sin(phi))
        z = zc + radius * np.outer(np.ones(np.size(theta)), np.cos(phi))
    x = np.rint(x).astype(int).ravel()
    y = np.rint(y).astype(int).ravel()
    z = np.rint(z).astype(int).ravel()
    return list(set(zip(x, y, z)))

def torus(center: Tuple[int, int, int] = (0, 0, 0), major_radius: int = 3, minor_radius: int = 2, n = 100) -> List[Tuple[int, int, int]]:
    theta = np.linspace(0, 2 * np.pi, n)
    phi = np.linspace(0, 2 * np.pi, n)
    theta, phi = np.meshgrid(theta, phi)
    xc, yc, zc = center
    x = xc + (major_radius + minor_radius * np.cos(theta)) * np.cos(phi)
    y = yc + (major_radius + minor_radius * np.cos(theta)) * np.sin(phi)
    z = zc + minor_radius * np.sin(theta)
    x = np.rint(x).astype(int).ravel()
    y = np.rint(y).astype(int).ravel()
    z = np.rint(z).astype(int).ravel()
    return list(set(zip(x, y, z)))


def unzip(coord: List[Tuple[int, int, int]]):
    return map(list, zip(*coord))


def main():
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    # sphere 1
    sphere1 = sphere(center=(0, 0, 0), radius=25)
    X1, Y1, Z1 = unzip(sphere1)
    # sphere 2
    sphere2 = sphere(center=(10, 30, 20), radius=5)
    X2, Y2, Z2 = unzip(sphere2)

    fig = plt.figure()
    plt.gca().set_aspect('equal', adjustable='box')
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X1, Y1, Z1, marker='.', color='b', alpha=0.1)
    ax.scatter(X2, Y2, Z2, marker='.', color='r', alpha=0.1)

    # torus
    torus1 = torus(center=(50, 50, 50), major_radius=15, minor_radius=5)
    X3, Y3, Z3 = unzip(torus1)
    ax.scatter(X3, Y3, Z3, marker='.', color='g', alpha=0.1)

    plt.savefig("geometry.png")
    plt.close()


if __name__ == "__main__":
    main()
