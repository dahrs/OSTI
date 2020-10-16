#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import logging
import argparse
from bin.txt2tmx import segmentAlignMakeTmx
from bin.tmx2html import makeHtmlFromTmx

"""
 Copyright (c) 2019-2021 Laboratoire de Recherche Appliquee en Linguistique Informatique (RALI Laboratory)
 rali.iro.umontreal.ca
 @author david.alfonso.hermelo@gmail.com
 @author shivendra.bhardwaj@umontreal.ca 
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 
 Unless otherwise expressed by the authors, any issues or requests should 
 be expressed through the Github page of the project:
 https://github.com/dahrs/OSTI
"""


def launchIt(inSrc, inTrgt, langOrder, aligner, classif, outHtml="./html/", outTmx=None):
    outHtml = outHtml if outHtml[-1] == "/" else "{0}".format(outHtml)
    # segment, align and make the tmx for the given documents
    outTmx, outAllLabelTmx = segmentAlignMakeTmx(inSrc, inTrgt, langOrder, aligner, classif, outputTmxPath=outTmx)
    # make the html using the tmx
    makeHtmlFromTmx(outAllLabelTmx, "{0}index.html".format(outHtml))
    return None


if __name__ == '__main__':
    """
    example:
    python main.py -insrc ./test.en -lsrc en -intrgt ./test.fr -ltrgt fr   
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-insrc", "--inputsource", type=str, default="None", help="path to the Source file")
    parser.add_argument("-intrgt", "--inputtarget", type=str, default="None", help="path to the Target file")
    parser.add_argument("-lsrc", "--langsource", type=str, default="en",
                        help="""ISO 639-1 language code of the Source file:
                        en, fr""")
    parser.add_argument("-ltrgt", "--langtarget", type=str, default="fr",
                        help="""ISO 639-1 language code of the Target file:
                        en, fr""")
    parser.add_argument("-html", "--outputfolder", type=str, default="None", help="path to the output folder")
    parser.add_argument("-tmx", "--outputtmx", type=str, default="None", help="path to the output tmx file")
    parser.add_argument("-ali", "--aligner", type=str, default="None",
                        help="""string indicating what aligner should the script use to show potential errors: 
                        yasa, vecalign, None (yasa by default)""")
    parser.add_argument("-cls", "--classifier", type=str, default="None",
                        help="""string indicating what classifier should the script use to show potential errors: 
                        metaheuristic, randomforest, svm, laser, none (laser by default, unless badly configured)""")
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
    outTmx = None if args.outputtmx == "None" else args.outputtmx

    # make a log file to add warnings and errors
    fmtstr = " %(asctime)s: (%(filename)s): %(levelname)s: %(funcName)s Line: %(lineno)d - %(message)s"
    logging.basicConfig(filename="OSTI_d.log", level=logging.DEBUG, filemode="w",
                        format=fmtstr, datefmt="%Y-%m-%d %I:%M:%S %p ")

    logging.info("Started running")
    startTime = time.time()

    if classif is None:
        if args.classifier.lower() == "none":
            logging.info("Non-specified classifier, switching to LASER")
            print("Non-specified classifier, switching to LASER")
        else:
            logging.info("Unsupported classifier, switching to LASER. Supported values: 'none', 'metaheuristic', 'randomforest', 'svm', 'laser'")
            print("Unsupported classifier, switching to LASER. Supported values: \n    none\n    metaheuristic\n    randomforest\n    svm\n    laser")

    launchIt(inSrc, inTrgt, [srcLang, trgtLang], aligner, classif, outHtml, outTmx)

    # print the time the algorithm took to run
    print(u'\nTIME IN SECONDS ::', time.time() - startTime)
    logging.info("Finished running. TIME IN SECONDS :: {0}".format(time.time() - startTime))



    # TODO: read file extension others that .txt
    # TODO: verify or ask for the language of the files
    # TODO: remove the sys add to path before importing the scripts in bin
