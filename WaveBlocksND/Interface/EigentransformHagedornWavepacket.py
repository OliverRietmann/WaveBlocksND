"""The WaveBlocks Project

Compute the transformation to the eigen basis for wavepackets.

@author: R. Bourquin
@copyright: Copyright (C) 2012, 2013, 2016 R. Bourquin
@license: Modified BSD License
"""

from WaveBlocksND import BlockFactory
from WaveBlocksND import BasisTransformationHAWP


def transform_hawp_to_eigen(iomin, iomout, blockidin=0, blockidout=0):
    """Compute the transformation to the eigenbasis for a wavepacket.
    Save the result back to a file.

    :param iomin: An :py:class:`IOManager: instance providing the simulation data.
    :param iomout: An :py:class:`IOManager: instance for saving the transformed data.
    :param blockidin: The data block from which the values are read. Default is `0`.
    :param blockidout: The data block to which the values are written. Default is `0`.
    """
    parameters = iomin.load_parameters()

    KEY = ("q", "p", "Q", "P", "S", "adQ")

    # Number of time steps we saved
    timesteps = iomin.load_wavepacket_timegrid(blockid=blockidin)
    nrtimesteps = timesteps.shape[0]

    # The potential used
    Potential = BlockFactory().create_potential(parameters)

    # Basis transformator
    BT = BasisTransformationHAWP(Potential)

    # Initialize a Hagedorn wavepacket with the data
    descr = iomin.load_wavepacket_description(blockid=blockidin)
    HAWP = BlockFactory().create_wavepacket(descr)

    iomout.add_wavepacket(descr, timeslots=nrtimesteps, blockid=blockidout, key=KEY)
    iomout.save_wavepacket_description(HAWP.get_description(), blockid=blockidout)

    BT.set_matrix_builder(HAWP.get_innerproduct())

    # Basis shapes
    BS_descr = iomin.load_wavepacket_basisshapes(blockid=blockidin)
    BS = {}
    for ahash, descr in BS_descr.items():
        BS[ahash] = BlockFactory().create_basis_shape(descr)

    # Iterate over all timesteps
    for i, step in enumerate(timesteps):
        print(" Compute eigentransform at timestep %d" % step)

        # Retrieve simulation data
        params = iomin.load_wavepacket_parameters(timestep=step, blockid=blockidin, key=KEY)
        hashes, coeffs = iomin.load_wavepacket_coefficients(timestep=step, get_hashes=True, blockid=blockidin)

        # Configure the wavepacket
        HAWP.set_parameters(params, key=KEY)
        HAWP.set_basis_shapes([BS[int(ha)] for ha in hashes])
        HAWP.set_coefficients(coeffs)

        # Transform to the eigenbasis.
        BT.transform_to_eigen(HAWP)

        # Save the transformed packet
        # Pi
        iomout.save_wavepacket_parameters(HAWP.get_parameters(key=KEY), timestep=step, blockid=blockidout, key=KEY)
        # Basis shapes (in case they changed!)
        for shape in HAWP.get_basis_shapes():
            iomout.save_wavepacket_basisshapes(shape, blockid=blockidout)
        # Coefficients
        iomout.save_wavepacket_coefficients(HAWP.get_coefficients(), HAWP.get_basis_shapes(), timestep=step, blockid=blockidout)


def transform_inhawp_to_eigen(iomin, iomout, blockidin=0, blockidout=0):
    """Compute the transformation to the eigenbasis for a wavepacket.
    Save the result back to a file.

    :param iomin: An :py:class:`IOManager: instance providing the simulation data.
    :param iomout: An :py:class:`IOManager: instance for saving the transformed data.
    :param blockidin: The data block from which the values are read. Default is `0`.
    :param blockidout: The data block to which the values are written. Default is `0`.
    """
    parameters = iomin.load_parameters()

    KEY = ("q", "p", "Q", "P", "S", "adQ")

    # Number of time steps we saved
    timesteps = iomin.load_inhomogwavepacket_timegrid(blockid=blockidin)
    nrtimesteps = timesteps.shape[0]

    # The potential used
    Potential = BlockFactory().create_potential(parameters)

    # Basis transformator
    BT = BasisTransformationHAWP(Potential)

    # Initialize a Hagedorn wavepacket with the data
    descr = iomin.load_inhomogwavepacket_description(blockid=blockidin)
    HAWP = BlockFactory().create_wavepacket(descr)

    iomout.add_inhomogwavepacket(descr, timeslots=nrtimesteps, blockid=blockidout, key=KEY)
    iomout.save_inhomogwavepacket_description(HAWP.get_description(), blockid=blockidout)

    BT.set_matrix_builder(HAWP.get_innerproduct())

    # Basis shapes
    BS_descr = iomin.load_inhomogwavepacket_basisshapes(blockid=blockidin)
    BS = {}
    for ahash, descr in BS_descr.items():
        BS[ahash] = BlockFactory().create_basis_shape(descr)

    # Iterate over all timesteps
    for i, step in enumerate(timesteps):
        print(" Compute eigentransform at timestep %d" % step)

        # Retrieve simulation data
        params = iomin.load_inhomogwavepacket_parameters(timestep=step, blockid=blockidin, key=KEY)
        hashes, coeffs = iomin.load_inhomogwavepacket_coefficients(timestep=step, get_hashes=True, blockid=blockidin)

        # Configure the wavepacket
        HAWP.set_parameters(params, key=KEY)
        HAWP.set_basis_shapes([BS[int(ha)] for ha in hashes])
        HAWP.set_coefficients(coeffs)

        # Transform to the eigenbasis.
        BT.transform_to_eigen(HAWP)

        # Save the transformed packet
        # Pi
        iomout.save_inhomogwavepacket_parameters(HAWP.get_parameters(key=KEY), timestep=step, blockid=blockidout, key=KEY)
        # Basis shapes (in case they changed!)
        for shape in HAWP.get_basis_shapes():
            iomout.save_inhomogwavepacket_basisshapes(shape, blockid=blockidout)
        # Coefficients
        iomout.save_inhomogwavepacket_coefficients(HAWP.get_coefficients(), HAWP.get_basis_shapes(), timestep=step, blockid=blockidout)
