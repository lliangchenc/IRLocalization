import numpy as np

def normalized(v):
    return v / np.linalg.norm(v)

# we only retrieve the second row of correspondent 3x3 matrix, which is the forward vector
def quat2vec(q):
    return [
        2 * q[1] * q[2] - 2 * q[0] * q[3],
        q[0] ** 2 - q[1] ** 2 + q[2] ** 2 - q[3] ** 2,
        2 * q[2] * q[3] + 2 * q[0] * q[1]
    ]