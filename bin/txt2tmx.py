#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import time
import nltk
import datetime
import subprocess
from bin.classifier import loadRfModel
from bin.classifier import loadSvmModel
from bin.classifier import getBoolClassifPred
from bin.classifier import getLaserAlignAndClassif
from bin.metaheuristics import getBoolAndTypePreds
from resources.vecalign.vecalign_wrap import makeVecAlign


def segment(filePath):
    # sentence segmentation
    sentList = []
    with open(filePath) as txtFile:
        for paragraph in txtFile.readlines():
            doc = nltk.sent_tokenize(paragraph)
            sentList += [sent.replace("\n", "") for sent in doc]
    return sentList


def segmentAndDump(inSrcPath, inTrgtPath, langOrder):
    outSrcPath = "./tmp/segment.output.{0}".format(langOrder[0])
    outTrgtPath = "./tmp/segment.output.{0}".format(langOrder[1])
    inSrcSegmLns = segment(inSrcPath)
    with open(outSrcPath, "w") as outSrcFile:
        for segmLn in inSrcSegmLns:
            outSrcFile.write("{0}\n".format(segmLn))
    inTrgtSegmLns = segment(inTrgtPath)
    with open(outTrgtPath, "w") as outTrgtFile:
        for segmLn in inTrgtSegmLns:
            outTrgtFile.write("{0}\n".format(segmLn))
    return outSrcPath, outTrgtPath


def dumpRawLines(listOfRawLines, filePath, addNewline=True, rewrite=True):
    """
    Dumps a list of raw lines in a a file
    so the Benchmark script can analyse the results
    """
    folderPath = u'/'.join((filePath.split(u'/'))[:-1] + [''])
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    # we dump an empty string to make sure the file is empty
    if rewrite == True:
        openedFile = codecs.open(filePath, 'w', encoding='utf8')
        openedFile.write('')
        openedFile.close()
    openedFile = codecs.open(filePath, 'a', encoding='utf8')
    # we dump every line of the list
    for line in listOfRawLines:
        if addNewline == True:
            openedFile.write(u'%s\n' % (line))
        else:
            openedFile.write(u'%s' % (line))
    openedFile.close()
    return


def createEmptyFolder(folderPath):
    """ given a non existing folder path, creates the necessary folders so the path exists """
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)


def getYasaAlign(srcFilePath, trgtFilePath, outputFolderPath="./tmp/"):
    """
    use YASA to align two parallel files and output the result in a human readeable fashion
    :param srcFilePath: path to the source file
    :param trgtFilePath: path to the target file
    :param outputFolderPath:
    :return:
    """
    createEmptyFolder(outputFolderPath)
    # apply the yasa script
    subprocess.call(["./resources/yasa/yasa", "-i", "o", "-o", "a",
                     srcFilePath, trgtFilePath, u"{0}yasa.output.arcadeformat".format(outputFolderPath)])
    subprocess.call(["./resources/yasa/yasa", "-i", "o", "-o", "r",
                     srcFilePath, trgtFilePath, u"{0}yasa.output.raliformat".format(outputFolderPath)])
    # open the arcade format and get the index of the aligned sentences
    indexInfo = []
    with open(u"{0}yasa.output.arcadeformat".format(outputFolderPath)) as arcadeFile:
        with open(u"{0}yasa.output.raliformat".format(outputFolderPath)) as raliFile:
            # first line
            arcadeLn = arcadeFile.readline()
            raliLn = raliFile.readline()
            while arcadeLn:
                # split the different sections of the output data
                arcadeSplit = arcadeLn.split(u'"')
                raliSplit = raliLn.split(u" ")
                # get the line indexes and score
                indexSect = arcadeSplit[1].split(";")
                indexSrc = [int(s.replace(u",", "")) - 1 if s != "" else None for s in indexSect[0].split(" ")]
                indexTgrt = [int(s.replace(u",", "")) - 1 if s != "" else None for s in indexSect[1].split(" ")]
                arcadeScore = float(arcadeSplit[3].replace(u",", ""))
                raliScore = float(raliSplit[1].replace(u"\n", "").replace(u",", ""))
                indexInfo.append({u"src": indexSrc, "trgt": indexTgrt, "scores": [arcadeScore, raliScore]})
                # next line
                arcadeLn = arcadeFile.readline()
                raliLn = raliFile.readline()
    # prepare the output files
    srcRefOutputPath = u"{0}yasa.output.source.reference".format(outputFolderPath)
    srcOutputPath = u"{0}yasa.output.source".format(outputFolderPath)
    srcOutputPathCutIndex = u"{0}yasa.output.source.cut.index".format(outputFolderPath)
    trgtRefOutputPath = u"{0}yasa.output.target.reference".format(outputFolderPath)
    trgtOutputPath = u"{0}yasa.output.target".format(outputFolderPath)
    trgtOutputPathCutIndex = u"{0}yasa.output.target.cut.index".format(outputFolderPath)
    scoreOutputPath = u"{0}yasa.output.score".format(outputFolderPath)
    for filePath in [srcRefOutputPath, srcOutputPath, srcOutputPathCutIndex, trgtRefOutputPath, trgtOutputPath,
                     trgtOutputPathCutIndex, scoreOutputPath]:
        with open(filePath, u"w") as openFile:
            openFile.write("")
    # browse the index list
    srcFileIndexes, srcFileSentences, srcIndex = [], [], 0
    trgtFileIndexes, trgtFileSentences, trgtIndex = [], [], 0
    with open(srcFilePath) as srcFile:
        with open(trgtFilePath) as trgtFile:
            # get lines of source file
            srcLns = [s.replace(u"\n", "") for s in srcFile.readlines()]
            # get lines of target file
            trgtLns = [s.replace(u"\n", "") for s in trgtFile.readlines()]
            # browse the alingment indexes data
            for alignDict in indexInfo:
                # src data
                srcSent, srcCuts = "", []
                for i, alignSrcInd in enumerate(alignDict["src"]):
                    # match to a sentence
                    if alignSrcInd is not None:
                        srcSent = u"{0}{1} ".format(srcSent, srcLns[alignSrcInd])
                        srcCuts.append(len(srcSent))
                    else:
                        srcSent = u"{0} ".format(srcSent)
                        srcCuts.append(None)
                srcRef = [e for e in alignDict["src"] if e is not None]
                srcSent = srcSent[:-1]
                srcCuts = srcCuts[:-1]
                # dump src data
                with open(srcRefOutputPath, "a") as refFile:
                    refFile.write(u"{0}\t{1}\n".format(srcFilePath, srcRef))
                with open(srcOutputPath, "a") as srcSentFile:
                    srcSentFile.write(u"{0}\n".format(srcSent))
                with open(srcOutputPathCutIndex, "a") as cutsFile:
                    cutsFile.write(u"{0}\n".format(srcCuts))
                # trgt data
                trgtSent, trgtCuts = "", []
                for i, aligntrgtInd in enumerate(alignDict["trgt"]):
                    # match to a sentence
                    if aligntrgtInd is not None:
                        trgtSent = u"{0}{1} ".format(trgtSent, trgtLns[aligntrgtInd])
                        trgtCuts.append(len(trgtSent))
                    else:
                        trgtSent = u"{0} ".format(trgtSent)
                        trgtCuts.append(None)
                trgtRef = [e for e in alignDict["trgt"] if e is not None]
                trgtSent = trgtSent[:-1]
                trgtCuts = trgtCuts[:-1]
                # dump all trgt data
                with open(trgtRefOutputPath, "a") as refFile:
                    refFile.write(u"{0}\t{1}\n".format(trgtFilePath, trgtRef))
                with open(trgtOutputPath, "a") as trgtSentFile:
                    trgtSentFile.write(u"{0}\n".format(trgtSent))
                with open(trgtOutputPathCutIndex, "a") as cutsFile:
                    cutsFile.write(u"{0}\n".format(trgtCuts))
                # dump the scores
                with open(scoreOutputPath, "a") as refFile:
                    refFile.write(u"{0}\n".format(alignDict["scores"]))
    return srcOutputPath, trgtOutputPath


def getFlag(classif, srcLn, trgtLn, langOrder, noErrLst=None, errLst=None):
    noErrLst = [] if noErrLst is None else noErrLst
    errLst = [] if errLst is None else errLst
    # no need to classify
    if classif is None:
        return ""
    # empty lines
    elif srcLn in ["", " "] and trgtLn in ["", " "]:
        return ""
    # if one of the sentences is empty, then the flag is "alignment_not_found"
    elif (srcLn in ["", " "] and trgtLn not in ["", " "]) or (srcLn not in ["", " "] and trgtLn in ["", " "]):
        dt = str(datetime.datetime.now()).split(".")[0]
        return ''' flag="true" flag_date="{0}" flag_type="alignment_not_found" flag_score="1.0"'''.format(dt)
    # apply the metatheuristic/randomforest/svm/laser classifier and get the result
    dt = str(datetime.datetime.now()).split(".")[0]
    boolClass, typeClass, heurSc4Feat = getBoolAndTypePreds(srcLn, trgtLn, langOrder, humanReadable=True, boolClassify=classif)
    # if the classifier is "metaheuristic"
    if classif == "metaheuristic":
        pass
    # "laser" (laser requires a path to the files, not the lines)
    elif classif in ["laser", True]:
        if [srcLn, trgtLn] in noErrLst:
            boolClass = "no_error"
        elif [srcLn, trgtLn] in errLst:
            boolClass = "error"
        else:
            boolClass = "silence"
    # if a different classifier must be applied
    elif classif in ["randomforest", "svm"]:
        if classif == "randomforest":
            classifModel = loadRfModel()
        elif classif == "svm":
            classifModel = loadSvmModel()
        else:
            classifModel = None
        # get the boolean class in a human-readeable way
        boolClass = getBoolClassifPred(heurSc4Feat, classif, classifModel, humanReadable=True)
    else:
        raise ValueError("Unknown classifier {0}. Supported values: 'none', 'metaheuristic', 'randomforest', 'svm', 'laser'".format(classif))
    # get
    if boolClass == "no_error" and typeClass[0] == "no_error":
        flagClass, score = "no_error", typeClass[1]
    elif boolClass in ["no_error", "silence"] and typeClass[0] in ["no_error", "silence"]:
        flagClass, score = "silence", 1.0
    elif typeClass[0] in ["no_error", "silence"] and boolClass == "error":
        flagClass, score = "error", 1.0
    else:
        flagClass, score = typeClass
    return ''' flag="true" flag_date="{0}" flag_type="{1}" flag_score="{2}"'''.format(dt, flagClass, score)


def fromAlignTxtToTmx(srcSegmentPath, trgtSegmentPath, srcAlignedPath, trgtAlignedPath, langOrder, rmEmptyLns=True, classif=True,
                      outputTmxPath=None, overwrite=True, laserClassif=None):
    outputTmxPath = "./tmp/aligned.tmx" if outputTmxPath is None else outputTmxPath
    head = """<tmx version="1.4b">\n  <header\n    creationtool="RALIYasaAligner" creationtoolversion="0.1"\n    datatype="PlainText" segtype="phrase"\n    adminlang="en-US" srclang="{0}"\n    o-tmf="TMX"/>\n  <body>\n""".format(langOrder[0])
    foot = """  </body>\n</tmx>"""
    contentList = []
    noErrLst, errLst = None, None
    with open(srcAlignedPath) as srcFile:
        srcAlignLns = srcFile.readlines()
    with open(trgtAlignedPath) as trgtFile:
        trgtAlignLns = trgtFile.readlines()
    # LASER
    # starttime = time.time()  ##################################
    if classif in ["laser", True, None]:
        if laserClassif is None:
            noErrLst, errLst = getLaserAlignAndClassif(srcSegmentPath, trgtSegmentPath, langOrder,
                                                       outputFolderPath="./tmp/")
        else:
            noErrLst, errLst = laserClassif
    # get flag for each aligned line
    for srcLn, trgtLn in zip(srcAlignLns, trgtAlignLns):
        srcLn, trgtLn = srcLn.replace("\n", ""), trgtLn.replace("\n", "")
        # get the flag, if there is one
        flag = getFlag(classif, srcLn, trgtLn, langOrder, noErrLst, errLst)
        # print("CLASSIFIER", time.time() - starttime)  ##################################
        # add tmx line by line
        if rmEmptyLns is True and srcLn in ["", " "] and trgtLn in ["", " "]:
            pass
        else:
            tmxLn = """    <tu{0}>\n      <tuv xml:lang="{1}">\n        <seg><![CDATA[{2}]]></seg>\n      </tuv>\n      <tuv xml:lang="{3}">\n        <seg><![CDATA[{4}]]></seg>\n      </tuv>\n    </tu>\n""".format(flag, langOrder[0], srcLn, langOrder[1], trgtLn)
            contentList.append(tmxLn)
    # if we don't want to overwrite, load the previous tmx content
    if overwrite is not True:
        if os.path.isfile(outputTmxPath):
            with open(outputTmxPath) as previousFile:
                head = previousFile.read().replace(foot, "")
    # dump all labeled data in a tmx file
    tmxContent = head + "".join(contentList) + foot
    outputTmxAllPath = outputTmxPath.replace(".tmx", "_all_labeled.tmx")
    with open(outputTmxAllPath, "w") as outputFile:
        outputFile.write(tmxContent)
    # dump the translation memory (only good/neutral sentences)
    # contentList = [ln for ln in contentList if (
    #             'flag_type="silence"' in ln or 'flag_type="no_error"' in ln or "flag_type='silence'" in ln or "flag_type='no_error'" in ln or "<tu>" in ln)]
    contentList = [ln for ln in contentList if re.match('''.+(flag_type=["'](silence|no_error)["']|<tu>)''', ln)]
    tmxContent = head + "".join(contentList) + foot
    with open(outputTmxPath, "w") as outputFile:
        outputFile.write(tmxContent)
    return outputTmxPath, outputTmxAllPath


def getVecAlign(srcPath, trgtPath, langOrder, txtSrcOutputPath=None, txtTrgtOutputPath=None):
    txtSrcOutputPath = "./tmp/vecalign.output.align.{0}".format(langOrder[0]) if txtSrcOutputPath is None else txtSrcOutputPath
    txtTrgtOutputPath = "./tmp/vecalign.output.align.{0}".format(langOrder[1]) if txtTrgtOutputPath is None else txtTrgtOutputPath
    # get the text lines
    with open(srcPath) as srcFile:
        srcLns = srcFile.readlines()
    with open(trgtPath) as trgtFile:
        trgtLns = trgtFile.readlines()

    # get the alignments and scores
    alAndSc = makeVecAlign(srcPath, trgtPath, langOrder)
    alignPath = "{0}.tsv".format(".".join(txtSrcOutputPath.split(".")[:-1]))
    raliPath = "{0}.raliformat".format(".".join(txtSrcOutputPath.split(".")[:-1]))
    with open(alignPath, "w") as alignFile:
        with open(raliPath, "w") as raliFile:
            with open(txtSrcOutputPath, "w") as outSrc:
                with open(txtTrgtOutputPath, "w") as outTrgt:
                    for alignments, scores in alAndSc:
                        for (srcIndexes, trgtIndexes), score in zip(alignments, scores):
                            # dump the alignment to line index format
                            alignFile.write("{0}\t{1}\t{2}\n".format(",".join([str(i) for i in srcIndexes]),
                                                                     ",".join([str(i) for i in trgtIndexes]), score))
                            # dump the alignment to rali format
                            raliFile.write("{0}-{1} {2}\n".format(len(srcIndexes), len(trgtIndexes), score))
                            # dump the aligned lines
                            alSrcLn = []
                            for srcI in srcIndexes:
                                alSrcLn.append(srcLns[srcI].replace("\n", ""))
                            outSrc.write("{0}\n".format(" ".join(alSrcLn)))
                            alTrgtLn = []
                            for trgtI in trgtIndexes:
                                alTrgtLn.append(trgtLns[trgtI].replace("\n", ""))
                            outTrgt.write("{0}\n".format(" ".join(alTrgtLn)))
    return txtSrcOutputPath, txtTrgtOutputPath

def removeEmbed(path="./embed/"):
    for filePath in ["{0}{1}".format(path, file) for file in os.listdir(path)]:
        os.remove(filePath)

def segmentAlignMakeTmx(srcFilePath, trgtFilePath, langOrder, aligner=True, classif=True, outputTmxPath=None):
    # remove content of embedding folder
    removeEmbed()
    # segment
    srcSegmPath, trgtSegmPath = segmentAndDump(srcFilePath, trgtFilePath, langOrder)
    # yasa aligner
    starttime = time.time() #########################################
    if aligner not in ["vecaligner", True]:
        srcAlignedPath, trgtAlignedPath = getYasaAlign(srcSegmPath, trgtSegmPath)
        lsrClassif = None
    # vecaligner (laser) aligner
    else:
        srcAlignedPath, trgtAlignedPath = getVecAlign(srcSegmPath, trgtSegmPath, langOrder)
        lsrClassif = None
    print("ALIGNER", time.time() - starttime) ##################################
    # remove content of embedding folder
    removeEmbed()
    # tmx
    overwrt = True if outputTmxPath is not None else False
    tmxPath, tmxAllLabelsPath = fromAlignTxtToTmx(srcSegmPath, trgtSegmPath, srcAlignedPath, trgtAlignedPath, langOrder, classif=classif,
                                laserClassif=lsrClassif, outputTmxPath=outputTmxPath, overwrite=overwrt)
    return tmxPath, tmxAllLabelsPath
