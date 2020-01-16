# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:57:26 2020

@author: Davide Laghi
"""
import os


class Status():
    def __init__(self, session):
        cp = os.path.dirname(os.getcwd())
        # Paths
        self.test_path = os.path.join(cp, 'Tests')
        self.run_path = os.path.join(self.test_path, '01_MCNP_Run')
        self.pp_path = os.path.join(self.test_path, '02_Output')

        self.config = session.conf

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

    def check_override_run(self, lib, session):
        """
        Check status of the requested run. If overridden is required permission
        is requested to the user

        Parameters
        ----------
        lib : str
            Library to run.
        session : Session
            Jade Session.

        Returns
        -------
        ans : Boolean
            if True proceed with the run, if False, abort.

        """

        test_runned = self.check_lib_run(lib, session)
        # Ask for override
        if len(test_runned) > 0:
            while True:
                print(' The following benchmark(s) have already been run:')
                for test in test_runned:
                    print(' - '+test)

                print("""
     You can manage the selection of benchmarks to run in the Config.xlsx file
    """)
                i = input(' Would you like to override the results?(y/n) ')

                if i == 'y':
                    ans = True
                    logtext = '\nThe following test results have been overwritten:'
                    for test in test_runned:
                        logtext = logtext+'\n'+'- '+test+' ['+lib+']'
                    session.log.adjourn(logtext)
                    break
                elif i == 'n':
                    ans = False
                    break
                else:
                    print('\n please select one between "y" or "n"')

        else:
            ans = True

        return ans

    def check_lib_run(self, lib, session):
        # Update Tree
        self.update_run_status()
        # Check if/what is already run
        config = self.config.comp_default
        test_runned = []
        for idx, row in config.iterrows():
            filename = str(row['File Name'])
            testname = filename.split('.')[0]

            # Check if test is active
            to_perform = session.check_active_tests('Run')

            if testname in to_perform:
                # Check if benchmark folder exists
                try:
                    test = self.run_tree[lib][testname]
                    if testname == 'Sphere':
                        flag_test_run = True
                        for zaid, files in test.items():
                            # Check if output is present
                            flag_run_zaid = False
                            for file in files:
                                c1 = (file[-1] == 'm')  # mctal file
                                c2 = (file[-4:] == 'msht')  # meshtally file
                                if c1 or c2:
                                    flag_run_zaid = True

                            if not flag_run_zaid:
                                flag_test_run = False

                        if flag_test_run:
                            test_runned.append('Sphere')
                    else:
                        # Check if output is present
                        for file in test:
                            c1 = file[-1] == 'm'  # mctal file
                            c2 = file[-4:] == 'msht'  # meshtally file
                            if not c1 and not c2:
                                pass  # It has not been run correctly
                            else:
                                test_runned.append(testname)
                except KeyError:  # Folder does not exist
                    pass

        return test_runned

    def check_pp_single(self, lib, session):
        self.update_pp_status()
        try:
            library_tests = self.single_tree[lib]
            to_pp = session.check_active_tests('Post-Processing')
            ans = True
            for test in to_pp:
                if test not in library_tests:
                    ans = False
            return ans
        except KeyError:
            return False

    def check_override_pp(self, session):
        """
        Asks for the library/ies to post-process and checks which tests have
        already been performed and would be overidden according to the
        configuration file

        Parameters
        ----------
        session : Session
            JADE session

        Returns
        -------
        lib, ans

        """
        lib_input = input(' Libraries to post-process (e.g. 31c-71c): ')
        # Individuate libraries to pp
        libs = lib_input.split('-')
        if len(libs) == 1:
            tagpp = 'Single Libraries'
        else:
            tagpp = 'Comparison'

        # Check if libraries have been run
        flag_not_run = False
        for lib in libs:
            test_run = self.check_lib_run(lib, session)
            if len(test_run) == 0:  # TODO not checking for each benchmark
                flag_not_run = True

        to_single_pp = []

        if flag_not_run:
            ans = False
            print(' '+lib+' was not run. Please run it first.')
        else:
            # Check if single pp has been done
            for lib in libs:
                if not self.check_pp_single(lib, session):
                    to_single_pp.append(lib)

            if tagpp == 'Single Libraries':
                # Ask for override
                if len(to_single_pp) == 0:
                    lib = libs[0]
                    to_single_pp = [lib]
                    while True:
                        print("""
 One or more benchmark were already post-processed for this library.
 You can manage the selection of benchmarks in the Config.xlsx file.
""")
                        i = input(' Would you like to override the results?(y/n) ')
                        if i == 'y':
                            ans = True
                            logtext = '\nThe Post-Process for library ' + \
                                str(lib)+' has been overwritten'
                            session.log.adjourn(logtext)
                            break
                        elif i == 'n':
                            ans = False
                            break
                        else:
                            print('\n please select one between "y" or "n"')

                else:
                    ans = True

        return ans, to_single_pp
