import numpy as np

def normalized(v):
    return v / np.linalg.norm(v)

def quat_to_mat(q):
    q0, q1, q2, q3 = q
    return np.array([
        [q0*q0+q1*q1-q2*q2-q3*q3, 2*q1*q2+2*q0*q3, 2*q0*q3-2*q1*q2], 
        [2*q1*q2-2*q0*q3, q0*q0-q1*q1+q2*q2-q3*q3, 2*q2*q3+2*q0*q1], 
        [2*q1*q3+2*q0*q2, 2*q2*q3-2*q0*q1, q0*q0-q1*q1-q2*q2-q3*q3]
    ])
