import os
from matplotlib import pyplot as plt
import argparse
from collections import defaultdict


COLORLIST = [
    "red",
    "green",
    "blue",
    "yellow",
    "lightseagreen",
    "violet",
    "slategray",
    "orange",
]


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


parser = argparse.ArgumentParser(formatter_class=SmartFormatter)

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
    "-s", "--save", action="store_true", help="to save the result in current directory"
)
parser.add_argument(
    "-t",
    "--txtpath",
    metavar="PATH",
    help="if given, program will read images from txt file, in which each line is a image path. Either a single txt path or a directory path could be given, if it's a directory, program will read all txt files in it.",
)

args = parser.parse_args()
datapath = args.path
txtpath = args.txtpath

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
examples = dict()
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
            examples[len(annotations)] = file


def plot(dict, title="", xlabel=""):
    x = dict.keys()
    y = dict.values()
    xint = range(min(x), max(x) + 1)
    plt.bar(x, y, color=COLORLIST, width=0.9)
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


for key, value in sorted(classlist.items()):
    print(f"class:{key} has {value} instances")



for ex in annotationlenlist.items():
    print(f"{ex[1]} annotations have {ex[0]} messages in single row")
    
for ex in examples.items():
    print(f"example of {ex[0]} messages in single row: {ex[1]}")
    
plot(classlist, title="label_classes", xlabel="classes")
plot(annotationlenlist, title="messages in single row", xlabel="length")