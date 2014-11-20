# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qgis2threejs
                                 A QGIS plugin
 export terrain data, map canvas image and vector data to web browser
                             -------------------
        begin                : 2014-01-11
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
from qgis.core import QGis
from Qgis2threejs.stylewidget import StyleWidget

def geometryType():
  return QGis.Point

def objectTypeNames():
  return ["Sphere", "Cylinder", "Cube", "Cone"]

def setupForm(ppage, mapTo3d, layer, type_index=0):
  defaultValue = 0.5 / mapTo3d.multiplier
  defaultValueZ = 0.5 / mapTo3d.multiplierZ

  ppage.colorWidget.setup()
  ppage.transparencyWidget.setup()

  if type_index == 0:  # Sphere
    ppage.styleWidgets[0].setup(StyleWidget.FIELD_VALUE, "Radius", "Value", defaultValue, layer)
    styleCount = 1
  elif type_index in [1, 3]: # Cylinder, Cone
    ppage.styleWidgets[0].setup(StyleWidget.FIELD_VALUE, "Radius", "Value", defaultValue, layer)
    ppage.styleWidgets[1].setup(StyleWidget.FIELD_VALUE, "Height", "Value", defaultValueZ, layer)
    styleCount = 2
  elif type_index == 2:  # Cube
    ppage.styleWidgets[0].setup(StyleWidget.FIELD_VALUE, "Width", "Value", defaultValue, layer)
    ppage.styleWidgets[1].setup(StyleWidget.FIELD_VALUE, "Depth", "Value", defaultValue, layer)
    ppage.styleWidgets[2].setup(StyleWidget.FIELD_VALUE, "Height", "Value", defaultValueZ, layer)
    styleCount = 3
  else:
    styleCount = 0
  for i in range(styleCount, ppage.STYLE_MAX_COUNT):
    ppage.styleWidgets[i].hide()

def write(writer, feat):
  mat = writer.materialManager.getMeshLambertIndex(feat.color(), feat.transparency())
  mapTo3d = writer.context.mapTo3d
  vals = feat.propValues()
  pts = feat.pointsAsList()
  if feat.prop.type_index == 0:  # Sphere
    r = float(vals[0]) * mapTo3d.multiplier
    if r != 0:
      writer.writeFeature({"m": mat, "pts": pts,"r": r})
  elif feat.prop.type_index in [1, 3]: # Cylinder, Cone
    rb = float(vals[0]) * mapTo3d.multiplier
    rt = 0 if feat.prop.type_index == 3 else rb
    h = float(vals[1]) * mapTo3d.multiplierZ
    for pt in pts:
      pt[2] += h / 2
    writer.writeFeature({"m": mat, "pts": pts, "rt": rt, "rb": rb, "h": h, "rotateX": 90})
  elif feat.prop.type_index == 2:  # Cube
    w = float(vals[0]) * mapTo3d.multiplier
    d = float(vals[1]) * mapTo3d.multiplier
    h = float(vals[2]) * mapTo3d.multiplierZ
    for pt in pts:
      pt[2] += h / 2
    writer.writeFeature({"m": mat, "pts": pts, "w": w, "d": d, "h": h, "rotateX": 90})
