# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mmqgis_attribute_join_form.ui'
#
# Created: Fri Dec 20 08:54:18 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_mmqgis_attribute_join_form(object):
    def setupUi(self, mmqgis_attribute_join_form):
        mmqgis_attribute_join_form.setObjectName(_fromUtf8("mmqgis_attribute_join_form"))
        mmqgis_attribute_join_form.setWindowModality(QtCore.Qt.ApplicationModal)
        mmqgis_attribute_join_form.setEnabled(True)
        mmqgis_attribute_join_form.resize(378, 339)
        mmqgis_attribute_join_form.setMouseTracking(False)
        self.buttonBox = QtGui.QDialogButtonBox(mmqgis_attribute_join_form)
        self.buttonBox.setGeometry(QtCore.QRect(110, 300, 160, 26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label.setGeometry(QtCore.QRect(10, 180, 261, 22))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_3 = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label_3.setGeometry(QtCore.QRect(200, 120, 161, 22))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.outfilename = QtGui.QLineEdit(mmqgis_attribute_join_form)
        self.outfilename.setGeometry(QtCore.QRect(10, 200, 261, 21))
        self.outfilename.setReadOnly(False)
        self.outfilename.setObjectName(_fromUtf8("outfilename"))
        self.browse_outfile = QtGui.QPushButton(mmqgis_attribute_join_form)
        self.browse_outfile.setGeometry(QtCore.QRect(280, 200, 79, 26))
        self.browse_outfile.setObjectName(_fromUtf8("browse_outfile"))
        self.joinlayerattribute = QtGui.QComboBox(mmqgis_attribute_join_form)
        self.joinlayerattribute.setGeometry(QtCore.QRect(200, 140, 161, 27))
        self.joinlayerattribute.setObjectName(_fromUtf8("joinlayerattribute"))
        self.joinlayer = QtGui.QComboBox(mmqgis_attribute_join_form)
        self.joinlayer.setGeometry(QtCore.QRect(10, 140, 161, 27))
        self.joinlayer.setObjectName(_fromUtf8("joinlayer"))
        self.label_4 = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label_4.setGeometry(QtCore.QRect(10, 120, 111, 22))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_2 = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 141, 22))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.infilename = QtGui.QLineEdit(mmqgis_attribute_join_form)
        self.infilename.setGeometry(QtCore.QRect(10, 30, 261, 21))
        self.infilename.setText(_fromUtf8(""))
        self.infilename.setReadOnly(False)
        self.infilename.setObjectName(_fromUtf8("infilename"))
        self.browse_infile = QtGui.QPushButton(mmqgis_attribute_join_form)
        self.browse_infile.setGeometry(QtCore.QRect(280, 30, 79, 26))
        self.browse_infile.setObjectName(_fromUtf8("browse_infile"))
        self.label_5 = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label_5.setGeometry(QtCore.QRect(10, 240, 261, 22))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.notfoundfilename = QtGui.QLineEdit(mmqgis_attribute_join_form)
        self.notfoundfilename.setGeometry(QtCore.QRect(10, 260, 261, 21))
        self.notfoundfilename.setReadOnly(False)
        self.notfoundfilename.setObjectName(_fromUtf8("notfoundfilename"))
        self.browse_notfound = QtGui.QPushButton(mmqgis_attribute_join_form)
        self.browse_notfound.setGeometry(QtCore.QRect(280, 260, 79, 26))
        self.browse_notfound.setObjectName(_fromUtf8("browse_notfound"))
        self.csvfilefield = QtGui.QComboBox(mmqgis_attribute_join_form)
        self.csvfilefield.setGeometry(QtCore.QRect(100, 80, 171, 27))
        self.csvfilefield.setObjectName(_fromUtf8("csvfilefield"))
        self.label_6 = QtGui.QLabel(mmqgis_attribute_join_form)
        self.label_6.setGeometry(QtCore.QRect(100, 60, 117, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))

        self.retranslateUi(mmqgis_attribute_join_form)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), mmqgis_attribute_join_form.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), mmqgis_attribute_join_form.reject)
        QtCore.QMetaObject.connectSlotsByName(mmqgis_attribute_join_form)

    def retranslateUi(self, mmqgis_attribute_join_form):
        mmqgis_attribute_join_form.setWindowTitle(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Join by Attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Output Shapefile", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Join Layer Attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.outfilename.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "join.shp", None, QtGui.QApplication.UnicodeUTF8))
        self.browse_outfile.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Join Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Input CSV File (UTF-8)", None, QtGui.QApplication.UnicodeUTF8))
        self.browse_infile.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Not Found CSV Output List", None, QtGui.QApplication.UnicodeUTF8))
        self.notfoundfilename.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "unjoined.csv", None, QtGui.QApplication.UnicodeUTF8))
        self.browse_notfound.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("mmqgis_attribute_join_form", "CSV File Field", None, QtGui.QApplication.UnicodeUTF8))

