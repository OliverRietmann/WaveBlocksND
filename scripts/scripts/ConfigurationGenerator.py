#!/usr/bin/env python
"""The WaveBlocks Project

This file contains code for automatically generate
a bunch of simulation configuration given some
sets of parameters.

@author: R. Bourquin
@copyright: Copyright (C) 2010, 2011, 2012, 2013, 2014 R. Bourquin
@license: Modified BSD License
"""

from itertools import product
import argparse
import os

from WaveBlocksND import GlobalDefaults
from functools import reduce


def sort_statements(preamble, alist):
    """Try to sort a list of valid python statements
    such that they all can be executed w.r.t. local variable
    references. This is some kind of topological sorting
    and uses a good ammount of black magic!!

    :param alist: The list of statements
    """

    # TODO: Rewrite and improve this using reflection

    ordered_statements= []

    # The preamble statements, once
    exec(preamble)

    while len(alist) > 0:
        curlen = len(alist)

        # Try to execute each statement right now
        for item in alist:
            try:
                exec(item)
            except NameError:
                continue

            # Ah, we suceeded, append the statement to the ordered list.
            ordered_statements.append(item)
            alist.remove(item)

        if len(alist) == curlen:
            print(50*"=")
            print("Last item was: "+str(item))
            raise ValueError("Could not sort configuration statements. Maybe an unescaped string? Or possibly a dependency cycle?")

    return ordered_statements


def construct_name(filename, adict):
    """Construct a filename which contains several
    ``key=value`` pairs after a given prefix. The filename
    will end with the python extension ``.py``

    :param filename: The beginning of the filename.
    :param names: A dict containing the ``key=value`` pairs.
    """
    # Put all key=value pairs as string into a list
    kvs = [ GlobalDefaults.kvp_ldel + str(k) + GlobalDefaults.kvp_mdel + str(v) + GlobalDefaults.kvp_rdel for k, v in adict.items() ]

    # Concatenate all key=value pairs in a string
    if len(kvs) == 0:
        s = ""
    else:
        s = reduce(lambda x, y: x+y, kvs)

    # Remove duplicate kvp delimiters
    if GlobalDefaults.kvp_ldel == GlobalDefaults.kvp_rdel:
        s = s.replace(GlobalDefaults.kvp_ldel+GlobalDefaults.kvp_rdel, GlobalDefaults.kvp_ldel)

    # Remove some possibly harmful characters
    # Warning: destroys meaning of filename if some of them are used as kvp delimiters!
    s = s.replace("\"", "")
    s = s.replace("\\", "")
    s = s.replace("*", "")
    s = s.replace("?", "")
    s = s.replace("(", "")
    s = s.replace(")", "")

    # Construct full filename
    filename = filename + s + ".py"

    return filename


def write_file(filepath, preamble, settings, sort_code=False):
    """Write a configuration file containing several
    configuration statements of the form ``key = value``.
    The ``key`` has to be a valid python variable name,
    the ``value`` a valid python statement.

    :param path: The filepath where to put the new files.
    :param filepath: The name and path of the output file.
    :param setting: A python ``dict`` containing the ``key=value`` pairs
    """
    # Create new file
    f = open(filepath, "w")

    header = [
    "#########################################\n",
    "# This file was automatically generated #\n",
    "#########################################\n",
    "\n" ]

    f.writelines(header)

    f.writelines(preamble)
    f.writelines("\n")

    # Write all the key=value konfiguration pairs
    code = []
    for k, v in settings.items():

        statement = str(k) + " = " + str(v) + "\n"
        code.append(statement)

    if sort_code:
        code = sort_statements(preamble, code)

    f.writelines(code)

    f.close()


def generate_configurations(pa, gp, lp, cfname="Parameters", cfpath=GlobalDefaults.path_to_autogen_configs):
    """Generate a bunch of configuration files from a set
    of global parameters which are the same in all configurations
    and a set of local parameters which differ. We compute the
    cartesian product of the sets of all local parameter.

    :param gp: A ``dict`` of global parameters.
    :param lp: A ``dict`` of local parameter lists.
    :param cfname: The common filename prefix. Default is ``Parameters``
    :param cfpath: The path where the new configuration files will be
                   placed. It is interpreted relative to ``.``.
    """
    # Check if the destination for the new configuration files is prepared
    configpath = os.path.join(".", cfpath)

    if not os.path.lexists(configpath):
        os.mkdir(configpath)
    else:
        raise ValueError("The directory for autogenerated configurations already exists.")

    print("Preamble:")
    print("---------")
    print(pa)

    print("Global paramaters:")
    print("------------------")
    print(gp)

    print("Local parameters:")
    print("-----------------")
    print(lp)

    # Sort into keys and values
    lpk = [ k for k in lp.keys() ]
    lpv = [ v for v in lp.values() ]

    # Compute a cartesian product of all local parameters
    VG = product(*lpv)

    # Iterate over all conbinations in the cartesian product
    i = 0
    for cv in VG:
        i += 1
        params = {k:v for k,v in zip(lpk, cv)}

        filename = construct_name(cfname, params)
        filepath = os.path.join(".", cfpath, filename)

        # Add global parameters to the dict
        params.update(gp)

        print("Current configuration:")
        print(params)

        write_file(filepath, pa, params, sort_code=True)

    print("Wrote all "+str(i)+" configuration files.")




if __name__ == "__main__":
    """Remarks:

    - You can use any valid python statement as value
    - All statements are written to a pure python code file
    - You can write numbers, lists etc as plain text strings
    - All that is not in string form gets evaluated *right now*
    - Remember to escape python strings twice
    - You can use variable references but with great care!
    - The ordering of the statements in the output file is such that
      all statements can be executed w.r.t. local variables. This is
      some kind of topological sorting. Be warned, it's implemented
      using black magic and may fail now and then!

    That should be all ...
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("metaconfiguration",
                        type = str,
                        help = "The meta-configuration file.",
                        default = GlobalDefaults.file_metaconfiguration)

    parser.add_argument("-d", "--destination",
                        type = str,
                        help = "The destination where to store the configurations generated.",
                        default = GlobalDefaults.path_to_autogen_configs)

    args = parser.parse_args()

    print("Meta configuration read from: " + args.metaconfiguration)
    print("Write configurations to: " + args.destination)

    # Read the configuration file
    with open(args.metaconfiguration) as f:
        content = f.read()

    # Execute the metaconfiguration file
    # Assuming that it defines the two dicts 'GP' and 'LP' in the toplevel namespace.
    exec(content)

    try:
        PA is None
    except NameError:
        print("Warning: no preamble found.")
        PA = """ """

    # Generate the configuration files
    generate_configurations(PA, GP, LP, cfpath=args.destination)