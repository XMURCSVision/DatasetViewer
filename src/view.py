import os
import random
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--txtpath", help="if given, program will read images from txt file, in which each line is a image path. You could give either a single txt path or a directory path, if it's a directory, program will read all txt files in it.")
parser.add_argument("-k", "--keypoints", action="store_true", help="draw key points if there is any in label")
parser.add_argument(
    "--path", help="specify the path of your dataset, current working directory is default"
)
parser.add_argument(
    "--class",
    help="specify class number which you'd like to view, either list or a single number is OK, spilt the list with ','",
    dest="_class",
)
parser.add_argument("--num", help="number of images you'd like to view", type=int)

args = parser.parse_args()
datapath = args.path if args.path else "./"
classlist = args._class.split(",") if args._class else None
imgnum = args.num if args.num else 20
txtpath = args.txtpath
colorlist = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (127,127,127), (255,0,255),(255,255,0),(255,255,255)]


def pntn2pnt(points):
    points = np.asarray(points)
    points = points.reshape((-1, 2))
    points[:, 0] *= w
    points[:, 1] *= h
    return points.astype(np.int32)


if txtpath:
    if not os.path.exists(txtpath):
        print("invalid path of txt")
        exit(1)
    txtlist = (
        [txtpath]
        if not os.path.isdir(txtpath)
        else [
            os.path.join(txtpath, txt)
            for txt in os.listdir(txtpath)
            if os.path.splitext(txt)[-1] == ".txt"
        ]
    )
    imlist = []
    for txt in txtlist:
        with open(txt, "r") as f:
            imlist.extend([line.replace("\n", "") for line in f.readlines()])
else:
    imgpath = os.path.join(datapath, "images/")
    imlist = [os.path.join(imgpath, im) for im in os.listdir(imgpath)]

print(classlist)
random.shuffle(imlist)
displayed = 0
for file in imlist:
    if displayed == imgnum:
        break
    path, filename = file.split("/images/")
    filename = os.path.splitext(filename)[0] + ".txt"
    labelpath = "{}/labels/{}".format(path, filename)
    if not os.path.exists(labelpath):
        print(f"cannot find label in {labelpath}")
        continue
    if classlist:
        with open(labelpath) as f:
            for line in f.readlines():
                if line.split()[0] in classlist:
                    break
            else:
                continue
    im = cv2.imread(file)
    h, w, _ = im.shape
    while h > 960 or w > 1440:
        im = cv2.resize(im, (-1, -1), fx=0.5, fy=0.5)
        h, w, _ = im.shape
    with open("{}/labels/{}".format(path, filename)) as f:
        for line in f.readlines():
            tag = line.split()[0]
            xywh = list(map(float, line.split()[1:5]))
            xywh = pntn2pnt(xywh)
            if args.keypoints:
                points = list(map(float, line.split()[5:]))
                points = pntn2pnt(points)
                cv2.polylines(im, [points], True, (255, 255, 255), 1)
                for idx, point in enumerate(points):
                    cv2.circle(im, point, 2, colorlist[idx%len(colorlist)], 4)
            cv2.rectangle(
                im,
                xywh[0, :] - xywh[1, :] // 2,
                xywh[0, :] + xywh[1, :] // 2,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                im, f"{tag}", xywh[0, :] + xywh[1, :] // 2, 0, 0.75, (255, 255, 255), 2
            )
            print(line)
    cv2.putText(im, f"{file[max(len(file)-20,0):]}", (0, 20), 0, 0.5, (0, 0, 255), 1)
    cv2.imshow("", im)
    q = cv2.waitKey(0)
    if ord("q") == q:
        break
    displayed += 1
cv2.destroyAllWindows()
