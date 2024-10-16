
try:
    import jade.openmc as omc
    OMC_AVAIL = True
except ImportError:
    OMC_AVAIL = False
    print("OpenMC has not been installed")