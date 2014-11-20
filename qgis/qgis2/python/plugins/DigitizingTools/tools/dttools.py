# -*- coding: utf-8 -*-
"""
dttools
`````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-02-25
* copyright          : (C) 2013 by Bernhard Ströbl
* email                : bernhard.stroebl@jena.de

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from PyQt4 import QtGui,  QtCore
from qgis.core import *
from qgis.gui import *
import dtutils

class DtTool():
    '''Abstract class; parent for any Dt tool or button'''
    def __init__(self,  iface,  geometryTypes):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.geometryTypes = []
        self.shapeFileGeometryTypes = []

        # ESRI shapefile does not distinguish between single and multi geometries
        # source of wkbType numbers: http://cosmicproject.org/OGR/ogr_classes.html
        for aGeomType in geometryTypes:
            if aGeomType == 1: # wkbPoint
                self.geometryTypes.append(1)
                self.shapeFileGeometryTypes.append(1)
                self.geometryTypes.append(-2147483647) #wkbPoint25D
                self.shapeFileGeometryTypes.append(-2147483647)
            elif aGeomType == 2: # wkbLineString
                self.geometryTypes.append(2)
                self.shapeFileGeometryTypes.append(2)
                self.geometryTypes.append(-2147483646) #wkbLineString25D
                self.shapeFileGeometryTypes.append(-2147483646)
            elif aGeomType == 3: # wkbPolygon
                self.geometryTypes.append(3)
                self.shapeFileGeometryTypes.append(3)
                self.geometryTypes.append(-2147483645) #wkbPolygon25D
                self.shapeFileGeometryTypes.append(-2147483645)
            elif aGeomType == 4: # wkbMultiPoint
                self.geometryTypes.append(4)
                self.shapeFileGeometryTypes.append(1) # wkbPoint
                self.geometryTypes.append(-2147483644) #wkbMultiPoint25D
                self.shapeFileGeometryTypes.append(-2147483647) #wkbPoint25D
            elif aGeomType == 5: # wkbMultiLineString
                self.geometryTypes.append(5)
                self.shapeFileGeometryTypes.append(2) # wkbLineString
                self.geometryTypes.append(-2147483643) #wkbMultiLineString25D
                self.shapeFileGeometryTypes.append(-2147483646) #wkbLineString25D
            elif aGeomType == 6: # wkbMultiPolygon
                self.geometryTypes.append(6)
                self.shapeFileGeometryTypes.append(3) # wkbPolygon
                self.geometryTypes.append(-2147483642) #wkbMultiPolygon25D
                self.shapeFileGeometryTypes.append(-2147483645) #wkbPolygon25D

    def allowedGeometry(self,  layer):
        '''check if this layer's geometry type is within the list of allowed types'''
        if layer.dataProvider().storageType() == u'ESRI Shapefile': # does not distinguish between single and multi
            result = self.shapeFileGeometryTypes.count(layer.wkbType()) >= 1
        else:
            result = self.geometryTypes.count(layer.wkbType()) == 1

        return result

class DtSingleButton(DtTool):
    '''Abstract class for a single button
    icon [QtGui.QIcon]
    tooltip [str]
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [1, 2, 3],  dtName = None):
        DtTool.__init__(self,  iface,  geometryTypes)

        self.act = QtGui.QAction(icon, tooltip, self.iface.mainWindow())
        self.act.triggered.connect(self.process)

        if dtName != None:
            self.act.setObjectName(dtName)

        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.act)
        self.geometryTypes = geometryTypes

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.act.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                if self.allowedGeometry(layer):
                    self.act.setEnabled(layer.isEditable())
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)

class DtSingleTool(DtSingleButton):
    '''Abstract class for a tool'''
    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2],  crsWarning = True,  dtName = None):
        DtSingleButton.__init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes,  dtName)
        self.tool = None
        self.act.setCheckable(True)
        self.canvas.mapToolSet.connect(self.toolChanged)

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def deactivate(self):
        if self.tool != None:
            self.tool.reset()

        self.reset()
        self.act.setChecked(False)

    def reset(self):
        pass

class DtSingleEditTool(DtSingleTool):
    '''Abstract class for a tool for interactive editing'''
    def __init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes = [0, 1, 2],  crsWarning = True,  dtName = None):
        DtSingleTool.__init__(self, iface,  toolBar,  icon,  tooltip,  geometryTypes,  dtName)
        self.crsWarning = crsWarning
        self.editLayer = None

    def reset(self):
        self.editLayer = None

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        doEnable = False
        layer = self.iface.activeLayer()

        if layer <> None:
            if layer.type() == 0: #Only for vector layers.
                if self.allowedGeometry(layer):
                    doEnable = layer.isEditable()
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)

        if self.editLayer != None: # we have a current edit session, activeLayer may have changed or editing status of self.editLayer
            try:
                self.editLayer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
            except:
                pass
            try:
                self.editLayer.editingStopped.disconnect(self.enable) # when it becomes active layer again
            except:
                pass

            self.tool.reset()
            self.reset()

        if not doEnable:
            self.deactivate()

        if doEnable and self.crsWarning:
            layerCRSSrsid = layer.crs().srsid()
            renderer = self.canvas.mapRenderer()
            projectCRSSrsid = renderer.destinationCrs().srsid()

            if layerCRSSrsid != projectCRSSrsid:
                self.iface.messageBar().pushMessage("DigitizingTools",  self.act.toolTip() + " " +
                    QtGui.QApplication.translate("DigitizingTools", "is disabled because layer CRS and project CRS do not match!" ),
                    level=QgsMessageBar.WARNING)
                doEnable = False

        self.act.setEnabled(doEnable)

class DtDualTool(DtTool):
    '''Abstract class for a tool with interactive and batch mode
    icon [QtGui.QIcon] for interactive mode
    tooltip [str] for interactive mode
    iconBatch [QtGui.QIcon] for batch mode
    tooltipBatch [str] for batch mode
    geometryTypes [array:integer] 0=point, 1=line, 2=polygon'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  dtName = None):
        DtTool.__init__(self,  iface,  geometryTypes)

        self.iface.currentLayerChanged.connect(self.enable)
        self.canvas.mapToolSet.connect(self.toolChanged)
        #create button
        self.button = QtGui.QToolButton(toolBar)
        self.button.clicked.connect(self.runSlot)
        self.button.toggled.connect(self.hasBeenToggled)
        #create menu
        self.menu = QtGui.QMenu(toolBar)

        if dtName != None:
            self.menu.setObjectName(dtName)

        self.menu.triggered.connect(self.menuTriggered)
        self.button.setMenu(self.menu)
        self.button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # create actions
        self.act = QtGui.QAction(icon, tooltip,  self.iface.mainWindow())

        if dtName != None:
            self.act.setObjectName(dtName + "Action")

        self.act.setToolTip(tooltip)
        self.act_batch = QtGui.QAction(iconBatch, tooltipBatch,  self.iface.mainWindow())

        if dtName != None:
            self.act_batch.setObjectName(dtName + "BatchAction")

        self.act_batch.setToolTip(tooltipBatch)
        self.menu.addAction(self.act)
        self.menu.addAction(self.act_batch)
        # set the interactive action as default action, user needs to click the button to activate it
        self.button.setIcon(self.act.icon())
        self.button.setToolTip(self.act.toolTip())
        self.button.setCheckable(True)
        self.batchMode = False
        # add button to toolBar
        toolBar.addWidget(self.button)
        self.geometryTypes = geometryTypes
        # run the enable slot
        self.enable()

    def menuTriggered(self,  thisAction):
        if thisAction == self.act:
            self.batchMode = False
            self.button.setCheckable(True)
            if not self.button.isChecked():
                self.button.toggle()
        else:
            self.batchMode = True
            if self.button.isCheckable():
                if self.button.isChecked():
                    self.button.toggle()
                self.button.setCheckable(False)

            self.runSlot(False)

        self.button.setIcon(thisAction.icon())
        self.button.setToolTip(thisAction.toolTip())

    def toolChanged(self,  thisTool):
        if thisTool != self.tool:
            self.deactivate()

    def hasBeenToggled(self,  isChecked):
        raise NotImplementedError("Should have implemented hasBeenToggled")

    def deactivate(self):
        if self.button.isChecked():
            self.button.toggle()

    def runSlot(self,  isChecked):
        if self.batchMode:
            layer = self.iface.activeLayer()

            if layer.selectedFeatureCount() > 0:
                self.process()
        else:
            if not isChecked:
                self.button.toggle()

    def process(self):
        raise NotImplementedError("Should have implemented process")

    def enable(self):
       # Disable the Button by default
        self.button.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer <> None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:

                # only for certain layers
                if self.allowedGeometry(layer):
                    if not layer.isEditable():
                        self.deactivate()

                    self.button.setEnabled(layer.isEditable())

                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)
                else:
                    self.deactivate()

class DtDualToolSelectFeature(DtDualTool):
    '''Abstract class for a DtDualToo which uses the DtSelectFeatureTool for interactive mode'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  dtName = None):
        DtDualTool.__init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes,  dtName)
        self.tool = DtSelectFeatureTool(self.canvas)

    def featureSelectedSlot(self,  fids):
        if len(fids) >0:
            self.process()

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.featureSelected.disconnect(self.featureSelectedSlot)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.featureSelected.connect(self.featureSelectedSlot)
        else:
            self.canvas.unsetMapTool(self.tool)

class DtDualToolSelectVertex(DtDualTool):
    '''Abstract class for a DtDualTool which uses the DtSelectVertexTool for interactive mode
    numVertices [integer] nnumber of vertices to be snapped until vertexFound signal is emitted'''

    def __init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes = [1, 2, 3],  numVertices = 1,  dtName = None):
        DtDualTool.__init__(self, iface,  toolBar,  icon,  tooltip,  iconBatch,  tooltipBatch,  geometryTypes,  dtName)
        self.tool = DtSelectVertexTool(self.canvas,  numVertices)

    def hasBeenToggled(self,  isChecked):
        try:
            self.tool.vertexFound.disconnect(self.vertexSnapped)
            # disconnect if it was already connected, so slot gets called only once!
        except:
            pass

        if isChecked:
            self.canvas.setMapTool(self.tool)
            self.tool.vertexFound.connect(self.vertexSnapped)
        else:
            self.canvas.unsetMapTool(self.tool)

    def vertexSnapped(self,  snapResult):
        raise NotImplementedError("Should have implemented vertexSnapped")

class DtMapTool(QgsMapTool):
    '''abstract subclass of QgsMapTool'''
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas

        #custom cursor
        self.cursor = QtGui.QCursor(QtGui.QPixmap(["16 16 3 1",
                                        "      c None",
                                        ".     c #FF0000",
                                        "+     c #FFFFFF",
                                        "                ",
                                        "       +.+      ",
                                        "      ++.++     ",
                                        "     +.....+    ",
                                        "    +.     .+   ",
                                        "   +.   .   .+  ",
                                        "  +.    .    .+ ",
                                        " ++.    .    .++",
                                        " ... ...+... ...",
                                        " ++.    .    .++",
                                        "  +.    .    .+ ",
                                        "   +.   .   .+  ",
                                        "   ++.     .+   ",
                                        "    ++.....+    ",
                                        "      ++.++     ",
                                        "       +.+      "]))

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.reset()

    def reset(self,  emitSignal = False):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

class DtSelectFeatureTool(DtMapTool):
    featureSelected = QtCore.pyqtSignal(list)

    def __init__(self, canvas):
        DtMapTool.__init__(self, canvas)

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer <> None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)

            #we need a snapper, so we use the MapCanvas snapper
            snapper = QgsMapCanvasSnapper(self.canvas)
            (hasSnapSettings,  snapEnabled,  snapType,  snapUnits,  snapTolerance, avoidInters) = QgsProject.instance().snapSettingsForLayer(layer.id())

            if not hasSnapSettings:
                dtutils.showSnapSettingsWarning()
            elif not snapEnabled:
                dtutils.showSnapSettingsWarning()
            else:
                #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
                (retval,result) = snapper.snapToCurrentLayer(startingPoint, snapType)

                if result == []:
                    dtutils.showSnapSettingsWarning()
                else:
                    #mehrere fids
                    fids = []
                    for i in range(len(result)):
                        fid = result[i].snappedAtGeometry # QgsFeatureId of the snapped geometry
                        fids.append(fid)

                    layer.removeSelection()
                    layer.setSelectedFeatures(fids)
                    self.featureSelected.emit(fids)

class DtSelectVertexTool(DtMapTool):
    '''select and mark numVertices vertices in the active layer'''
    vertexFound = QtCore.pyqtSignal(list)

    def __init__(self, canvas,  numVertices = 1):
        DtMapTool.__init__(self,canvas)

        # desired number of marked vertex until signal
        self.numVertices = numVertices
        # number of marked vertex
        self.count = 0
        # arrays to hold markers and vertex points
        self.markers = []
        self.points = []
        self.fids = []

    def canvasReleaseEvent(self,event):
        if self.count < self.numVertices: #not yet enough
            #Get the click
            x = event.pos().x()
            y = event.pos().y()

            layer = self.canvas.currentLayer()

            if layer <> None:
                #the clicked point is our starting point
                startingPoint = QtCore.QPoint(x,y)

                #we need a snapper, so we use the MapCanvas snapper
                snapper = QgsMapCanvasSnapper(self.canvas)

                #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
                (retval,result) = snapper.snapToCurrentLayer (startingPoint,QgsSnapper.SnapToVertex)

                if result == []:
                    #warn about missing snapping tolerance if appropriate
                    #self.showSettingsWarning()
                    pass

                if result <> []:
                    #mark the vertex
                    p = QgsPoint()
                    p.setX( result[0].snappedVertex.x() )
                    p.setY( result[0].snappedVertex.y() )
                    m = QgsVertexMarker(self.canvas)
                    m.setIconType(1)

                    if self.count == 0:
                        m.setColor(QtGui.QColor(255,0,0))
                    else:
                        m.setColor(QtGui.QColor(0, 0, 255))

                    m.setIconSize(12)
                    m.setPenWidth (3)
                    m.setCenter(p)
                    self.points.append(p)
                    self.markers.append(m)
                    fid = result[0].snappedAtGeometry # QgsFeatureId of the snapped geometry
                    self.fids.append(fid)
                    self.count += 1

                    if self.count == self.numVertices:
                        self.vertexFound.emit([self.points,  self.markers,  self.fids])
                        #self.emit(SIGNAL("vertexFound(PyQt_PyObject)"), [self.points,  self.markers])

    def showSettingsWarning(self):
        m = QgsMessageViewer()
        m.setWindowTitle("Snap tolerance")
        m.setCheckBoxText("Don't show this message again")
        m.setCheckBoxVisible(True)
        m.setCheckBoxQSettingsLabel(settingsLabel)
        m.setMessageAsHtml( "<p>Could not snap vertex.</p><p>Have you set the tolerance in Settings > Project Properties > General?</p>")
        m.showMessage()

    def reset(self,  emitSignal = False):
        for m in self.markers:
            self.canvas.scene().removeItem(m)

        self.markers = []
        self.points = []
        self.fids = []
        self.count = 0

class DtSelectSegmentTool(DtMapTool):
    segmentFound = QtCore.pyqtSignal(list)

    def __init__(self, canvas):
        DtMapTool.__init__(self,canvas)
        self.rb1 = QgsRubberBand(self.canvas,  False)

    def canvasReleaseEvent(self,event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer <> None:
            #the clicked point is our starting point
            startingPoint = QtCore.QPoint(x,y)

            #we need a snapper, so we use the MapCanvas snapper
            snapper = QgsMapCanvasSnapper(self.canvas)

            #we snap to the current layer (we don't have exclude points and use the tolerances from the qgis properties)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint,QgsSnapper.SnapToSegment)

            #if we have found a linesegment
            if result <> []:
                # we like to mark the segment that is choosen, so we need a rubberband
                self.rb1.reset()
                color = QtGui.QColor(255,0,0)
                self.rb1.setColor(color)
                self.rb1.setWidth(2)
                self.rb1.addPoint(result[0].beforeVertex)
                self.rb1.addPoint(result[0].afterVertex)
                self.rb1.show()
                self.segmentFound.emit([self.rb1.getPoint(0, 0),  self.rb1.getPoint(0, 1),  self.rb1])
            else:
                pass

    def showSettingsWarning(self):
        m = QgsMessageViewer()
        m.setWindowTitle("Snap tolerance")
        m.setCheckBoxText("Don't show this message again")
        m.setCheckBoxVisible(True)
        m.setCheckBoxQSettingsLabel(settingsLabel)
        m.setMessageAsHtml( "<p>Could not snap segment.</p><p>Have you set the tolerance in Settings > Project Properties > General?</p>")
        m.showMessage()

    def reset(self,  emitSignal = False):
        self.rb1.reset()
