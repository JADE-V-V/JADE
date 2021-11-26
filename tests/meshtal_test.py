from ntpath import join
import sys
import os

cp = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(cp)
sys.path.insert(1, modules_path)

from meshtal import Meshtal

MSHTAL_FILE = os.path.join(cp, 'TestFiles', 'meshtal', 'test_msht')

class TestMeshtal:
    meshtal = Meshtal(MSHTAL_FILE)

    def test_extract_1D(self):
        fmesh = self.meshtal.fmeshes['244']
        assert fmesh.tallynum == '244'
        assert fmesh.description == 'Photon Flux [#/cc/n_s]'

        fmeshes1D = self.meshtal.extract_1D()
        assert len(fmeshes1D) == 5
        fmesh1D = fmeshes1D['234']
        assert fmesh1D['desc'] == 'Neutron Flux [#/cc/n_s]'
        assert fmesh1D['num'] == '234'
        assert fmesh1D['data'].shape == (79, 3)
        assert list(fmesh1D['data'].columns) == ['Cor A', 'Value', 'Error']
