# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 09:26:52 2019

@author: laghi
"""

# import matreader as mr
# import libmanager as lm
# import computational as comp
# import main
# import inputfile as ipt
# import os
# import numpy
# import subprocess
# from subprocess import Popen, CREATE_NEW_CONSOLE
# import Parser as par
# import xlwings as xw
# import atlas as at
# template = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Code\Templates\AtlasTemplate.docx'
# lib = '71c'
# atlas = at.Atlas(template, lib)
# atlas.build(r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Tests\02_Output\Single Libraries\71c\Sphere\Atlas\tmp')
# atlas.save(r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Tests\02_Output\Single Libraries\71c\Sphere\Atlas')
#     #x.xaxis.set_minor_locator(LogLocator(base=10,numticks=15))
# import status
# st = status.Status()
# print(st.run_tree)
# print(st.comparison_tree)
# print(st.single_tree)
# number = 0.00000001455
# # number = round(number,5)
# stringa = '%s' % float('%.5g' % number)
# print(stringa+' test')
# # import warnings

# def fxn():
#     warnings.warn("deprecated", RuntimeWarning)

# # with warnings.catch_warnings():
# #     warnings.simplefilter("ignore")
# #     fxn()
# fxn()
#     #ax.tick_params(which='major', width=1.00)
#     #ax.tick_params(which='major', length=5)
#     #ax.tick_params(which='minor', width=0.75)
#     #ax.tick_params(which='minor', length=2.5)

import pandas as pd

df1 = pd.DataFrame([{'idx': 1, 'value1': 3648, 'value2': 'yep'},
                    {'idx': 'no', 'value1': 468, 'value2': 'yep'},
                    {'idx': 'yes', 'value1': 348, 'value2': 'yep'}])

df2 = pd.DataFrame([{'idx': 1, 'value1': 3648, 'value2': 'yep'},
                    {'idx': 'no', 'value1': 348, 'value2': 'yep'}])

df1.set_index(['idx', 'value1'], inplace=True)
df2.set_index(['idx', 'value1'], inplace=True)

print(df1.index.intersection(df2.index))


# o = { 'temparature': '50', 
#       'logging': {
#         'handlers': {
#           'console': {
#             'formatter': 'simple', 
#             'class': 'logging.StreamHandler', 
#             'stream': 'ext://sys.stdout', 
#             'level': 'DEBUG'
#           }
#         },
#         'loggers': {
#           'simpleExample': {
#             'handlers': ['console'], 
#             'propagate': 'no', 
#             'level': 'INFO'
#           },
#          'root': {
#            'handlers': ['console'], 
#            'level': 'DEBUG'
#          }
#        }, 
#        'version': '1', 
#        'formatters': {
#          'simple': {
#            'datefmt': "'%Y-%m-%d %H:%M:%S'", 
#            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#          }
#        }
#      }, 
#      'treatment': {'second': 5, 'last': 4, 'first': 4},   
#      'treatment_plan': [[4, 5, 4], [4, 5, 4], [5, 5, 5]]
# }

# def gen_dict_extract(key, var):
#     if hasattr(var,'items'):
#         for k, v in var.items():
#             if k == key:
#                 yield v
#             if isinstance(v, dict):
#                 for result in gen_dict_extract(key, v):
#                     yield result
#             elif isinstance(v, list):
#                 for d in v:
#                     for result in gen_dict_extract(key, d):
#                         yield result
# results = gen_dict_extract('treatment_plan', o)
# print(list(results)[0])
# for result in results:
#     print(result)    
    #plt.tight_layout() #This cuts the white space surrounding the image

# app = xw.App(visible=False)

# file = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Code\Templates\Sphere_single.xlsx'
# outfile = 'test.xlsx'
# wb = app.books.open(file)
        
# ws = wb.sheets[1]
# ws.range('D10').value = 131

# app.calculate()
# wb.save(outfile)
# wb.close()
# file = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Tests\01_MCNP_Run\71c\Sphere\Sphere_1001_H-1\Sphere_1001_H-1_m'
# o = output.MCNPoutput(file)

# print(o.get_single_excel_data())
# import MCTAL_READER as mtal

# file = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Tests\01_MCNP_Run\71c\Sphere\Sphere_1001_H-1\Sphere_1001_H-1_m'
# mctal = mtal.MCTAL(file)
# mctal.name
#code = 'mcnp6'
#command = 'name='+'test'+' tasks '+ str(4)
#
#
##Popen('cmd', creationflags=CREATE_NEW_CONSOLE)
#subprocess.run([code,command], creationflags =subprocess.CREATE_NEW_CONSOLE)#,shell=True)
#
#session = main.Session()
###
#inputfile = 'mcardExample4Testing.i'
##outfile = 'mcardExample4Testing.i_test'
##
#c = session.conf.comp_default.set_index('Description').loc['Sphere Leakage Test'].dropna()
#print(c)
#
#
##print(text)#text = []
##with open(inputfile,'r') as infile:
##    for line in infile:21
##        text.append(line)
##        
#
#sub = mr.SubMaterial.from_text(text)
##sub.collapse_zaids()
#        
#materialList = mr.MatCardsList.from_input(inputfile)
#
##for submaterial in material.submaterials:
##    print(submaterial.to_text())
##    print('--------')
#

##
##sub = material.submaterials[0]
##print(sub.header+sub.name)
#
#
# ##
# inputfile = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_JADE\Benchmarks inputs\TypicalMaterials'
# lmanager = lm.LibManager(r'C:\Users\laghi\Documents\MCNP\MCNP_DATA\xsdir_mcnp6.2')
# inp = ipt.InputFile.from_text(inputfile)
# print(inp.matlist.materials)
#
#card = inp.cards['cells'][0]
#density='-100.515'
#card.get_values()
#card.set_d(density)
##card.get_input()
#card.lines = card.card()
#print(card.lines)
#print(inp.cards['cells'][0].lines)
##inp2 = ipt.InputFile.from_text(inputfile)
##
##matcard =  inp.matlist
###mat = matcard.materials[3]
##submat = mat.submaterials[0]
##submat.update_info(lmanager)
##print(submat.to_text())
##mat.update_info(lmanager)
##print(mat.to_text())
#
#df = matcard.get_info()
#df2 = matcard.get_info()
#diff = df['Fraction']-df2['Fraction']
#print(diff)
#
#dic = {'a':1,'b':2}
#print(list(dic.values())[0])
#for elem in submat.elements:
#    for zaid in elem.zaids:
#        print(zaid.name,zaid.additional_info)
#print('\n')    
#for zaid in submat.zaidList:
#    print(zaid.name,zaid.additional_info)
#    
#submat.elements[0].update_zaidinfo(lmanager)
#print('#########################')
#for elem in submat.elements:
#    for zaid in elem.zaids:
#        print(zaid.name,zaid.additional_info)
#print('\n')    
#for zaid in submat.zaidList:
#    print(zaid.name,zaid.additional_info)

#inp.write(outfile)
#newlib = input('Library to use: ')
#inputfile = input('Input to translate: ')
#comp.sphereTestRun(session,newlib)
#print(materialList.to_text())
#
#print('\n\n\n')
#
#materialList.translate('21c',lmanager)
#
#print(materialList.to_text())
#
#print(lmanager.convertZaid('17000','21c'))

# file = r'C:\Users\laghi\Documents\03_dottorato\04_F4E\01_code\Tests\01_MCNP_Run\71c\Sphere\Sphere_1001_H-1\Sphere_1001_H-1_m'
# m = MCTAL(file)
 
# T = m.Read()
 

# txtFileName = 'arguments.txt'
 
# txtFile = open(txtFileName, "w")
 

# for tally in T:
#     tallyLetter = "f"
#     if tally.radiograph:
#         tallyLetter = tally.getDetectorType(True) # Here the argument set to True enables the short version of the tally type
#     if tally.mesh:
#         tallyLetter = tally.getDetectorType(True)
 
#         # name and tally comment:
#         print("# %s%d" % (tallyLetter, tally.tallyNumber) + ' '.join(tally.tallyComment.tolist()).strip(), file=txtFile)
 
#     nCells  = tally.getNbins("f",False)
#     nCora   = tally.getNbins("i",False) # Is set to 1 even when mesh tallies are not present
#     nCorb   = tally.getNbins("j",False) # Is set to 1 even when mesh tallies are not present
#     nCorc   = tally.getNbins("k",False) # Is set to 1 even when mesh tallies are not present
#     nDir    = tally.getNbins("d",False)
#     usrAxis = tally.getAxis("u")
#     nUsr    = tally.getNbins("u",False)
#     segAxis = tally.getAxis("s")
#     nSeg    = tally.getNbins("s",False)
#     nMul    = tally.getNbins("m",False)
#     cosAxis = tally.getAxis("c")
#     nCos    = tally.getNbins("c",False)
#     ergAxis = tally.getAxis("e")
#     nErg    = tally.getNbins("e",False)
#     timAxis = tally.getAxis("t")
#     nTim    = tally.getNbins("t",False)
 
#     for f in range(nCells):
#         for d in range(nDir):
#             for u in range(nUsr):
#                 for s in range(nSeg):
#                     for m in range(nMul):
#                         for c in range(nCos):
#                             for e in range(nErg):
#                                 for t in range(nTim):
#                                     for k in range(nCorc):
#                                         for j in range(nCorb):
#                                             for i in range(nCora):
#                                                 val = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,0)
#                                                 err = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,1)
#                                                 print("%5d %5d %5d %5d %5d %5d %5d %5d %5d %5d %5d %13.5e %13.5e" % (f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1,val,err), file=txtFile)
 

# print("\n\033[1;34mASCII file saved to:\033[1;32m %s\033[0m\n" % (txtFileName))
    
# txtFile.close()
