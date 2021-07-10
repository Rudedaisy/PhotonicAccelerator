# File:    generate_ResNet50.py
# Author:  Edward Hanson (edward.t.hanson@duke.edu)
# Desc.    Generate ResNet50 config file

startingH = 224 #1254 #1225 #256
startingW = 224 #1254 #1225 #256

def appendToFile(fp, name, H, W, KH, KW, IC, OC, stride):
    fp.write(str(name)+",\t" + str(H)+",\t" + str(W)+",\t" + str(KH)+",\t" + str(KW)+",\t" + str(IC)+",\t" + str(OC)+",\t" + str(stride)+",\n")

def update(nextC, layerNum):
    curC = nextC
    layerNum += 1
    return curC, layerNum

def block(fp, layerNum, curH, curW, curC, midC, lastC, first=False, downsample=False):
    if first:
        residC = curC
        residH = curH
        residW = curW
        
    if first and downsample:
        initial_stride = 2
    else:
        initial_stride = 1
    
    # bottleneck
    nextC = midC
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 1, 1, curC, nextC, initial_stride)
    curC, layerNum = update(nextC, layerNum)

    if first and downsample:
        curH = curH // 2
        curW = curW // 2
    
    # 3x3 conv
    nextC = midC
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 3, 3, curC, nextC, 1)
    curC, layerNum = update(nextC, layerNum)

    # bottleneck
    nextC = lastC
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 1, 1, curC, nextC, 1)
    curC, layerNum = update(nextC, layerNum)

    if first:
        nextC = lastC
        # residual output
        appendToFile(fp, "Resid"+str(layerNum), residH, residW, 1, 1, residC, nextC, initial_stride)
        _, layerNum = update(nextC, layerNum)
    
    return layerNum, curC, curH, curW

def gen_yolov3():
    curH = startingH
    curW = startingW
    curC = 3
    layerNum = 1
    
    fp = open("ResNet50.csv", "w")
    appendToFile(fp, "Layer name", "IFMAP Height", "IFMAP Width", "Filter Height", "Filter Width", "Channels", "Num Filter", "Strides")
    
    # 1
    nextC = 64
    appendToFile(fp, "Conv"+str(layerNum), curH, curW, 7, 7, curC, nextC, 2)
    curH = curH // 4
    curW = curW // 4
    curC, layerNum = update(nextC, layerNum)
    
    # block 2
    for i in range(3):
        layerNum, curC, curH, curW = block(fp, layerNum, curH, curW, curC, 64, 256, first=(i==0), downsample=False)

    # block 3
    for i in range(4):
        layerNum, curC, curH, curW = block(fp, layerNum, curH, curW, curC, 128, 512, first=(i==0), downsample=True)

    # block 4
    for i in range(6):
        layerNum, curC, curH, curW = block(fp, layerNum, curH, curW, curC, 256, 1024, first=(i==0), downsample=True)

    # block 5
    for i in range(3):
        layerNum, curC, curH, curW = block(fp, layerNum, curH, curW, curC, 512, 2048, first=(i==0), downsample=True)

    fp.close()
    
gen_yolov3()
