#
# computes some characteristics for data read from input
# to demonstrate indirect API implementation
#
import sys

values=[]
for line in sys.stdin:
    tokens = line.split()
    if tokens:
        value = float(tokens[0])
        values.append(value)

#loop over input and compute some characteristics
_count = 0
_sum = 0
_min = min(values)
_max = max(values)

for val in values:
    _count+=1
    _sum += val

print (_min, _max, _sum/_count)