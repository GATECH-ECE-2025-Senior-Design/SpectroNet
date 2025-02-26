import os 
  
  
# checking if the directory demo_folder2  
# exist or not. 

def convert(imgf, labelf, outf, n):
    if not os.path.isdir("../dataset/"): 
        os.makedirs("../dataset/") 
    f = open(imgf, "rb")
    o = open(outf, "w")
    l = open(labelf, "rb")

    f.read(16)
    l.read(8)
    images = []

    for i in range(n):
        image = [ord(l.read(1))]
        for j in range(28*28):
            image.append(ord(f.read(1)))
        images.append(image)

    o.write("label"+",")
    for i in range(28*28 - 1):
        o.write(("pixel" + str(i))+",")
    o.write(("pixel" + str(i+1)))
    o.write("\n")
        
    for image in images:
        o.write(",".join(str(pix) for pix in image)+"\n")
    f.close()
    o.close()
    l.close()

convert("train-images.idx3-ubyte", "train-labels.idx1-ubyte",
"../dataset/train.csv", 60000)
convert("t10k-images.idx3-ubyte", "t10k-labels.idx1-ubyte",
"../dataset/test.csv", 10000)

