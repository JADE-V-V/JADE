"""

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
import sys
import os

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from jade.configuration import Configuration, Log

MAIN_CONFIG_FILE = os.path.join(cp, 'TestFiles', 'configuration',
                                'mainconfig.xlsx')
LOGFILE = os.path.join(cp, 'tmplog.txt')


# class TestConfiguration:
#     config = Configuration(MAIN_CONFIG_FILE)

#     def test_read(self):
#         # TODO
#         # Check that everything is read in a correct way
#         assert True

#     def test_get_lib_name(self):
#         suffix_list = ['21c', '33c', 'pincopalle']
#         expected_list = ['FENDL 2.1c', '33c', 'pincopalle']
#         for suffix, expected in zip(suffix_list, expected_list):
#             assert self.config.get_lib_name(suffix) == expected


class TestLog:
    # Here it is tested that the class just works without prompting errors
    # In depth test makes no sense because the class should be substitued
    # with the pre-built python log module.
    log = Log(LOGFILE)

    def test_bar_adjourn(self):
        txt = 'assdad'
        self.log.bar_adjourn(txt)
        self.log.bar_adjourn(txt, spacing=True)

        txt = 'asdadasdadasdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        self.log.bar_adjourn(txt)

        txt = 'asa'
        self.log.bar_adjourn(txt)

        assert True

    def test_adjourn(self):
        try:
            txt = 'adsdadasdadasd'
            self.log.adjourn(txt, spacing=True, time=True)
            assert True
        finally:
            os.remove(LOGFILE)
