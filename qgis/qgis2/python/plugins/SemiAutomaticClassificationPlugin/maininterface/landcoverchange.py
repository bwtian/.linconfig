# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

"""

import os
import numpy as np
import itertools
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg


class LandCoverChange:

	def __init__(self):
		pass
	
	# reference classification name
	def classificationReferenceLayerName(self):
		cfg.refClssfctnNm = str(cfg.ui.classification_reference_name_combo.currentText())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification name: " + str(cfg.refClssfctnNm))
	
	# start land cover change calculation
	def landCoverChange(self):
		# register drivers
		gdal.AllRegister()
		# input
		refRstr = cfg.utls.selectLayerbyName(cfg.refClssfctnNm, "Yes")
		try:
			refRstrSrc = refRstr.source()
			rstrCheck = "Yes"
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
		newRstr = cfg.utls.selectLayerbyName(cfg.newClssfctnNm, "Yes")
		try:
			newRstrSrc = newRstr.source()
			rstrCheck = "Yes"
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
		# check if numpy is updated
		try:
			np.count_nonzero([1,1,0])
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
			cfg.mx.msgErr26()
			return "No"
		if rstrCheck == "No":
			cfg.mx.msg4()
		else:
			# open input with GDAL
			refRstrDt = gdal.Open(refRstrSrc, GA_ReadOnly)
			newRstrDt = gdal.Open(newRstrSrc, GA_ReadOnly)
			# number of x pixels
			refRstrCols = refRstrDt.RasterXSize
			newRstrCols = newRstrDt.RasterXSize
			# number of y pixels
			refRstrRows = refRstrDt.RasterYSize
			newRstrRows = newRstrDt.RasterYSize
			# check projections
			refRstrProj = refRstrDt.GetProjection()
			newRstrProj = newRstrDt.GetProjection()
			# pixel size and origin
			refRstGeoTrnsf = refRstrDt.GetGeoTransform()
			newRstGeoTrnsf = newRstrDt.GetGeoTransform()
			refRstPxlXSz = abs(refRstGeoTrnsf[1])
			newRstPxlXSz = abs(newRstGeoTrnsf[1])
			refRstPxlYSz = abs(refRstGeoTrnsf[5])
			newRstPxlYSz = abs(newRstGeoTrnsf[5])
			if refRstrProj != newRstrProj:
				cfg.mx.msg9()
			else:
				rstrOut = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save land cover change raster output"), "", "*.tif")
				if len(rstrOut) > 0:
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					chngRstPath = rstrOut
					chngRstPath = chngRstPath.replace('\\', '/')
					chngRstPath = chngRstPath.replace('//', '/')
					tblOut = os.path.dirname(chngRstPath) + "/" + os.path.basename(chngRstPath)
					tblOut = os.path.splitext(tblOut)[0] + ".csv"
					if unicode(chngRstPath).endswith(".tif"):
						pass
					else:
						chngRstPath = chngRstPath + ".tif"
					qApp.processEvents()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "change raster output: " + str(cfg.clssPth))	
					if str(refRstPxlXSz) != str(newRstPxlXSz) or str(refRstPxlYSz) != str(newRstPxlYSz):
						cfg.mx.msgWar5()
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " land cover change")
					# get band
					refRstrBnd = refRstrDt.GetRasterBand(1)
					newRstrBnd = newRstrDt.GetRasterBand(1)
					# calculate raster offset
					xOffst = int((refRstGeoTrnsf[0] - newRstGeoTrnsf[0]) / refRstPxlXSz) 
					yOffst = int((refRstGeoTrnsf[3] - newRstGeoTrnsf[3]) / refRstPxlYSz)
					# calculate overlapping origins, rows and columns
					if xOffst <= 0:
						refRstrXOrig = abs(xOffst)
						newRstrXOrig = 0
						if refRstrCols + xOffst < newRstrCols:
							ovlpCols = refRstrCols +  xOffst
						elif refRstrCols + xOffst >= newRstrCols:
							ovlpCols = newRstrCols
					if xOffst > 0:
						refRstrXOrig = 0
						newRstrXOrig = xOffst
						if refRstrCols < newRstrCols - xOffst:
							ovlpCols = refRstrCols
						elif refRstrCols >= newRstrCols - xOffst:
							ovlpCols = newRstrCols - xOffst
					if yOffst >= 0:
						refRstrYOrig = yOffst
						newRstrYOrig = 0
						if refRstrRows - yOffst <= newRstrRows:
							ovlpRows = refRstrRows - yOffst
						elif refRstrRows - yOffst > newRstrRows:
							ovlpRows = newRstrRows
					if yOffst < 0:
						refRstrYOrig = 0
						newRstrYOrig = abs(yOffst)
						if refRstrRows < newRstrRows + yOffst:
							ovlpRows = refRstrRows
						elif refRstrRows >= newRstrRows + yOffst:
							ovlpRows = newRstrRows + yOffst
					blockSizeX = cfg.utls.calculateBlockSize(5)
					blockSizeY = blockSizeX
					# reference raster range blocks
					lX = range(refRstrXOrig, refRstrXOrig + ovlpCols, blockSizeX)
					lY = range(refRstrYOrig, refRstrYOrig + ovlpRows, blockSizeY)
					# new raster range blocks
					nlX = range(newRstrXOrig, newRstrXOrig + ovlpCols, blockSizeX)
					nlY = range(newRstrYOrig, newRstrYOrig + ovlpRows, blockSizeY)
					cfg.uiUtls.updateBar(20)
					# set initial value for progress bar
					progresStep = 60 / (len(lX) * len(lY))
					progressStart = 20 - progresStep
					# block size
					if blockSizeX > ovlpCols:
						blockSizeX = ovlpCols
					if blockSizeY > ovlpRows:
						blockSizeY = ovlpRows
					# create output raster
					oC = []
					oC.append(rstrOut)
					oCR = cfg.utls.createRasterFromReference(refRstrDt, 1, oC, cfg.NoDataVal, "GTiff", GDT_Int32)
					cmbntns = []
					valSum = []
					n = 1
					# process
					for y in lY:
						bSY = blockSizeY
						for x in lX:
							if cfg.actionCheck == "Yes":
								progress = progressStart + n * progresStep
								cfg.uiUtls.updateBar(progress)
								bSX = blockSizeX
								if bSY + y > refRstrYOrig + ovlpRows:
									bSY = ovlpRows - y
								if x + bSX > refRstrXOrig + ovlpCols:
									bSX = ovlpCols - x
								# combinations of classes
								refRstrArr = refRstrBnd.ReadAsArray(x, y, bSX, bSY)
								newRstrArr = newRstrBnd.ReadAsArray(nlX[lX.index(x)], nlY[lY.index(y)], bSX, bSY)
								refRstrVal = np.unique(refRstrArr).tolist()
								newRstrVal = np.unique(newRstrArr).tolist()
								cmb = list(itertools.product(refRstrVal, newRstrVal))
								for i in cmb:
									if i not in cmbntns:
										if cfg.unchngMaskCheck is False:
											if str(i[0]) != str(i[1]):
												cmbntns.extend([i])
												valSum.append(0)
										elif cfg.unchngMaskCheck is True:
											cmbntns.extend([i])
											valSum.append(0)
								val = 1
								changeArray = None
								for i in cmbntns:
									# change conditions
									cmbsArr = val * np.logical_and(refRstrArr == i[0], newRstrArr == i[1])
									sum = np.count_nonzero(cmbsArr)
									# change raster
									if changeArray == None:
										changeArray = cmbsArr
									else:
										e = np.ma.masked_equal(cmbsArr, 0)
										changeArray =  e.mask * changeArray + cmbsArr
										e = None
									valSum[val - 1] = valSum[val - 1] + sum
									cfg.utls.writeArrayBlock(oCR[0], 1, changeArray, x, y, cfg.NoDataVal)
									val = val + 1
							n = n + 1
					cfg.uiUtls.updateBar(80)
					# save combination to table
					l = open(tblOut, 'w')
					t = str(QApplication.translate("semiautomaticclassificationplugin", 'ChangeCode')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'ReferenceClass')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'NewClass')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + str("\n"))
					l.write(t)
					val = 1
					for i in cmbntns:
						t = str(val) + "	" + str(i[0]) + "	" + str(i[1]) + "	" + str(valSum[val - 1]) + str("\n")
						l.write(t)
						val = val + 1
					l.close()
					# close bands
					refRstrBnd = None
					newRstrBnd = None
					oCR[0] = None
					refRstrDt = None
					newRstrDt = None
					# add raster to layers
					cfg.iface.addRasterLayer(unicode(rstrOut), unicode(os.path.basename(rstrOut)))
					rstr = cfg.utls.selectLayerbyName(unicode(os.path.basename(rstrOut)), "Yes")
					cfg.utls.rasterSymbolGeneric(rstr)
					# open csv
					try:
						f = open(tblOut)
						if os.path.isfile(tblOut):
							changeTxt = f.read()
							cfg.ui.change_textBrowser.setText(str(changeTxt))
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.uiUtls.updateBar(100)
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
						
	# state of checkbox for mask unchanged
	def maskUnchangedCheckbox(self):
		if cfg.ui.mask_unchanged_checkBox.isChecked() is True:
			cfg.unchngMaskCheck = True
		else:
			cfg.unchngMaskCheck = False
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.unchngMaskCheck))
	
	# new classification name
	def newClassificationLayerName(self):
		cfg.newClssfctnNm = str(cfg.ui.new_classification_name_combo.currentText())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification name: " + str(cfg.newClssfctnNm))
	
	# refresh reference classification name
	def refreshClassificationReferenceLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.classification_reference_name_combo.clear()
		# reference classification name
		cfg.refClssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.classification_reference_layer_combo(l.name())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification layers refreshed")
	
	# refresh new classification name
	def refreshNewClassificationLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.new_classification_name_combo.clear()
		# new classification name
		cfg.newClssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.new_classification_layer_combo(l.name())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "new classification layers refreshed")