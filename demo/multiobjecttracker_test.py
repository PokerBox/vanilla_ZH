# from ifs.MultiObjectTracker import MultiObjectTracker
# import pprint
# pp=pprint.PrettyPrinter(indent=4)
# o=MultiObjectTracker(None)
# list1=[('Blue',0.9,(185,132,213,168)),('Blue',0.9,(249,142,275,172)),('Red',0.9,(183,145,215,186))]
# o.update(list1)
# pp.pprint(o.objects)
# list2=[('Red',0.9,(185,136,213,171)),('Blue',0.9,(250,150,275,182)),('Blue',0.9,(33,184,61,214)),('Blue',0.9,(185,136,213,171))]
# o.update(list2)
# pp.pprint(o.objects)

#
# a=[(1,3),(10,9),(2,0)]
# print(sorted(a))
# print(a[0:2])
# flag=True
# for i, item in enumerate(a):
#     print(i,item)
#     if flag:
#         del a[i+1]
#         flag=False
#     print(a)


# from scipy.spatial import distance as dist
# import numpy as np
# maxIgnoreDistance=10
# inputCentroids=[(1,1),(2,2),(5,5),(11,11),(21,21),(22,22),(23,23),(33,33)]
# newCentroids = []
# skipList = []
# addedList = []
# for i in range(0, len(inputCentroids)):
#     if i in skipList:
#         continue
#     for j in range(0, len(inputCentroids)):
#         print(newCentroids)
#         distance=dist.cdist(np.array([inputCentroids[i]]), np.array([inputCentroids[j]]))
#         print(inputCentroids[i],inputCentroids[j],distance,end=" ")
#         if i == j or (j in skipList):
#             continue
#         elif distance < maxIgnoreDistance:
#             skipList.append(j)
#         else:
#             if i not in addedList:
#                 print("Mode4")
#                 newCentroids.append(inputCentroids[i])
#                 addedList.append(i)
#
# print(newCentroids)

from ifs.MultiObjectTracker import MultiObjectTracker
import pprint
pp=pprint.PrettyPrinter(indent=4)
o=MultiObjectTracker(None,debugMode=True)
list1=[('Blue',0.9,(247,146,274,177)),('Blue',0.9,(184,136,211,173))]
o.update(list1)
pp.pprint(o.objects)
list2=[('Blue',0.9,(185,132,213,168)),('Blue',0.9,(249,142,275,172))]
o.update(list2)
pp.pprint(o.objects)

# a={}
# print(123 in a)
# a[123]=[456]
# print(123 in a)
#
# import datetime
# print(datetime.datetime.now().time())