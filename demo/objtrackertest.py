import numpy as np
from scipy.spatial import distance
# a=np.array([[1,5,3,4],[2,1,4,4]])
# b=a.min(axis=0)
# print(b)

a = np.array([[0, 0, 0],
               [0, 0, 1],
               [0, 1, 0],
               [0, 1, 1],
               [1, 0, 0],
               [1, 0, 1],
               [1, 1, 0],
               [1, 1, 1]])
b = np.array([[ 0.1,  0.2,  0.4]])
d=distance.cdist(b, a, 'cityblock')
print(d)

c=d.min(axis=0)
print(c.argsort())