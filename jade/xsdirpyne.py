# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:21:15 2019

@author: Pyne https://github.com/pyne/pyne

Copyright 2011-2020, the PyNE Development Team. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE PYNE DEVELOPMENT TEAM ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of the stakeholders of the PyNE project or the employers of PyNE developers.
"""
import math
import os
import sys
from typing import List, Tuple
from f4enix.input.xsdirpyne import Xsdir, XsdirTable


class SerpentXsdir(Xsdir):
    """
    Serpent Xsdir class
    """

    def read(self):
        for i, line in enumerate(self.f):
            if i % 2 == 0:
                # Create XsdirTable object and add to line
                table = XsdirTable()
                self.tables.append(table)
                words = line.split()
                if len(words) > 0:
                    table.name = words[0]
                    table.awr = float(words[5]) / 1.0086649670000
                    table.filename = words[8]
                    table.temperature = float(words[6]) / 1.1604518025685e10


class OpenMCXsdir(Xsdir):
    """
    OpenMC Xsdir class
    """

    def __init__(self, filename, libmanager, library):
        """Parameters
        ----------
        filename : str
            Path to xsdir file.
        """
        self.f = open(filename, "r")
        self.filename = os.path.abspath(filename)
        self.directory = os.path.dirname(filename)
        self.tables = []

        self.read(libmanager, library)

        # It is useful to have a list of the available tables names to be
        # computed only once at initializations
        tablenames = []
        for table in self:
            name = table.name
            zaidname = name[:-4]
            libname = name[-3:]
            tablenames.append((zaidname, libname))
        self.tablenames = tablenames

    def read(self, libmanager, library):
        for i, line in enumerate(self.f):
            if "<library" in line:
                line = line.replace('"', "")
                parts = line.split()
                data = {}
                for part in parts:
                    if "=" in part:
                        values = part.split("=")
                        data[values[0]] = values[1]
                if data["type"] == "neutron":
                    table = XsdirTable()
                    table.name = (
                        libmanager.get_formulazaid(data["materials"]) + "." + library
                    )
                    table.filename = data["path"]
