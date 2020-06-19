#!/usr/bin/python
# -*- coding:utf-8 -*-

import pickle
import numpy as np
from sklearn import preprocessing


def fromTsvToMatrix(path, justTheNFirstColumns='all'):
    """ given the path to a tsv file of scores (with no header), transforms them into a numpy array """
    listOfLists = []
    with open(path) as heurFile:
        # get line
        ln = heurFile.readline()
        while ln:
            lnList = ln.replace(u'\n', u'').replace(u'na', u'-1.0').replace(u'None', u'-1.0').split(u'\t')
            if lnList != '':
                # take all the columns
                if justTheNFirstColumns == u'all':
                    listOfLists.append([float(sc) for sc in lnList])
                else:
                    listOfLists.append([float(sc) for sc in lnList[:justTheNFirstColumns]])
                # take only the n first columns
            # next line
            ln = heurFile.readline()
    return np.asarray(listOfLists)


def concatContent(listOfFilePaths, vectorDim=60):
    concatenated = None
    for fPath in listOfFilePaths:
        if concatenated is None:
            if vectorDim in [60, 62]:
                concatenated = fromTsvToMatrix(fPath)
            elif vectorDim in [13, 15]:
                concatenated = fromTsvToMatrix(fPath, justTheNFirstColumns=1)
            else:
                raise ValueError(u'the function accepts only 2 values: 13 and 60 (15 and 62 when added 2 arbitrary)')
        else:
            if vectorDim in [60, 62]:
                concatenated = np.vstack((concatenated, fromTsvToMatrix(fPath)))
            else:
                concatenated = np.vstack((concatenated, fromTsvToMatrix(fPath, justTheNFirstColumns=1)))
    return concatenated


def concatContentTrain(listOfFilePaths, vectorDim=60):
    concatenated = None
    for fPath in listOfFilePaths:
        # decide wether to train on the 13D or the 60D data
        if vectorDim in [13, 15]:
            fPath = fPath.replace(u'scoresAndMetaData', u'scores')
        # concatenate the right data
        if concatenated is None:
            concatenated = fromTsvToMatrix(fPath)
        else:
            concatenated = np.vstack((concatenated, fromTsvToMatrix(fPath)))
    return concatenated


def appendAdditionalFeat(featList):
    """ return the feature list with 2 more features :
    the nb of features indicating good and nb of features indicating bad """
    goodThreshold = [1.0, 0.65]
    badThreshold = [0.35, 0.3, 0.95, 0.1]
    nbGood = 0
    nbBad = 0
    # count the very goods: cog, wbw
    veryGoods = [featList[2], featList[9]] if len(featList) == 13 else [featList[14], featList[43]]
    for i, feat in enumerate(veryGoods):
        if feat >= goodThreshold[i]:
            nbGood += 1
    # count the very bads: fa, ion, spell, tabl
    veryBads = [featList[3], featList[4], featList[6], featList[12]]
    veryBads = veryBads if len(featList) == 13 else [featList[18], featList[22], featList[28], featList[55]]
    for i, feat in enumerate(veryBads):
        if feat < badThreshold[i]:
            nbBad += 1
    return np.append(featList, [nbGood, nbBad])


def makeClassificationBinary(annotArray):
    # if we want to use a binary system of classes
    annotArray = np.equal(annotArray, [1.0])
    annotArray = annotArray.astype(int)
    return np.array(annotArray).reshape(-1, 1)


def makeClassificationByType(annotArray):
    """ use a type based classification system where [0.0, 0.1, 0.2], [1.1, 1.2, 1.4], [1.3], [1.0] are the classes
    at output:
    0 = not aligned
    1 = good
    2 = bad qual
    3 = gibberish"""
    notBadAlignArray = np.greater_equal(annotArray, [1.0]).astype(int)
    notGood = np.greater(annotArray, [1.0]).astype(int)
    notGibbArray = np.equal(annotArray, [1.3]).astype(int)
    annotArray = notBadAlignArray+notGood+notGibbArray
    return np.array(annotArray).reshape(-1, 1)


def makeLabelClasses(annotArray):
    try:
        labelEncoder = preprocessing.LabelEncoder()
    except NameError:
        from sklearn import preprocessing
        labelEncoder = preprocessing.LabelEncoder()
    annotationClasses = labelEncoder.fit_transform(annotArray)
    return annotationClasses.reshape(-1, 1)


def getRightClasses(annotArray, makeClassifBinary=False, makeClassifByGroup=False):
    # use label as classes
    if makeClassifBinary is False and makeClassifByGroup is False:
        annotArray = makeLabelClasses(annotArray)
    # use group labels into 2+ classes
    elif makeClassifBinary is False:
        annotArray = makeClassificationByType(annotArray)

    else:
        # use a binary system of classes
        annotArray = makeClassificationBinary(annotArray)
    return annotArray


def addArbitraryFeatures(features):
    # add two arbitrary features : the nb of features indicating good and nb of features indicating bad
    arrayList = []
    for ind, featList in enumerate(features):
        arrayList.append(appendAdditionalFeat(featList))
    return np.asarray(arrayList)


def naiveOversampling(featArray, classesArray):
    """ oversampling randomly until all classes have the same number of elements
    (exceeding even the max of the most common class) """
    unq, unq_idx = np.unique(classesArray, return_inverse=True)
    unq_cnt = np.bincount(unq_idx)
    cnt = np.max(unq_cnt)
    cnt = int(cnt*1.5)
    out = np.empty((cnt * len(unq),) + featArray.shape[1:], featArray.dtype)
    outClasses = []
    for j in range(len(unq)):
        indices = np.random.choice(np.where(unq_idx == j)[0], cnt)
        outClasses += [j] * len(indices)
        out[j * cnt:(j + 1) * cnt] = featArray[indices]
    outClasses = np.asarray(outClasses).reshape(-1, 1)
    return out, outClasses


def dataTrainPreparation(listOfPathsToFeaturesTsvFiles, listOfPathsToClassificationTsvFiles,
                         makeClassifBinary=False, makeClassifGroup=False, vectorDim=60):
    # be sure the list of paths are lists of paths and not strings
    if type(listOfPathsToFeaturesTsvFiles) is str:
        listOfPathsToFeaturesTsvFiles = [listOfPathsToFeaturesTsvFiles]
    if type(listOfPathsToClassificationTsvFiles) is str:
        listOfPathsToClassificationTsvFiles = [listOfPathsToClassificationTsvFiles]
    # concatenate the content of all the feature paths
    features = concatContentTrain(listOfPathsToFeaturesTsvFiles, vectorDim)
    # add two arbitrary features : the nb of features indicating good and nb of features indicating bad
    features = addArbitraryFeatures(features)
    # concatenate the content of all the classifications paths
    annotationClasses = concatContentTrain(listOfPathsToClassificationTsvFiles)
    # if we want to use multiple classes
    annotationClasses = getRightClasses(annotationClasses, makeClassifBinary, makeClassifGroup)
    # oversample
    features, annotationClasses = naiveOversampling(features, annotationClasses)
    return features, annotationClasses


def trainSvmModel(listOfPathsToFeaturesTsvFiles, listOfPathsToClassificationTsvFiles,
                  makeClassifBinary=False, makeClassifGroup=False, vectorDim=60):
    """ given a list of paths leading to the features files and the classification (one per vector of features)
     returns a simple trained SVM """
    from sklearn import svm
    # be sure the list of paths are lists of paths and not strings
    if type(listOfPathsToFeaturesTsvFiles) is str:
        listOfPathsToFeaturesTsvFiles = [listOfPathsToFeaturesTsvFiles]
    if type(listOfPathsToClassificationTsvFiles) is str:
        listOfPathsToClassificationTsvFiles = [listOfPathsToClassificationTsvFiles]
    # concatenate the content of all the feature paths
    features = concatContentTrain(listOfPathsToFeaturesTsvFiles, vectorDim)
    features = addArbitraryFeatures(features)
    # concatenate the content of all the classifications paths
    annotationClasses = concatContent(listOfPathsToClassificationTsvFiles)
    # if we want to use multiple classes
    annotationClasses = getRightClasses(annotationClasses, makeClassifBinary, makeClassifGroup)
    # make and train the classifier
    classifier = svm.SVC(gamma='scale', kernel='rbf')
    classifier.fit(features, annotationClasses.ravel())
    return classifier


def trainRdmForestModel(listOfPathsToFeaturesTsvFiles, listOfPathsToClassificationTsvFiles,
                        makeClassifBinary=False, makeClassifType=False, vectorDim=60):
    """ given a list of paths leading to the features files and the classification (one per vector of features)
        returns a simply trained random forest classifier """
    from sklearn.ensemble import RandomForestClassifier
    features, annotationClasses = dataTrainPreparation(listOfPathsToFeaturesTsvFiles,
                                                       listOfPathsToClassificationTsvFiles,
                                                       makeClassifBinary, makeClassifType, vectorDim)
    # make and train the classifier
    classifier = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=0)
    classifier.fit(features, annotationClasses.ravel())
    return classifier


def dumpModel(model, modelFilePath):
    """
    Using pickle.
    :param model: sklearn machine learning model
    :param modelFilePath: path to the output file
    :return: dumped model
    """
    with open(modelFilePath, u'wb') as modelFile:
        pickle.dump(model, modelFile)
