import os
from matplotlib import pyplot as plt
import argparse
from collections import defaultdict


colorlist = [
    "red",
    "green",
    "blue",
    "yellow",
    "lightseagreen",
    "violet",
    "slategray",
    "orange",
]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--path",
    help="specify the path of your dataset, working directory is default",
    default="./",
)
parser.add_argument("-s", "--save", action="store_true")
parser.add_argument("-t", "--txt")
args = parser.parse_args()
datapath = args.path
txtpath = args.txt

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
    labels = []
    for txt in txtlist:
        with open(txt, "r") as f:
            labels.extend(
                [
                    line[:-4].replace("images", "labels") + "txt"
                    for line in f.readlines()
                ]
            )
else:
    if os.path.exists(datapath):
        newpath = os.path.join(datapath, "labels/")
        labelpath = newpath if os.path.exists(newpath) else datapath
        labels = [os.path.join(labelpath, label) for label in os.listdir(labelpath)]
    else:
        print("data path not found")
        exit(1)

classlist = defaultdict(int)
annotationlenlist = defaultdict(int)
for file in labels:
    if not os.path.exists(file):
        continue
    with open(file, "r") as f:
        for line in f.readlines():
            annotations = line.split()
            tag = int(annotations[0])
            classlist[tag] += 1
            # xywh = list(map(float, annotations[1:5]))
            # points = list(map(float, annotations[5:]))
            annotationlenlist[len(annotations)] += 1


def plot(dict, title="", xlabel=""):
    x = dict.keys()
    y = dict.values()
    xint = range(min(x), max(x) + 1)
    plt.bar(x, y, color=colorlist, width=0.9)
    plt.xticks(xint)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("frequency")
    if args.save:
        name = f"{os.path.split(datapath)[-1]}_{title}"
        idx = 0
        savepath = "./{}_{}.jpg"
        while os.path.exists(savepath.format(name, idx)):
            idx += 1
        plt.savefig(savepath.format(name, idx))
    plt.show()


plot(classlist, title="label_classes", xlabel="classes")
plot(annotationlenlist, title="messages in single row", xlabel="length")
