# OSTI
Open-source tool to process and visualize a pair of bilingual documents (original and translation) into automatically labeled sentence pairs.  Can serve a translation professional as human-accessible quality evaluation tool, as a pre-processing step for human annotation as well as an intermediate step to populate a Translation Memory.

## External Tools instructions
For an optimal use of the aligners and classifiers of this system, it is recommended to install the VecAlign and
LASER toolkits. These can be downloaded freely from : 
VecAlign : https://github.com/thompsonb/vecalign/archive/master.zip  or  https://github.com/thompsonb/vecalign
LASER : https://github.com/facebookresearch/LASER/archive/master.zip  or  https://github.com/facebookresearch/LASER

Follow the instructions to install each of them : 
VecAlign : https://github.com/thompsonb/vecalign/blob/master/README.md
LASER : https://github.com/facebookresearch/LASER/blob/master/README.md)

You may install them directly into the ''resources'' folder or you may replace the following paths (in 'options')
with the corresponding paths for each of them.

We HIGHLY recommend that the VecAlign toolkit be installed or copied into the 'resources/vecalign' folder,
making sure not delete the 'vecalign\_wrap.py' file (which can also be found in 'resources/wrap').
If you choose NOT to install the VecAlign toolkit in 'resources/vecalign' then, you will need to copy
the 'vecalign\_wrap.py' file into the folder it is installed on and change the explicit relative import path in
line 16 of the 'bin/txt2tmx.py' file to match its correct location
