#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import os
import sys
import json
import nltk
import math
from collections import Counter
from nltk.metrics import distance


########################################################################
# HEURISTIC TOOLS
########################################################################

def appendLineToFile(stringLine, filePath, addNewLine=True):
    if not theFileExists(filePath):
        createEmptyFolder(filePath.replace(filePath.split(u"/")[-1], u""))
        with open(filePath, 'w') as emptyFile:
            emptyFile.write(u'')
    if addNewLine is True:
        stringLine = u'{0}\n'.format(stringLine)
    with open(filePath, 'a') as file:
        file.write(stringLine)


def isItAlphaNumeric(char):
    """ given a character, returns True if it's alphanumeric ( ASCII alone: [a-zA-Z0-1] ), False otherwise """
    alphaNumericDecimalCodes = set([32] + list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123)))
    if ord(char) not in alphaNumericDecimalCodes:
        return False
    return True


def getEditDistance(str1, str2):
    return distance.edit_distance(str1, str2)


def getNormalizedEditDist(str1, str2, lowerCase=True):
    """ returns a score corresponding to a naive normalizaton of
     the edit dist, the closer to 1, the more distant the 2 strings are"""
    if lowerCase:
        str1, str2 = str1.lower(), str2.lower()
    return getEditDistance(str1, str2) / max(len(str1), len(str2))


def extractNumbersFromString(string, digitByDigit=False):
    """ given a string, extract all the digit characters in the string in list form as integrals """
    if digitByDigit == False:
        nbPattern = re.compile(r'[0-9]+')
    else:
        nbPattern = re.compile(r'[0-9]')
    numbers = re.findall(nbPattern, string)
    return [int(nb) for nb in numbers]


def transformNbNameToNb(stringOrStringList):
    """ given a string or a string list, if we find a number name, we replace it with the number
    (function to be perfected) """
    nbToNbName = {0.5: {u'half', u'demi', u'moitié', u'semi', u'mid', u'mi'},
                  0: {u'zero', u'zéro', u'null', u'none'},
                  1: {u'january', u'janvier', 'first', u'premier', u'première', u'1rst', u'1st', u'1er',
                      u'1ere', u'1ère', u'ist', u'ier'},
                  2: {u'two', u'deux', u'february', u'février', u'square', u'carré', u'second', u'seconde',
                      u'deuxième', u'ii', u'2nd', u'2nd', u'2nde', u'2eme', u'2ème', u'iind', u'iinde', u'iième'},
                  3: {u'three', u'trois', u'tri', u'march', u'mars', u'third', u'tiers', u'troisième', u'cube',
                      u'1pm', u'11pm', u'iii', u'3rd', u'3eme', u'3ieme', u'3ième', u'3ème', u'iiird', u'iiieme',
                      u'iième'},
                  4: {u'four', u'quatre', u'fourty', u'quarante', u'april', u'avril', u'fourth', u'quart',
                      u'quatrième', u'iiii', u'4th', u'4eme', u'4ieme', u'4ième', u'4ème', u'ivth', u'iveme',
                      u'ivème', u'ivième'},
                  5: {u'five', u'cinq', u'fifty', u'cinquante', u'mai', u'fifth',
                      u'cinquième', u'5th', u'5eme', u'5ieme', u'5ième', u'5ème', u'vth', u'veme', u'vème'},
                  6: {u'six', u'sixty', u'soixante', u'sixtieth', u'sixième', u'june', u'juin', u'6th', u'6eme',
                      u'6ieme', u'6ième', u'6ème', u'vith', u'vieme', u'vième'},
                  7: {u'seven', u'sept', u'seventy', u'septante', u'seventh', u'septième', u'july', u'juillet', u'vii',
                      u'7th', u'7eme', u'7ieme', u'7ième', u'7ème', u'viith', u'viieme', u'viième'},
                  8: {u'eight', u'huit', u'eighty', u'octante', u'eighth', u'huitième', u'august', u'aout', u'août',
                      u'viii', u'8th', u'8eme', u'8ieme', u'8ième', u'8ème', u'viiith', u'viiieme', u'viiième'},
                  9: {u'nine', u'neuf', u'ninety', u'nonante', u'ninth', u'neuvième', u'september', u'septembre',
                      u'9th', u'9eme', u'9ieme', u'9ième', u'9ème', u'ixth', u'ixeme', u'ixème', u'ixième'},
                  10: {u'ten', u'dix', u'october', u'octobre', u'tenth', u'dixième', u'10th', u'10eme', u'10ieme',
                       u'10ième', u'10ème', u'xth', u'xeme', u'xème'},
                  11: {u'eleven', u'onze', u'november', u'novembre', u'11th', u'11eme', u'11ieme', u'11ième',
                       u'11ème', u'xith', u'xieme', u'xième', u'xième'},
                  12: {u'twelve', u'douze', u'december', u'decembre', u'décembre', u'midday', u'noon', u'midi',
                       u'dozen',
                       u'douzaine', u'xii', u'12th', u'12eme', u'12ieme', u'12ième', u'12ème', u'xiith', u'xiieme',
                       u'xiième'},
                  13: {u'thirteen', u'treize', u'1pm', u'xiii', u'13th', u'13eme', u'13ieme', u'13ième', u'13ème',
                       u'xiiith', u'xiiieme', u'xiiième'},
                  14: {u'fourteen', u'quatorze', u'2pm', u'xiv', u'14th', u'14eme', u'14ieme', u'14ième', u'14ème',
                       u'xivth', u'xiveme', u'xivème', u'xivième'},
                  15: {u'fifteen', u'quinze', u'3pm', u'15th', u'15eme', u'15ieme', u'15ième', u'15ème',
                       u'xvth', u'xveme', u'xvème'},
                  16: {u'sixteen', u'seize', u'4pm', u'xvi', u'16th', u'16eme', u'16ieme', u'16ième', u'16ème',
                       u'xvith', u'xvieme', u'xvième'},
                  17: {u'seventeen', u'5pm', u'xvii', u'17th', u'17eme', u'17ieme', u'17ième', u'17ème', u'xviith',
                       u'xviieme', u'xviième'},
                  18: {u'eighteen', u'6pm', u'xviii', u'18th', u'18eme', u'18ieme', u'18ième', u'18ème', u'xviiith',
                       u'xviiieme', u'xviiième'},
                  19: {u'nineteen', u'7pm', u'xix', u'19th', u'19eme', u'19ieme', u'19ième', u'19ème', u'xixth',
                       u'xixeme', u'xixème', u'xixième'},
                  20: {u'twenty', u'vingt', u'8pm', u'xx', u'20th', u'20eme', u'20ieme', u'20ième', u'20ème', u'20th',
                       u'xxeme', u'xxème'},
                  21: {u'9pm', u'xxi', u'21th', u'21eme', u'21ieme', u'21ième', u'21ème', u'xxith', u'xxieme',
                       u'xxième'},
                  22: {u'10pm', u'22nd', u'22eme', u'22ieme', u'22ième', u'22ème'},
                  23: {u'11pm', u'23rd', u'23eme', u'23ieme', u'23ième', u'22ème'},
                  24: {u'midnight', u'minuit', u'24th', u'24eme', u'24ieme', u'24ième', u'24ème'},
                  25: {u'25th', u'25eme', u'25ieme', u'25ième', u'25ème'},
                  26: {u'26th', u'26eme', u'26ieme', u'26ième', u'26ème'},
                  27: {u'27th', u'27eme', u'27ieme', u'27ième', u'27ème'},
                  28: {u'28th', u'28eme', u'28ieme', u'28ième', u'28ème'},
                  29: {u'29th', u'29eme', u'29ieme', u'29ième', u'29ème'},
                  30: {u'thirty', u'trente', u'30th', u'30eme', u'30ieme', u'30ième', u'30ème'},
                  31: {u'31st', u'31rst', u'31eme', u'31ieme', u'31ième', u'31ème'},
                  40: {u'forty', u'quarante'}, 50: {u'fifty', u'cinquante'},
                  60: {u'sixty', u'soixante'}, 70: {u'seventy'}, 80: {u'eighty'}, 90: {u'ninety'},
                  100: {u'hundred', u'cent'}, 1000: {u'thousand', u'mille', u'mil'},
                  1000000: {u'million', u'millions'}, 1000000000: {u'billion', u'milliard', u'billions', u'milliards'}
                  }

    # (eliminated because of ambiguity mismatches) u'uni', u'mono', u'bi', u'score', u'one', u'un', u'may',
    #                                              u'i', u'v', u'x', u'iv', u'vi', u'xv', u'ix', u'xi',
    # get a set containing all the number names
    def fromDict(aDict):
        for v in aDict.values():
            for elem in v:
                yield elem

    allNbNames = set(fromDict(nbToNbName))
    # if the stringOrStringList arg is a string
    if type(stringOrStringList) is str:
        stringOrStringList = stringOrStringList.lower()
        for intNb, nameSet in nbToNbName.items():
            for name in nameSet:
                stringOrStringList = ((stringOrStringList.replace(u'{0} '.format(name), u'{0} '.format(intNb))).replace(
                    u' {0}'.format(name), u' {0}'.format(intNb))).replace(name, str(intNb))
    # if the stringOrStringList arg is a list of strings
    elif type(stringOrStringList) is list:
        # verify if there is a nb name among the tokens
        intersectNames = set(stringOrStringList).intersection(allNbNames)
        if len(intersectNames) != 0:
            for index, token in enumerate(stringOrStringList):
                # if the token corresponds to a number, we replace it
                if token in intersectNames:
                    for nb, nbNames in nbToNbName.items():
                        # replace the nb name with the number
                        if token in nbNames:
                            stringOrStringList[index] = str(nb)
    return stringOrStringList


def separate(listTok, sep):
    for index, tok in enumerate(list(listTok)):
        tokL = [to for to in tok.split(sep) if to != u'']
        newTokL = []
        for t in tokL:
            newTokL.append(t)
            newTokL.append(sep)
        listTok = listTok[:index] + newTokL[:-1] + listTok[index + 1:]
    return listTok


def copyOfString(string):
    return u'{0}*'.format(string)[:-1]


def nltkTokenizer(string, additionalSeparators=None):
    if additionalSeparators == None:
        return nltk.word_tokenize(string)
    # first tokenize as nltk would
    tokenizedString = nltk.word_tokenize(string)
    newTokenizedString = []
    # tokenize each token using the additional separators
    for token in nltk.word_tokenize(string):
        temp = copyOfString(token)
        additionalTokenization = [temp]
        # tokenize using the separators
        for separator in additionalSeparators:
            additionalTokenization = separate(additionalTokenization, separator)
        # add individual tokens if we got an additional tokenization
        if len(additionalTokenization) > 1:
            newTokenizedString = newTokenizedString + additionalTokenization
        else:
            newTokenizedString.append(token)
    return newTokenizedString


def addToDict(extractedSp, filePath, index, extrType=0):
    if filePath not in extractedSp[extrType]:
        extractedSp[extrType][filePath] = [index]
    else:
        extractedSp[extrType][filePath].append(index)
    return extractedSp


def getNbsAlone(tokList):
    finalList = []
    for tok in tokList:
        numbersIntok = extractNumbersFromString(tok, digitByDigit=False)
        finalList += numbersIntok
    return finalList


def getNbLongLines(listOfSent, n=141):
    ''' returns the number of long lines that exceed n characters '''
    longLines = 0
    for sent in listOfSent:
        # make sure the sentence has no red keywords in it
        sent = sent.replace(u'\033[1;31m', u'').replace(u'\033[0m', u'')
        long = len(sent)
        while long > n:
            longLines += 1
            long -= n
    return longLines


def getCognates(tokensList, cognateSize):
    cognates = []
    for token in tokensList:
        if len(token) > cognateSize:
            cognates.append(token[:cognateSize])
    return cognates


def heuristTokenize(string1, string2, addSeparators=None):
    addSeparators = addSeparators if addSeparators is not None else ['.', '?', '!', ',', ':', '/', '-', "''", "'", "%"]
    # tokenize if not already
    if type(string1) is str:
        string1 = string1.lower()
        string1 = nltkTokenizer(string1, addSeparators)
    if type(string2) is str:
        string2 = string2.lower()
        string2 = nltkTokenizer(string2, addSeparators)
    return string1, string2


def tableOfContentStart(aString, separateNbAndSymbScores=False):
    # if there is a number or a symbol indicating a table of contents at the start of the string
    extractedNmbrs = extractNumbersFromString(aString[:3])
    if separateNbAndSymbScores is False:
        strStart = aString[:3]
        if len(extractedNmbrs) != 0 or u'-' in strStart or u'.' in strStart or u'*' in strStart or u'•' in strStart:
            return [0]
        else:
            return [1]
    # separate the number and the symbol appearance scores
    strStart = aString[:5]
    scrs = []
    if len(extractedNmbrs) != 0:
        scrs.append(0)
    else:
        scrs.append(1)
    if u'-' in strStart or u'.' in strStart or u'*' in strStart or u'•' in strStart:
        scrs.append(0)
    else:
        scrs.append(1)
    return scrs


def makeListIntersection(iterElem1, iterElem2):
    return list((Counter(iterElem1) & Counter(iterElem2)).elements())


def isCharNgramGibberish(charTrigram):
    """ returns a boolean indicating the presence of non-alphanumeric (+ space) characters in the character-ngram
    TRUE means more than 2/3 of the chars in the trigram are non-alphanumeric"""
    # if the trigram is a repetition of the same char trice, it's possibly gibberish
    if charTrigram == charTrigram[0] * 3:
        return True
    # measure the number of potential gibberish characters
    gibbScore = 0.0
    for char in charTrigram:
        if isItAlphaNumeric(char) is False:
            gibbScore += 1.0
    # if there is 1 or more not alphanumeric character in the trigram, the trigram is classified as gibberish
    if gibbScore >= 1:
        return True
    return False


def openJsonFileAsDict(pathToFile):
    """    loads a json file and returns a dict """
    dirPath = os.path.dirname(os.path.realpath(__file__))
    try:
        pathToFile = pathToFile.replace("./resources/", "{0}/resources/".format(dirPath))
        with open(pathToFile) as openedFile:
            return json.load(openedFile)
    except FileNotFoundError:
        with open(pathToFile.replace("/bin/resources/", "/resources/")) as openedFile:
            return json.load(openedFile)


def openFauxAmisDict(enToFr=True, withDescription=False, reducedVersion=False):
    """ opens the faux amis (false cognates) dict """
    path = u'./resources/fauxAmis/fauxAmis'
    if withDescription is not False:
        path = u'{0}AndDescrip'.format(path)
    if reducedVersion is not False:
        path = u'{0}Reduced'.format(path)
    if enToFr is True:
        path = u'{0}En-Fr.json'.format(path)
    else:
        path = u'{0}Fr-En.json'.format(path)
    return openJsonFileAsDict(path)


def detectBadSpelling(tokenList, orthDictOrSet=None, lang=u'en'):
    """ given a list of tokens it returns a list containing the word and a score:
     - 0 if the token is not in the orth dict
     - 1 if it's in the orth dict """
    output = []
    if orthDictOrSet is None:
        pth = u'./resources/tokDict/{0}TokReducedLessThan1000Instances.json'.format(lang)
        orthDictOrSet = openJsonFileAsDict(pth)
        orthDictOrSet = set(orthDictOrSet.keys())
    # get rid of numbers and symbols
    nbAndSymb = re.compile(r"""[\.,:;?!\(\)\[\]\{\}"'«»`´@#$%&*+\-=<>_\\/0-9]+""")
    for indexTok, tok in enumerate(tokenList):
        tokenList[indexTok] = nbAndSymb.sub('', tok)
    tokenList = [tok for tok in tokenList if tok != u'']
    # compare to the orth dict
    for tok in tokenList:
        # lowercase it before searching in the dict
        if tok.lower() in orthDictOrSet:
            output.append(tuple([tok, 1]))
        else:
            output.append(tuple([tok, 0]))
    return output


def detectUrlAndFolderPaths(string):
    """ given a string detects if there is an url or folder path
    in the string and returns in a list the parts of the string with the urls """
    urlAndFolderPaths = re.compile(
        r'((?!\s)((([A-Z]:|\/|(~|\.)\/|http:\/\/|https:\/\/|www\.)(.(?!\s))+.)|(((?!\s)[a-z](\/|\\|\.)*)+\.([a-z]{2,4})(\/)*)))')
    allUrlsAndPaths = re.findall(urlAndFolderPaths, string)
    if len(allUrlsAndPaths) == 0:
        return False, []
    return True, allUrlsAndPaths


def openEn2FrLitteralDict():
    """ opens and returns the litteral expression and word dicts """
    exprPath = u'./resources/litteralTranslationDict/litteralEn-FrExpr.json'
    wordPath = u'./resources/litteralTranslationDict/litteralEn-FrWord.json'
    return openJsonFileAsDict(exprPath), openJsonFileAsDict(wordPath)


def charNgramArray(string, n=3):
    """ given a string, returns a list containing the character ngrams """
    ngramList = []
    for i in range(len(string) - (n - 1)):
        ngramList.append(string[i:i + n])
    return ngramList


########################################################################
# HEURISTICS
########################################################################

def nbMismatch(stringSrc, stringTrgt, includeNumberNames=True, useEditDistance=True, addInfo=False):
    """ given a string sentence pair, returns a score indicating how much the
    numbers in the source appear in the target """
    # if it's not already tokenized
    addSeparators = [u'.', u',', u':', u'/', u'-', u"''", u"'"]
    if type(stringSrc) is str:
        stringSrc = stringSrc.lower().replace(u' pm', u'pm')
        stringSrc = nltkTokenizer(stringSrc, addSeparators)
    if type(stringTrgt) is str:
        stringTrgt = stringTrgt.lower().replace(u' pm', u'pm')
        stringTrgt = nltkTokenizer(stringTrgt, addSeparators)
    # transform all number names in actual numbers
    if includeNumberNames is True:
        stringSrc = transformNbNameToNb(stringSrc)
        stringTrgt = transformNbNameToNb(stringTrgt)
    # get the tokens containing a digit
    nbrs = re.compile(r'[0-9]')
    stringSrcList = [tok for tok in stringSrc if len(re.findall(nbrs, tok)) != 0]
    stringTrgtList = [tok for tok in stringTrgt if len(re.findall(nbrs, tok)) != 0]
    # if there were no numbers, return silence
    if len(stringSrcList) + len(stringTrgtList) == 0:
        if addInfo is False:
            return None
        return None, 0, 0, 0
    # if we want to search for the exact same numbers
    elif useEditDistance == False:
        # extract the figures from the tokens
        numbersInSrc = set(getNbsAlone(stringSrcList))
        numbersInTrgt = set(getNbsAlone(stringTrgtList))
        # calculate the score of src-trgt coincidence
        nbIntersection = numbersInSrc.intersection(numbersInTrgt)
        # print(1000, len(nbIntersection) / ((len(stringSrcList) + len(stringTrgtList)) / 2), nbIntersection)
        sc = len(nbIntersection) / ((len(numbersInSrc) + len(numbersInTrgt)) / 2)
        if addInfo is False:
            return sc
        return sc, len(nbIntersection), len(numbersInSrc), len(numbersInTrgt)
    # if we want to use the edit distance to match the source digit tokens with the target ones
    else:
        nbIntersection = []
        # sort the digitfull src token list by decreasing length
        stringSrcList.sort(key=lambda tok: len(tok), reverse=True)
        # make a copy of the target list
        trgtList = stringTrgtList.copy()
        for srcTok in stringSrcList:
            # find the most similar trgt token
            mostSimil = [None, None, None, 1]
            for trgtInd, trgtTok in enumerate(trgtList):
                editDistScore = getNormalizedEditDist(srcTok, trgtTok)
                # get the less distant in the trgt tokens
                if editDistScore < 0.5 and editDistScore < mostSimil[-1]:
                    mostSimil = [srcTok, trgtTok, trgtInd, editDistScore]
            # remove the most similar from the trgt list
            if mostSimil[0] is not None:
                del trgtList[mostSimil[-2]]
                nbIntersection.append(tuple(mostSimil[:2]))
        sc = len(nbIntersection) / ((len(stringSrcList) + len(stringTrgtList)) / 2)
        if addInfo is False:
            return sc
        return sc, len(nbIntersection), len(stringSrcList), len(stringTrgtList)


def tooFewTokens(stringSrc, stringTrgt=None, nTokens=4):
    """ given a string sentence pair return 0 if there are less
    than N tokens on either the src or the trgt and return 1 otherwise """
    # if it's not already tokenized
    stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)
    # count the tokens
    if stringTrgt != None:
        if len(stringSrc) <= nTokens or len(stringTrgt) <= nTokens:
            return 0
        return 1
    score = 0 if len(stringSrc) <= nTokens else 1
    return score


def tableOfContents(stringSrc, stringTrgt, nTokens=4, contextScores=None, placeInDocument=None, addInfo=False):
    """ given a string sentence pair return a score of the ratio
    of small sentence pairs in the context of the current sp """
    # if it's not already tokenized
    stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)
    # get scores
    scores = [tooFewTokens(stringSrc, stringTrgt, nTokens)]
    # re make the token list a string so we can check the first characters
    origSrcString = u' '.join(stringSrc)
    origTrgtString = u' '.join(stringTrgt)
    # if the string is longer than 4 char
    if len(origSrcString) > 4:
        # if there is a number or a symbol indicating a table of contents at the start of the string
        scores += tableOfContentStart(origSrcString)
    # add the context to the current scores
    if contextScores is not None:
        scores = scores + contextScores
    # add the location of the sentence in the document to the current scores
    if placeInDocument is not None:
        # change the place in the doc to obtain low metric in the beginning and end of doc and a high one at the middle
        placeInDocument = math.sqrt(placeInDocument - (placeInDocument ** 2)) * 2
        scores = scores + [placeInDocument]
    if addInfo == False:
        return sum(scores) / len(scores)
    return sum(scores) / len(scores), sum(scores), len(scores)


def tableOfContentsMismatch(stringSrc, stringTrgt, nTokens=4, addInfo=False):
    """ given a string sentence pair return a score of the probability
    that one of the sentences is a table of content and the other not
    0.0 : one is and the other not
    1.0 : they are both table of contents of neither of them are"""
    # if it's not already tokenized
    stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)
    # get scores
    scoresSrc = [tooFewTokens(stringSrc, nTokens=nTokens)]
    scoresTrgt = [tooFewTokens(stringTrgt, nTokens=nTokens)]
    # re make the token list a string so we can check the first characters
    origSrcString = u' '.join(stringSrc)
    origTrgtString = u' '.join(stringTrgt)
    # if the string is longer than 4 char
    if len(origSrcString) > 4:
        # if there is a number or a symbol indicating a table of contents at the start of the string
        scoresSrc += tableOfContentStart(origSrcString, separateNbAndSymbScores=True)
    if len(origTrgtString) > 4:
        # if there is a number or a symbol indicating a table of contents at the start of the string
        scoresTrgt += tableOfContentStart(origTrgtString, separateNbAndSymbScores=True)
    # calculate the difference between the src and target scores
    scSrc = float(sum(scoresSrc)) / float(len(scoresSrc))
    scTrgt = float(sum(scoresTrgt)) / float(len(scoresTrgt))
    # if return the score difference between them, 0.0 = they are very different and 1.0 = they are exactly alike
    if addInfo == False:
        return 1.0 - abs(scSrc - scTrgt)
    return 1.0 - abs(scSrc - scTrgt), sum(scoresSrc), sum(scoresTrgt), len(scoresSrc), len(scoresTrgt)


def cognateCoincidence(stringSrc, stringTrgt, cognateSize=4, addInfo=False):
    """ given a string sentence pair return the ratio of coincidence
     between the cognates (start of word char ngram) between source and target"""
    # if it's not already tokenized
    stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)
    # sort by decreasing length of the original word
    stringSrc.sort(key=lambda tok: len(tok), reverse=True)
    stringTrgt.sort(key=lambda tok: len(tok), reverse=True)
    # compile the cognates of each token for the source and target
    srcCognates = getCognates(stringSrc, cognateSize)
    trgtCognates = set(getCognates(stringTrgt, cognateSize))
    # get intersection of cognates
    intersection = [cog for cog in srcCognates if cog in trgtCognates]
    # if there is nothing in the intersection, return silence, we can't infer anything
    if len(intersection) == 0:
        if addInfo is False:
            return None
        return None, len(intersection), len(srcCognates), len(trgtCognates)
    smallerLength = min(len(srcCognates), len(trgtCognates))
    # if there are no cognates to be found in at least one of the sentences
    if smallerLength == 0:
        if addInfo is False:
            return None, len(intersection), len(srcCognates), len(trgtCognates)
        return 0
    # if there are cognates
    sc = len(intersection) / smallerLength
    if addInfo is False:
        return sc
    return sc, len(intersection), len(srcCognates), len(trgtCognates)


def compareLengths(stringSrc, stringTrgt, useCharInsteadOfTokens=False, addInfo=False, onlyLongSentOfNPlusLen=10):
    """ given a string sentence pair return a score of how comparable the lengths of
     the source and target are. 0.0 being very dissimilar lengths and 1.0 being similar lengths """
    # use the token size instead of the char size
    if useCharInsteadOfTokens == False:
        stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)
    elif type(stringSrc) is list and type(stringTrgt) is list:
        stringSrc, stringTrgt = u' '.join(stringSrc), u' '.join(stringTrgt)
    # get the lengths
    srcLength = len(stringSrc)
    trgtLength = len(stringTrgt)
    diff = float(abs(srcLength - trgtLength))
    # get the silence
    if srcLength + trgtLength == 0:
        if addInfo is False:
            return None
        return None, int(diff), srcLength, trgtLength
    # if we take only the long sentences into account, short sentences are returned as silence
    if onlyLongSentOfNPlusLen != None:
        if srcLength <= onlyLongSentOfNPlusLen and trgtLength <= onlyLongSentOfNPlusLen:
            if addInfo is False:
                return None
            return None, 0, 0, 0
    # get the score
    sc = min([srcLength, trgtLength]) / max([srcLength, trgtLength])
    if addInfo is False:
        return sc
    return sc, int(diff), srcLength, trgtLength


def fauxAmis(stringEn, stringFr, addInfo=False, fauxAmisEn=None, fauxAmisFr=None):
    """ given the SP separated in english and french, returns a score between 0 and 1 representing the quality of the
    translation according to the presence or absence of faux amis (false cognates), 0.0 being bad and 1.0 being good"""
    if fauxAmisEn is None:
        fauxAmisEn = openFauxAmisDict(enToFr=True, withDescription=False, reducedVersion=False)
    if fauxAmisFr is None:
        fauxAmisFr = openFauxAmisDict(enToFr=False, withDescription=False, reducedVersion=False)
    # tokenize if not already
    stringEn, stringFr = heuristTokenize(stringEn, stringFr)
    # get the singulars too
    singular = [e[:-1] for e in stringEn if e[-1] == u's']
    stringEn = stringEn + singular
    singular1 = [e[:-1] for e in stringFr if e[-1] == u's']
    singular2 = [u'{0}al'.format(e[:-3]) for e in stringFr if e[-3:] == u'aux']
    stringFr = stringFr + singular1 + singular2
    # if we find a faux-ami in the english string we check if the french counterpart is in the target
    englishFA = []
    frenchFA = []
    totalFA = []
    # get the english faux amis
    for enTok in stringEn:
        if enTok in fauxAmisEn:
            # add it to the english faux amis
            englishFA.append(enTok)
            # we check if the corresponding french faux ami is there too
            if fauxAmisEn[enTok] in stringFr:
                totalFA.append(enTok)
    # get the french faux amis
    for frTok in stringFr:
        if frTok in fauxAmisFr:
            # add it to the english faux amis
            frenchFA.append(frTok)
    # if there were no FA, return silence
    if len(englishFA) == 0 or len(frenchFA) == 0:
        if addInfo is False:
            return None
        return None, 0, len(englishFA), len(frenchFA)
    # otherwise return the score and metadata
    avgFaLen = (float(len(englishFA)) + float(len(frenchFA))) / 2.0
    scFa = 1.0 - (float(len(totalFA)) / avgFaLen)
    if addInfo is False:
        return scFa
    return scFa, len(totalFA), len(englishFA), len(frenchFA)


def ionSuffixMismatch(stringSrc, stringTrgt, addInfo=False):
    """ given the source and target strings, counts how many -ion words appear in both sides
     the more different these numbers are, the less likely to be aligned """
    # tokenize if not already
    stringSrc, stringTrgt = heuristTokenize(stringSrc, stringTrgt)

    # count how many ion words there are

    def hasIonSuffix(token):
        if token[-3:] == u'ion':
            return True
        elif token[-4:] == u'ions':
            return True
        return False

    ionInSrc = [tok for tok in stringSrc if hasIonSuffix(tok) is True]
    ionInTrgt = [tok for tok in stringTrgt if hasIonSuffix(tok) is True]
    # take the silence into account
    if len(ionInSrc) + len(ionInTrgt) <= 2:
        if addInfo is False:
            return None
        return None, 0, 0
    # return the score: the smallest of the src/trgt divided by the greater
    smallest = min([len(ionInSrc), len(ionInTrgt)])
    greatest = max([len(ionInSrc), len(ionInTrgt)])
    scIon = float(smallest) / float(greatest)
    if addInfo is False:
        return scIon
    return scIon, len(ionInSrc), len(ionInTrgt)


def stopWordsMismatch(stringEn, stringFr, addInfo=False, stopWordsEnFrDict=None):
    """ given the english and french sentences, it returns a score of how many the presence of
     english stopwords is reflected in the french sentence """
    stopWEn, stopWEnFr = [], []
    if stopWordsEnFrDict is None:
        stopWordsEnFrDict = path = openJsonFileAsDict(u'./resources/litteralTranslationDict/stopWordsEn-Fr.json')
    # tokenize if not already
    stringEn, stringFr = heuristTokenize(stringEn, stringFr)
    # search for the stopwords in english
    for tokEn in stringEn:
        if tokEn in stopWordsEnFrDict:
            stopWEn.append(tokEn)
            # search the french tokens for a translation of the english stop words
            stringFrCopy = list(stringFr)
            for tokFr in stopWordsEnFrDict[tokEn]:
                if tokFr in stringFrCopy:
                    stopWEnFr.append(tokFr)
                    stringFrCopy.remove(tokFr)
                    break
    # take the silence into account
    if len(stopWEnFr) + len(stopWEn) == 0:
        if addInfo is False:
            return None
        return None, 0, 0
    # we use the english as the base because of its lack of genre liaison and lexic simplicity
    scSW = float(len(stopWEnFr)) / float(len(stopWEn))
    if addInfo is False:
        return scSW
    return scSW, len(stopWEn), len(stopWEnFr)


def spellingCheck(stringEn, stringFr, addInfo=False, enLexicon=None, frLexicon=None):
    """ returns a score of the general spelling of both sentences (mean of both),
     0.0 being awful spelling, 1.0 being perfect spelling """
    # tokenize if not already
    stringEn, stringFr = heuristTokenize(stringEn, stringFr)
    # get the score for each token in english and french
    tokenScoreEn = detectBadSpelling(stringEn, lang=u'en', orthDictOrSet=enLexicon)
    tokenScoreFr = detectBadSpelling(stringFr, lang=u'fr', orthDictOrSet=frLexicon)
    # get one score for the whole sentence pair
    sumScEn = 0
    sumScFr = 0
    for tokScTupl in tokenScoreEn:
        if tokScTupl[1] == 1:
            sumScEn += 1
    for tokScTupl in tokenScoreFr:
        if tokScTupl[1] == 1:
            sumScFr += 1
    # take the silence into account
    if len(tokenScoreEn) == 0 or len(tokenScoreFr) == 0:
        if addInfo is False:
            return None
        return None, sumScEn, sumScFr, len(tokenScoreEn), len(tokenScoreFr)
    # get the score
    scSpell = float(sumScEn + sumScFr) / float(len(tokenScoreEn) + len(tokenScoreFr))
    if addInfo is False:
        return scSpell
    return scSpell, sumScEn, sumScFr, len(tokenScoreEn), len(tokenScoreFr)


def urlMismatch(stringSrc, stringTrgt, addInfo=False):
    """ 1.0 = has the same number of url in src and trgt
     0.5 = has twice as many urls in one side
     0.0 = has urls on one side and not the other"""
    # if the src and trgt strings are tokenized, join them in order to get the urls
    if type(stringSrc) is list:
        tokensSrc = list(stringSrc)
        stringSrc = u' '.join(stringSrc)
    else:
        tokensSrc = stringSrc.replace(u'\n', u'').replace(u'\t', u' ').split(u' ')
    if type(stringTrgt) is list:
        tokensTrgt = list(stringTrgt)
        stringTrgt = u' '.join(stringTrgt)
    else:
        tokensTrgt = stringTrgt.replace(u'\n', u'').replace(u'\t', u' ').split(u' ')
    # get the urls
    srcContainsUrl, srcUrlList = detectUrlAndFolderPaths(stringSrc)
    trgtContainsUrl, trgtUrlList = detectUrlAndFolderPaths(stringTrgt)
    # if there is no url, we return the silence
    if srcContainsUrl is False and trgtContainsUrl is False:
        if addInfo is False:
            return None
        return None, 0, 0, len(tokensSrc), len(tokensTrgt)
    # score the mismatch of urls on each side
    smallest = min([len(srcUrlList), len(trgtUrlList)])
    greatest = max([len(srcUrlList), len(trgtUrlList)])
    scUrl = float(smallest) / float(greatest)
    if addInfo is False:
        return scUrl
    return scUrl, len(srcUrlList), len(trgtUrlList), len(tokensSrc), len(tokensTrgt)


def monoling(stringSrc, stringTrgt, addInfo=False):
    """ verifies if part of the source is in the target or if part of the target is in the source
     and returns a score of how much of one is in the other
     1.0 = no part of the string is shared
     0.0 = the source and target are exactly the same"""
    # if the src and trgt strings are tokenized, join them in order to get the urls
    if type(stringSrc) is list and type(stringTrgt) is list:
        tokensSrc = list(stringSrc)
        stringSrc = u' '.join(stringSrc)
        tokensTrgt = list(stringTrgt)
        stringTrgt = u' '.join(stringTrgt)
    else:
        tokensSrc, tokensTrgt = heuristTokenize(stringSrc, stringTrgt)
    # take the silence into account
    if len(tokensSrc) <= 10 or len(tokensTrgt) <= 10:
        if addInfo is False:
            return None
        return None, len(stringSrc), len(stringTrgt), len(tokensSrc), len(tokensTrgt)
    smallest = min([len(stringSrc), len(stringTrgt)])
    greatest = max([len(stringSrc), len(stringTrgt)])
    scMono = float(smallest) / float(greatest)
    # compare
    if stringSrc == stringTrgt:
        if addInfo is False:
            return 0.0
        return 0.0, len(stringSrc), len(stringTrgt), len(tokensSrc), len(tokensTrgt)
    elif stringSrc in stringTrgt:
        if addInfo is False:
            return scMono
        return scMono, len(stringSrc), len(stringTrgt), len(tokensSrc), len(tokensTrgt)
    elif stringTrgt in stringSrc:
        if addInfo is False:
            return scMono
        return scMono, len(stringSrc), len(stringTrgt), len(tokensSrc), len(tokensTrgt)
    # if there is no exact similarity return silence (could be perfected by measuring the edit distance)
    else:
        if addInfo is False:
            return None
        return None, len(stringSrc), len(stringTrgt), len(tokensSrc), len(tokensTrgt)


def litteralTranslationMismatch(stringEn, stringFr, addInfo=False, litteralExprDict=None, litteralWordDict=None):
    """ given the english and french sentences, it returns a score of how close
    is the english sentence to its word-by-word french translation,
     - 0.0 : the french sentence has no token in common with the english sentence
     - 1.0 : the french sentence is very similar to the english sentence """
    tokensEn, intersectionTokens = set([]), set([])
    if litteralExprDict is None or litteralWordDict is None:
        litteralExprDict, litteralWordDict = openEn2FrLitteralDict()
    # untokenize the english string if needed
    if type(stringEn) is list:
        stringEn, stringFr = u' '.join(stringEn.lower()), u' '.join(stringFr.lower())
    # the expressions first
    for starbExpr in litteralExprDict:
        starbExprLw = starbExpr.lower()
        # search for the expression in the english sentence
        if starbExprLw in stringEn:
            # remove from the english string
            stringEn = stringEn.replace(starbExprLw, u'')
            # add to the english tokens set
            tokensEn.add(starbExprLw)
            # add to the intersection if the expression translation appears also in the french string
            for frencExpr in litteralExprDict[starbExpr]:
                if frencExpr.lower() in stringFr:
                    # remove from the french string
                    stringFr = stringFr.replace(frencExpr.lower(), u'')
                    # add to the intersection token set
                    intersectionTokens.add(frencExpr.lower())
    # tokenize
    stringEn, stringFr = heuristTokenize(stringEn, stringFr)
    # lowercase all the word keys
    for wordKey in dict(litteralWordDict):
        if wordKey.lower() != wordKey:
            litteralWordDict[wordKey.lower()] = litteralWordDict[wordKey]
    # the words
    for enTok in stringEn:
        if enTok in litteralWordDict:
            # add to the english token set
            tokensEn.add(enTok)
            # if it also appears in french
            for possibleTranslation in litteralWordDict[enTok]:
                if possibleTranslation in stringFr:
                    # add it to the french token set
                    intersectionTokens.add(possibleTranslation)
                    # remove it from the french
                    stringFr.remove(possibleTranslation)
    # take the silence into account
    if len(tokensEn) + len(intersectionTokens) == 0 or len(stringEn) <= 10 or len(stringFr) <= 10:
        if addInfo is False:
            return None
        return None, 0, 0
    # we use the english as the base because of its lack of genre liaison and lexic simplicity
    scSB = float(len(intersectionTokens)) / float(len(tokensEn))
    if addInfo is False:
        return scSB
    return scSB, len(tokensEn), len(intersectionTokens)


def punctAndSymb(stringSrc, stringTrgt, addInfo=False):
    """ given the SP source and target, returns a score between 0 and 1 representing the
    presence of punctuation and symbols, 0.0 being not having any in common
     and 1.0 being havging the exact same type and number of punct.&symb. in common """
    # un-tokenize if not already
    if type(stringSrc) is list:
        stringSrc = u' '.join(stringSrc)
    if type(stringTrgt) is list:
        stringTrgt = u' '.join(stringTrgt)
    # define the punct and symb to look for
    punctSymb = {u'!', u'"', u"'", u',', u'.', u':', u';', u'?', u'-', u'(', u')', u'[', u']', u'{', u'}', u'#', u'$',
                 u'%', u'&', u'*', u'+', u'/', u'\\', u'<', u'>', u'=', u'@', u'^', u'_', u'`', u'|', u'~'}
    # we look-up for punctuation and symbols in the src and trgt
    srcPunctAndSymb = []
    trgtPunctAndSymb = []
    for char in stringSrc:
        # in the src
        if char in punctSymb:
            srcPunctAndSymb.append(char)
    for char in stringTrgt:
        # in the trgt
        if char in punctSymb:
            trgtPunctAndSymb.append(char)
    intersection = makeListIntersection(srcPunctAndSymb, trgtPunctAndSymb)
    # if there is no or very low intersection, return silence
    if len(intersection) <= 2:
        if addInfo is False:
            return None
        return None, len(intersection), len(srcPunctAndSymb), len(trgtPunctAndSymb)
    # otherwise return the score and metadata
    avgPunctSymbLen = (float(len(srcPunctAndSymb)) + float(len(trgtPunctAndSymb))) / 2.0
    scPs = (float(len(intersection)) / avgPunctSymbLen)
    if addInfo is False:
        return scPs
    return scPs, len(intersection), len(srcPunctAndSymb), len(trgtPunctAndSymb)


def gibberish(stringSrc, stringTrgt, addInfo=False):
    """ given the SP source and target, returns a score between 0 and 1 representing the presence of "gibberish"
     (unreadeable and incomprehensible text) inside the 2 strings
     0.0 being it's very probably gibberish
     1.0 being it's very unlikely to be gibberish"""
    # un-tokenize if not already
    if type(stringSrc) is list:
        stringSrc = (u''.join(stringSrc))
    if type(stringTrgt) is list:
        stringTrgt = (u''.join(stringTrgt))
    stringSrc = stringSrc.replace(u' ', u'').replace(u'\t', u'').replace(u'\n', u'')
    stringTrgt = stringTrgt.replace(u' ', u'').replace(u'\t', u'').replace(u'\n', u'')
    # get the trigram set of the source
    srcTrigramSet = set(charNgramArray(stringSrc, n=3))
    srcGibb3grams = []
    trgtGibb3grams = []
    if len(srcTrigramSet) == 0:
        scGibbSrc = 0
    else:
        # get the source trigrams that appear to be gibberish
        for src3gram in srcTrigramSet:
            if isCharNgramGibberish(src3gram) is True:
                srcGibb3grams.append(src3gram)
        scGibbSrc = float(len(srcGibb3grams)) / float(len(srcTrigramSet))
    # get the trigram set of the target
    trgtTrigramSet = set(charNgramArray(stringTrgt, n=3))
    if len(trgtTrigramSet) == 0:
        scGibbTrgt = 0
    else:
        # get the target trigrams that appear to be gibberish
        for trgt3gram in trgtTrigramSet:
            if isCharNgramGibberish(trgt3gram) is True:
                trgtGibb3grams.append(trgt3gram)
        scGibbTrgt = float(len(trgtGibb3grams)) / float(len(trgtTrigramSet))
    # if the strings are too short (less than 10 char), return silence
    if len(stringSrc) <= 10 or len(stringTrgt) <= 10:
        if addInfo is False:
            return None
        return None, len(srcGibb3grams), len(trgtGibb3grams), len(srcTrigramSet), len(trgtTrigramSet)
    # get the score
    scGibb = 1.0 - ((scGibbSrc + scGibbTrgt) / 2)
    # return the score
    if addInfo is False:
        return scGibb
    return scGibb, len(srcGibb3grams), len(trgtGibb3grams), len(srcTrigramSet), len(trgtTrigramSet)


########################################################################
# META-HEURISTIC TOOLS
########################################################################

def sc2bool(sc, scThreshhold=None):
    """
    Given a minimum and maximum thresholds, transforms a normalized threshold into a "boolean" score (True, False, None)
    :param sc: float score
    :param scThreshhold: list containing 2 floats (minimum and maximum thresholds)
    :return: True if score indicates aligned, False if it indicates not aligned, None if indicates silence
    """
    scThreshhold = scThreshhold if (scThreshhold is not None and type(scThreshhold) is list) else [0.44, 0.74]
    # returns None (silence) if the score is None
    if sc is None:
        return None
    # returns False if the score indicates the SP has an error (below min threshold)
    if sc < scThreshhold[0]:
        return False
    # returns True if the score indicates the SP has no error (below max threshold)
    elif sc >= scThreshhold[1]:
        return True
    # returns None (silence) if the score is in between the min and max thresholds
    return None


def applyHeur(heurFunc, string1, string2):
    # ATTENTION !!! : the following dictionnary contains function objects as keys
    thresholds = {nbMismatch: [0.5, 1.0], compareLengths: [0.35, 0.7], cognateCoincidence: [0.1, 0.2],
                  fauxAmis: [float("-inf"), 0.6], ionSuffixMismatch: [0.5, 0.65], stopWordsMismatch: [0.3, 0.9],
                  spellingCheck: [0.25, 0.85], urlMismatch: [0.9, 0.95], monoling: [0.95, float("inf")],
                  litteralTranslationMismatch: [0.25, 0.65], punctAndSymb: [0.5, 0.85],
                  gibberish: [0.1, 0.85], tableOfContentsMismatch: [0.65, 0.75]}
    # get scores: bool decision and meta data (intermediary analytics)
    if heurFunc is not compareLengths:
        heurScoreAndMeta = heurFunc(string1, string2, addInfo=True)
    else:
        heurScoreAndMeta = heurFunc(string1, string2, onlyLongSentOfNPlusLen=10, addInfo=True)
    heurScore = heurScoreAndMeta[0]
    heurDecision = sc2bool(heurScore, thresholds[heurFunc])
    # add the remaining medatadata in specific cases
    if heurFunc is nbMismatch:
        nbSupplMeta = nbMismatch(string1, string2, includeNumberNames=True, addInfo=True)
        heurScoreAndMeta = [heurScoreAndMeta[0]] + [nbSupplMeta[0]] + list(heurScoreAndMeta[1:]) + list(nbSupplMeta[1:])
    elif heurFunc is compareLengths:
        lenSuplMeta = compareLengths(string1, string2, useCharInsteadOfTokens=True, addInfo=True)
        heurScoreAndMeta = [heurScoreAndMeta[0]] + [lenSuplMeta[0]] + list(heurScoreAndMeta[2:]) + list(lenSuplMeta[2:])
    return heurDecision, heurScoreAndMeta


def getAllHeurScores(stringSrc, stringTrgt, langOrder=None):
    """
    Given a sentence pair in English and French, outputs
    all heuristic scores and meta scores: nb len cog fa ion sw spell url mono wbw punct gibb tabl
    'nb', scAb, totalIntersect, totalSrc, totalTrgt, ttInterAb, ttSrcAb, ttTrgtAb,
    'len', scCh, totalSrc, totalTrgt, ttSrcCh, ttTrgtCh,
    'cog', totalIntersect, totalSrc, totalTrgt,
    'fa', totalIntersect, totalSrc, totalTrgt,
    'ion', totalSrc, totalTrgt,
    'sw', totalSrc, totalTrgt,
    'spell', totalElSrc, totalElTrgt, totalSrc, totalTrgt,
    'url', totalElSrc, totalElTrgt, totalSrc, totalTrgt,
    'mono', totalElSrc, totalElTrgt, totalSrc, totalTrgt,
    'wbw', totalSrc, totalTrgt,
    'punct', totalIntersect, totalSrc, totalTrgt,
    'gibb', totalElSrc, totalElTrgt, totalSrc, totalTrgt
    'tabl', totalElSrc, totalElTrgt, totalSrc, totalTrgt,
    :param stringSrc: source sentence (in En or Fr)
    :param stringTrgt: target sentence (in En or Fr)
    :param langOrder: the 1rst element in the list corresponds to the lang id of the source and the 2nd to the target's
    :return: decision (bool) and scores+metascores for the heuristics
            (nb len cog fa ion sw spell url mono wbw punct gibb tabl)
    """
    langOrder = langOrder if langOrder is not None else ["en", "fr"]
    sEn, sFr = [stringTrgt, stringSrc] if langOrder[0].lower() in ["fr", "fre", "french"] else [stringSrc, stringTrgt]
    # number coincidence
    nbDecision, nbMeta = applyHeur(nbMismatch, stringSrc, stringTrgt)
    # disproportionate length
    lenDecision, lenMeta = applyHeur(compareLengths, stringSrc, stringTrgt)
    # cognates
    cogDecision, cogMeta = applyHeur(cognateCoincidence, stringSrc, stringTrgt)
    # faux-amis coincidence
    faDecision, faMeta = applyHeur(fauxAmis, sEn, sFr)
    # ion suffixes mismatch
    ionDecision, ionMeta = applyHeur(ionSuffixMismatch, stringSrc, stringTrgt)
    # stop words mismatch
    swDecision, swMeta = applyHeur(stopWordsMismatch, sEn, sFr)
    # spell check
    spellDecision, spellMeta = applyHeur(spellingCheck, sEn, sFr)
    # url detection
    urlDecision, urlMeta = applyHeur(urlMismatch, stringSrc, stringTrgt)
    # monolingual sentences detection
    monoDecision, monoMeta = applyHeur(monoling, stringSrc, stringTrgt)
    # word by word translation mismatch
    wbwDecision, wbwMeta = applyHeur(litteralTranslationMismatch, sEn, sFr)
    # punctuation and symbols mismatch
    punctDecision, punctMeta = applyHeur(punctAndSymb, stringSrc, stringTrgt)
    # gibberish presence
    gibbDecision, gibbMeta = applyHeur(gibberish, stringSrc, stringTrgt)
    # table of contents mismatch detector
    tablDecision, tablMeta = applyHeur(tableOfContentsMismatch, stringSrc, stringTrgt)
    # order : nb len cog fa ion sw spell url mono wbw punct gibb tabl
    scoresAndMetas = [nbDecision, nbMeta, lenDecision, lenMeta, cogDecision, cogMeta, faDecision, faMeta,
                      ionDecision, ionMeta, swDecision, swMeta, spellDecision, spellMeta,
                      urlDecision, urlMeta, monoDecision, monoMeta, wbwDecision, wbwMeta,
                      punctDecision, punctMeta, gibbDecision, gibbMeta, tablDecision, tablMeta]
    return scoresAndMetas


########################################################################
# META-HEURISTICS
########################################################################

def getTypePred(stringSrc, stringTrgt, langOrder=None, humanReadable=False, dm=None):
    """
    Given a sentence pair, returns a prediction if there is an error in it and what type of error it is
    (gold, alignment error, quality error, gibberish)
    :param stringSrc: source sentence (in En or Fr)
    :param stringTrgt: target sentence (in En or Fr)
    :param langOrder: the 1rst element in the list corresponds to the lang id of the source and the 2nd to the target's
    :param humanReadable: If True, returns the classes as a short human-readable string
    :param dm: list of the decision "scores" of all heuristics (nb len cog fa ion sw spell url mono wbw punct gibb tabl)
    :return: predicted class: 0 (absence of error in the sentence pair), 1 ("gold" error), 2 (quality error),
            3 (gibberish), None (silence/uncertain of presence of error) with a respective score of the probability of
            said type (0.0 == not at all probable, 1.0 == extremely probable)
    """
    # get decisions based on heur scores
    dm = getAllHeurScores(stringSrc, stringTrgt, langOrder) if dm is None else dm
    # decision order : nb(0) len(1) cog(2) fa(3) ion(4) sw(5) spell(6) url(7) mono(8) wbw(9) punct(10) gibb(11) tabl(12)
    d = [dm[0], dm[2], dm[4], dm[6], dm[8], dm[10], dm[12], dm[14], dm[16], dm[18], dm[20], dm[22], dm[24]]
    # absence of errors : nb len wbw punct
    noError = len([t for t in [d[0], d[1], d[9], d[10]] if t is True])
    # alignment error : nb len cog ion sw url wbw punct
    alignError = len([f for f in [d[0], d[1], d[2], d[4], d[5], d[7], d[9], d[10]] if f is False])
    # quality error : fa spell mono tabl
    qualError = len([f for f in [d[3], d[6], d[8], d[12]] if f is False])
    # gibberish : gibb
    gibbError = 1 if d[11] is False else 0
    # predict the type of error encountered (no error, alignment error, quality error, gibberish)
    if noError > alignError and noError > qualError and noError > gibbError:
        noErrorScore = noError/(noError+(sum([alignError, qualError])/2.0))
        return [0, noErrorScore] if humanReadable is not True else ["gold", noErrorScore]
    elif gibbError == 1:
        gibbErrorScore = 1/(1+noError)
        return [3, gibbErrorScore] if humanReadable is not True else ["gibberish", gibbErrorScore]
    elif alignError > qualError:
        alignErrorScore = alignError/(alignError+qualError+noError)
        return [1, alignErrorScore] if humanReadable is not True else ["alignment_error", alignErrorScore]
    elif qualError > 0:
        qualErrorScore = qualError/(qualError+alignError+noError)
        return [2, qualErrorScore] if humanReadable is not True else ["quality_error", qualErrorScore]
    # silence : uncertain to determine
    return [None, 1.0] if humanReadable is not True else ["silver", 1.0]


def getBoolPred(stringSrc, stringTrgt, langOrder=None, humanReadable=False, dm=None):
    """
    Given a sentence pair, returns a prediction if there is an error in it
    (any error: with alignment, with quality, etc.)
    :param stringSrc: source sentence (in En or Fr)
    :param stringTrgt: target sentence (in En or Fr)
    :param langOrder: the 1rst element in the list corresponds to the lang id of the source and the 2nd to the target's
    :param humanReadable: If True, returns the classes as a short human-readable string
    :param dm: list of the decision "scores" of all heuristics (nb len cog fa ion sw spell url mono wbw punct gibb tabl)
    :return: predicted class: 1 (absence of error in the sentence pair) or 0 (an error appears) or
            None (silence/uncertain of presence of error)
    """
    # get decisions based on heur scores
    dm = getAllHeurScores(stringSrc, stringTrgt, langOrder) if dm is None else dm
    # decision order : nb(0) len(1) cog(2) fa(3) ion(4) sw(5) spell(6) url(7) mono(8) wbw(9) punct(10) gibb(11) tabl(12)
    d = [dm[0], dm[2], dm[4], dm[6], dm[8], dm[10], dm[12], dm[14], dm[16], dm[18], dm[20], dm[22], dm[24]]
    # worst errors : len, fa, mono, gibb
    worstError = len([f for f in [d[1], d[3], d[8], d[11]] if f is False])
    # some errors : nb ion sw spell url wbw punct tabl
    someError = len([f for f in [d[0], d[2], d[4], d[5], d[6], d[7], d[9], d[10], d[12]] if f is False])
    # no evident errors : ion punct
    maybeError = len([t for t in [d[1], d[10]] if t is True])
    # absence of errors : nb wbw
    noError = len([t for t in [d[0], d[9]] if t is True])
    # get prediction for "errors" class using a weighted vote
    if worstError >= 1 or someError >= 3:
        return 0 if humanReadable is not True else "error"
    # get prediction for "no errors" class using a weighted vote
    if noError == 2 or (noError == 1 and maybeError >= 1):
        return 1 if humanReadable is not True else "gold"
    # silence : uncertain to determine
    return None if humanReadable is not True else "silver"


def getBoolAndTypePreds(stringSrc, stringTrgt, langOrder=None, humanReadable=False, boolClassify=True):
    """
    Given a sentence pair, returns both the boolean and the type predictions
    :param stringSrc: source sentence (in En or Fr)
    :param stringTrgt: target sentence (in En or Fr)
    :param langOrder: the 1rst element in the list corresponds to the lang id of the source and the 2nd to the target's
    :param humanReadable: If True, returns the classes as a short human-readable string
    :return: predicted class: 1 (absence of error in the sentence pair) or 0 (an error appears) or
            None (silence/uncertain of presence of error)
    """
    dm = getAllHeurScores(stringSrc, stringTrgt, langOrder)
    if boolClassify not in [True, "metaheuristic"]:
        boolClass = None
    else:
        boolClass = getBoolPred(stringSrc, stringTrgt, langOrder, humanReadable, dm)
    typeClass = getTypePred(stringSrc, stringTrgt, langOrder, humanReadable, dm)
    return boolClass, typeClass, dm


# nb(0) len(1) cog(2) fa(3) ion(4) sw(5) spell(6) url(7) mono(8) wbw(9) punct(10) gibb(11) tabl(12)
