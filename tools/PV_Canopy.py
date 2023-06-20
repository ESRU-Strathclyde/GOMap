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
import os
import xlrd
from qgis.utils import iface
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication

# Import resources from dockwidgets
from ..dockwidgets.configure_pv_canopy_dockwidget import configure_pv_canopy

from .TechnologyFunctions import TechFunctions


class PV_Canopy:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.configure_pv_canopy_dockwidget = configure_pv_canopy()

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')


#-------------------------------Load PV model-------------------------------------------------------
    def load_PV_model(self):
        model_path = str(self.plugin_dir) + '/tools/PV_model.xlsm'
        os.startfile(model_path)

#-------------------------------Read from PV model-------------------------------------------
    def read_PV_model(self, interface):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # To open Workbook 
        model_path = str(self.plugin_dir) + '/tools/PV_model.xlsm'
        book = xlrd.open_workbook(model_path)
        data_sheet = book.sheet_by_index(0)
        pv_sheet = book.sheet_by_index(1)
        module_sheet = book.sheet_by_index(2)

        # cell_value(row_index, column_index) starting from 0
        # Get location
        latitude = float(pv_sheet.cell_value(1,1))
        longitude = float(pv_sheet.cell_value(2,1))
        ground_reflectance = float(pv_sheet.cell_value(3,1))
        orientation = int(pv_sheet.cell_value(4,1))

        # Get Panel Data
        module_index = int(data_sheet.cell_value(2,25))
        horizon_index = int(data_sheet.cell_value(2,24))
        if module_index == 1:
            module_type = 'Default (mono-Si)'
        else:
            module_type = str(module_sheet.cell_value(module_index, 1))
        # Horizon index: TRUE = 1; FALSE = 0
        if horizon_index == 1:
            horizon_brightening = 'Included'
        else:
            horizon_brightening = 'Not included'
        
        module_length = float(module_sheet.cell_value(module_index, 2))
        module_width = float(module_sheet.cell_value(module_index, 3))
        module_area = float(module_sheet.cell_value(module_index, 4))
        module_pstc = float(module_sheet.cell_value(module_index, 5))
        module_temp_coeff = float(module_sheet.cell_value(module_index, 6))
        module_rated_current = float(module_sheet.cell_value(module_index, 7))
        module_rated_voltage = float(module_sheet.cell_value(module_index, 8))
        module_circuit_current = float(module_sheet.cell_value(module_index, 9))
        module_circuit_voltage = float(module_sheet.cell_value(module_index, 10))

        # Get Output 
        optimal_angle = int(pv_sheet.cell_value(16,1))
        energy_yield = int(round(pv_sheet.cell_value(17,1)))
        power_output = int(round(pv_sheet.cell_value(18,1)))
        inter_row_spacing = float(pv_sheet.cell_value(19,1))

        # Set values to configuration settings
        self.configure_pv_canopy_dockwidget.length_spinbox.setValue(module_length)
        self.configure_pv_canopy_dockwidget.width_spinbox.setValue(module_width)
        self.configure_pv_canopy_dockwidget.pv_angle_spinbox.setValue(optimal_angle)
        self.configure_pv_canopy_dockwidget.energy_spinBox.setValue(power_output)
        self.configure_pv_canopy_dockwidget.inter_row_spinbox.setValue(inter_row_spacing)

        stats = str(
            '<b>PV canopy specification</b>' +
            '<br>EV consumption (kWh/yr): ' + str("{:,.0f}".format(self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value())) +
            '<br>Optimal tilt angle (<sup>o</sup>): ' + str(optimal_angle) +
            '<br>' + str(u'Energy yield (kWh/m<sup>2</sup>y): ') + str(int(energy_yield)) +
            '<br>Power output (kWh/y): ' + str(int(power_output)) +
            '<br>Inter-row spacing (m): ' + str("{:,.1f}".format(inter_row_spacing)) +
            '<br>' +
            '<br><b>Location</b>' +
            '<br>Latitude: ' + str(latitude) +
            '<br>Longitude: ' + str(longitude) +
            '<br>Ground reflectance: ' + str(ground_reflectance) +
            '<br>Orientation (<sup>o</sup>): ' + str(orientation) +
            '<br>Horizon brightening: ' + str(horizon_brightening) +
            '<br>' +
            '<br><b>Panel data</b>' +
            '<br>Module type: ' + str(module_type) +
            '<br>Length, Width (m): ' + str("{:,.1f}".format(module_length)) + ', ' + str(module_width) +            
            '<br>Area of panel (m<sup>2</sup>): ' + str(module_area) +
            '<br>P<sub>STC</sub> (W): ' + str(module_pstc) +
            '<br>β (temp coefficient): ' + str(module_temp_coeff) +
            '<br>Current at rated power (A): ' + str(module_rated_current) +
            '<br>Voltage at rated power (V): ' + str(module_rated_voltage) +
            '<br>Short-circuit current (A): ' + str(module_circuit_current) +
            '<br>Open-circuit voltage (V): ' + str(module_circuit_voltage) +
            '<br>'
            )

        # Output results to Report
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml('<br><br>' + stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)

        # Close PV model
        book.release_resources()
        del book

        # Enable invisible checkbox to avoid resetting information in textbrowser after clicking "Read model" button
        model_checkBox = self.configure_pv_canopy_dockwidget.model_checkBox
        model_checkBox.setChecked(True)

        QApplication.restoreOverrideCursor()

#-------------------------------"Configure" options-------------------------------------------------------
    def configure_PV_canopy_tools(self):
        load_PV_pushButton = self.configure_pv_canopy_dockwidget.load_PV_pushButton
        read_PV_pushButton = self.configure_pv_canopy_dockwidget.read_PV_pushButton
        ok_button = self.configure_pv_canopy_dockwidget.ok_pushButton
        reset_button = self.configure_pv_canopy_dockwidget.reset_pushButton
        vehicle_classes_comboBox = self.configure_pv_canopy_dockwidget.vehicleClass_comboBox
        model_checkBox = self.configure_pv_canopy_dockwidget.model_checkBox

        try:
            load_PV_pushButton.clicked.disconnect(self.load_PV_model)
        except TypeError:
            pass
        try:
            read_PV_pushButton.clicked.disconnect(self.read_PV_model)
        except TypeError:
            pass
        try:
            vehicle_classes_comboBox.currentIndexChanged.disconnect(self.refresh_vehicle_consumption)
        except TypeError:
            pass
        try:
            ok_button.clicked.disconnect(self.configure_PV_canopy_tools_OK)
        except TypeError:
            pass
        try:
            reset_button.clicked.disconnect(self.configure_PV_canopy_tools_reset)
        except TypeError:
            pass

        # Get prvious settings
        selected_vehicle = vehicle_classes_comboBox.currentIndex()
        vehicle_classes = ['EV', 'PHEV', 'Custom']
        vehicle_classes_comboBox.clear()
        vehicle_classes_comboBox.addItems(vehicle_classes)
        vehicle_classes_comboBox.setItemData(0, "Electric vehicle", Qt.ToolTipRole)
        vehicle_classes_comboBox.setItemData(1, "Plugin hybrid electric vehicle", Qt.ToolTipRole)        
        vehicle_classes_comboBox.setCurrentIndex(selected_vehicle)

        vehicle_classes_comboBox.currentIndexChanged.connect(self.refresh_vehicle_consumption)
        if not vehicle_classes_comboBox.currentText():
            vehicle_classes_comboBox.setCurrentIndex(0)

        load_PV_pushButton.clicked.connect(self.load_PV_model)
        read_PV_pushButton.clicked.connect(self.read_PV_model)
        ok_button.clicked.connect(self.configure_PV_canopy_tools_OK)
        reset_button.clicked.connect(self.configure_PV_canopy_tools_reset)
        model_checkBox.setVisible(False)
        
        self.configure_pv_canopy_dockwidget.show()


#-------------------------------"Configure" OK button-------------------------------------------------------
    def configure_PV_canopy_tools_OK(self):
        # Define checkbox
        model_checkBox = self.configure_pv_canopy_dockwidget.model_checkBox

        # If model_checkbox is checked, do not update text browser other update
        if model_checkBox.isChecked():
            self.configure_pv_canopy_dockwidget.close()
        else:            
            self.configure_pv_canopy_dockwidget.close()
            self.TechFunctions.populate_EnergyYieldEstimator()
            # Output specification from configure dockwidget
            stats = str(
                '<b>PV canopy specification</b>' +
                '<br>Vehicle class: ' + str(self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText()) +
                '<br>EV consumption (kWh/yr): ' + str("{:,.0f}".format(self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value())) +
                '<br>Optimal tilt angle (<sup>o</sup>): ' + str(self.configure_pv_canopy_dockwidget.pv_angle_spinbox.value()) +
                '<br>Power output (kWh/y): ' + str(int(self.configure_pv_canopy_dockwidget.energy_spinBox.value())) +
                '<br>Inter-row spacing (m): ' + str("{:,.1f}".format(self.configure_pv_canopy_dockwidget.inter_row_spinbox.value())) +
                '<br>Length, Width (m): ' + str("{:,.1f}".format(self.configure_pv_canopy_dockwidget.length_spinbox.value())) + ', ' + str(self.configure_pv_canopy_dockwidget.width_spinbox.value()) +
                '<br>Area of panel (m<sup>2</sup>): ' + str("{:,.1f}".format(self.configure_pv_canopy_dockwidget.length_spinbox.value() * self.configure_pv_canopy_dockwidget.width_spinbox.value())) +
                '<br><br>'
                )
            # Output stats to energy yield estimator textbox
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)

        # Reset model checkbox
        model_checkBox.setChecked(False)


#-------------------------------"Configure" Reset button-------------------------------------------------------
    def configure_PV_canopy_tools_reset(self):
        # Reset to default settings
        initial_consumption = self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value()
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'EV':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(1500)
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'PHEV':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(1000)
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'Custom':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(initial_consumption)
        self.configure_pv_canopy_dockwidget.energy_spinBox.setValue(345.6)
        self.configure_pv_canopy_dockwidget.length_spinbox.setValue(2.0)
        self.configure_pv_canopy_dockwidget.width_spinbox.setValue(1.0)
        self.configure_pv_canopy_dockwidget.pv_angle_spinbox.setValue(37)
        self.configure_pv_canopy_dockwidget.inter_row_spinbox.setValue(7.4)

#-------------------------------"Configure" Vehicle class button-------------------------------------------------------
    def refresh_vehicle_consumption(self):
        initial_consumption = self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value()
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'EV':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(1500)
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'PHEV':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(1000)
        if self.configure_pv_canopy_dockwidget.vehicleClass_comboBox.currentText() == 'Custom':
            self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.setValue(initial_consumption)