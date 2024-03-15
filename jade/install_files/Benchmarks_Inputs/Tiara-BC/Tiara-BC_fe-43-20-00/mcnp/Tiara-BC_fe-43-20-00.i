TIARA Fe, 43 MeV, 20 cm shield, B. Kos (bor.kos@ijs.si), 2018
c TIARA Fe, 43 MeV, 20 cm shield
c Bor Kos, JSI, July 2018
c BC501A spectra on-axis
100 6  -2.31      -100:-101:-102 :-103: -104: -105 :(-106 110):
                   (-110 -109 -106.3 104.1 105.1 111):
                   (-111  108 -106.3 104.1 105.1 112):
                   (-112  107 -106.3 104.1 105.1) imp:n=1                      $ Concrete structure
101 1  -7.87      -150 151 imp:n=1                                             $ Beam dump
102 1  -7.08      -200 201 202 2 imp:n=1                                       $ Iron filler (density is 10 % lower than ordinary iron - original documentation assumes a mixutre of iron sand and balls)
103 1  -7.87      -201 2 imp:n=1                                               $ Rotary shutter - iron
104 2  -0.928     -202 2  imp:n=1                                              $ Rotary shutter - polyethylene
105 3  -2.6989    -210 : -211 : -212 imp:n=1                                   $ Trolly (aluminium - assumed, not in benchmark documetation)
108 3  -2.6989    -232 : -233 : -234 : -235 : -236 imp:n=1                     $ Detector support table - aluminium assumed -  BC 501A Liquid scintilator on-axis
109 4  -0.874     -237 imp:n=1                                                 $ BC 501A Liquid scintilator - only dimenssions in benchmark documentation - BC 501A on axis
110 1  -7.87      -1000 imp:n=1                                                $ Iron test shield 
600 0             -600 #100 #101 #102 #103 #104 -2.2 imp:n=1                   $ void
700 5  -0.001205  -600 1000 #100 #104 #105 #108 #109  2.2 imp:n=1              $ air                                                         
601 0              600 imp:n=0                                                 $ Outer space

c -----------------------------------------------------------------------------
c         SURFACES                                                         
c -----------------------------------------------------------------------------
c Source
1   px    0.0                                                                   $ Source plane
c Beam line
2   rcc 0.0 0.0 0.0 396.0 0.0 0.0 5.45  
c Concret stucture
100 box -124.0  250.0 -109.0 0.0 0.0 -200.0 0.0 -500.0 0.0 300.0 0.0 0.0
101 box  176.0  250.0 -119.0 0.0 -500.0 0.0 60.0 0.0 0.0 0.0 0.0 -190.0
102 box  716.0 -250.0 -309.0 0.0 0.0 232.65 0.0 500.0 0.0 -480.0 0.0 0.0
103 box  236.0  250.0  -20.0 0.0 -500.0 0.0 160.0 0.0 0.0 0.0 0.0 -56.35
104 box -124.0 -250.0 -119.0 0.0 190.0 0.0 0.0 0.0 399.065125 640.0 0.0 0.0
105 box -124.0  250.0 -119.0 0.0 -190.0 0.0 0.0 0.0 399.065125 640.0 0.0 0.0
106 box  516.0 -60.0    60.0 0.0 120.0 0.0 0.0 0.0 220.065122 -640.0 0.0 0.0
107 p    16020.908203 0.0 16038.62915 2.5053e+6
108 pz   146.558
109 p   -5443.936157 0.0 -5563.590088 -1.5211e+6
110 px   176
111 px   129.637
112 px   9.65524
c Beam dump
150 box 236.0 -20.0 -119.0 -60.0 0.0 0.0 0.0 40.0 0.0 0.0 0.0 99.0
151 box 206.0 -20.0 -89.0 0.0 40.0 0.0 -30.0 0.0 0.0 0.0 0.0 50.0
c Iron filler (iron balls and iron sand)
200 box 176.0 60.0 60.0 0.0 0.0 -80.0 0.0 -120.0 0.0 220.0 0.0 0.0
c Rotary shutter - iron
201 rcc 183 0 9.08 100.0 0.0 0.0 21.8
c Rotary shutter - polyethylene
202 rcc 283 0 9.08 50.0 0.0 0.0 21.8
c Trolly
210 box 398.5 -60.0 -60.0 0.0 0.0 -10.0 0.0 120.0 0.0 120.0 0.0 0.0
211 rcc 409.718 -60.0 -70.0 0.0 120.0 0.0 6.35
212 rcc 503.650752 -60.0 -70.0 0.0 120.0 0.0 6.35
c BC 501A Liquid scintilator - on-axis
232 box 421.0 10.0 -6.351 0.0 0.0 -0.99 0.0 -20.0 0.0 40.0 0.0 0.0 $ Detector support table - aluminium assumed
233 rcc 422.0  9.0 -7.350 0.0 0.0 -52.65 0.99
234 rcc 422.0 -9.0 -7.350 0.0 0.0 -52.65 0.99
235 rcc 460.0  9.0 -7.350 0.0 0.0 -52.65 0.99
236 rcc 460.0 -9.0 -7.350 0.0 0.0 -52.65 0.99
237 rcc 421.0  0.0  0.0  12.7 0.0   0.0  6.350 $ Liquid Scintilator BC 501A on-axis  
c Outside world
600 box -130 -252 -315 850 0.0 0.0 0.0 504.0 0.0 0.0 0.0 600.0
c Additional iron colimator
c 800
c Shield
1000 box 401.0 -60 -60 20.0 0.0 0.0 0.0 120.0 0.0 0.0 0.0 120.0

c -----------------------------------------------------------------------------
c         MATERIALS
c -----------------------------------------------------------------------------
c Iron shield - atom density, Density ( g /cm3 )= 7.87. Naturan iron from benchmark documetation - Table 1.2 JAERI-Data/Code 96-029
m1   26054. 4.9605E-03
     26056. 7.7869E-02
     26057. 1.7983E-03
     26058. 2.3933E-04
c Polyethylene - atom density, Density ( g /cm3 )= 0.928, Reference: http://physics.nist.gov/PhysRefData/XrayMassCoef/tab2.html    
m2    1001. 0.079855
      6000. 0.039929
c Aluminum - atom density, Density ( g /cm3 )= 2.6989
m3   13027. 0.060238
c Liquid scintillator - atom density, Density ( g /cm3 )= 0.874  "https://www.crystals.saint-gobain.com/sites/imdf.crystals.com/files/documents/sgc-bc501-501a-519-data-sheet_69711.pdf"
m4    1001. 0.0482
      6000. 0.0398
c Dry Air - atom density, Density ( g /cm3 )= 0.001205
m5    6000. 7.4919E-09
      7014. 3.8987E-05
      7015. 1.4243E-07
      8016. 1.0487E-05
      8017. 3.9948E-09
     18036. 7.8407E-10
     18038. 1.4726E-10
     18040. 2.3208E-07
c Concrete from benchmark documentation (per nuclide definition) - atom desnity, Density ( g /cm3 )= 2.31   
m6    1001. 1.49783E-02
      1002. 1.72270E-06 
      8016. 4.18641E-02
      8017. 1.59471E-05
     11023. 1.23000E-03
     12024. 4.89740E-04
     12025. 6.19982E-05
     12026. 6.82614E-05
     13027. 3.12000E-03
     14028. 1.02368E-02
     14029. 5.20043E-04
     14030. 3.43204E-04
     19039. 3.54381E-04
     19040. 4.44605E-08
     19041. 2.55745E-05
     20040. 4.16846E-03
     20042. 2.78219E-05
     20043. 5.80511E-06
     20044. 8.96994E-05
     20046. 1.72004E-07
     20048. 8.04130E-06
     26054. 8.24154E-05
     26056. 1.29373E-03
     26057. 2.98785E-05
     26058. 3.97622E-06
c -----------------------------------------------------------------------------
c         SOURCE
c -----------------------------------------------------------------------------
c Point isotropic neutron source collimated into an -x cone. 
c Particles are confined to a (+x axis) cone whose half-angle
c is acos(0.99990531) = 0.7788 degrees about the x-axis. 
c Angles are with respect to the vector specified by VEC
c
sdef cell=600 pos=0 0 0 erg=d1 par=1 vec=1 0 0 dir=d2
si2 -1  0.99990531  1          $ histogram for cosine bin limits
sp2  0  0.99995265  0.00004735 $ frac. solid angle for each bin
sb2  0. 0.          1.         $ source bias for each bin
si1 H    0.0
         5.5  6.5  7.5  8.5  9.5 10.5 11.5 12.5 13.5 14.5
        15.5 16.5 17.5 18.5 19.5 20.5 21.5 22.5 23.5 24.5
        25.5 26.5 27.5 28.5 29.5 30.5 31.5 32.5 33.5 34.5
        35.5 36.5 37.5 38.5 39.5 40.5 41.5 42.5 43.5 44.5
        45.5
sp1   0.0      0.
        4.405E-2 4.405E-2 4.423E-2 4.483E-2 4.503E-2
        4.390E-2 4.501E-2 4.633E-2 4.931E-2 4.895E-2
        4.885E-2 4.752E-2 4.977E-2 4.611E-2 4.707E-2
        4.749E-2 4.686E-2 4.653E-2 4.488E-2 4.358E-2
        4.097E-2 3.960E-2 3.473E-2 3.491E-2 3.081E-2
        2.639E-2 2.097E-2 1.875E-2 1.490E-2 1.290E-2
        1.083E-2 7.232E-3 1.337E-2 1.377E-1 3.629E-1
        3.677E-1 1.135E-1 5.063E-3 6.359E-4 1.634E-4
c -----------------------------------------------------------------------------
c         TALLIES
c -----------------------------------------------------------------------------  
c Absolute normalization of results 8.5854E+10 (=2.17*3150000000*4*3.14=peak to continuum from SINBAD html note, peak flux of neutrons in SINBAD html, solid angle (4 pi))    
F14:n 109
FC14 BC 501A Liquid scintilator - on-axis
FM14 8.5854E+10
E14      5  6  7  8  9 10 11 12 13 14
        15 16 17 18 19 20 21 22 23 24
        25 26 27 28 29 30 31 32 33 34
        35 36 37 38 39 40 41 42 43 44
print
c nps 1000000
cut:n j 4.0
prdmp  2J  -1
