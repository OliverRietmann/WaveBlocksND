#!/usr/bin/env python
"""The WaveBlocks Project

Sample wavepackets at the nodes of a given grid and save
the results back to the given simulation data file.

@author: R. Bourquin
@copyright: Copyright (C) 2010, 2011, 2012, 2013, 2014, 2016 R. Bourquin
@license: Modified BSD License
"""

import argparse
import os

from WaveBlocksND import IOManager
from WaveBlocksND import ParameterLoader
from WaveBlocksND import GlobalDefaults as GD

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--datafile",
                    type = str,
                    help = "The simulation data file.",
                    nargs = "?",
                    default = GD.file_resultdatafile)

parser.add_argument("-b", "--blockid",
                    type = str,
                    help = "The data block to handle.",
                    nargs = "*",
                    default = ["all"])

parser.add_argument("-p", "--parametersfile",
                    type = str,
                    help = "The configuration parameter file.",
                    nargs = "?",
                    default = None)

parser.add_argument("-r", "--resultspath",
                    type = str,
                    help = "Path where to put the results.",
                    nargs = "?",
                    default = '.')

parser.add_argument("-noet", "--noeigentransform",
                    help = "Disable transformation of data into the eigenbasis before computing norms.",
                    action = "store_false")

args = parser.parse_args()


# File with the simulation data
resultspath = os.path.abspath(args.resultspath)

if not os.path.exists(resultspath):
    raise IOError("The results path does not exist: {}".format(args.resultspath))

datafile = os.path.abspath(os.path.join(args.resultspath, args.datafile))

# Read file with simulation data
iom = IOManager()
iom.open_file(filename=datafile)

# Read the additional grid parameters
if args.parametersfile:
    parametersfile = os.path.abspath(os.path.join(args.resultspath, args.parametersfile))
    PA = ParameterLoader().load_from_file(parametersfile)
else:
    PA = None

# Which blocks to handle
blockids = iom.get_block_ids()
if "all" not in args.blockid:
    blockids = [bid for bid in args.blockid if bid in blockids]

# Iterate over all blocks
for blockid in blockids:
    print("Evaluating wavepackets in data block '{}'".format(blockid))

    if iom.has_wavefunction(blockid=blockid):
        print("Datablock '{}' already contains wavefunction data, silent skip.".format(blockid))
        continue

    # NOTE: Add new algorithms here

    if iom.has_wavepacket(blockid=blockid):
        from WaveBlocksND.Interface import EvaluateWavepackets
        EvaluateWavepackets.compute_evaluate_wavepackets(PA, iom, blockid=blockid, eigentrafo=args.noeigentransform)
    elif iom.has_inhomogwavepacket(blockid=blockid):
        from WaveBlocksND.Interface import EvaluateWavepacketsInhomog
        EvaluateWavepacketsInhomog.compute_evaluate_wavepackets(PA, iom, blockid=blockid, eigentrafo=args.noeigentransform)
    else:
        print("Warning: Not evaluating any wavepackets in block '{}'!".format(blockid))

iom.finalize()
