# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 17:42:33 2020

@author: Davide Laghi
"""
import output as out

class Comparison:
    def __init__(self, libraries, testname):
        # Generate a Benchmark Output
        self.benchmark = out.BenchmarkOutput(libraries, testname)


class SphereComparison(Comparison):
    def get_Data(self):
        