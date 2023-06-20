# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GOMap
                                 A QGIS plugin
 For examining renewable energy systems deployment opportunities in cities.
                              -------------------
        begin                : 2016-12-07
        git sha              : $Format:%H$
        copyright            : (C) 2022 by ESRU, University of Strathclyde
        email                : esru@strath.ac.uk
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

# Initialize Qt resources from file resources.py
from ..resources import *
# Import required modules
import csv, glob, os, processing, subprocess, sys
import xlrd, xlwt
from functools import partial
from math import ceil, floor, sin, asin, cos, acos, tan, radians, degrees
from statistics import mean
from qgis.core import QgsProject, QgsField, QgsLayerTreeLayer, QgsVectorLayer, QgsVectorFileWriter, QgsMapLayer, QgsFeature, QgsGeometry, QgsRectangle, Qgis, \
QgsWkbTypes, QgsProcessingFeedback, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeatureRequest, QgsProcessingFeatureSourceDefinition
from qgis.utils import iface
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, Qt
from qgis.PyQt.QtWidgets import QApplication, QFileDialog, QTableWidgetItem

# Import resources from dockwidgets
from ..dockwidgets.area_statistics_dockwidget import area_statistics
from ..dockwidgets.ahp_help_dockwidget import ahp_help

from .General import General
from .TechnologyFunctions import TechFunctions


class Statistics:
    def __init__(self,
                 land_availability_dockwidget,
                 ahp_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.area_statistics_dockwidget = area_statistics()
        self.ahp_dockwidget = ahp_dockwidget
        self.ahp_help_dockwidget = ahp_help()
        #self.ahp_dockwidget = ahp()

        # Reference General class
        self.General = General(None)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')

        # Hide CR warning message
        self.ahp_dockwidget.warningCR_label.hide()



#-------------------------------"Configure" Area statistics-------------------------------------------------------
    def area_statistics_configuration(self):
        # Define groups
        information_group = self.General.identify_group_state('Additional information')

        # Define buttons
        areaLayer_combobox = self.area_statistics_dockwidget.areaLayer_combobox
        areafield_combobox = self.area_statistics_dockwidget.areafield_combobox
        ok_pushButton = self.area_statistics_dockwidget.ok_pushButton
        close_pushButton = self.area_statistics_dockwidget.close_pushButton
        progress_bar = self.area_statistics_dockwidget.progressBar

        # Set progress bar
        progress_bar.setValue(0)

        # Disconnect signals/slots
        try:
            areaLayer_combobox.currentIndexChanged.disconnect(self.get_area_fields)
        except TypeError:
            pass
        try:
            ok_pushButton.clicked.disconnect(self.area_statistics_configuration_OK)
        except TypeError:
            pass
        try:
            close_pushButton.clicked.disconnect(self.area_statistics_configuration_close)
        except TypeError:
            pass

        # Get relevant polygon layers for area
        layers_list = []
        for child in information_group.children():
            if isinstance(child, QgsLayerTreeLayer):
                try:
                    if child.layer().geometryType() == QgsWkbTypes.PolygonGeometry:
                        layers_list.append(child.name())
                except AttributeError:
                    pass

        # Populate area combobox
        areaLayer_combobox.clear()
        areaLayer_combobox.addItems(layers_list)
        self.get_area_fields()

        # Connect functions
        interface = 'generate'
        areaLayer_combobox.currentIndexChanged.connect(self.get_area_fields)
        ok_pushButton.clicked.connect(self.area_statistics_configuration_OK)
        close_pushButton.clicked.connect(self.area_statistics_configuration_close)

        self.area_statistics_dockwidget.show()


#-------------------------------Get area layer--------------------------------------------
    def get_area_fields(self):
        # Define buttons
        areaLayer_combobox = self.area_statistics_dockwidget.areaLayer_combobox.currentText()
        areafield_combobox = self.area_statistics_dockwidget.areafield_combobox
        # Find layer name from list of loaded layers and if field has the word 'name' in the heading then select this automatically
        try:
            selectedLayer = QgsProject.instance().mapLayersByName(areaLayer_combobox)[0]
            field_names = [field.name() for field in selectedLayer.fields()]
            areafield_combobox.clear()
            areafield_combobox.addItems(field_names)
            index = areafield_combobox.findText('name', QtCore.Qt.MatchFixedString | QtCore.Qt.MatchContains)
            if index >= 0:
                areafield_combobox.setCurrentIndex(index)
        except IndexError:
            self.area_statistics_dockwidget.areafield_combobox.clear()

#-------------------------------"Configure" OK button-------------------------------------------------------
    def area_statistics_configuration_OK(self):
        self.area_statistics()

#-------------------------------"Configure" close button-------------------------------------------------------
    def area_statistics_configuration_close(self):
        self.area_statistics_dockwidget.close()

#-------------------------------Run Area Statistics-------------------------------------------------------
    def area_statistics(self):
        # Define buttons
        areaLayer_combobox = self.area_statistics_dockwidget.areaLayer_combobox
        areafield_combobox = self.area_statistics_dockwidget.areafield_combobox
        progress_bar = self.area_statistics_dockwidget.progressBar

        # Define opportunity map layer
        opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        # Get opportunity map features
        features = self.TechFunctions.land_area('opportunity_features')

        # Get land exclusion percentage
        land_exclusion = float(self.land_availability_dockwidget.utilisation_green_spinBox.value())
        land_exclusion_percentage = float(float(land_exclusion) / 100)

        # Define and connect progress feedback from processing tool to interface
        f = QgsProcessingFeedback()
        f.progressChanged.connect(partial(self.General.progress_changed, progress_bar))
        # Join area layer with PV output layer, sum no of panels by area
        area_layer = QgsProject.instance().mapLayersByName(areaLayer_combobox.currentText())[0]
        area_field = areafield_combobox.currentText()

        feature_ids = [f.id() for f in features]
        opportunity_layer.selectByIds(feature_ids)

        dissolve_layer = processing.run("native:dissolve", 
                                    {'INPUT':QgsProcessingFeatureSourceDefinition(opportunity_layer.source(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                    'FIELD':[],
                                    'OUTPUT':'TEMPORARY_OUTPUT'},
                                    feedback = f)

        opportunity_layer.selectByIds([])

        clip_layer = processing.run("native:clip", 
                                {'INPUT':area_layer,
                                'OVERLAY':dissolve_layer['OUTPUT'],
                                'OUTPUT':'TEMPORARY_OUTPUT'},
                                feedback = f)

        clip_layer_name = str(clip_layer['OUTPUT'].name())
        area_stats_layer = processing.run("native:calculatevectoroverlaps", 
                                        {'INPUT':area_layer,
                                        'LAYERS':clip_layer['OUTPUT'],
                                        'OUTPUT':'TEMPORARY_OUTPUT'},
                                        feedback = f)

        # Retrieve area statistics {0. Area utilised, 1. Area of Ward, 2. % Area utilised}
        area_stats = {}
        for feats in area_stats_layer['OUTPUT'].getFeatures():
            if feats[clip_layer_name + '_area'] != 0:
                area_stats[feats[area_field]] = [float(feats[clip_layer_name + '_area'] * land_exclusion_percentage), float(feats.geometry().area()), float(round(float(feats[clip_layer_name + '_pc'] * land_exclusion_percentage), 1))]

        # Sort summary statistics
        sorted_stats = dict(sorted(area_stats.items(), key=lambda x: x[1], reverse=True))

        # Get units
        units_dict = {u'm\u00B2': 'm<sup>2</sup>', u'km\u00B2': 'km<sup>2</sup>', 'acre': 'acre', 'ha': 'ha'}
        units = units_dict[self.land_availability_dockwidget.areaUnits_combo_2.currentText()]

        # Prepare text
        summary = str(
            '<br><b>Area statistics</b><br><br>')
        summary += str(
            '<b>ID | Area utilised/Area of Ward (' + str(units) + ')</b><br><br>')
        for x in sorted_stats:
            summary += str(x) + ' <b>|</b> ' + str(self.TechFunctions.convert_land_units_to_textBroswer(sorted_stats[x][0])) + '/' + str(self.TechFunctions.convert_land_units_to_textBroswer(sorted_stats[x][1])) + ' (' + str(sorted_stats[x][2]) + ' %)' + '<br>'

        summary += '<br><br>'
        # Output results to energy yield estimator textbox
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(summary)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)

        # Remove temporary layers
        del dissolve_layer
        del clip_layer
        del area_stats_layer
    
        # Close configuration
        self.area_statistics_dockwidget.close()


#------------------------------- Analytical Hierarchy Process (AHP)-------------------------------------------------------
#------------------------------- Following code adapted from Mehmet Selim BILGIN - EasyAHP plugin for QGIS-------------------------------------------------------
#------------------------------- (https://github.com/MSBilgin/EasyAHP) (https://plugins.qgis.org/plugins/EasyAHP/)-------------------------------------------------------

    def show_AHP(self, aspect_type):

        # Define root and groups
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        main_group = root.findGroup(aspect_type)

        # Define list
        #self.paramList = []
        self.paramList = list()

        # Fetch layers and store in layer_data list
        for group in main_group.children():
            aspect_group = root.findGroup(str(group.name()))
            if aspect_group.isVisible():
                self.paramList.append(group.name())

        # Preparing the pairwise table.
        self.tableWidget = self.ahp_dockwidget.tableWidget
        self.tableWidget2 = self.ahp_dockwidget.tableWidget2

        self.tableWidget.clear()
        self.tableWidget2.clear()

        self.tableWidget.setRowCount(len(self.paramList))
        self.tableWidget.setColumnCount(len(self.paramList))
        self.tableWidget.setHorizontalHeaderLabels(self.paramList)
        self.tableWidget.setVerticalHeaderLabels(self.paramList)

        row = col = len(self.paramList)
        for rows in range(0, row):
            for cols in range(0, col):
                if cols == rows:
                    cellItem = QTableWidgetItem()
                    brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
                    brush.setStyle(Qt.SolidPattern)
                    cellItem.setBackground(brush)
                    cellItem.setText('1')
                    cellItem.setFlags(Qt.ItemIsEnabled)
                    cellItem.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cols,rows,cellItem)
                if rows < cols:
                    cellItem = QTableWidgetItem()
                    brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
                    brush.setStyle(Qt.SolidPattern)
                    cellItem.setBackground(brush)
                    #cellItem.setText('0.5')
                    cellItem.setFlags(Qt.ItemIsEnabled)
                    cellItem.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cols,rows,cellItem)


        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        # Disconnect signals
        calc_pushButton = self.ahp_dockwidget.calc_pushButton
        cancel_pushButton = self.ahp_dockwidget.cancel_pushButton
        save_pushButton = self.ahp_dockwidget.save_pushButton
        load_pushButton = self.ahp_dockwidget.load_pushButton
        help_pushButton = self.ahp_dockwidget.help_pushButton
        help_pushButton.setIcon(QIcon(':/plugins/GOMap/icons/About.png'))

        try:
            calc_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            cancel_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            save_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            load_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            help_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.tableWidget.itemChanged.disconnect()
        except TypeError:
            pass

        calc_pushButton.clicked.connect(self.parameterCalculator)
        cancel_pushButton.clicked.connect(self.cancel_ahp)
        save_pushButton.clicked.connect(self.saveTable)
        load_pushButton.clicked.connect(self.loadTable)
        help_pushButton.clicked.connect(self.help)

        help_pushButton.setToolTip('Help')
        ahp_help_textBrowser = self.ahp_help_dockwidget.ahp_help_textBrowser
        ahp_help_description = ''
        ahp_help_description += str('<pre><b>λ</b> = average value of the consistency vector' +
                                    '<br><b>CI</b> = Consistency Index, a measure of inconsistency to determine how reliable the decisions' +
                                    '<br>   were made in relation to several criteria of purely random judgments' +
                                    '<br><b>CR</b> = Consistency Ratio, to ensure the original preference ratings are consistent' +
                                    '<br>' +
                                    '<br>Input scales for AHP analysis:' +
                                    '<br>Scale  Level of importance     Inverse scale (decimal)' +
                                    '<br>1      Equal                   1 (1.000)' +
                                    '<br>2      Equal - moderate        1/2 (0.500)' +
                                    '<br>3      Moderate                1/3 (0.333)' +
                                    '<br>4      Moderate - strong       1/4 (0.250)' +
                                    '<br>5      Strong                  1/5 (0.200)' +
                                    '<br>6      Strong - very strong    1/6 (0.167)' +
                                    '<br>7      Very strong             1/7 (0.143)' +
                                    '<br>8      Very strong - extreme   1/8 (0.125)' +
                                    '<br>9      Extreme                 1/9 (0.111)</pre>'
                                    )

        ahp_help_textBrowser.setText(ahp_help_description)
        self.ahp_help_dockwidget.setFixedSize(800, 400)
        save_pushButton.setEnabled(False)
        #load_pushButton.setEnabled(False)

        AHPWeightingsApply_pushButton = self.ahp_dockwidget.AHPWeightingsApply_pushButton
        AHPWeightingsApply_pushButton.setEnabled(False)
        AHPWeightingsApply_pushButton.setToolTip('Apply AHP weightings to current opportunity map')

        self.tableWidget.itemChanged.connect(self.check)
        #self.ahp_dockwidget.widget.setGeometry(0, 0, 500, 500)
        self.ahp_dockwidget.show()


    def help(self):
        self.ahp_help_dockwidget.show()


    def cancel_ahp(self):
        self.ahp_dockwidget.close()

    def isTableCompleted(self):
        #checking the table for containing any blank cell.
        row = col = 0
        control = 0
        tableSize = self.tableWidget.columnCount()
        while row < tableSize:
            while col < tableSize:
                try:
                    if not self.tableWidget.item(row,col).text():
                        control+=1
                except:
                    control+=1
                col+=1
            row+=1
            col=0

        if control > 0:
            return False
        else:
            return True

    def parameterCalculator(self):
        AHPWeightingsApply_pushButton = self.ahp_dockwidget.AHPWeightingsApply_pushButton
        if self.isTableCompleted():
            self.ahpCalculator()
        else:
            self.iface.messageBar().pushMessage('AHP', 'You must fill all the cells in the pairwise table', Qgis.Info, 6)
                


    def ahpCalculator(self):
        self.istableEdited = False #user calculates parameter and makes this attr. FALSE
        self.LAYER_WEIGHT_LIST = self.weightCalculator(self.matrixNormalizer(self.columnAddition()))
        LAMBDA_PARAMETER = self.lambdaParameter(self.LAYER_WEIGHT_LIST)
        CONSISTENCY_INDEX = self.conIndex(LAMBDA_PARAMETER, self.LAYER_WEIGHT_LIST)
        CONSISTENCY_RATIO = self.conRatio(CONSISTENCY_INDEX, len(self.LAYER_WEIGHT_LIST))

        if not self.istableEdited:
            self.tableWidget2.setRowCount(len(self.paramList))
            self.tableWidget2.setColumnCount(2)
            self.tableWidget2.setHorizontalHeaderLabels(['Aspect', 'Weighting'])

            for i in range(len(self.paramList)):
                itemLayerName = QTableWidgetItem()
                itemLayerName.setTextAlignment(Qt.AlignCenter)
                itemLayerName.setText(self.paramList[i])
                itemLayerName.setFlags(Qt.ItemIsEnabled)
                self.tableWidget2.setItem(i,0, itemLayerName)

                itemWeight= QTableWidgetItem()
                itemWeight.setTextAlignment(Qt.AlignCenter)
                itemWeight.setText(str(self.LAYER_WEIGHT_LIST[i]))
                itemWeight.setFlags(Qt.ItemIsEnabled)
                self.tableWidget2.setItem(i,1, itemWeight)

            self.tableWidget2.resizeColumnsToContents()
            self.tableWidget2.resizeRowsToContents()


        else:
            self.iface.messageBar().pushMessage('AHP', 'You must calculate AHP Indicators before passing the next step.', Qgis.Info, 3)

    def get_ahp_results(self):
        ahp_results = {}

        for i in range(len(self.paramList)):
            aspect = str(self.tableWidget2.item(i, 0).text())
            weighting = str(self.tableWidget2.item(i, 1).text())
            ahp_results[aspect] = weighting

        return ahp_results

    def columnAddition(self):
        #Sums QtableWidget columns and inserting into columnSum list.
        columnCount = self.tableWidget.columnCount()-1
        columnSum = list()

        while columnCount> -1:
            sum = float()
            counter = self.tableWidget.columnCount()-1
            while counter > -1:
                sum+= float(self.tableWidget.item(counter,columnCount).text())
                counter-=1
            columnSum.append(sum)
            columnCount-=1
        columnSum.reverse()
        #iface.messageBar().pushMessage('columnSum', str(columnSum), Qgis.Info, 6)
        return columnSum

    def matrixNormalizer(self, sumOfColumns):
        normalizedMatrix = list()
        columnCount = self.tableWidget.columnCount()-1
        while columnCount> -1:
            numberList = list()
            counter = self.tableWidget.columnCount()-1
            while counter > -1:
                divided = round(float(self.tableWidget.item(counter,columnCount).text()) / sumOfColumns[columnCount],3)
                numberList.append(divided)
                counter-=1
            normalizedMatrix.extend([numberList])
            columnCount-=1
        #iface.messageBar().pushMessage('normalizedMatrix', str(normalizedMatrix), Qgis.Info, 6)
        return normalizedMatrix

    def weightCalculator(self, normalMatrix):
        #layers weight calculations.
        listlen = len(normalMatrix) -1
        layerWeights = list()
        while listlen > -1:
            sum = float()
            for i in normalMatrix:
                sum+= i[listlen]
            sumAverage = round(sum / len(normalMatrix),3)
            layerWeights.append(sumAverage)
            listlen-=1
        #iface.messageBar().pushMessage('layerWeights', str(layerWeights), Qgis.Info, 6)
        return layerWeights

    def lambdaParameter(self, layerWeightList):
        #lambda value calculations.
        listLen = len(layerWeightList)
        row = col = 0
        lambdaValue = lambdaSum = float()
        while row < listLen:
            sum = float()
            while col < listLen:
                sum += round(float(self.tableWidget.item(row,col).text()) * layerWeightList[col] , 3)
                col += 1
            lambdaSum += round(sum / layerWeightList[row] , 3)
            row += 1
            col = 0
        lambdaValue = round(lambdaSum / listLen , 3)
        self.ahp_dockwidget.label_5.setText(str(lambdaValue))
        #iface.messageBar().pushMessage('lambdaValue', str(lambdaValue), Qgis.Info, 6)
        return lambdaValue

    def conIndex(self, lambdaValue, layerWeightList):
        #consistency index calculations.
        criteriaNumber = len(layerWeightList)
        ci = round((lambdaValue - criteriaNumber) / (criteriaNumber-1) , 3)
        self.ahp_dockwidget.label_6.setText(str(ci))
        #iface.messageBar().pushMessage('ci', str(ci), Qgis.Info, 6)
        return ci

    def conRatio(self, consistencyIndex, numberOfLayers):
        randomConsIndex = {1:0.0 , 2:0.0 , 3:0.58 , 4:0.9 , 5:1.12 , 6:1.24 , 7:1.32 ,
                            8:1.41 , 9:1.45 , 10:1.49 , 11:1.51 , 12:1.48 , 13:1.56 , 14:1.57 , 15:1.59}

        cr = round(consistencyIndex / randomConsIndex[numberOfLayers] , 3)

        self.ahp_dockwidget.label_7.setText(str(cr))
        if cr >= 0.1:
            self.ahp_dockwidget.warningCR_label.show()
            self.ahp_dockwidget.AHPWeightingsApply_pushButton.setEnabled(False)
            self.ahp_dockwidget.save_pushButton.setEnabled(False)
            #self.ahp_dockwidget.load_pushButton.setEnabled(False)
        else:
            self.ahp_dockwidget.warningCR_label.hide()
            self.ahp_dockwidget.AHPWeightingsApply_pushButton.setEnabled(True)
            self.ahp_dockwidget.save_pushButton.setEnabled(True)
            #self.ahp_dockwidget.load_pushButton.setEnabled(True)
        
        #iface.messageBar().pushMessage('cr', str(cr), Qgis.Info, 6)
        return cr
        

    ##### checking #####

    def check(self):
        try:
            self.tableWidget.itemChanged.disconnect()
        except TypeError:
            pass

        self.istableEdited = True #this attibute is used for passing NEXT STEP. If it is True the user must re-calculate indicators.
        #Everything about the pairwise table (tableWidget) is handling in here.

        try:
            self.tableWidget.currentItem().setTextAlignment(Qt.AlignCenter) #text alignment for pairwise table.
            self.tableWidget.currentItem().setText(self.tableWidget.currentItem().text().replace(',' , '.')) #handling precise char (comma -> point)
        except:
            pass

        if self.tableWidget.currentItem() == None:
            #clears the cross cell
            pass

        elif self.tableWidget.currentItem().text()== '':
            #clears the cross cell
            self.tableWidget.setItem(self.tableWidget.currentItem().column(), self.tableWidget.currentItem().row(), QTableWidgetItem(''))

        else:
            if self.isNumeric(self.tableWidget.currentItem().text()): #checking the cell is numeric or not
                if float(self.tableWidget.currentItem().text()) > 9 or float(self.tableWidget.currentItem().text()) < 0.111:
                    self.iface.messageBar().pushMessage('AHP', 'Your value cannot be greater than 9 and less than 0.1111', Qgis.Warning, 6)
                    self.tableWidget.currentItem().setText('')
                    #clears the cross cell
                    self.tableWidget.setItem(self.tableWidget.currentItem().column(), self.tableWidget.currentItem().row(), QTableWidgetItem(''))

                else:
                    #numeric values is rounding in here.
                    numericvalue = str(round(float(self.tableWidget.currentItem().text()),3))
                    self.tableWidget.currentItem().setText(numericvalue)
                    self.crossFill()

            else:
                self.iface.messageBar().pushMessage('AHP', 'Please enter a numeric value', Qgis.Warning, 6)
                self.tableWidget.currentItem().setText('')
                self.tableWidget.setItem(dock.currentItem().column(), self.tableWidget.currentItem().row(), QTableWidgetItem(''))

        self.tableWidget.itemChanged.connect(self.check)

    def isNumeric(self,inputListValue):
        #checking for cell input value is numeric or not.
        try:
            float(inputListValue)
        except:
            return False
        return True


    def crossFill(self):
        self.tableWidget.blockSignals(True) #disabling signals before updating table.
        #Filling cross cell
        normalValue = float(self.tableWidget.currentItem().text())
        reverseValue = round((1/normalValue),3)

        if reverseValue > 9: #1/9 = 0.11111111 but 1/0.11111111 > 9 so this problem is handling in here.
            reverseValue = 9

        reverveItem = QTableWidgetItem()
        reverveItem.setTextAlignment(Qt.AlignCenter)
        reverveItem.setText(str(reverseValue))
        self.tableWidget.setItem(self.tableWidget.currentItem().column(), self.tableWidget.currentItem().row(), reverveItem)
        brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
        brush.setStyle(Qt.SolidPattern)
        reverveItem.setBackground(brush)
        reverveItem.setFlags(Qt.ItemIsEnabled)
        self.tableWidget.blockSignals(False) #enabling signals.


    def saveTable(self):
        #Saving the pairwise table.
        if not self.istableEdited:
            saveDlg = QFileDialog.getSaveFileName(None, 'Save Table', QgsProject.instance().readPath("./Weightings/"), 'CSV file (*.csv)')
            saveDlg = saveDlg[0]

            if saveDlg:
                try:
                    if not os.path.splitext(saveDlg)[1]:
                        saveDlg += '.csv'
                except TypeError:
                    pass

                tableSize = self.tableWidget.columnCount()
                

                try:
                    with open(saveDlg, 'w', newline='' ) as csvOutput:
                        writer = csv.writer(csvOutput, delimiter=',')

                        for i in range(int(tableSize)):
                            tempList = list()
                            for j in range(int(tableSize)):
                                tempList.append(self.tableWidget.item(i,j).text())
                            writer.writerow(tempList)

                    self.iface.messageBar().pushMessage('AHP', 'The pairwise table has been successfully saved.', Qgis.Info, 3)

                except Exception as saveError:
                    self.iface.messageBar().pushMessage('AHP', str(saveError), Qgis.Warning, 3)

        else:
            self.iface.messageBar().pushMessage('AHP', 'You must calculate AHP Indicators to save the table.', Qgis.Info, 3)


    def loadTable(self):
        #Loading the pairwise table.
        loadDlg = QFileDialog.getOpenFileName(None, 'Load Table', QgsProject.instance().readPath("./Weightings/"), 'CSV file (*.csv)')
        loadDlg = loadDlg[0]

        if loadDlg:
            self.tableWidget.blockSignals(True)
            try:

                with open(loadDlg, 'r') as csvFile:
                    reader  =csv.reader(csvFile, delimiter=',')
                    csvList = list()
                    for i in reader:
                        csvList.append(i)

                if self.tableWidget.rowCount() == len(csvList):
                    for i in range(len(csvList)):
                        for j in range(len(csvList)):
                            cellItem = QTableWidgetItem()
                            cellItem.setText(csvList[i][j])
                            cellItem.setTextAlignment(Qt.AlignCenter)
                            self.tableWidget.setItem(i,j,cellItem)
                            if i > j:
                                brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
                                brush.setStyle(Qt.SolidPattern)
                                cellItem.setBackground(brush)
                                cellItem.setFlags(Qt.ItemIsEnabled)
                                cellItem.setTextAlignment(Qt.AlignCenter)
                    self.tableMaker() #preparing the table structure.

                else:
                    self.iface.messageBar().pushMessage('AHP', 'The pairwise table size and the loaded table size are not compatible.', Qgis.Warning, 3)

            except Exception as loadError:
                    self.iface.messageBar().pushMessage('AHP', str(loadError), Qgis.Warning, 3)

            self.tableWidget.blockSignals(False)


    def tableMaker(self):
        #preparing the pairwise table.
        self.tableWidget.setRowCount(len(self.paramList))
        self.tableWidget.setColumnCount(len(self.paramList))

        row = col = len(self.paramList)
        for rows in range(0, row):
            for cols in range(0, col):
                if cols == rows:
                    cellItem = QTableWidgetItem()
                    brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
                    brush.setStyle(Qt.SolidPattern)
                    cellItem.setBackground(brush)
                    cellItem.setText('1')
                    cellItem.setFlags(Qt.ItemIsEnabled)
                    cellItem.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cols,rows,cellItem)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()