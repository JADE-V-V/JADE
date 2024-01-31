# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:33:01 2020

@author: Davide Laghi

Copyright 2021, the JADE Development Team. All rights reserved.

This file is part of JADE.

JADE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JADE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JADE.  If not, see <http://www.gnu.org/licenses/>.
"""
import datetime

import jade.expoutput as expo
import jade.output as bencho
import jade.sphereoutput as spho


def compareBenchmark(session, lib_input: str, testname: str, exp = False) -> None:
    """Compare benchmark results and perform post-processing.

    Parameters
    ----------
    session : session
        JADE session
    lib_input : str
        Data library
    testname : str
        Named of the test to be compared and post-processed
    """

    print("\n Comparing " + testname + ":" + "    " + str(datetime.datetime.now()))
    lib = lib_input.split("-")
    """# get the correct output object
    out = _get_output('compare', testname, lib, session)
    if out:
        out.compare()

    session.log.adjourn(testname+' benchmark comparison completed' +
                        '    ' + str(datetime.datetime.now()))"""

    # Get the settings for the tests
    if exp == True:
        config = session.conf.exp_default.set_index("Description")
    else:        
        config = session.conf.comp_default.set_index("Description")
    # Get the log
    log = session.log

    for testname, row in config.iterrows():
        if (bool(row["Post-Processing"])) and (
            bool(row["MCNP"])
            or bool(row["Serpent"])
            or bool(row["OpenMC"])
            or bool(row["d1S"])
        ):
            print(
                "\n Post-Processing "
                + testname
                + ":"
                + "    "
                + str(datetime.datetime.now())
            )
            # get the correct output object
            out = _get_output("compare", row, lib, session)
            if out:
                out.compare()

            log.adjourn(
                testname
                + " benchmark post-processing completed"
                + "    "
                + str(datetime.datetime.now())
            )


def postprocessBenchmark(session, lib: str) -> None:
    """Perform post-processing for specific benchmarks where specified.

    Parameters
    ----------
    session : session
        JADE session
    lib : str
        Data library
    """

    # Get the settings for the tests
    config = session.conf.comp_default.set_index("Description")
    # Get the log
    log = session.log

    for testname, row in config.iterrows():
        if (bool(row["Post-Processing"])) and (
            bool(row["MCNP"])
            or bool(row["Serpent"])
            or bool(row["OpenMC"])
            or bool(row["d1S"])
        ):
            print(
                "\n Post-Processing "
                + testname
                + ":"
                + "    "
                + str(datetime.datetime.now())
            )
            # get the correct output object
            out = _get_output("pp", row, lib, session)
            if out:
                out.single_postprocess()

            log.adjourn(
                testname
                + " benchmark post-processing completed"
                + "    "
                + str(datetime.datetime.now())
            )


def _get_output(action, config, lib, session):
    exp_pp_message = "\n No single pp is foreseen for experimental benchmarks"
    testname = config["Folder Name"]

    if testname == "Sphere":
        out = spho.SphereOutput(lib, config, session)

    elif testname == "SphereSDDR":
        out = spho.SphereSDDRoutput(lib, config, session)

    #TODO change testname to config
    elif testname in ['Oktavian']:
        if action == 'compare':
            out = expo.SpectrumOutput(lib, config, session, multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname in ['Tiara-BC', 'FNS-TOF', 'TUD-Fe', 'TUD-W']:
        if action == 'compare':
            out = expo.MultipleSpectrumOutput(lib, config,
                                              session, multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname in ['TUD-FNG']:
        if action == 'compare':
            out = expo.MultipleSpectrumOutput(lib, config, session)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname == 'Tiara-FC':
        if action == 'compare':
            out = expo.TiaraFCOutput(lib, config, session, multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname == 'Tiara-BS':
        if action == 'compare':
            out = expo.TiaraBSOutput(lib, config, session, multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname in ['FNG-BKT', 'FNG-W', 'ASPIS-Fe88']:
        if action == 'compare':
            out = expo.ShieldingOutput(lib, config, session,
                                       multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False

    elif testname == "FNG":
        if action == "compare":
            out = expo.FNGOutput(lib, config, session, multiplerun=True)
        elif action == "pp":
            print(exp_pp_message)
            return False

    else:
        out = bencho.BenchmarkOutput(lib, config, session)

    return out
