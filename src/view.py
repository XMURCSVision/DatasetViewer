import os
import random
import cv2
import numpy as np
import argparse


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


parser = argparse.ArgumentParser(
    formatter_class=SmartFormatter,
    description="view dataset, press 'q' to exit, press 'd' to delete, press 'r' to recover delete, other keys for next image",
    epilog="Enjoy it!",
)

parser.add_argument(
    "-p",
    "--path",
    help="R|specify the path of your dataset, if not given, current directory will be used. Notice that the file structure of dataset is assumed like:\n"
    "dataset\n"
    "├── images\n"
    "    ├── 1.jpg\n"
    "    ├── ...\n"
    "├── labels\n"
    "    ├── 1.txt\n"
    "    ├── ...\n",
    default="./",
)
parser.add_argument(
    "-t",
    "--txtpath",
    metavar="PATH",
    help="if given, program will read images from txt file, in which each line is a image path. Either a single txt path or a directory path could be given, if it's a directory, program will read all txt files in it.",
)
parser.add_argument(
    "-k",
    "--keypoints",
    help="draw key points if there is any in label",
    type=int,
)
parser.add_argument(
    "-c",
    "--class",
    metavar="LIST",
    help="specify class number which you'd like to view, either list or a single number is OK, spilt the list with ','",
    dest="_class",
)
parser.add_argument(
    "-n", "--num", help="number of images you'd like to view, default 20", type=int
)

parser.add_argument(
    "-f",
    "--file",
    help="if config, only read given file/files, files should split with ','",
)

args = parser.parse_args()
datapath = args.path if args.path else "./"
classlist = args._class.split(",") if args._class else None
imgnum = args.num if args.num else 20
txtpath = args.txtpath
colorlist = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 255, 255),
    (127, 127, 127),
    (255, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]


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
elif args.file:
    imgpath = os.path.join(datapath, "images/")
    imlist = [os.path.join(imgpath, im) for im in args.file.split(",")]
else:
    imgpath = os.path.join(datapath, "images/")
    imlist = [os.path.join(imgpath, im) for im in os.listdir(imgpath)]


print(colorlist)
print(classlist)


random.shuffle(imlist)

print(imlist)
del_list = []
displayed = 0
idx = 0
while idx < len(imlist):
    file = imlist[idx]
    if displayed == imgnum and not args.file:
        break
    path, filename = file.split("/images/")
    filename = os.path.splitext(filename)[0] + ".txt"
    labelpath = "{}/labels/{}".format(path, filename)
    if not os.path.exists(labelpath):
        print(f"cannot find label in {labelpath}")
        idx += 1
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
                points = list(map(float, line.split()[5 : 5 + args.keypoints * 2]))
                points = pntn2pnt(points)
                cv2.polylines(im, [points], True, (255, 255, 255), 1)
                for idx, point in enumerate(points):
                    cv2.circle(im, point, 2, colorlist[idx % len(colorlist)], 4)
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
    if ord("r") == q:
        if file in del_list:
            del_list.remove(file)
            print(f'recovered file {file}')
        else:
            print('file was not deleted')
        continue
    if ord("d") == q:
        del_list.append(file)
        print(f"deleted file {file}, press 'r' for recovery")
        continue
    
    idx += 1
    displayed += 1

for file in del_list:
    os.remove(file)
    path, filename = file.split("/images/")
    filename = os.path.splitext(filename)[0] + ".txt"
    labelpath = "{}/labels/{}".format(path, filename)
    os.remove(labelpath)
    
cv2.destroyAllWindows()
