TIARA Fe, 68 MeV, 40 cm shield, 40 cm colimator, B. Kos (bor.kos@ijs.si), 2018
c TIARA Fe, 68 MeV, 40 cm shield, 40 cm colimator
c Bor Kos, JSI, July 2018
c BC501A spectra off-axis
100 6  -2.31      -100:-101:-102 :-103: -104: -105 :(-106 110):
                   (-110 -109 -106.3 104.1 105.1 111):
                   (-111  108 -106.3 104.1 105.1 112):
                   (-112  107 -106.3 104.1 105.1) imp:n=1                      $ Concrete structure
101 1  -7.87      -150 151 imp:n=1                                             $ Beam dump
102 1  -7.08      -200 201 202 2 imp:n=1                                       $ Iron filler (density is 10 % lower than ordinary iron - original documentation assumes a mixutre of iron sand and balls)
103 1  -7.87      -201 2 imp:n=1                                               $ Rotary shutter - iron
104 2  -0.928     -202 2  imp:n=1                                              $ Rotary shutter - polyethylene
105 3  -2.6989    -210 : -211 : -212 imp:n=1                                   $ Trolly (aluminium - assumed, not in benchmark documetation)
110 1  -7.87      -1000 imp:n=1                                                $ Iron test shield 
112 3  -2.6989    -238 : -239 : -240 : -241 : -242 imp:n=1                     $ Detector support table - aluminium assumed -  BC 501A Liquid scintilator off-axis 20 cm
113 4  -0.874     -243 imp:n=1                                                 $ BC 501A Liquid scintilator - only dimenssions in benchmark documentation - BC 501A off-axis 20 cm
114 3  -2.6989    -244 : -245 : -246 : -247 : -248 imp:n=1                     $ Detector support table - aluminium assumed -  BC 501A Liquid scintilator off-axis 40 cm
115 4  -0.874     -249 imp:n=1                                                 $ BC 501A Liquid scintilator - only dimenssions in benchmark documentation - BC 501A off-axis 40 cm
500 1  -7.87      -800 2.1 imp:n=1                                             $ Additional iron collimator
600 0             -600 #100 #101 #102 #103 #104 -2.2 imp:n=1                   $ Void
700 5 -0.001205   -600 1000 #500 #100 #105 #112 #113 #114 #115 #110 2.2 imp:n=1  $ Air                                                         
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
c BC 501A Liquid scintilator - off-axis 20 cm
238 box 481.0 -10.0 -6.350 0.0 0.0 -1.000 0.0 -20.0 0.0 40.0 0.0 0.0 $ Detector support table - aluminium assumed
239 rcc 482.0 -11.0 -7.350 0.0 0.0 -52.65 0.99
240 rcc 482.0 -29.0 -7.350 0.0 0.0 -52.65 0.99
241 rcc 520.0 -11.0 -7.350 0.0 0.0 -52.65 0.99
242 rcc 520.0 -29.0 -7.350 0.0 0.0 -52.65 0.99
243 rcc 481.0 -20.0  0.0  12.7 0.0   0.0  6.350 $ Liquid Scintilator BC 501A off-axis 20 cm  
c BC 501A Liquid scintilator - off-axis 40 cm
244 box 481.0 -30.0 -6.350 0.0 0.0 -1.000 0.0 -20.0 0.0 40.0 0.0 0.0 $ Detector support table - aluminium assumed
245 rcc 482.0 -31.0 -7.350 0.0 0.0 -52.65 0.99
246 rcc 482.0 -49.0 -7.350 0.0 0.0 -52.65 0.99
247 rcc 520.0 -31.0 -7.350 0.0 0.0 -52.65 0.99
248 rcc 520.0 -49.0 -7.350 0.0 0.0 -52.65 0.99
249 rcc 481.0 -40.0  0.0  12.7 0.0   0.0  6.350 $ Liquid Scintilator BC 501A off-axis 40 cm  
c Outside world
600 box -130 -252 -315 850 0.0 0.0 0.0 504.0 0.0 0.0 0.0 600.0
c Additional iron colimator
800 box 401.0 -60 -60 40.0 0.0 0.0 0.0 120.0 0.0 0.0 0.0 120.0
c Shield
1000 box 441.0 -60 -60 40.0 0.0 0.0 0.0 120.0 0.0 0.0 0.0 120.0

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
c --- Point isotropic neutron source collimated into an -x cone. 
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
        45.5 46.5 47.5 48.5 49.5 50.5 51.5 52.5 53.5 54.5
        55.5 56.5 57.5 58.5 59.5 60.5 61.5 62.5 63.5 64.5
        65.5 66.5 67.5 68.5 69.5 70.5 71.5 72.5
  sp1   0.0      0.
        2.373E-2 2.373E-2 2.395E-2 2.440E-2 2.508E-2
        2.569E-2 2.533E-2 2.592E-2 2.678E-2 2.714E-2
        2.788E-2 2.795E-2 2.855E-2 2.954E-2 3.100E-2
        3.149E-2 3.334E-2 3.383E-2 3.528E-2 3.624E-2
        3.669E-2 3.841E-2 3.806E-2 3.927E-2 3.845E-2
        3.875E-2 3.857E-2 3.878E-2 3.762E-2 3.702E-2
        3.716E-2 3.656E-2 3.615E-2 3.399E-2 3.345E-2
        3.324E-2 3.340E-2 3.137E-2 3.211E-2 3.103E-2
        3.102E-2 3.160E-2 3.086E-2 3.003E-2 2.856E-2
        2.804E-2 2.656E-2 2.505E-2 2.391E-2 2.177E-2
        1.959E-2 1.604E-2 1.281E-2 1.088E-2 9.010E-3
        7.428E-3 8.095E-3 4.701E-2 2.104E-1 3.614E-1
        2.765E-1 8.202E-2 8.896E-3 1.074E-3 4.013E-4
        4.973E-4 1.324E-4
c -----------------------------------------------------------------------------
c         TALLIES
c -----------------------------------------------------------------------------  
c Absolute normalization of results 1.56368E+11 (=2.61*4770000000*4*3.14=peak to continuum from SINBAD html note, peak flux of neutrons in SINBAD html, solid angle (4 pi))    
F24:n 113
FC24 Neutron flux 20 cm off-axis
FM24 1.56368E+11
E24    6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27
      28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 46 48 50 52 54
      56 58 60 62 64 66 68 70
F34:n 115
FC34 Neutron flux 40 cm off-axis
FM34 1.56368E+11
E34    6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27
      28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 46 48 50 52 54
      56 58 60 62 64 66 68 70
print
c nps 1000000
cut:n j 5.0
c * added by ADVANTG
wwp:n 5.0 j 100 j -1 0 4.008745734e+00
prdmp  2J  -1
