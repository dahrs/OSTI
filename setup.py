#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])