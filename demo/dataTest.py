import numpy as np
data = [0x12, 0x23, 0x34, 0x45, 0x56, 0x78, 0x89, 0xab]

def hexToNumArray(data):
    nums = []
    for i in range(4):
        a = data[2*i: 2*i+2]
        num1 = bin(a[0])[2:10]
        num2 = bin(a[1])[2:10]
        for i in range(8-len(num1)):
            num1 = "0" + num1
        for i in range(8-len(num2)):
            num2 = "0" + num2
        nums.append(int(num1 + num2, 2))
    return nums

def numToHex(num):
    num = bin(num)
    num = num[2: len(num)]
    data = []
    for i in range(16-len(num)):
        num = "0" + num
    data.append(int(num[0:8], 2))
    data.append(int(num[8:16], 2))
    return data

print(hexToNumArray(data))
# print(numToHex(12))