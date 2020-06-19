#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
import argparse
from bin.txt2tmx import segmentAlignMakeTmx
from bin.tmx2html import makeHtmlFromTmx

"""
"""


def launchIt(inSrc, inTrgt, langOrder, aligner, classif, outHtml="./html/", outTmx="./tmp/aligned.tmx"):
    outHtml = outHtml if outHtml[-1] == "/" else "{0}".format(outHtml)
    # segment, align and make the tmx for the given documents
    outTmx, outAllLabelTmx = segmentAlignMakeTmx(inSrc, inTrgt, langOrder, aligner, classif, outputTmxPath=outTmx)
    # make the html using the tmx
    makeHtmlFromTmx(outAllLabelTmx, "{0}index.html".format(outHtml))
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-insrc", "--inputsource", type=str, default="None", help="path to the Source file")
    parser.add_argument("-intrgt", "--inputtarget", type=str, default="None", help="path to the Target file")
    parser.add_argument("-lsrc", "--langsource", type=str, default="en", help="language of the Source file")
    parser.add_argument("-ltrgt", "--langtarget", type=str, default="fr", help="language of the Target file")
    parser.add_argument("-html", "--outputfolder", type=str, default="None", help="path to the output folder")
    parser.add_argument("-tmx", "--outputtmx", type=str, default="None", help="path to the output tmx file")
    parser.add_argument("-ali", "--aligner", type=str, default="None",
                        help="""string indicating what aligner should the script use to show potential errors: 
                        none, yasa, vecalign""")
    parser.add_argument("-cls", "--classifier", type=str, default="None",
                        help="""string indicating what classifier should the script use to show potential errors: 
                        none, metaheuristic, randomforest, svm, laser""")
    args = parser.parse_args()

    classifDict = {"metaheuristic": "metaheuristic", "meta": "metaheuristic", "metah": "metaheuristic",
                   "mh": "metaheuristic", "randomforest": "randomforest", "random": "randomforest",
                   "rf": "randomforest", "svm": "svm", "supportvectormachine": "svm", "laser": "laser", "l": "laser"}

    inSrc = args.inputsource
    inTrgt = args.inputtarget
    srcLang = args.langsource
    trgtLang = args.langtarget
    aligner = "yasa" if args.aligner.lower() not in ["vecalign", "laser", "vector"] else "vecaligner"
    classif = None if args.classifier.lower() not in classifDict else classifDict[args.classifier.lower()]
    outHtml = "./html/" if args.outputfolder == "None" else args.outputfolder
    outTmx ="./tmp/aligned.tmx" if args.outputtmx == "None" else args.outputtmx

    startTime = time.time()

    launchIt(inSrc, inTrgt, [srcLang, trgtLang], aligner, classif, outHtml, outTmx)

    # print the time the algorithm took to run
    print(u'\nTIME IN SECONDS ::', time.time() - startTime)



    # TODO: read file extension others that .txt
    # TODO: verify or ask for the language of the files
    # TODO: remove the sys add to path before importing the scripts in bin
