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

def quats_to_angles(quats):
		angles = []
		if len(quats) == 0:
			return []
		vec_origin = normalized(quat_to_mat(quats[0])[1])
		for q in quats:
			if q == quats[0]:
				angles.append(0)
				continue
			mat = quat_to_mat(q)
			vec_forward = normalized(mat[1])
			vec_upper = mat[2]
			sgn = np.sign(np.cross(vec_origin, vec_forward).dot(vec_upper))
			angles.append(np.arccos(vec_forward.dot(vec_origin)) * sgn)
		return np.degrees(angles)