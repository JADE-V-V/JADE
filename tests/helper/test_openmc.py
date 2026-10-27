from __future__ import annotations

from importlib.resources import files

import pytest, os

import pandas as pd

from jade.helper.__optionals__ import OMC_AVAIL
from tests.post.resources import openmc as resources

if OMC_AVAIL:
    import openmc

    import jade.helper.openmc as omc


STATEPOINT = files(resources).joinpath("statepoint.10.h5")
CELL_VOLUMES = files(resources).joinpath("volumes.json")
XML_PATH = os.path.dirname(STATEPOINT)


class TestOpenMCCellData:
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_from_files(self):
        omc_cell_data = omc.OpenMCCellData.from_files(CELL_VOLUMES, XML_PATH)
        assert omc_cell_data.cell_volumes[84] == 396061.0
        assert omc_cell_data.cell_volumes[106] == 225997.0
        assert omc_cell_data.cell_volumes[73] == 758884.0
        assert omc_cell_data.cell_masses[84] == pytest.approx(2864154.7276)
        assert omc_cell_data.cell_masses[106] == pytest.approx(1634319.9052)
        assert omc_cell_data.cell_masses[73] == pytest.approx(5487945.534399999)


class TestOpenMCStatePoint:
    @pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
    def test_tallies_to_dataframes(self):
        out = omc.OpenMCStatePoint(STATEPOINT, CELL_VOLUMES)
        tallies = out.tallies_to_dataframes()
        assert "photon" == tallies[56]["particle"][5]
        assert "total" == tallies[86]["nuclide"][0]
        assert 11 == tallies[56]["cell"][2]
        assert 5.398984399675055e-06 == pytest.approx(
            tallies[24]["mean"][5] / out.cell_data.cell_volumes[tallies[24]["cell"][5]]
        )
        assert 3.70844522806895e-08 == pytest.approx(
            tallies[24]["std. dev."][5]
            / out.cell_data.cell_volumes[tallies[24]["cell"][5]]
        )
        # photon heating includes the separate electron and positron tallies
        assert 561 not in tallies and 562 not in tallies
        raw_sum = sum(
            out._get_tally_data(out.statepoint.tallies[i])["mean"]
            for i in (56, 561, 562)
        )
        assert list(tallies[56]["mean"]) == pytest.approx(list(raw_sum))


def _heating_df(cells, particles, means, stds, score="heating", nuclide="total"):
    """Build a dataframe with the same layout as openmc get_pandas_dataframe"""
    rows = []
    i = 0
    for cell in cells:
        for particle in particles:
            rows.append([cell, particle, nuclide, score, means[i], stds[i]])
            i += 1
    return pd.DataFrame(
        rows, columns=["cell", "particle", "nuclide", "score", "mean", "std. dev."]
    )


def _tally(tally_id, particles, filters, scores=("heating",)):
    tally = openmc.Tally(tally_id=tally_id)
    tally.filters = [*filters, openmc.ParticleFilter(particles)]
    tally.scores = list(scores)
    return tally


@pytest.mark.skipif(not OMC_AVAIL, reason="OpenMC is not available")
class TestHeatingCombination:
    def test_fold_single_tally(self):
        particles = ["neutron", "photon", "electron", "positron"]
        df = _heating_df(
            [1, 2], particles, [1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8]
        )
        out = omc.OpenMCStatePoint._fold_charged_into_photon(df)
        assert list(out.columns) == list(df.columns)
        assert list(out["particle"]) == ["neutron", "photon"] * 2
        assert list(out["cell"]) == [1, 1, 2, 2]
        assert list(out["mean"]) == [1, 9, 5, 21]
        assert out["std. dev."][1] == pytest.approx((4 + 9 + 16) ** 0.5)
        assert out["std. dev."][3] == pytest.approx((36 + 49 + 64) ** 0.5)

    def test_fold_zero_charged(self):
        # OpenMC >= 0.16.0 attributes the charged particle heating to photons
        df = _heating_df([1], ["photon", "electron", "positron"], [2, 0, 0], [1, 0, 0])
        out = omc.OpenMCStatePoint._fold_charged_into_photon(df)
        assert len(out) == 1
        assert out["mean"][0] == 2
        assert out["std. dev."][0] == pytest.approx(1)

    def test_fold_other_scores_untouched(self):
        heating = _heating_df([1], ["photon", "electron"], [1, 2], [1, 1])
        flux = _heating_df([1], ["photon", "electron"], [3, 4], [1, 1], score="flux")
        df = pd.concat([heating, flux], ignore_index=True)
        out = omc.OpenMCStatePoint._fold_charged_into_photon(df)
        assert list(out["score"]) == ["heating", "flux", "flux"]
        assert list(out["particle"]) == ["photon", "photon", "electron"]
        assert list(out["mean"]) == [3, 3, 4]

    def test_fold_no_particle(self):
        df = _heating_df([1], ["photon"], [1], [1]).drop(columns="particle")
        out = omc.OpenMCStatePoint._fold_charged_into_photon(df)
        assert out.equals(df)

    def _combine(self, monkeypatch, tallies: dict, dfs: dict) -> dict:
        sp = object.__new__(omc.OpenMCStatePoint)
        monkeypatch.setattr(sp, "_get_tally_data", lambda tally: dfs[tally.id])
        return sp._combine_heating_tallies(tallies)

    def test_combine_separate_tallies(self, monkeypatch):
        materials = openmc.MaterialFilter([1, 2])
        tallies = {
            1: _tally(1, ["neutron"], [materials]),
            2: _tally(2, ["photon"], [materials]),
            3: _tally(3, ["electron"], [materials]),
            4: _tally(4, ["positron"], [materials]),
        }
        dfs = {
            1: _heating_df([1, 2], ["neutron"], [10, 20], [1, 1]),
            2: _heating_df([1, 2], ["photon"], [1, 2], [1, 1]),
            3: _heating_df([1, 2], ["electron"], [3, 4], [1, 1]),
            4: _heating_df([1, 2], ["positron"], [5, 6], [1, 1]),
        }
        out = self._combine(monkeypatch, tallies, dfs)
        assert set(out.keys()) == {1, 2}
        assert list(out[1]["mean"]) == [10, 20]
        assert list(out[2]["particle"]) == ["photon", "photon"]
        assert list(out[2]["mean"]) == [9, 12]
        assert out[2]["std. dev."][0] == pytest.approx(3**0.5)

    def test_combine_electron_positron_tally(self, monkeypatch):
        cells = openmc.CellFilter([1, 2])
        tallies = {
            2: _tally(2, ["photon"], [cells]),
            3: _tally(3, ["electron", "positron"], [cells]),
        }
        dfs = {
            2: _heating_df([1, 2], ["photon"], [1, 2], [1, 1]),
            3: _heating_df([1, 2], ["electron", "positron"], [3, 4, 5, 6], [1] * 4),
        }
        out = self._combine(monkeypatch, tallies, dfs)
        assert set(out.keys()) == {2}
        assert list(out[2]["mean"]) == [8, 13]

    def test_combine_single_tally(self, monkeypatch):
        cells = openmc.CellFilter([1])
        particles = ["neutron", "photon", "electron", "positron"]
        tallies = {5: _tally(5, particles, [cells])}
        dfs = {5: _heating_df([1], particles, [1, 2, 3, 4], [1] * 4)}
        out = self._combine(monkeypatch, tallies, dfs)
        assert list(out[5]["particle"]) == ["neutron", "photon"]
        assert list(out[5]["mean"]) == [1, 9]

    def test_combine_no_double_counting(self, monkeypatch):
        cells = openmc.CellFilter([1])
        tallies = {
            2: _tally(2, ["photon", "electron"], [cells]),
            3: _tally(3, ["electron", "positron"], [cells]),
        }
        dfs = {
            2: _heating_df([1], ["photon", "electron"], [1, 2], [1, 1]),
            3: _heating_df([1], ["electron", "positron"], [2, 4], [1, 1]),
        }
        out = self._combine(monkeypatch, tallies, dfs)
        assert list(out[2]["mean"]) == [7]

    def test_combine_different_filters(self, monkeypatch):
        cells = openmc.CellFilter([1])
        energy = openmc.EnergyFilter([0.0, 1e6, 2e7])
        other_cells = openmc.CellFilter([2])
        tallies = {
            2: _tally(2, ["photon"], [cells, energy]),
            3: _tally(3, ["electron"], [cells]),
            4: _tally(4, ["positron"], [other_cells]),
        }
        dfs = {
            2: _heating_df([1], ["photon"], [1], [1]),
            3: _heating_df([1], ["electron"], [2], [1]),
            4: _heating_df([2], ["positron"], [4], [1]),
        }
        out = self._combine(monkeypatch, tallies, dfs)
        assert list(out[2]["mean"]) == [1]

    def test_combine_no_particle_filter(self, monkeypatch):
        tally = openmc.Tally(tally_id=7)
        tally.filters = [openmc.CellFilter([1])]
        tally.scores = ["heating"]
        df = _heating_df([1], ["photon"], [1], [1]).drop(columns="particle")
        out = self._combine(monkeypatch, {7: tally}, {7: df})
        assert out[7].equals(df)
