# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 17:18:07 2020

@author: Davide Laghi
"""
import pandas as pd
import MCTAL_READER as mctal
import numpy as np
import math
import os

from output import BenchmarkOutput


class ExperimentalOutput(BenchmarkOutput):
    def __init__(self, lib, testname, session):
        super().__init__(lib, testname, session)
        # The experimental data needs to be loaded
        self.path_exp_res = os.path.join(session.path_exp_res, testname)

    def single_postprocess(self):
        # Shall be implemented in the specific output
        pass

    def compare(self):
        # Shall be implemented in the specific output
        pass

    @staticmethod
    def _convert_TOF_to_E(distance, times, p_mass):
        """
        Given a distance, the Time of flight are converted to energies in [eV]

        Parameters
        ----------
        distance : float
            distance in [m].
        times : array
            times to be converted in MCNP shakes.
        mass : float
            mass of the particle under study in [Kg]

        Returns
        -------
        energies : array
            result of the time conversion in energies.

        """
        # --- Additional constants ---
        shakes2time = 1e-8  # s/shake
        j2eV = 6.242e+18  # eV/J

        # Convert TOF MCNP tally into energies
        velocities = distance/(times*shakes2time)  # m/s
        energies = 1/2*p_mass*velocities**2*j2eV

        return energies

    @staticmethod
    def _get_Espectrum(flux, energies, overLethargy=False, let_ratio=None):
        """
        Normalize the flux over the integral in order to obtain the energy
        spectrum. The spectrum per lethargy unit can be also obtained

        Parameters
        ----------
        flux : array
            flux values to normalize.
        energies : array
            correspondent energy values.
        overLethargy : bool, optional
            If True the spectrum is given by unit lethargy.
            The default is False.
        let_ratio : float, optional
            ratio between max and min energy to use for lethargy normalization.
            The default is None.

        Returns
        -------
        y : array
            energy spectrum.

        """
        # Normalize the flux respect to the integral to obtain the spectrum
        tot_area = np.trapz(flux, x=energies)
        y = flux/(tot_area)

        # Normalize and divide for lethargy
        if overLethargy:
            if let_ratio is None:
                norm = math.log(min(energies)/max(energies))
            else:
                norm = math.log(let_ratio)

            y = y/(-norm)

        return y


class OktavianOutput(ExperimentalOutput):
    def single_postprocess(self):
        pass

    def compare(self):
        pass

    def _processMCNPdata(self):
        # --- Main constants ---
        distance = 9.5  # m
        # E0 = 15  # MeV
        mass = 1.67e-27   # kg

        # Load ref results
        file = os.path.join(self.path_exp_res, 'Energy spectrum.xlsx')
        lowE = pd.read_excel(file, sheet_name='Low Energy')
        highE = pd.read_excel(file, sheet_name='High Energy')

        # Read tally TOF
        TOF_tally = mctal.tallies[0]
        times = TOF_tally.tim
        values = []
        for i, t in enumerate(times):
            val = TOF_tally.getValue(0, 0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0)
            values.append(val)

        # Read tally energy
        E_tally = mctal.tallies[1]
        energies_e = E_tally.erg
        values_e = []
        for i, t in enumerate(energies_e):
            val = E_tally.getValue(0, 0, 0, 0, 0, 0, i, 0, 0, 0, 0, 0)
            values_e.append(val)

        # Infinity problem given by the time = 0
        # To have negative times is a no-sense
        values = np.flip(np.array(values[2:]))  # mid values
        times = np.flip(np.array(times[2:]))  # bin limits
        # Convert TOF MCNP tally into energies in MeV
        energies_TOF = self._convert_TOF_to_E(distance, times, mass)*10**-6
        spectrum_TOF = self._getEspectrum(values, energies_TOF,
                                          overLethargy=True)
        spectrum_E = self._getEspectrum(values_e, energies_e,
                                        overLethargy=True)


        # # Plot MCNP results
        # fix, ax = plt.subplots(figsize=(16,9))

        # Normalize the flux respect to the integral to obtain the spectrum
        y = values
        tot_area = np.trapz(y, x=energies)
        y = y/(tot_area)

        # # Convert the spectrum into lethargy
        # # norm will be the log between min and reference energy
        # norm = math.log(min(data['Energy [MeV]'])/E0)
        # # norm will be the log between min and max energy
        # #norm = math.log(min(data['Energy [MeV]'])/max(data['Energy [MeV]']))
        # y = y/(-norm)

        # ax.plot(energies, y, label='MCNP TOF', color='black')
        # #ax.plot(data['Energy [MeV]'], data['Value'], label='Experiment')

        # ax.plot(data['Energy [MeV]'], data['Value'], '.', label='Experiment', color='green')
        # plus_error = (1+data['Error']/100)*data['Value']
        # minus_error = (1-data['Error']/100)*data['Value']

        # # normalize energy bin
        # y = values_e
        # tot_area = np.trapz(y, x=energies_e)
        # y = y/(tot_area)

        # norm = math.log(min(data['Energy [MeV]'])/E0)
        # y = y/(-norm)

        # ax.plot(energies_e, y, '--', label='MCNP energy', alpha=0.5, color='red')



    # ax.fill_between(data['Energy [MeV]'], plus_error, minus_error, color='green', alpha=0.2)

    # ax.set_yscale('log')
    # ax.set_xscale('log')
    # ax.set_xlabel('Energy [MeV]')
    # ax.set_ylabel('Neutrons spectrum (n/Lethargy)')
    # ax.set_title('Time of Flight')
    # ax.grid()

    # ax.legend()

