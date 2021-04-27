

FNAME = "YOLOv3.csv"


Mx = []
My = []
Nx = []
Ny = []
Ni = []
No = []
Stride = []
fp = open(FNAME, "r")
next(fp)
for line in fp:
    line = line.strip().split(',')
    Mx.append(int(line[3]))
    My.append(int(line[4]))
    Nx.append(int(line[1]))
    Ny.append(int(line[2]))
    Ni.append(int(line[5]))
    No.append(int(line[6]))
    Stride.append(int(line[7]))
    
print(Mx)
print(My)
print(Nx)
print(Ny)
print(Ni)
print(No)
print(Stride)
