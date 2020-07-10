#!/usr/bin/python
# -*- coding:utf-8 -*-

from random import randint
from shutil import copyfile
import xml.etree.ElementTree as ET


def getListFromTmx(tmxFilePath):
    langOrder = []
    contentList = []
    tree = ET.parse(tmxFilePath)
    root = tree.getroot()
    for indChild, child in enumerate(root[1]):
        flag = child.get("flag_type")
        score = child.get("flag_score")
        # make sure it has the right structure
        if child.tag == "tu":
            tuList = []
            if flag is not None:
                e = 0
                # TODO: mark flag differently
            # get the language
            for indTuv, tuv in enumerate(child):
                attributes = tuv.attrib
                langAttribute = [a for a in attributes if "lang" in a][0]
                lang = attributes[langAttribute]
                # get the language order
                if indChild == 0 and indTuv in [0, 1]:
                    langOrder.append(lang)
                # get the text
                tuvText = tuv[0].text
                # add the language and text
                tuList.append([flag, lang, tuvText, score])
            contentList.append(tuList)
    return contentList


def getHeaderAndFootWithBar():
    navCheckboxes = {"Unspecified error": "error", "Alignment not found": "n_alignment_error",
                     "Alignment error": "alignment_error", "Quality error": "quality_error",
                     "Gibberish": "gibberish", "Gold": "gold"}
    # header metadata and css internal stylesheet
    header = """\n<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="utf-8" />\n"""
    header += """    <link rel="stylesheet" href="styles.css">  </head>\n  <body>\n    <div class="navbar">\n"""
    header += """      <table border="0px">\n        </tr>\n"""
    for txt, err in navCheckboxes.items():
        header += """      <th><label class="container">{0}\n""".format(txt)
        header += """        <input type="checkbox" checked="checked"  onclick="uncolor_class('{0}')">\n""".format(err)
        header += """        <span class="checkmark"></span>\n        </label></th>\n"""
    header += """        </tr>\n      </table>\n    </div>\n"""
    foot = """    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>\n"""
    foot += """    <script src="app.js"></script>  </body>\n  </html>"""
    return header, foot


def getHeaderAndFoot():
    # header metadata and css internal stylesheet
    header = """\n<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="utf-8" />\n"""
    header += """    <link rel="stylesheet" href="styles.css">  </head>\n  <body>\n"""
    foot = """    <div class="container">\n      <div class="vertical-center">\n"""
    foot += """<button type="button" class="button greybutton" onclick="to_tmx()">Selection to TMX</button>"""
    foot += """\n      </div>\n    </div>\n\n    <p>&nbsp;</p>\n"""
    foot += """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>\n"""
    foot += """<script src="app.js"></script>  </body>\n</html>"""
    return header, foot


def verboseFloatScore(flagType, flagScore):
    commentDict = {"gold": {0.4: ["It looks fine, but I'm not 100% sure.", "This doesn't look to bad.",
                                      "This one looks kind of fine.", "I mean... it's fine enough.",
                                      "Maybe it could use some changes, but nothing major.", "It's kind of OK.",
                                      "I could be wrong, but I this this one is fine", "This is fiiiiiiine... right?"],
                                0.8: ["There doesn't seem to be an error here.", "That's not half-bad, right?",
                                      "Could not find anything bad to say about this one.", "Pretty sure it's fine.",
                                      "This one seems to work fine.", "This one looks fine as it is"],
                                1.0: ["Looks perfectly fine to me.", "Looks great to me.", "Not bad! Isn't it?",
                                      "That is one good pair of sentences", "Look how pretty this one is!"]},
                   "alignment_error": {0.4: ["""There might be an <span class="alignment_comment">alignment error</span> here."""],
                                       0.8: ["""I'm pretty sure there is an <span class="alignment_comment">alignment error</span> here."""],
                                       1.0: ["""Now That's an <span class="alignment_comment">alignment error</span>!"""]},
                   "quality_error": {0.4: ["""There seems to be a <span class="quality_comment">quality error</span> here."""],
                                     0.8: ["""Doesn't this look like a <span class="quality_comment">quality error</span> to you?"""],
                                     1.0: ["""Now, that's a <span class="quality_comment">quality error</span>!""",
                                           """I'm pretty sure that's a <span class="quality_comment">quality error</span>.""",
                                           """Quite a <span class="quality_comment">quality error</span>, isn't it?"""]},
                   "error": ["""I can't spot it but I'm pretty sure there is an <span class="error_comment">error</span> here.""",
                             """An <span class="error_comment">error</span> might have gone pass me on this one.""",
                             """There could be an <span class="error_comment">error</span> in here.""",
                             """You might want to take a look on this one, there could be an <span class="error_comment">error</span>."""],
                   "gibberish": ["""This looks like <span class="gibberish_comment">gibberish</span> to me.""",
                                 """What is this thing? Must be <span class="gibberish_comment">gibberish</span>.""",
                                 """What??? Sure looks like <span class="gibberish_comment">gibberish</span>.""",
                                 """<span class="gibberish_comment">Gibberish</span> sure looks awful, doesn'it?.""",
                                 """Is it just me or does this look like <span class="gibberish_comment">gibberish</span>?""",
                                 """What a load of <span class="gibberish_comment">gibberish</span>, don't you think?"""],
                   "n_alignment_error": ["""There's a sentence missing there, that's an <span class="alignment_comment">alignment error</span> for sure.""",
                                           """That's an <span class="alignment_comment">alignment error</span> right there!""",
                                           """That sure looks like an <span class="alignment_comment">alignment error</span>.""",
                                           """Of course it's an <span class="alignment_comment">alignment error</span>! There is a sentence missing!"""],
                   "silver": ["Doesn't seem to be anything wrong with this one.",
                               "I couldn't find a single error, but what do I know?",
                               "If there's an error, I could not find it.", "I was unable to decide."],
                   None: ["This translation unit shows no FLAG.", "This translation unit was not FLAGGED.",
                          "There is no FLAG available for this one.", "There's no FLAG we recognize in here",
                          "This sentence pair should have a FLAG but it doesn't."]}
    if flagType in ["error", "gibberish", "silver", "n_alignment_error", None]:
        comment = commentDict[flagType][randint(0, len(commentDict[flagType])-1)]
    else:
        if flagType is None:
            return ""
        flagScore = float(flagScore) if flagScore is not None else 1.0
        scoreBkt = 0.4 if flagScore <= 0.4 else 0.8
        scoreBkt = scoreBkt if flagScore <= 0.8 else 1.0
        comment = commentDict[flagType][scoreBkt][randint(0, len(commentDict[flagType][scoreBkt])-1)]
    return comment


def plainLabel(flagType):
    commentDict = {"gold": "GOLD (very good)",
                   "alignment_error": """<span class="alignment_comment">ALIGNMENT ERROR</span>""",
                   "quality_error": """<span class="quality_comment">QUALITY ERROR</span>""",
                   "error": """<span class="error_comment">ERROR</span>""",
                   "gibberish": """<span class="gibberish_comment">GIBBERISH</span>""",
                   "n_alignment_error": """<span class="alignment_comment">ALIGNMENT ERROR</span>""",
                   "silver": "SILVER (good)",
                   None: ""}
    return commentDict[flagType]


def makeHtmlFromTmx(tmxFilePath, outputPath=None, verbose=False):
    # get the TU from the tmx, each tu sentence has the following data: [flag, lang, tuvText]
    tmxContent = getListFromTmx(tmxFilePath)
    # get the header and foot of the page
    header, foot = getHeaderAndFoot()
    # start the tmx table
    table = """    <p>&nbsp;&nbsp;</p>    <table border="1px">\n"""
    # table header with instructions
    table += """    <thead>\n        <tr>\n"""
    table += """          <th colspan="2" class="instructions">Click on the INDEX checkbox to remove the line.</th>\n"""
    table += """          <th colspan="2" class="instructions">Click on the LABEL checkbox to remove all the lines with that same label.</th>\n        </tr>\n      </thead>\n"""
    # table header
    table += """    <thead>\n        <tr>\n          <th>Index</th>\n"""
    table += """          <th>{0}</th>\n          <th>{1}</th>\n""".format(tmxContent[0][0][1].upper(),
                                                                           tmxContent[0][1][1].upper())
    table += """          <th>Label</th>\n        </tr>\n      </thead>\n"""
    # table body
    for indTu, tuFLT in enumerate(tmxContent):
        txtSrc = tuFLT[0][2] if tuFLT[0][2] is not None else ""
        flag = tuFLT[0][0]
        txtTrgt = tuFLT[1][2] if tuFLT[1][2] is not None else ""
        checked = '''"1" checked''' if flag in ["silver", "gold"] else '''"0"'''
        table += """      <tr>\n        <th>"""
        table += """<input type="checkbox" id="ln{0}" onclick="change_value(this.id)" value={1}>""".format(indTu + 1, checked)
        table += """{0}</th>\n        <th id="src{0}" class="{1}">{2}</th>\n""".format(indTu + 1, flag, txtSrc)
        table += """        <th id="trgt{0}" class="{1}">{2}</th>\n""".format(indTu + 1, flag, txtTrgt)
        # add comment
        if verbose is False:
            table += """        <th class="check_{1}"><input type="checkbox" id="cl{2}" class="checkbox_{1}" onclick="uncheck_class('{1}', 'cl{2}')" value={0}>""".format(checked, flag, indTu + 1)
            table += """{0}</th>\n      </tr>\n""".format(plainLabel(flag))
        else:
            table += """        <th class="check_{1}"><input type="checkbox" id="cl{2}" class="checkbox_{1}" onclick="uncheck_class('{1}', 'cl{2}')>" value={0}""".format(checked, flag, indTu + 1)
            table += """{0}</th>\n      </tr>\n""".format(verboseFloatScore(flag, tuFLT[0][3]))
    table += """    </table>\n"""
    htmlPage = "{0}{1}{2}".format(header, table, foot)
    # dump if necessary
    if outputPath is not None:
        with open(outputPath, "w") as outHtml:
            outHtml.write(htmlPage)
        # copy the css stylesheet
        try:
            copyfile("./resources/css/styles.css", "/".join(outputPath.split("/")[:-1] + ["styles.css"]))
        except FileNotFoundError:
            try:
                copyfile("../resources/css/styles.css", "/".join(outputPath.split("/")[:-1] + ["styles.css"]))
            except FileNotFoundError:
                pass
        # copy the javascript stylesheet
        try:
            copyfile("./resources/javascript/app.js", "/".join(outputPath.split("/")[:-1] + ["app.js"]))
        except FileNotFoundError:
            try:
                copyfile("../resources/javascript/app.js", "/".join(outputPath.split("/")[:-1] + ["app.js"]))
            except FileNotFoundError:
                pass
    return htmlPage

makeHtmlFromTmx("../tmp/aligned.tmx", outputPath="../html/index.html", verbose=False)
