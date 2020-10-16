#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

import nltk
nltk.download('punkt')

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu-noavx2"])
except subprocess.CalledProcessError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu-noavx2"])
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu-noavx2"])
        except:
            pass
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fast-bpe"])
except subprocess.CalledProcessError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastBPE"])
    except subprocess.CalledProcessError:
        pass


subprocess.check_call(["gzip", "-dk",
                       "./resources/classifiers/bal_train_7M_scoresAndMetaData_rdmForest.pickle.gz"])
subprocess.check_call(["gzip", "-dk",
                       "./resources/classifiers/bal_train_7M_scoresAndMetaData_svm.pickle.gz"])
subprocess.check_call(["gzip", "-dk",
                       "./resources/classifiers/bal_train_7M_scores_rdmForest.pickle.gz"])
