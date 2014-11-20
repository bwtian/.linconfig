# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qgis2threejs
                                 A QGIS plugin
 export terrain data, map canvas image and vector data to web browser
                             -------------------
        begin                : 2014-04-03
        copyright            : (C) 2014 Minoru Akagi
        email                : akaginch@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#from PyQt4.QtCore import qDebug
from PyQt4.QtGui import QColor, QMessageBox
from qgis.core import QGis, QgsMessageLog
import random
from stylewidget import HeightWidgetFunc, ColorWidgetFunc, FieldValueWidgetFunc, TransparencyWidgetFunc, LabelHeightWidgetFunc

debug_mode = 0

colorNames = []

class DEMPropertyReader:
  def __init__(self, properties=None):
    self.properties = properties

  def width(self):
    if self.properties["comboBox_DEMLayer"]:
      return self.properties["dem_Width"]
    return 2

  def height(self):
    if self.properties["comboBox_DEMLayer"]:
      return self.properties["dem_Height"]
    return 2

class VectorPropertyReader:
  def __init__(self, objectTypeManager, layer, properties=None):
    self.properties = properties
    if properties is None:
      self.properties = {}
      self.visible = False
    else:
      self.properties = properties
      self.item_index = properties["comboBox_ObjectType"]
      typeitem = objectTypeManager.objectTypeItem(layer.geometryType(), self.item_index)  #
      self.type_name = typeitem.name
      self.mod_index = typeitem.mod_index
      self.type_index = typeitem.type_index #
      self.visible = properties["visible"]

  def color(self, layer=None, f=None):
    global colorNames   #TODO: add function to material manager
    vals = self.properties["colorWidget"]
    if vals[0] == ColorWidgetFunc.RGB:
      return vals[2]
    elif vals[0] == ColorWidgetFunc.RANDOM or layer is None or f is None:
      if len(colorNames) == 0:
        colorNames = QColor.colorNames()
      colorName = random.choice(colorNames)
      colorNames.remove(colorName)
      return QColor(colorName).name().replace("#", "0x")
    symbol = layer.rendererV2().symbolForFeature(f)
    if symbol is None:
      QgsMessageLog.logMessage(u'Symbol for feature is not found. Once try to show layer: {0}'.format(layer.name()), "Qgis2threejs")
      symbol = layer.rendererV2().symbols()[0]
    return symbol.color().name().replace("#", "0x")

  def transparency(self, layer=None, f=None):
    vals = self.properties["transparencyWidget"]
    if vals[0] == TransparencyWidgetFunc.VALUE:
      try:
        return int(vals[2])
      except:
        return 0

    if vals[0] == TransparencyWidgetFunc.LAYER:
      return layer.layerTransparency()

    symbol = layer.rendererV2().symbolForFeature(f)
    if symbol is None:
      QgsMessageLog.logMessage(u'Symbol for feature is not found. Once try to show layer: {0}'.format(layer.name()), "Qgis2threejs")
      symbol = layer.rendererV2().symbols()[0]
    return int((1.0 - symbol.alpha()) * 100)

  def useZ(self):
    return self.properties["heightWidget"][0] == HeightWidgetFunc.RELATIVE_TO_Z

  def isHeightRelativeToSurface(self):
    return self.properties["heightWidget"][0] == HeightWidgetFunc.RELATIVE

  def relativeHeight(self, f=None):
    lst = self.properties["heightWidget"]
    if lst[0] in [HeightWidgetFunc.RELATIVE, HeightWidgetFunc.ABSOLUTE, HeightWidgetFunc.RELATIVE_TO_Z] or f is None:
      return float(lst[2])
    # attribute value + addend
    return float(f.attribute(lst[1])) + float(lst[2])

  def values(self, f=None):
    vals = []
    for i in range(32):   # big number for style count
      p = "styleWidget" + str(i)
      if p in self.properties:
        lst = self.properties[p]
        if len(lst) == 0:
          break
        if lst[0] == FieldValueWidgetFunc.ABSOLUTE or f is None:
          vals.append(lst[2])
        else:
          # attribute value * multiplier
          vals.append(str(float(f.attribute(lst[1])) * float(lst[2])))
      else:
        break
    return vals
