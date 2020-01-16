# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:57:26 2020

@author: Davide Laghi
"""
import os


class Status():
    def __init__(self):
        cp = os.path.dirname(os.getcwd())
        # Paths
        self.test_path = os.path.join(cp, 'Tests')
        self.run_path = os.path.join(self.test_path, '01_MCNP_Run')
        self.pp_path = os.path.join(self.test_path, '02_Output')

        # Initialize run tree
        self.run_tree = self.update_run_status()
        # Initialize pp trees
        self.comparison_tree, self.single_tree = self.update_pp_status()

    def update_run_status(self):
        """
        Read/Update the run tree status. All files produced by runs are
        registered

        Returns
        -------
        libraries : dic
            dictionary of dictionaries representing the run tree

        """
        libraries = {}
        for lib in os.listdir(self.run_path):
            libraries[lib] = {}
            cp = os.path.join(self.run_path, lib)
            for test in os.listdir(cp):
                if test == 'Sphere':
                    libraries[lib][test] = {}
                    cp1 = os.path.join(cp, test)
                    for zaid in os.listdir(cp1):
                        libraries[lib][test][zaid] = []
                        cp2 = os.path.join(cp1, zaid)
                        for file in os.listdir(cp2):
                            libraries[lib][test][zaid].append(file)
                else:
                    libraries[lib][test] = []
                    cp1 = os.path.join(cp, test)
                    for file in os.listdir(cp1):
                        libraries[lib][test].append(file)

        # Update tree
        self.run_tree = libraries

        return libraries

    def update_pp_status(self):
        """
        Read/Update the post processing tree status. All files produced by
        post processing registered

        Returns
        -------
        comparison_tree : dic
            Dictionary registering all test post processed for each
            comparison of libraries.
        single_tree : dic
            Dictionary registering all test post processed performed for
            single libraries.

        """
        # Read comparison tree
        comparison_tree = {}
        cp = os.path.join(self.pp_path, 'Comparisons')
        for lib in os.listdir(cp):
            comparison_tree[lib] = []
            cp1 = os.path.join(cp, lib)
            for test in os.listdir(cp1):
                comparison_tree[lib].append(test)

        # Read Single library tree
        single_tree = {}
        cp = os.path.join(self.pp_path, 'Single Libraries')
        for lib in os.listdir(cp):
            single_tree[lib] = []
            cp1 = os.path.join(cp, lib)
            for test in os.listdir(cp1):
                single_tree[lib].append(test)

        # Update Trees
        self.comparison_tree = comparison_tree
        self.single_tree = single_tree

        return comparison_tree, single_tree
