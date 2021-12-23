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

from status import Status
from configuration import Configuration
from tests.configuration_test import MAIN_CONFIG_FILE
import shutil


class SessionMockUp:
    path_test = os.path.join(cp, 'TestFiles', 'status')
    path_run = os.path.join(path_test, 'MCNP simulations')
    path_single = os.path.join(path_test, 'Post-Processing',
                               'Single Libraries')
    path_comparison = os.path.join(path_test, 'Post-Processing', 'Comparison')

    def __init__(self, config):
        self.conf = config
        self.log = LogMockUp()

    def check_active_tests(self, config_option, exp=False):
        # Mocks the check in the configuration file
        if not exp:
            return ['Sphere', 'C_Model']
        elif exp:
            return ['Oktavian']


class LogMockUp:
    def adjourn(self, text):
        print('do nothing')


class TestStatus:

    def_config = Configuration(MAIN_CONFIG_FILE)

    def test_update_run_status(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)
        init_run_tree = status.run_tree

        # modify the run tree
        src = os.path.join(status.run_path, '31c')
        dst = os.path.join(status.run_path, '22c')
        shutil.copytree(src, dst)
        # re-read and check everything went fine
        try:
            status.update_run_status()
            try:
                get = status.run_tree['22c']
                assert True
            except KeyError:
                assert False
        finally:
            # remove the additional folder and check that everything is like
            # before
            shutil.rmtree(dst)

        status.update_run_status()
        assert init_run_tree == status.run_tree

    def test_update_pp_status(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)
        init_single_tree = status.single_tree
        init_comparison_tree = status.comparison_tree

        # modify one of trees
        src_single = os.path.join(status.single_path, '31c')
        dst_single = os.path.join(status.single_path, '22c')
        shutil.copytree(src_single, dst_single)
        # re-read and check everything went fine
        try:
            status.update_pp_status()
            try:
                get = status.single_tree['22c']
                assert True
            except KeyError:
                assert False
        finally:
            # remove the additional folder and check that everything is like
            # before
            shutil.rmtree(dst_single)

        status.update_pp_status()
        assert init_single_tree == status.single_tree
        assert init_comparison_tree == status.comparison_tree

    def test_get_path(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)

        itinerary = ['00c', 'Sphere', 'Sphere_1001_H-1']
        cp = status.run_path
        for step in itinerary:
            cp = os.path.join(cp, step)
        assert status.get_path('run', itinerary) == cp

        try:
            cp = status.get_path('sda', [])
            assert False
        except KeyError:
            assert True

        assert status.get_path('single', []) == status.single_path
        assert status.get_path('comparison', []) == status.comparison_path

    def test_get_unfinished_zaid(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)
        lib = '00c'
        unfinished, motherdir = status.get_unfinished_zaids(lib)
        assert unfinished == ['Sphere_1002_H-2']
        assert motherdir == os.path.join(status.run_path, lib, 'Sphere')

    def test_check_override_run(self, monkeypatch):
        session = SessionMockUp(self.def_config)
        status = Status(session)

        # If no tests are run it is safe to override
        ans = status.check_override_run('10d', session)
        assert ans

        # If tests are already run, ask for permission
        monkeypatch.setattr('builtins.input', lambda _: "y")
        ans = status.check_override_run('31c', session)
        assert ans

        monkeypatch.setattr('builtins.input', lambda _: "n")
        ans = status.check_override_run('31c', session)
        assert not ans

    def test_check_lib_run(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)

        # config option is not important since the session is just a mock-up
        libs = ['31c', '00c', '99c', '10d']
        exp_options = [False, False, True, True]
        expected_list = [['Sphere', 'C_Model'], [], ['Oktavian'], []]

        for lib, option, expected in zip(libs, exp_options, expected_list):
            testrun = status.check_lib_run(lib, session, config_option='Run',
                                           exp=option)
            assert testrun == expected

    def test_check_pp_single(self):
        session = SessionMockUp(self.def_config)
        status = Status(session)

        # Single
        libs = ['31c', '00c', '31d']
        tree = 'single'
        answers = [True, False, False]
        for lib, answer in zip(libs, answers):
            ans = status.check_pp_single(lib, session, tree=tree)
            assert ans == answer

        # Comparison
        libs = ['32c_Vs_31c', '99c_Vs_98c_Vs_31c', '31c_Vs_30c']
        tree = 'comparison'
        exp_options = [True, True, False]
        answers = [True, False, True]
        for lib, answer, exp in zip(libs, answers, exp_options):
            ans = status.check_pp_single(lib, session, tree=tree, exp=exp)
            assert ans == answer

    def test_check_override_pp(self, monkeypatch):
        session = SessionMockUp(self.def_config)
        status = Status(session)

        # The library has been run and pp. do not ovveride
        responses = iter(['31c', 'n'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert not ans
        assert to_single_pp == ['31c']

        # The library has been run and pp. ovveride
        responses = iter(['31c', 'y'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert ans
        assert to_single_pp == ['31c']

        # The library has been run but not pp.
        responses = iter(['32c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert ans
        assert to_single_pp == ['32c']

        # The library has not been run correctly
        responses = iter(['00c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert not ans
        assert to_single_pp == []

        # --- Comparisons ---
        # Both libraries were run and single pp. Override
        responses = iter(['31c-30c', 'y'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert ans
        assert to_single_pp == []

        # Both libraries were run and single pp. Do not override
        responses = iter(['31c-30c', 'n'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert not ans
        assert to_single_pp == []

        # Both libraries were run, experimental. No comparison still done
        responses = iter(['99c-98c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session, exp=True)
        assert ans
        assert to_single_pp == []

        # Both libraries were run, one is missing pp.
        responses = iter(['99c-98c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session, exp=True)
        assert ans
        assert to_single_pp == []

        # Both libraries were run, one is missing pp.
        responses = iter(['33c-31c'])
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        ans, to_single_pp, _ = status.check_override_pp(session)
        assert ans
        assert to_single_pp == ['33c']
