#!/usr/bin/env python
"""The WaveBlocks Project

Plot the wavepackets probability densities
for one-dimensional wavepackets.

@author: R. Bourquin
@copyright: Copyright (C) 2014, 2016 R. Bourquin
@license: Modified BSD License
"""

import argparse
import os
from numpy import angle, conj, real, imag
from matplotlib.pyplot import figure, close

from WaveBlocksND import ParameterLoader
from WaveBlocksND import BlockFactory
from WaveBlocksND import BasisTransformationHAWP
from WaveBlocksND import IOManager
from WaveBlocksND import GlobalDefaults as GLD
from WaveBlocksND.Plot import plotcf


def plot_frames(PP, iom, blockid=0, eigentransform=False, timerange=None, view=None,
                plotphase=True, plotcomponents=False, plotabssqr=False,
                load=False, gridblockid=None, imgsize=(12, 9), path='.'):
    """Plot the wavepacket for a series of timesteps.

    :param iom: An :py:class:`IOManager` instance providing the simulation data.
    """
    parameters = iom.load_parameters()
    BF = BlockFactory()

    if not parameters["dimension"] == 1:
        print("No one-dimensional wavepacket, silent return!")
        return

    if PP is None:
        PP = parameters

    if load is True:
        if gridblockid is None:
            gridblockid = blockid
        print("Loading grid data from datablock '{}'".format(gridblockid))
        G = iom.load_grid(blockid=gridblockid)
        grid = real(G.reshape(-1))
    else:
        print("Creating new grid")
        G = BlockFactory().create_grid(PP)
        grid = real(G.get_nodes(flat=True).reshape(-1))

    if eigentransform:
        V = BF.create_potential(parameters)
        BT = BasisTransformationHAWP(V)

    timegrid = iom.load_wavepacket_timegrid(blockid=blockid)
    if timerange is not None:
        if len(timerange) == 1:
            I = (timegrid == timerange)
        else:
            I = ((timegrid >= timerange[0]) & (timegrid <= timerange[1]))
        if any(I):
            timegrid = timegrid[I]
        else:
            raise ValueError("No valid timestep remains!")

    # View
    if view is not None:
        if view[0] is None:
            view[0] = grid.min()
        if view[1] is None:
            view[1] = grid.max()

    for step in timegrid:
        print(" Plotting frame of timestep # {}".format(step))

        HAWP = iom.load_wavepacket(step, blockid=blockid)

        # Transform the values to the eigenbasis
        if eigentransform:
            BT.transform_to_eigen(HAWP)

        values = HAWP.evaluate_at(G.get_nodes(), prefactor=True, component=0)

        # Plot
        fig = figure(figsize=imgsize)

        for index, component in enumerate(values):
            ax = fig.add_subplot(parameters["ncomponents"], 1, index + 1)
            ax.ticklabel_format(style="sci", scilimits=(0, 0), axis="y")

            if plotcomponents is True:
                ax.plot(grid, real(component))
                ax.plot(grid, imag(component))
                ax.set_ylabel(r"$\Re \varphi_{%d}, \Im \varphi_{%d}$" % (index, index))
            if plotabssqr is True:
                ax.plot(grid, real(component * conj(component)))
                ax.set_ylabel(r"$\langle \varphi_{%d} | \varphi_{%d} \rangle$" % (index, index))
            if plotphase is True:
                plotcf(grid, angle(component), real(component * conj(component)))
                ax.set_ylabel(r"$\langle \varphi_{%d} | \varphi_{%d} \rangle$" % (index, index))

            ax.set_xlabel(r"$x$")

            # Set the aspect window
            ax.set_xlim(view[:2])
            ax.set_ylim(view[2:])

        if "dt" in parameters:
            fig.suptitle(r"$\Psi$ at time $%f$" % (step * parameters["dt"]))
        else:
            fig.suptitle(r"$\Psi$")

        fig.savefig(os.path.join(path, "wavepacket_block_%s_timestep_%07d.png" % (blockid, step)))
        close(fig)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--datafile",
                        type = str,
                        help = "The simulation data file",
                        nargs = "?",
                        default = GLD.file_resultdatafile)

    parser.add_argument("-p", "--parametersfile",
                        type = str,
                        help = "The simulation data file",
                        nargs = "?",
                        default = None)

    parser.add_argument("-b", "--blockid",
                        type = str,
                        help = "The data block to handle",
                        nargs = "*",
                        default = ["all"])

    parser.add_argument("-r", "--resultspath",
                        type = str,
                        help = "Path where to put the results.",
                        nargs = "?",
                        default = '.')

    parser.add_argument("-et", "--eigentransform",
                        action = "store_true",
                        help = "Transform the data into the eigenbasis before plotting")

    parser.add_argument("-x", "--xrange",
                        type = float,
                        help = "The plot range on the x-axis",
                        nargs = 2,
                        default = [None, None])

    parser.add_argument("-y", "--yrange",
                        type = float,
                        help = "The plot range on the y-axis",
                        nargs = 2,
                        default = [0, 3.5])

    parser.add_argument("-t", "--timerange",
                        type = int,
                        help = "Plot only timestep(s) in this range",
                        nargs = "+",
                        default = None)

    parser.add_argument("--plotphase",
                        action = "store_false",
                        help = "Plot the complex phase (slow)")

    parser.add_argument("--plotcomponents",
                        action = "store_true",
                        help = "Plot the real/imaginary parts")

    parser.add_argument("--plotabssqr",
                        action = "store_true",
                        help = "Plot the absolute value squared")

    args = parser.parse_args()


    # File with the simulation data
    resultspath = os.path.abspath(args.resultspath)

    if not os.path.exists(resultspath):
        raise IOError("The results path does not exist: {}".format(args.resultspath))

    datafile = os.path.abspath(os.path.join(args.resultspath, args.datafile))
    parametersfile = os.path.abspath(os.path.join(args.resultspath, args.parametersfile))

    # Read file with simulation data
    iom = IOManager()
    iom.open_file(filename=datafile)

    # Read file with parameter data for grid
    if args.parametersfile:
        PL = ParameterLoader()
        PP = PL.load_from_file(parametersfile)
    else:
        PP = None

    # Which blocks to handle
    blockids = iom.get_block_ids()
    if "all" not in args.blockid:
        blockids = [bid for bid in args.blockid if bid in blockids]

    # The axes rectangle that is plotted
    view = args.xrange + args.yrange

    # Iterate over all blocks
    for blockid in blockids:
        print("Plotting frames of data block '{}'".format(blockid))
        # See if we have wavepacket values
        if iom.has_wavepacket(blockid=blockid):
            plot_frames(PP, iom, blockid=blockid,
                        eigentransform=args.eigentransform,
                        timerange=args.timerange,
                        view=view,
                        path=resultspath)
        else:
            print("Warning: Not plotting any wavepackets in block '{}'".format(blockid))

    iom.finalize()
