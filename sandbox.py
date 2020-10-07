#!/usr/bin/python
# -*- coding:utf-8 -*-

# import sys
# from bin.txt2tmx import getVecAlign
#
# for sub in ["citi1", "citi2", "cour", "hans", "ilo", "onu", "tao1", "tao2", "tao3", "verne", "xerox"]:
#     fr = "/data/rali5/Tmp/alfonsda/workRali/004tradBureau/023bafAlignmentTestCorpora/alignedWithVecalign/{0}.segm_ed.fr".format(sub)
#     en = "/data/rali5/Tmp/alfonsda/workRali/004tradBureau/023bafAlignmentTestCorpora/alignedWithVecalign/{0}.segm_ed.en".format(sub)
#     with open(fr, "r", encoding="latin1") as frf:
#         frcontent = frf.read()
#     with open(fr, "w") as frf:
#         frf.write(frcontent)
#     with open(en, "r", encoding="latin1") as enF:
#         encontent = enF.read()
#     with open(en, "w") as enF:
#         enF.write(encontent)
#
#     getVecAlign(fr,
#                 en,
#                 ["fr", "en"],
#                 txtSrcOutputPath="/data/rali5/Tmp/alfonsda/workRali/004tradBureau/023bafAlignmentTestCorpora/alignedWithVecalign/{0}.output.fr".format(sub),
#                 txtTrgtOutputPath="/data/rali5/Tmp/alfonsda/workRali/004tradBureau/023bafAlignmentTestCorpora/alignedWithVecalign/{0}.output.en".format(sub))



# # #COMPARE YASA TO VECALIGN USING BLEUALIGN (Vecalign eval set)
# import subprocess
# import sys, os
# from collections import defaultdict
# import numpy as np
# from ast import literal_eval
#
#
# def createEmptyFolder(folderPath):
#     """ given a non existing folder path, creates the necessary folders so the path exists """
#     if not os.path.exists(folderPath):
#         os.makedirs(folderPath)
#
#
# def getYasaAlign(srcFilePath, trgtFilePath, outputFolderPath="./tmp/"):
#     """
#     use YASA to align two parallel files and output the result in a human readeable fashion
#     :param srcFilePath: path to the source file
#     :param trgtFilePath: path to the target file
#     :param outputFolderPath:
#     :return:
#     """
#     createEmptyFolder(outputFolderPath)
#     # apply the yasa script
#     subprocess.call(["./resources/yasa/yasa", "-i", "o", "-o", "a",
#                      srcFilePath, trgtFilePath, u"{0}yasa.output.arcadeformat".format(outputFolderPath)])
#     subprocess.call(["./resources/yasa/yasa", "-i", "o", "-o", "r",
#                      srcFilePath, trgtFilePath, u"{0}yasa.output.raliformat".format(outputFolderPath)])
#     # open the arcade format and get the index of the aligned sentences
#     indexInfo = []
#     indexAlignList = []
#     with open(u"{0}yasa.output.arcadeformat".format(outputFolderPath)) as arcadeFile:
#         with open(u"{0}yasa.output.raliformat".format(outputFolderPath)) as raliFile:
#             # first line
#             arcadeLn = arcadeFile.readline()
#             raliLn = raliFile.readline()
#             while arcadeLn:
#                 # split the different sections of the output data
#                 arcadeSplit = arcadeLn.split(u'"')
#                 raliSplit = raliLn.split(u" ")
#                 # get the line indexes and score
#                 indexSect = arcadeSplit[1].split(";")
#                 indexSrc = [int(s.replace(u",", "")) - 1 if s != "" else None for s in indexSect[0].split(" ")]
#                 indexTgrt = [int(s.replace(u",", "")) - 1 if s != "" else None for s in indexSect[1].split(" ")]
#                 arcadeScore = float(arcadeSplit[3].replace(u",", ""))
#                 raliScore = float(raliSplit[1].replace(u"\n", "").replace(u",", ""))
#                 indexInfo.append({u"src": indexSrc, "trgt": indexTgrt, "scores": [arcadeScore, raliScore]})
#                 indexAlignList.append(([] if None in indexSrc else indexSrc,
#                                        [] if None in indexTgrt else indexTgrt))
#                 # next line
#                 arcadeLn = arcadeFile.readline()
#                 raliLn = raliFile.readline()
#     return indexAlignList
#
#
# def read_alignments(fin):
#     alignments = []
#     with open(fin, 'rt', encoding="utf-8") as infile:
#         for line in infile:
#             fields = [x.strip() for x in line.split(':') if len(x.strip())]
#             if len(fields) < 2:
#                 raise Exception('Got line "%s", which does not have at least two ":" separated fields' % line.strip())
#             try:
#                 src = literal_eval(fields[0])
#                 tgt = literal_eval(fields[1])
#             except:
#                 raise Exception('Failed to parse line "%s"' % line.strip())
#             alignments.append((src, tgt))
#
#     # I know bluealign files have a few entries entries missing,
#     #   but I don't fix them in order to be consistent previous reported scores
#     return alignments
#
#
# def _precision(goldalign, testalign):
#     """
#     Computes tpstrict, fpstrict, tplax, fplax for gold/test alignments
#     """
#     tpstrict = 0  # true positive strict counter
#     tplax = 0     # true positive lax counter
#     fpstrict = 0  # false positive strict counter
#     fplax = 0     # false positive lax counter
#
#     # convert to sets, remove alignments empty on both sides
#     testalign = set([(tuple(x), tuple(y)) for x, y in testalign if len(x) or len(y)])
#     goldalign = set([(tuple(x), tuple(y)) for x, y in goldalign if len(x) or len(y)])
#
#     # mappings from source test sentence idxs to
#     #    target gold sentence idxs for which the source test sentence
#     #    was found in corresponding source gold alignment
#     src_id_to_gold_tgt_ids = defaultdict(set)
#     for gold_src, gold_tgt in goldalign:
#         for gold_src_id in gold_src:
#             for gold_tgt_id in gold_tgt:
#                 src_id_to_gold_tgt_ids[gold_src_id].add(gold_tgt_id)
#
#     for (test_src, test_target) in testalign:
#         if (test_src, test_target) == ((), ()):
#             continue
#         if (test_src, test_target) in goldalign:
#             # strict match
#             tpstrict += 1
#             tplax += 1
#         else:
#             # For anything with partial gold/test overlap on the source,
#             #   see if there is also partial overlap on the gold/test target
#             # If so, its a lax match
#             target_ids = set()
#             for src_test_id in test_src:
#                 for tgt_id in src_id_to_gold_tgt_ids[src_test_id]:
#                     target_ids.add(tgt_id)
#             if set(test_target).intersection(target_ids):
#                 fpstrict += 1
#                 tplax += 1
#             else:
#                 print(111111111111, test_src, test_target)
#                 print(222222222222, [t for t in goldalign if t[0] == test_src])
#                 fpstrict += 1
#                 fplax += 1
#
#     return np.array([tpstrict, fpstrict, tplax, fplax], dtype=np.int32)
#
#
# def score_multiple(gold_list, test_list, value_for_div_by_0=0.0):
#     # accumulate counts for all gold/test files
#     pcounts = np.array([0, 0, 0, 0], dtype=np.int32)
#     rcounts = np.array([0, 0, 0, 0], dtype=np.int32)
#     for goldalign, testalign in zip(gold_list, test_list):
#         pcounts += _precision(goldalign=goldalign, testalign=testalign)
#         # recall is precision with no insertion/deletion and swap args
#         test_no_del = [(x, y) for x, y in testalign if len(x) and len(y)]
#         gold_no_del = [(x, y) for x, y in goldalign if len(x) and len(y)]
#         rcounts += _precision(goldalign=test_no_del, testalign=gold_no_del)
#
#     # Compute results
#     # pcounts: tpstrict,fnstrict,tplax,fnlax
#     # rcounts: tpstrict,fpstrict,tplax,fplax
#
#     if pcounts[0] + pcounts[1] == 0:
#         pstrict = value_for_div_by_0
#     else:
#         pstrict = pcounts[0] / float(pcounts[0] + pcounts[1])
#
#     if pcounts[2] + pcounts[3] == 0:
#         plax = value_for_div_by_0
#     else:
#         plax = pcounts[2] / float(pcounts[2] + pcounts[3])
#
#     if rcounts[0] + rcounts[1] == 0:
#         rstrict = value_for_div_by_0
#     else:
#         rstrict = rcounts[0] / float(rcounts[0] + rcounts[1])
#
#     if rcounts[2] + rcounts[3] == 0:
#         rlax = value_for_div_by_0
#     else:
#         rlax = rcounts[2] / float(rcounts[2] + rcounts[3])
#
#     if (pstrict + rstrict) == 0:
#         fstrict = value_for_div_by_0
#     else:
#         fstrict = 2 * (pstrict * rstrict) / (pstrict + rstrict)
#
#     if (plax + rlax) == 0:
#         flax = value_for_div_by_0
#     else:
#         flax = 2 * (plax * rlax) / (plax + rlax)
#
#     result = dict(recall_strict=rstrict,
#                   recall_lax=rlax,
#                   precision_strict=pstrict,
#                   precision_lax=plax,
#                   f1_strict=fstrict,
#                   f1_lax=flax)
#
#     return result
#
#
# def log_final_scores(res):
#     print(' ---------------------------------', file=sys.stderr)
#     print('|             |  Strict |    Lax  |', file=sys.stderr)
#     print('| Precision   |   {precision_strict:.3f} |   {precision_lax:.3f} |'.format(**res), file=sys.stderr)
#     print('| Recall      |   {recall_strict:.3f} |   {recall_lax:.3f} |'.format(**res), file=sys.stderr)
#     print('| F1          |   {f1_strict:.3f} |   {f1_lax:.3f} |'.format(**res), file=sys.stderr)
#     print(' ---------------------------------', file=sys.stderr)
#
#
# # gold_files = ["./resources/vecalign/bleualign_data/test0.defr", "./resources/vecalign/bleualign_data/test1.defr",
# #               "./resources/vecalign/bleualign_data/test2.defr", "./resources/vecalign/bleualign_data/test3.defr",
# #               "./resources/vecalign/bleualign_data/test4.defr", "./resources/vecalign/bleualign_data/test5.defr",
# #               "./resources/vecalign/bleualign_data/test6.defr"]
# gold_files = ["./resources/vecalign/bleualign_data/test0.defr", "./resources/vecalign/bleualign_data/test1.defr",
#               "./resources/vecalign/bleualign_data/test2.defr", "./resources/vecalign/bleualign_data/test3.defr",
#               "./resources/vecalign/bleualign_data/test4.defr", "./resources/vecalign/bleualign_data/test5.defr",
#               "./resources/vecalign/bleualign_data/test6.defr"]
# gold_list = [read_alignments(x) for x in gold_files]
#
# # test_files = [["./resources/vecalign/bleualign_data/test0.de", "./resources/vecalign/bleualign_data/test0.fr"],
# #               ["./resources/vecalign/bleualign_data/test1.de", "./resources/vecalign/bleualign_data/test1.fr"],
# #               ["./resources/vecalign/bleualign_data/test2.de", "./resources/vecalign/bleualign_data/test2.fr"],
# #               ["./resources/vecalign/bleualign_data/test3.de", "./resources/vecalign/bleualign_data/test3.fr"],
# #               ["./resources/vecalign/bleualign_data/test4.de", "./resources/vecalign/bleualign_data/test4.fr"],
# #               ["./resources/vecalign/bleualign_data/test5.de", "./resources/vecalign/bleualign_data/test5.fr"],
# #               ["./resources/vecalign/bleualign_data/test6.de", "./resources/vecalign/bleualign_data/test6.fr"],
# #               ]
# test_files = [["./resources/vecalign/bleualign_data/test0.de", "./resources/vecalign/bleualign_data/test0.fr"],
#               ["./resources/vecalign/bleualign_data/test1.de", "./resources/vecalign/bleualign_data/test1.fr"],
#               ["./resources/vecalign/bleualign_data/test2.de", "./resources/vecalign/bleualign_data/test2.fr"],
#               ["./resources/vecalign/bleualign_data/test3.de", "./resources/vecalign/bleualign_data/test3.fr"],
#               ["./resources/vecalign/bleualign_data/test4.de", "./resources/vecalign/bleualign_data/test4.fr"],
#               ["./resources/vecalign/bleualign_data/test5.de", "./resources/vecalign/bleualign_data/test5.fr"],
#               ["./resources/vecalign/bleualign_data/test6.de", "./resources/vecalign/bleualign_data/test6.fr"],
#               ]
# test_list = [getYasaAlign(tfiles[0], tfiles[1], outputFolderPath="./sandboxtmp/") for tfiles in test_files]
# res = score_multiple(gold_list=gold_list, test_list=test_list)
# log_final_scores(res)



### DISTRIBUTION OF ALIGNMENTS
import os
# path = "/home/d/Documents/programming/workRali/019DemoPipeline/resources/vecalign/bleualign_data/"
# elInCommon = ["test", ".defr"] # gold bleaualign
# sep = [":", ", "]

path = "/home/d/Documents/programming/workRali/023bafAlignmentTestCorpora/baf-1.1/"
elInCommon = [".ind.cesalign"] # gold baf
sep = [";", " "]

# path = "/home/d/Documents/programming/workRali/023bafAlignmentTestCorpora/alignedWithVecalign/"
# elInCommon = [".tsv"] # vecalign align for baf corpus
# sep = ["\t", ","]

# path = "/home/d/Documents/programming/workRali/023bafAlignmentTestCorpora/alignedWithYasa/yasa/allArcade/"
# elInCommon = [".arcadeformat"] # yasa align for baf corpus
# sep = [";", " "]

adict = {"t":0}
files = ["{0}{1}".format(path, file) for file in os.listdir(path) if (elInCommon[0] in file)]
for file in files:
    with open(file) as file:
        lns = file.readlines()
    for ln in lns:
        if ln not in ["""<!DOCTYPE CESALIGN PUBLIC "-//CES//DTD cesAlign//EN" []>\n""",
                      """<CESALIGN VERSION="1.14">\n""", """<LINKLIST>\n""", """<LINKGRP>\n""", """</LINKGRP>\n""",
                      """</LINKLIST>\n""", """</CESALIGN>\n""", """</CESALIGN>"""]:
            spl = ln.split(sep[0])
            print(spl)
            l = spl[0].replace("[", "").replace("]", "").split('"')[-1]
            r = spl[1].replace("[", "").replace("]", "").replace("\n", "").split('"')[0]
            print(1111, repr(l), repr(r))
            l = len([x.replace(",", "") for x in l.split(sep[1])]) if l.split(sep[1])[0] != "" else 0
            r = len(r.split(sep[1])) if r.split(sep[1])[0] != "" else 0
            print(22222, l, r)
            k = "{0}:{1}".format(l,r)
            if k not in adict:
                adict[k] = 0
            adict[k] += 1
            adict["t"] += 1

print(adict)

