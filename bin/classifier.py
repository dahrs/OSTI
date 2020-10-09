#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import json
import gzip
import shutil
import pickle
import subprocess
import numpy as np


def dumpModel(model, modelFilePath):
    """
    Using pickle.
    :param model: sklearn machine learning model
    :param modelFilePath: path to the output file
    :return: dumped model
    """
    with open(modelFilePath, u'wb') as modelFile:
        pickle.dump(model, modelFile)


def loadModel(modelFilePath):
    """
    Using pickle.
    :param modelFilePath: path to the input file
    :return: load model
    """
    if ".gz" in modelFilePath:
        with gzip.open(modelFilePath, 'rb') as modelFile:
            pickleModel = pickle.load(modelFile)
    else:
        with open(modelFilePath, u'rb') as modelFile:
            pickleModel = pickle.load(modelFile)
    return pickleModel


# ## RF & SVM ##

def appendAdditionalFeat(featList):
    """ return the feature list with 2 more features :
    the nb of features indicating good and nb of features indicating bad """
    goodThreshold = [1.0, 0.65]
    badThreshold = [0.35, 0.3, 0.95, 0.1]
    nbGood = 0
    nbBad = 0
    # count the very goods: cog, wbw
    veryGoods = [featList[2], featList[9]] if len(featList) == 13 else [featList[8], featList[37]]
    for i, feat in enumerate(veryGoods):
        feat = feat if feat is not None else -1.0
        if feat >= goodThreshold[i]:
            nbGood += 1
    # count the very bads: fa, ion, spell, tabl
    veryBads = [featList[3], featList[4], featList[6], featList[12]]
    veryBads = veryBads if len(featList) == 13 else [featList[12], featList[16], featList[22], featList[49]]
    for i, feat in enumerate(veryBads):
        feat = feat if feat is not None else -1.0
        if feat < badThreshold[i]:
            nbBad += 1
    return np.append(featList, [nbGood, nbBad])


def loadRfModel():
    try:
        rfModel = loadModel("./resources/classifiers/bal_train_7M_scoresAndMetaData_rdmForest.pickle.gz")
    except FileNotFoundError:
        try:
            rfModel = loadModel("../resources/classifiers/bal_train_7M_scoresAndMetaData_rdmForest.pickle")
        except MemoryError:
            try:
                rfModel = loadModel("./resources/classifiers/train_35K_scoresAndMetaData_rdmForest.pickle")
            except FileNotFoundError:
                rfModel = loadModel("../resources/classifiers/train_35K_scoresAndMetaData_rdmForest.pickle")
    return rfModel


def loadSvmModel():
    try:
        svmModel = loadModel("./resources/classifiers/bal_train7M_scores_svm.pickle.gz")
    except FileNotFoundError:
        try:
            svmModel = loadModel("../resources/classifiers/bal_train7M_scores_svm.pickle")
        except MemoryError:
            try:
                svmModel = loadModel("./resources/classifiers/train_35K_scores_svm.pickle")
            except FileNotFoundError:
                svmModel = loadModel("../resources/classifiers/train_35K_scores_svm.pickle")
    return svmModel


def getpredRf(heurVect60plus2, rfModel=None):
    if type(heurVect60plus2) is list:
        heurVect60plus2 = np.asarray(heurVect60plus2)
    if len(heurVect60plus2) == 60:
        heurVect60plus2 = appendAdditionalFeat(heurVect60plus2)
    # load the model
    rfModel = rfModel if rfModel is not None else loadRfModel()
    # get the prediction
    pred = rfModel.predict(np.asarray([heurVect60plus2]))
    return pred


def getpredSvm(heurVect13plus2, svmModel=None):
    if type(heurVect13plus2) is list:
        heurVect13plus2 = np.asarray(heurVect13plus2)
    if len(heurVect13plus2) == 13:
        heurVect13plus2 = appendAdditionalFeat(heurVect13plus2)
    # load the model
    svmModel = svmModel if svmModel is not None else loadSvmModel()
    pred = svmModel.predict(np.asarray([heurVect13plus2]))
    return pred


def getFeatFromScoresAndMetaData(heurSc4Feat):
    """
    Given a list containing the standalone scores for each heuristic followed by the score + the metadata
    (ie, [score0, score0+metadata, score1, score+metadata, ...]) returns 2 arrays, one of the scores alone and
    one with the scores and metadata (+2 arbitrary features for each)
    """
    # the score and metadata appear in this order: nb, len, cog, fa, ion, sw, spell, url, mono, wbw, punct, gibb, tabl
    decisionScores = []
    for nb in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]:
        featSc = heurSc4Feat[nb][0] if heurSc4Feat[nb][0] is not None else -1.0
        decisionScores.append(featSc)
    feat13 = np.asarray(decisionScores)
    # prepare the arrays (remove the None/"na")
    metadataScores = []
    for nb in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]:
        metadataScores += [sc if sc not in [None, "na"] else -1.0 for sc in heurSc4Feat[nb]]
    feat60 = np.asarray(metadataScores)
    return appendAdditionalFeat(feat13), appendAdditionalFeat(feat60)


def getBoolClassifPred(heurSc4Feat, classifierName, classierModel=None, humanReadable=True):
    """

    :param heurSc4Feat: list containing the standalone scores for each heuristic followed by the score + the metadata
    :param classifierName: either 'randomforest', 'svm' or 'laser'
    :return: a boolean classification
    """
    feat13plus2, feat60plus2 = getFeatFromScoresAndMetaData(heurSc4Feat)
    if classifierName == "randomforest":
        pred = getpredRf(feat60plus2, classierModel)
    elif classifierName == "svm":
        pred = getpredSvm(feat13plus2, classierModel)
    # return a human-readable string instead of a int/float/bool as a class
    if humanReadable:
        pred = "error" if pred in [0, False] else "gold"
    return pred


# ## LASER ##

def removeOldOuts(op, suppl=None):
    suppl = [] if suppl is None else suppl
    embeds = ["./{0}".format(file) for file in os.listdir("./embed/")]
    for oldOut in ["./0_class_laser.csv", "./1_class_laser.csv", "./classification_labels.out",
                   "{0}laser.output.align".format(op), "{0}laser.output.source".format(op),
                   "{0}laser.output.target".format(op)] + embeds + suppl:
        try:
            os.remove(oldOut)
        except FileNotFoundError:
            pass


def equalizeLength(srcPath, trgtPath, langOrder):
    added2src, added2trgt = [], []
    # get the lines
    with open(srcPath) as srcFile:
        srcLns = srcFile.readlines()
    with open(trgtPath) as trgtFile:
        trgtLns = trgtFile.readlines()
    # add the fake lines and save the line indexes
    if len(srcLns) > len(trgtLns):
        added2trgt = list(range(len(trgtLns), len(srcLns)))
        diff = len(srcLns) - len(trgtLns)
        trgtLns += ["_na_\n"] * diff
    elif len(srcLns) < len(trgtLns):
        added2src = list(range(len(srcLns), len(trgtLns)))
        diff = len(trgtLns) - len(srcLns)
        srcLns += ["_na_\n"] * diff
    # dump
    outCommonPath = "{0}/segment.output4laser".format("/".join(srcPath.split("/")[:-1]))
    lsrSrcPath = "{0}.{1}".format(outCommonPath, langOrder[0])
    lsrTrgtPath = "{0}.{1}".format(outCommonPath, langOrder[1])
    with open(lsrSrcPath, "w") as srcFile:
        for srcLn in srcLns:
            srcFile.write(srcLn)
    with open(lsrTrgtPath, "w") as trgtFile:
        for trgtLn in trgtLns:
            trgtFile.write(trgtLn)
    return lsrSrcPath, lsrTrgtPath, outCommonPath, added2src, added2trgt


def mkGenLablFile(outCommonPath, genLblPath):
    with open("./configuration.json") as config:
        configuration = json.load(config)
    gen = """
# Modification for creating labels for Classification task and generating matched Indices for Corpus Cleaning.
# No changes was made in LASER model, only modified the output of the model.

export LASER='""" + configuration["options"]["path to laser"] + """'
if [ -z ${LASER+x} ] ; then
  echo "Please set the environment variable 'LASER'"
  exit
fi

model_dir="${LASER}/models"
encoder="${model_dir}/bilstm.93langs.2018-12-26.pt"
bpe_codes="${model_dir}/93langs.fcodes"
edir="embed"

python3 ${LASER}//source/similarity_search.py --bpe-codes ${bpe_codes} --encoder ${encoder} --base-dir . --data  """ + \
          outCommonPath + """ --lang en fr --verbose --output ${edir}/laser.output
"""
    with open(genLblPath, "w") as genFile:
        genFile.write(gen)
    return gen


def getLaserAlignAndClassif(srcFilePath, trgtFilePath, langOrder, outputFolderPath="./tmp/"):
    laserOutAlign0 = "./tmp/laser.output.{0}-{1}.align".format(langOrder[0], langOrder[1])
    laserOutAlign1 = "./tmp/laser.output.{1}-{0}.align".format(langOrder[0], langOrder[1])
    laserOutClass = "./tmp/laser.output.class"
    # equalize the length of the input files
    lsrSrcPath, lsrTrgtPath, outCommonPath, indxAdded2src, indxAdded2trgt = equalizeLength(srcFilePath, trgtFilePath,
                                                                                           langOrder)
    # remove old output files
    removeOldOuts(outputFolderPath, [laserOutAlign0, laserOutAlign1, laserOutClass])
    # apply laser (takes paths as input)
    genLblPath = "./resources/LASER/generate_labels_indices.sh"
    mkGenLablFile(outCommonPath, genLblPath)
    subprocess.call(["bash", genLblPath])
    # move the raw outputs of laser
    shutil.move("./0_class_laser.csv", laserOutAlign0)
    shutil.move("./1_class_laser.csv", laserOutAlign1)
    shutil.move("./classification_labels.out", laserOutClass)
    # adapt the raw outputs of laser to the rali format
    alignRawPath = laserOutAlign0 if sorted(langOrder) == langOrder else laserOutAlign1
    classCol = 1 if sorted(langOrder) == langOrder else 2
    indxAddedA = indxAdded2src if sorted(langOrder) == langOrder else indxAdded2trgt
    indxAddedB = indxAdded2trgt if sorted(langOrder) == langOrder else indxAdded2src
    with open(alignRawPath) as aliRaw:
        alignClean = [ln.replace("\n", "").split(",") for ln in aliRaw.readlines()]
        alignClean = [[int(ali[0]), int(ali[1])] for ali in alignClean]
        alignClean = [ali for ali in alignClean if (ali[0] not in indxAddedA and ali[1] not in indxAddedB)]
    # # output the alignments
    # with open("./tmp/laser.output.align.index", "w") as laserAlign:
    #     with open("./tmp/laser.output.align.raliformat", "w") as laserRali:
    #         for ali in alignClean:
    #             # output the alignment by alignment index
    #             laserAlign.write("{0}-{1}\n".format(ali[0], ali[1]))
    #             # get an alignment similar to the rali format
    #
    #             alignRaliFormat = ["{0}-{1} 0\n".format(ali[0], ali[1]) for ali in alignClean]
    # # output the alignment in rali format
    #
    #     for lasAlignLn in alignRaliFormat:
    #         laserRali.write(lasAlignLn)
    # # output the alignment lines
    # with open("./tmp/laser.output.segment.{0}".format(langOrder[0]), "w") as segmentSrcFile:
    #     with open("./tmp/laser.output.segment.{0}".format(langOrder[0]), "w") as segmentTrgtFile:

    # get the laser predictions into two lists: goods and bads
    noErrLst, errLst = [], []
    lsrPathA = lsrSrcPath if sorted(langOrder) == langOrder else lsrTrgtPath
    lsrPathB = lsrTrgtPath if sorted(langOrder) == langOrder else lsrSrcPath
    with open(laserOutClass) as predFile:
        preds = [ln.replace("\n", "").split(",")[classCol] for ln in predFile.readlines()]
    with open(lsrPathA) as aFile:
        aLns = [ln.replace("\n", "") for ln in aFile.readlines()]
    with open(lsrPathB) as bFile:
        bLns = [ln.replace("\n", "") for ln in bFile.readlines()]
    # get the predictions
    for indx, ali in enumerate(alignClean):
        pred = preds[indx]
        srcTrgt = [aLns[ali[0]], bLns[ali[1]]] if sorted(langOrder) == langOrder else [bLns[ali[1]], aLns[ali[0]]]
        # get the pred as good
        if pred in ["True", True]:
            noErrLst.append(srcTrgt)
        # get the pred as bad
        elif pred in ["False", False]:
            errLst.append(srcTrgt)
    return noErrLst, errLst

