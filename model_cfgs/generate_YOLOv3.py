# File:    generate_YOLOv3.py
# Author:  Edward Hanson (edward.t.hanson@duke.edu)
# Desc.    Generate YOLOv3 (Darknet-53) config file

startingH = 1024 #1225 #256
startingW = 1024 #1225 #256

def appendToFile(fp, name, H, W, KH, KW, IC, OC, stride):
    fp.write(str(name)+",\t" + str(H)+",\t" + str(W)+",\t" + str(KH)+",\t" + str(KW)+",\t" + str(IC)+",\t" + str(OC)+",\t" + str(stride)+",\n")

def update(nextC, layerNum):
    curC = nextC
    layerNum += 1
    return curC, layerNum

def block(fp, layerNum, curH, curW, curC):
    residC = curC

    # bottleneck
    nextC = curC // 2
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 1, 1, curC, nextC, 1)
    curC, layerNum = update(nextC, layerNum)

    # 3x3 conv
    nextC = int(curC * 2)
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 3, 3, curC, nextC, 1)
    curC, layerNum = update(nextC, layerNum)

    ## residual output
    #appendToFile(fp, "Resid"+str(layerNum), curH, curW, 1, 1, residC, nextC, 1)
    #_, layerNum = update(nextC, layerNum)
    
    return layerNum, curC

def downsample(fp, layerNum, curH, curW, curC):
    nextC = int(curC * 2)
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 3, 3, curC, nextC, 2)
    curH = int(curH/2)
    curW = int(curW/2)
    curC, layerNum = update(nextC, layerNum)

    return layerNum, curH, curW, curC

def gen_yolov3():
    curH = startingH
    curW = startingW
    curC = 3
    layerNum = 1
    
    fp = open("YOLOv3.csv", "w")
    appendToFile(fp, "Layer name", "IFMAP Height", "IFMAP Width", "Filter Height", "Filter Width", "Channels", "Num Filter", "Strides")
    
    # 1
    nextC = 32
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 3, 3, curC, nextC, 1)
    curC, layerNum = update(nextC, layerNum)
    
    # 2
    layerNum, curH, curW, curC = downsample(fp, layerNum, curH, curW, curC)
    # block 1
    layerNum, curC = block(fp, layerNum, curH, curW, curC)

    # 3
    layerNum, curH, curW, curC = downsample(fp, layerNum, curH, curW, curC)
    # block 2
    for i in range(2):
        layerNum, curC = block(fp, layerNum, curH, curW, curC)

    # 4
    layerNum, curH, curW, curC = downsample(fp, layerNum, curH, curW, curC)
    # block 3
    for i in range(8):
        layerNum, curC = block(fp, layerNum, curH, curW, curC)

    # 5
    layerNum, curH, curW, curC = downsample(fp, layerNum, curH, curW, curC)
    # block 4
    for i in range(8):
        layerNum, curC = block(fp, layerNum, curH, curW, curC)

    # 6
    layerNum, curH, curW, curC = downsample(fp, layerNum, curH, curW, curC)
    # block 5
    for i in range(4):
        layerNum, curC = block(fp, layerNum, curH, curW, curC)

    fp.close()
    
gen_yolov3()
