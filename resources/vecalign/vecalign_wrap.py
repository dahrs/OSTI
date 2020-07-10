#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
DISCLAIMER:
This is a simple wrapper to adapt the Vecalign script to this project's specific environment.
The original script for the Vecalign module is as follows:
Copyright 2019 Brian Thompson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import sys
import pickle
import logging
import subprocess
import numpy as np
from math import ceil
from random import seed as seed

sys.path.insert(0, './resources/vecalign/')
os.environ["LASER"] = "./resources/LASER/"

logger = logging.getLogger('vecalign')
logger.setLevel(logging.WARNING)
logFormatter = logging.Formatter("%(asctime)s  %(levelname)-5.5s  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

from dp_utils import make_alignment_types, print_alignments, read_alignments, read_in_embeddings, make_doc_embedding
from dp_utils import vecalign, yield_overlaps
from score import score_multiple, log_final_scores
from overlap import go


def aligner(src, trgt, src_embed, trgt_embed, alignment_max_size=4, del_percentile_frac=0.2, debug_save_stack=False):
    # make runs consistent
    seed(42)
    np.random.seed(42)
    max_size_full_dp = 300
    costs_sample_size = 20000
    num_samps_for_norm = 100
    search_buffer_size = 5

    if alignment_max_size < 2:
        logger.warning('Alignment_max_size < 2. Increasing to 2 so that 1-1 alignments will be considered')
        alignment_max_size = 2

    src_sent2line, src_line_embeddings = read_in_embeddings(src_embed[0], src_embed[1])
    tgt_sent2line, tgt_line_embeddings = read_in_embeddings(trgt_embed[0], trgt_embed[1])

    width_over2 = ceil(alignment_max_size / 2.0) + search_buffer_size

    test_alignments = []
    stack_list = []
    for src_file, tgt_file in zip(src, trgt):
        logger.info('Aligning src="%s" to tgt="%s"', src_file, tgt_file)

        src_lines = open(src_file, 'rt', encoding="utf-8").readlines()
        vecs0 = make_doc_embedding(src_sent2line, src_line_embeddings, src_lines, alignment_max_size)

        tgt_lines = open(tgt_file, 'rt', encoding="utf-8").readlines()
        vecs1 = make_doc_embedding(tgt_sent2line, tgt_line_embeddings, tgt_lines, alignment_max_size)

        final_alignment_types = make_alignment_types(alignment_max_size)
        logger.debug('Considering alignment types %s', final_alignment_types)

        stack = vecalign(vecs0=vecs0,
                         vecs1=vecs1,
                         final_alignment_types=final_alignment_types,
                         del_percentile_frac=del_percentile_frac,
                         width_over2=width_over2,
                         max_size_full_dp=max_size_full_dp,
                         costs_sample_size=costs_sample_size,
                         num_samps_for_norm=num_samps_for_norm)

        test_alignments.append(stack[0]['final_alignments'])
        stack_list.append(stack)
        yield [stack[0]['final_alignments'], stack[0]['alignment_scores']]

    if debug_save_stack:
        pickle.dump(stack_list, open(debug_save_stack, 'wb'))


def makeEmbedFiles(input_file, lang, output_file, output_emb_file):
    # make overlaps
    go(output_file, [input_file], num_overlaps=10)
    # make embedding files
    subprocess.call(["bash", "./resources/LASER/tasks/embed/embed.sh", output_file, lang, output_emb_file])


def makeVecAlign(srcPath, trgtPath, langOrder):
    srcOverlapTokenized = "./embed/vecalign.src.overlaps.{0}".format(langOrder[0])
    srcOverlapEmbed = "{0}.emb".format(srcOverlapTokenized)
    trgtOverlapTokenized = "./embed/vecalign.trgt.overlaps.{0}".format(langOrder[1])
    trgtOverlapEmbed = "{0}.emb".format(trgtOverlapTokenized)
    # remove the old embedding files
    for embedFile in [srcOverlapTokenized, srcOverlapEmbed, trgtOverlapTokenized, trgtOverlapEmbed]:
        try:
            os.remove(embedFile)
        except FileNotFoundError:
            pass
    # make the embeddings
    makeEmbedFiles(srcPath, langOrder[0], srcOverlapTokenized, srcOverlapEmbed)
    makeEmbedFiles(trgtPath, langOrder[1], trgtOverlapTokenized, trgtOverlapEmbed)
    alignmentsAndScores = aligner([srcPath], [trgtPath], [srcOverlapTokenized, srcOverlapEmbed],
                                  [trgtOverlapTokenized, trgtOverlapEmbed], alignment_max_size=3,
                                  del_percentile_frac=0.2, debug_save_stack="./tmp/vecalign.output.align.pkl")
    return alignmentsAndScores
