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
import glob, os, processing, subprocess, sys
import xlrd
from functools import partial
import pandas as pd
from math import ceil, floor, sin, asin, cos, acos, tan, radians, degrees
from statistics import mean
from qgis.core import QgsProject, QgsField, QgsLayerTreeLayer, QgsVectorLayer, QgsVectorFileWriter, QgsMapLayer, QgsFeature, QgsGeometry, QgsRectangle, Qgis, \
QgsWkbTypes, QgsProcessingFeedback, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeatureRequest, QgsProcessingFeatureSourceDefinition
from qgis.utils import iface
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import QVariant, Qt
from qgis.PyQt.QtWidgets import QApplication

# Import resources from dockwidgets
from ..dockwidgets.configure_pv_dockwidget import configure_pv
from ..dockwidgets.pv_generation_dockwidget import pv_generation
from ..dockwidgets.pv_generate_northerly_southerly_sites_dockwidget import pv_generate_northerly_southerly_sites

from .General import General
from .TechnologyFunctions import TechFunctions


class PV:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.configure_pv_dockwidget = configure_pv()
        self.pv_generation_dockwidget = pv_generation()
        self.pv_generate_northerly_southerly_sites_dockwidget = pv_generate_northerly_southerly_sites()

        # Reference General class
        self.General = General(None)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')


#-------------------------------Show Simple mode-------------------------------------------------------
    def show_simple_automatic_mode(self, mode_type):
        # Define dockwidgets for modes
        simple_mode = self.configure_pv_dockwidget
        advanced_mode = self.pv_generation_dockwidget

        if mode_type == 'simple_mode':
            self.configure_PV_tools()
            advanced_mode.close()
        if mode_type == 'advanced_mode':
            simple_mode.close()
            self.generate_PV_panels_configuration()


#-------------------------------Load PV modules-------------------------------------------------------
    def load_modules(self):
        # Open Workbook 
        model_path = str(self.plugin_dir) + '/tools/PV_model.xlsm'
        book = xlrd.open_workbook(model_path)
        module_sheet = book.sheet_by_index(2)

        # cell_value(row, column)
        # Create list and dictionary for module information
        module_list = []
        # Set global variable
        global module_size
        module_size = {}
        try:
            for i in range(1, 11):
                module_type = str(module_sheet.cell_value(i, 1))
                module_length = float(module_sheet.cell_value(i, 2))
                module_width = float(module_sheet.cell_value(i, 3))
                module_Pstc = float(module_sheet.cell_value(i, 5))
                if not module_type == '':
                    module_list.append(module_type)
                    module_size[module_type] = [module_length, module_width, module_Pstc]
        except IndexError:
            pass

        # Clear and fill module combobox
        module_comboBox = self.pv_generation_dockwidget.module_comboBox
        module_comboBox.clear()
        module_comboBox.addItems(module_list)


#-------------------------------Load PV modules-------------------------------------------------------
    def read_modules(self):
        # Define buttons
        module_comboBox = self.pv_generation_dockwidget.module_comboBox
        length_spinbox = self.pv_generation_dockwidget.length_spinbox
        width_spinbox = self.pv_generation_dockwidget.width_spinbox
        Pstc_spinbox = self.pv_generation_dockwidget.Pstc_spinbox

        # Read module dimensions
        module_type = module_comboBox.currentText()
        module_length = module_size[module_type][0]
        module_width = module_size[module_type][1]
        module_Pstc = module_size[module_type][2]
        # Set module dimensions
        length_spinbox.setValue(module_length)
        width_spinbox.setValue(module_width)
        Pstc_spinbox.setValue(module_Pstc)


#-------------------------------Mode options-------------------------------------------------------
    def mode_options(self):
        # Define textboxes and buttons
        length_spinbox = self.pv_generation_dockwidget.length_spinbox
        width_spinbox = self.pv_generation_dockwidget.width_spinbox
        Pstc_spinbox = self.pv_generation_dockwidget.Pstc_spinbox
        automatic_radioButton = self.pv_generation_dockwidget.automatic_radioButton
        custom_radioButton = self.pv_generation_dockwidget.custom_radioButton
        pv_angle_spinbox = self.pv_generation_dockwidget.pv_angle_spinbox
        energy_spinBox = self.pv_generation_dockwidget.energy_spinBox
        inter_row_spinbox = self.pv_generation_dockwidget.inter_row_spinbox
        orientation_spinbox = self.pv_generation_dockwidget.orientation_spinbox
        read_PV_pushButton = self.pv_generation_dockwidget.read_PV_pushButton
        weatherData_fileWidget = self.pv_generation_dockwidget.weatherData_fileWidget
        #PV_distance_x = self.pv_generation_dockwidget.PV_distance_x
        #distance_x_doubleSpinBox = self.pv_generation_dockwidget.distance_x_doubleSpinBox

        # Enable/disable options depending on user's choice
        if automatic_radioButton.isChecked():
            length_spinbox.setEnabled(False)
            width_spinbox.setEnabled(False)
            Pstc_spinbox.setEnabled(False)
            pv_angle_spinbox.setEnabled(False)
            energy_spinBox.setEnabled(False)
            inter_row_spinbox.setEnabled(False)
            #distance_x_doubleSpinBox.setEnabled(False)
            orientation_spinbox.setEnabled(False)
            read_PV_pushButton.setEnabled(False)
            weatherData_fileWidget.setEnabled(True)
            pv_angle_spinbox.clear()
            energy_spinBox.clear()
            inter_row_spinbox.clear()
            orientation_spinbox.clear()
        else:
            length_spinbox.setEnabled(True)
            width_spinbox.setEnabled(True)
            Pstc_spinbox.setEnabled(True)
            pv_angle_spinbox.setEnabled(True)
            energy_spinBox.setEnabled(True)
            inter_row_spinbox.setEnabled(True)
            #distance_x_doubleSpinBox.setEnabled(True)
            orientation_spinbox.setEnabled(True)
            read_PV_pushButton.setEnabled(True)
            weatherData_fileWidget.setEnabled(False)
            pv_angle_spinbox.setValue(37)
            energy_spinBox.setValue(345.6)
            inter_row_spinbox.setValue(7.4)
            orientation_spinbox.setValue(205)


#-------------------------------Load PV model-------------------------------------------------------
    def load_PV_model(self):
        # Define relative path to model file
        model_path = str(self.plugin_dir) + '/tools/PV_model.xlsm'
        #os.startfile(model_path)
        # Load model
        subprocess.Popen([model_path], shell=True)


#-------------------------------Read from PV model-------------------------------------------
    def read_PV_model(self, interface):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # Open Workbook and define worksheets
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

        # Horizon index: TRUE = 1; FALSE = 0
        horizon_index = int(data_sheet.cell_value(2,25))
        if horizon_index == 1:
            horizon_brightening = 'Included'
        else:
            horizon_brightening = 'Not included'

        # Get Panel Data
        module_index = int(data_sheet.cell_value(2,26))

        if module_index == 1:
            module_type = 'Default (mono-Si)'
        else:
            module_type = str(module_sheet.cell_value(module_index, 1))
        
        module_length = float(module_sheet.cell_value(module_index, 2))
        module_width = float(module_sheet.cell_value(module_index, 3))
        module_area = float(module_sheet.cell_value(module_index, 4))
        module_Pstc = float(module_sheet.cell_value(module_index, 5))
        module_temp_coeff = float(module_sheet.cell_value(module_index, 6))
        module_rated_current = float(module_sheet.cell_value(module_index, 7))
        module_rated_voltage = float(module_sheet.cell_value(module_index, 8))
        module_circuit_current = float(module_sheet.cell_value(module_index, 9))
        module_circuit_voltage = float(module_sheet.cell_value(module_index, 10))

        if interface == None:
            # Set information to be sent to text browser for summary
            # Break stats into 2 parts to calculate area of panel if using Custom mode
            first_stats = str(
                '---<br>' +
                '<b>Location</b>' +
                '<br>Latitude: ' + str(latitude) +
                '<br>Longitude: ' + str(longitude) +
                '<br>Ground reflectance: ' + str(ground_reflectance) +
                '<br>Horizon brightening: ' + str(horizon_brightening) +
                '<br>---' +
                '<br><b>Panel data</b>' +
                '<br>Module type: ' + str(module_type)
                )

            second_stats = str(
                '<br>β (temp coefficient): ' + str(module_temp_coeff) +
                '<br>Current at rated power (A): ' + str(module_rated_current) +
                '<br>Voltage at rated power (V): ' + str(module_rated_voltage) +
                '<br>Short-circuit current (A): ' + str(module_circuit_current) +
                '<br>Open-circuit voltage (V): ' + str(module_circuit_voltage) +
                '<br>'
                )

            # Close PV model
            book.release_resources()
            del book
            QApplication.restoreOverrideCursor()
            return first_stats, second_stats

        else:
            # Get Output 
            optimal_angle = int(pv_sheet.cell_value(16,1))
            energy_yield = int(round(pv_sheet.cell_value(17,1)))
            power_output = int(round(pv_sheet.cell_value(18,1)))
            inter_row_spacing = float(pv_sheet.cell_value(19,1))

            # Set values to configuration settings
            if interface == 'configure':
                house_consumption = self.configure_pv_dockwidget.houseConsumption_spinBox.value()
                self.configure_pv_dockwidget.length_spinbox.setValue(module_length)
                self.configure_pv_dockwidget.width_spinbox.setValue(module_length)
                self.configure_pv_dockwidget.pv_angle_spinbox.setValue(optimal_angle)
                self.configure_pv_dockwidget.energy_spinBox.setValue(power_output)
                self.configure_pv_dockwidget.inter_row_spinbox.setValue(inter_row_spacing)
                # Enable invisible checkbox to avoid resetting information in textbrowser after clicking "Read model" button
                model_checkBox = self.configure_pv_dockwidget.model_checkBox

            if interface == 'generate':
                house_consumption = self.pv_generation_dockwidget.houseConsumption_spinBox.value()
                self.pv_generation_dockwidget.length_spinbox.setValue(module_length)
                self.pv_generation_dockwidget.width_spinbox.setValue(module_length)
                self.pv_generation_dockwidget.Pstc_spinbox.setValue(module_Pstc)
                self.pv_generation_dockwidget.pv_angle_spinbox.setValue(optimal_angle)
                self.pv_generation_dockwidget.energy_spinBox.setValue(power_output)
                self.pv_generation_dockwidget.inter_row_spinbox.setValue(inter_row_spacing)
                self.pv_generation_dockwidget.orientation_spinbox.setValue(orientation)
                # Enable invisible checkbox to avoid resetting information in textbrowser after clicking "Read model" button
                model_checkBox = self.pv_generation_dockwidget.model_checkBox

            # Set information to be sent to text browser for summary
            stats = str(
                '<b>PV specification</b>' +
                '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(house_consumption)) +
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
                '<br>P<sub>STC</sub> (W): ' + str(module_Pstc) +
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
            # Set invisible parameter
            model_checkBox.setChecked(True)

            QApplication.restoreOverrideCursor()
        
        
#-------------------------------"Configure" options-------------------------------------------------------
    def configure_PV_tools(self):
        # Define buttons
        load_PV_pushButton = self.configure_pv_dockwidget.load_PV_pushButton
        read_PV_pushButton = self.configure_pv_dockwidget.read_PV_pushButton
        ok_button = self.configure_pv_dockwidget.ok_pushButton
        reset_button = self.configure_pv_dockwidget.reset_pushButton
        model_checkBox = self.configure_pv_dockwidget.model_checkBox
        mode_pushButton = self.configure_pv_dockwidget.mode_pushButton
        mode_pushButton.setToolTip('Advanced options - Generate PV panels as polygons to determine number of systems, optimal tilt angle and total energy output.')

        # Disconnect functions
        try:
            load_PV_pushButton.clicked.disconnect(self.load_PV_model)
        except TypeError:
            pass
        try:
            read_PV_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            ok_button.clicked.disconnect(self.configure_PV_tools_OK)
        except TypeError:
            pass
        try:
            reset_button.clicked.disconnect(self.configure_PV_tools_reset)
        except TypeError:
            pass
        try:
            mode_pushButton.clicked.disconnect(self.show_simple_automatic_mode)
        except TypeError:
            pass

        # Connect functions to buttons
        interface = 'configure'
        load_PV_pushButton.clicked.connect(self.load_PV_model)
        read_PV_pushButton.clicked.connect(partial(self.read_PV_model, interface))
        ok_button.clicked.connect(self.configure_PV_tools_OK)
        reset_button.clicked.connect(self.configure_PV_tools_reset)
        model_checkBox.setVisible(False)
        mode_pushButton.clicked.connect(partial(self.show_simple_automatic_mode, 'advanced_mode'))

        self.configure_pv_dockwidget.show()


#-------------------------------"Configure" OK button-------------------------------------------------------
    def configure_PV_tools_OK(self):
        # Define checkbox
        model_checkBox = self.configure_pv_dockwidget.model_checkBox

        # If model_checkbox is checked, do not update text browser again
        if model_checkBox.isChecked():
            self.configure_pv_dockwidget.close()
        else:            
            self.configure_pv_dockwidget.close()
            self.TechFunctions.populate_EnergyYieldEstimator()
            # Output specification from configure dockwidget
            stats = str(
                '<b>PV specification</b>' +
                '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(self.configure_pv_dockwidget.houseConsumption_spinBox.value())) +
                '<br>Optimal tilt angle (<sup>o</sup>): ' + str(self.configure_pv_dockwidget.pv_angle_spinbox.value()) +
                '<br>Power output (kWh/y): ' + str(int(self.configure_pv_dockwidget.energy_spinBox.value())) +
                '<br>Inter-row spacing (m): ' + str("{:,.1f}".format(self.configure_pv_dockwidget.inter_row_spinbox.value())) +
                '<br>Length, Width (m): ' + str("{:,.1f}".format(self.configure_pv_dockwidget.length_spinbox.value())) + ', ' + str(self.configure_pv_dockwidget.width_spinbox.value()) +
                '<br>Area of panel (m<sup>2</sup>): ' + str("{:,.1f}".format(self.configure_pv_dockwidget.length_spinbox.value() * self.configure_pv_dockwidget.width_spinbox.value())) +
                '<br><br>'
                )
            # Output stats to energy yield estimator textbox
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
            self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)

        # Reset model checkbox
        model_checkBox.setChecked(False)


#-------------------------------"Configure" Reset button-------------------------------------------------------
    def configure_PV_tools_reset(self):
        # Reset to default settings
        self.configure_pv_dockwidget.energy_spinBox.setValue(345.6)
        self.configure_pv_dockwidget.houseConsumption_spinBox.setValue(13000)
        self.configure_pv_dockwidget.length_spinbox.setValue(2.0)
        self.configure_pv_dockwidget.width_spinbox.setValue(1.0)
        self.configure_pv_dockwidget.pv_angle_spinbox.setValue(37)
        self.configure_pv_dockwidget.inter_row_spinbox.setValue(7.4)

#-------------------------------"Generate PV arrays" options-----------------------------------------------------------
    def generate_PV_panels_configuration(self):
        # Define groups
        information_group = self.General.identify_group_state('Additional information')

        # Define Mode buttons and function
        automatic_radioButton = self.pv_generation_dockwidget.automatic_radioButton
        custom_radioButton = self.pv_generation_dockwidget.custom_radioButton

        # Disconnect functions
        try:
            automatic_radioButton.clicked.disconnect(self.mode_options)
        except TypeError:
            pass
        try:
            custom_radioButton.clicked.disconnect(self.mode_options)
        except TypeError:
            pass

        # Connect functions and set tool tips
        automatic_radioButton.clicked.connect(self.mode_options)
        automatic_radioButton.setToolTip('Automatically generates PV systems with optimal tilt angle and inter-row shading for maximum energy output on a site-by-site basis.')
        custom_radioButton.clicked.connect(self.mode_options)
        custom_radioButton.setToolTip('Generates PV systems with user-defined parameters on all sites.')

        # Define buttons and progress bar
        module_comboBox = self.pv_generation_dockwidget.module_comboBox
        pv_angle_spinbox = self.pv_generation_dockwidget.pv_angle_spinbox
        energy_spinBox = self.pv_generation_dockwidget.energy_spinBox
        inter_row_spinbox = self.pv_generation_dockwidget.inter_row_spinbox
        orientation_spinbox = self.pv_generation_dockwidget.orientation_spinbox
        generate_button = self.pv_generation_dockwidget.generate_pushButton
        close_button = self.pv_generation_dockwidget.close_pushButton
        load_PV_pushButton = self.pv_generation_dockwidget.load_PV_pushButton
        read_PV_pushButton = self.pv_generation_dockwidget.read_PV_pushButton
        areaLayer_combobox = self.pv_generation_dockwidget.areaLayer_combobox
        model_checkBox = self.pv_generation_dockwidget.model_checkBox
        mode_pushButton = self.pv_generation_dockwidget.mode_pushButton
        progress_bar = self.pv_generation_dockwidget.progressBar

        # Hide horizontal distance parameter
        PV_distance_x = self.pv_generation_dockwidget.PV_distance_x
        PV_distance_x.setHidden(True)
        distance_x_doubleSpinBox = self.pv_generation_dockwidget.distance_x_doubleSpinBox
        distance_x_doubleSpinBox.setHidden(True)

        # Set texts for labels and tool tip
        self.pv_generation_dockwidget.PV_angle_label.setText(str(u'PV tilt angle (<sup>o</sup>)'))
        self.pv_generation_dockwidget.orientation_label.setText(str(u'PV orientation (<sup>o</sup>)'))
        mode_pushButton.setToolTip('Simple options - Estimate energy generation based on available area.')

        # Set progress bar
        progress_bar.setValue(0)

        # Set weather data default path
        weatherData_fileWidget = self.pv_generation_dockwidget.weatherData_fileWidget
        weatherData_fileWidget.setDefaultRoot(self.plugin_dir + '/weather_data/')

        # Disconnect signals/slots
        try:
            areaLayer_combobox.currentIndexChanged.disconnect(self.get_area_fields)
        except TypeError:
            pass
        try:
            load_PV_pushButton.clicked.disconnect(self.load_PV_model)
        except TypeError:
            pass
        try:
            read_PV_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            generate_button.clicked.disconnect(self.run_auto_custom_mode)
        except TypeError:
            pass
        try:
            close_button.clicked.disconnect(self.cancel_PV_panels_generation)
        except TypeError:
            pass
        try:
            module_comboBox.currentIndexChanged.disconnect(self.read_modules)
        except TypeError:
            pass
        try:
            mode_pushButton.clicked.disconnect(self.show_simple_automatic_mode)
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
        load_PV_pushButton.clicked.connect(self.load_PV_model)
        read_PV_pushButton.clicked.connect(partial(self.read_PV_model, interface))
        generate_button.clicked.connect(self.run_auto_custom_mode)
        close_button.clicked.connect(self.cancel_PV_panels_generation)
        model_checkBox.setVisible(False)
        mode_pushButton.clicked.connect(partial(self.show_simple_automatic_mode, 'simple_mode'))

        # Run load_modules() function to retrieve module information
        self.load_modules()
        module_comboBox.currentIndexChanged.connect(self.read_modules)
        module_comboBox.setCurrentIndex(0)
        # Possible bug - index turns to 0 but doesn't update length and width values. Workaround - set to default directly.
        self.pv_generation_dockwidget.length_spinbox.setValue(2.0)
        self.pv_generation_dockwidget.width_spinbox.setValue(1.0)
        #pv_angle_spinbox.clear()
        #energy_spinBox.clear()
        #inter_row_spinbox.clear()
        #orientation_spinbox.clear()
        self.pv_generation_dockwidget.show()


#-------------------------------Get area layer--------------------------------------------
    def get_area_fields(self):
        # Define buttons
        areaLayer_combobox = self.pv_generation_dockwidget.areaLayer_combobox.currentText()
        areafield_combobox = self.pv_generation_dockwidget.areafield_combobox
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
            self.pv_generation_dockwidget.areafield_combobox.clear()


#-------------------------------"Generate PV arrays" Cancel button--------------------------------------------
    def cancel_PV_panels_generation(self):
        # Close pv panel generation interface when clicked on Close
        self.pv_generation_dockwidget.close()



#-------------------------------Load xlsxwriter module-------------------------------------------
    '''
    def xlsx_writer(self):
        # Import xlsxwriter
        sys.path.append(self.plugin_dir + '/modules')
        from xlsxwriter import Workbook
        
        workbook = Workbook()
        print(workbook)
        return workbook
    '''

#-------------------------------Automatic mode for PV generation-------------------------------------------
    def automatic_mode(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Define buttons
        weatherData_fileWidget = self.pv_generation_dockwidget.weatherData_fileWidget

        # Set check parameter
        file_success = False
        weather_data_file = weatherData_fileWidget.filePath()

        try:
            with open(weather_data_file, 'r') as obj:
                file_success = True
        except FileNotFoundError:
            self.iface.messageBar().pushMessage("", 'Select weather data file.', Qgis.Warning, 5)

        # If weather file is selected then continue
        if file_success == True:
            # Read weather data from selected csv file
            weather_data = pd.read_csv(weather_data_file)

            # Open Workbook and define worksheets
            model_path = str(self.plugin_dir) + '/tools/PV_model.xlsm'
            book = xlrd.open_workbook(model_path)
            data_sheet = book.sheet_by_index(0)
            pv_sheet = book.sheet_by_index(1)
            module_sheet = book.sheet_by_index(2)

            # Get location

            #latitude = float(pv_sheet.cell_value(1,1))
            #longitude = float(pv_sheet.cell_value(2,1))
            ground_reflectance = float(pv_sheet.cell_value(3,1))
            #orientation = 205

            # Get Panel Data from cell values (row_index, column_index) starting from 0
            module_index = int(data_sheet.cell_value(2,26))

            if module_index == 1:
                module_type = 'Default (mono-Si)'
            else:
                module_type = str(module_sheet.cell_value(module_index, 1))
            
            panel_length = float(module_sheet.cell_value(module_index, 2))
            panel_width = float(module_sheet.cell_value(module_index, 3))
            panel_area = float(panel_length * panel_width)
            Pstc = float(module_sheet.cell_value(module_index, 5))
            temp_coefficient = float(module_sheet.cell_value(module_index, 6))
            horizontal_spacing = 0

            # Generate PV panels with collected information
            self.generate_PV_panels(weather_data, panel_length, panel_width, panel_area, None, None, Pstc, temp_coefficient, horizontal_spacing, None, None, None, None, None, 'automatic_mode')
 
        QApplication.restoreOverrideCursor()

#-------------------------------Find optimal tilt angle (key) with max energy output (value) from stored dictionary-------------------------------------------
    def max_values(self, angle_energy_dictionary, return_values):
        max_values = max(angle_energy_dictionary.items(), key=lambda x : x[1])
        if return_values == 1:
            return max_values[0]
        if return_values == 2:
            return max_values[0], max_values[1]


#-------------------------------PV model-------------------------------------------
    def PV_model(self, lat, lon, weather_data, reflectance, min_orientation, max_orientation, orientation_steps, module_Pstc, module_temp_coefficient, module_length, module_width, module_area, 
        min_tilt_angle, max_tilt_angle, tilt_angle_steps, get_mean_solar):
        # Define variables
        latitude = lat
        longitude = lon
        weather_data_frame = weather_data
        ground_reflectance = reflectance
        Pstc = module_Pstc
        temp_coefficient = module_temp_coefficient
        panel_length = module_length
        panel_width = module_width
        area_of_panel = module_area
        azimuth_direction = 0

        if latitude >= 0:
            azimuth_direction = 180
        if latitude <= 0:
            azimuth_direction = 0


        # Run PV model for range of orientations and tilt angles
        optimal_PV_orientation = {}

        for PV_orientation in range(min_orientation, max_orientation, orientation_steps):
            optimal_tilt_angle = {}

            for tilt_angle in range(min_tilt_angle, max_tilt_angle, tilt_angle_steps):
                solar_elevation_for_inter_row_shading = []
                energy_output = {}
                hour_list = []
                year_day_list = []
                hour = 1
                year_day = 1
                for i in range(1, 8761):
                    #print(i, hour, year_day)
                    hour+=1
                    if i % 24 == 0:
                        hour = 1
                        year_day = year_day + 1
                    hour_list.append(float(hour))
                    year_day_list.append(float(year_day))


                weather_data_frame['hour'] = hour_list
                weather_data_frame['year_day'] = year_day_list

                #weather_data_frame['year_day'].apply(lambda x: float(x))
                weather_data_frame['declination'] = 23.465*pd.np.sin(pd.np.radians(280.1+0.9863*weather_data_frame['year_day']))
                weather_data_frame['eq_of_time'] = 9.87*pd.np.sin(pd.np.radians(1.978*weather_data_frame['year_day']-160.22))-7.53*pd.np.cos(pd.np.radians(0.989*weather_data_frame['year_day']-80.11))-1.5*pd.np.sin((pd.np.radians(0.989*weather_data_frame['year_day']-80.11)))
                weather_data_frame['local_solar_time'] = (weather_data_frame['hour']-1)+(longitude/15)+(weather_data_frame['eq_of_time']/60)
                weather_data_frame['hour_angle'] = 15*(12-weather_data_frame['local_solar_time'])
                weather_data_frame['solar_elevation'] = pd.np.degrees(pd.np.arcsin((((pd.np.cos(pd.np.radians(latitude))*pd.np.cos(pd.np.radians(weather_data_frame['declination']))*pd.np.cos(pd.np.radians(weather_data_frame['hour_angle'])))+(pd.np.sin(pd.np.radians(latitude))*pd.np.sin(pd.np.radians(weather_data_frame['declination'])))))))
                weather_data_frame['solar_azimuth'] = pd.np.degrees(pd.np.arcsin((pd.np.cos(pd.np.radians(weather_data_frame['declination']))*pd.np.sin(pd.np.radians(weather_data_frame['hour_angle'])))/pd.np.cos(pd.np.radians(weather_data_frame['solar_elevation']))))
                weather_data_frame['abs_solar_azimuth'] = azimuth_direction - weather_data_frame['solar_azimuth']
                weather_data_frame['wall_solar_azimuth'] = abs(weather_data_frame['abs_solar_azimuth'] - PV_orientation)
                weather_data_frame['solar_incidence_angle'] = pd.np.degrees(pd.np.arccos((pd.np.sin(pd.np.radians(weather_data_frame['solar_elevation']))*pd.np.cos(pd.np.radians(90-tilt_angle))+pd.np.cos(pd.np.radians(weather_data_frame['solar_elevation']))*pd.np.cos(pd.np.radians(weather_data_frame['wall_solar_azimuth']))*pd.np.sin(pd.np.radians(90-tilt_angle)))))
                weather_data_frame['direct_solar_on_panel'] = weather_data_frame['Direct normal solar']*pd.np.cos(pd.np.radians(weather_data_frame['solar_incidence_angle']))/pd.np.sin(pd.np.radians(weather_data_frame['solar_elevation']))

                weather_data_frame['diffuse_solar_on_panel'] = weather_data_frame['Diffuse horizontal solar']*(0.5*(1+pd.np.cos(pd.np.radians(90-tilt_angle))*(1+(1-(weather_data_frame['Diffuse horizontal solar']**2/(weather_data_frame['Diffuse horizontal solar']+weather_data_frame['Direct normal solar'])**2))*(pd.np.sin(pd.np.radians(0.5*tilt_angle))**3)))*(1+(1-(weather_data_frame['Diffuse horizontal solar']**2/(weather_data_frame['Diffuse horizontal solar']+weather_data_frame['Direct normal solar'])**2))*(pd.np.cos(pd.np.radians(weather_data_frame['solar_incidence_angle']))**2)*(pd.np.sin(pd.np.radians(90-weather_data_frame['solar_elevation']))**3)))
                weather_data_frame['ground_reflected_on_panel'] = (0.5*(1-pd.np.cos(pd.np.radians(90-tilt_angle)))*(weather_data_frame['Direct normal solar']+weather_data_frame['Diffuse horizontal solar'])*ground_reflectance)
                weather_data_frame['total_solar_on_panel'] = weather_data_frame['direct_solar_on_panel'] + weather_data_frame['diffuse_solar_on_panel'] + weather_data_frame['ground_reflected_on_panel']
                weather_data_frame['panel_power_output'] = (Pstc*(weather_data_frame['total_solar_on_panel']/1000)*(1-temp_coefficient*((20+weather_data_frame['Ambient temp'])-25))*panel_length)/area_of_panel


                #weather_data_frame.fillna(0.0)

                energy_sum = weather_data_frame['panel_power_output'].sum()/1000
                optimal_tilt_angle[tilt_angle] = energy_sum
                optimal_PV_orientation[PV_orientation] = optimal_tilt_angle

        max_energy = float("-inf")
        PV_orientation = None
        max_angle = None

        for k_outer, v_outer in optimal_PV_orientation.items():
            for k_inner, v_inner in v_outer.items():
                if v_inner > max_energy:
                    max_energy = v_inner
                    PV_orientation = k_outer
                    max_angle = k_inner

        if get_mean_solar == False:
            lst = [weather_data_frame]
            del weather_data_frame
            del lst
            return PV_orientation, max_angle, max_energy
        else:    
            weather_data_frame['solar_elevation_for_inter_row_shading'] = weather_data_frame['solar_elevation'].clip(lower=0)
            mean_solar_elevation = weather_data_frame['solar_elevation_for_inter_row_shading'].mean()
            inter_row_spacing = panel_length*pd.np.cos(pd.np.radians(max_angle)) + panel_length*(pd.np.sin(pd.np.radians(max_angle))/pd.np.tan(pd.np.radians(mean_solar_elevation)))
            lst = [weather_data_frame]
            del weather_data_frame
            del lst
            return PV_orientation, max_angle, max_energy, inter_row_spacing



#-------------------------------Run Automatic or Custom mode--------------------------------------------------------
    def run_auto_custom_mode(self):
        # Define Mode buttons and function
        automatic_radioButton = self.pv_generation_dockwidget.automatic_radioButton
        #custom_radioButton = self.pv_generation_dockwidget.custom_radioButton

        if automatic_radioButton.isChecked():
            self.automatic_mode()
        else:
            self.custom_mode()


#-------------------------------Custom mode for PV generation-------------------------------------------
    def custom_mode(self):
        # Define parameters
        panel_length = float(self.pv_generation_dockwidget.length_spinbox.value())
        width = float(self.pv_generation_dockwidget.width_spinbox.value())
        area_of_panel = float(panel_length * width)
        PV_angle = float(self.pv_generation_dockwidget.pv_angle_spinbox.value())
        #distance_x = float(self.pv_generation_dockwidget.distance_x_doubleSpinBox.value())
        horizontal_spacing = 0
        inter_row_spacing = float(self.pv_generation_dockwidget.inter_row_spinbox.value())
        power = float(self.pv_generation_dockwidget.energy_spinBox.value())
        PV_orientation = int(self.pv_generation_dockwidget.orientation_spinbox.value())

        distance_x, state_x, distance_y, state_y = self.check_horizontal_distance(panel_length, width, PV_orientation, PV_angle, horizontal_spacing, inter_row_spacing)
        self.generate_PV_panels(None, panel_length, width, area_of_panel, PV_orientation, PV_angle, None, None, distance_x, inter_row_spacing, power, state_x, distance_y, state_y, 'custom_mode')


#-------------------------------Check horizontal distance when generating PV panels --------------------------------------------------------
    def check_horizontal_distance(self, module_length, module_width, module_orientation, tilt_angle, horizontal_spacing, inter_row_distance):
        # Define PV settings
        panel_length = module_length
        width = module_width
        PV_angle = tilt_angle
        distance_x = horizontal_spacing
        inter_row_spacing = inter_row_distance
        PV_orientation = module_orientation

        # Define variables
        start_x = 0
        start_y = 0
        state_x = False
        state_y = False
        # Calculate length based on tilt angle since looking at polygon from top-down view
        length = panel_length * float(cos(radians(PV_angle)))
        distance_y = float(inter_row_spacing + length)
        # Calculate required horizontal distance based on panel orientation
        # If rotation is 90 or 270 degrees, flip dimensions instead of calculating distance
        if PV_orientation in (90, 270):
            PV_orientation = 0
            length = width
            width = panel_length
        # If rotation is 0, 180, 360, all of which is original position so no need to calculate distance
        elif PV_orientation in (0, 180, 360):
            PV_orientation = 0
        else:
            # Define opportunity map layer
            opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
            # Set memory layer the same CRS as the source layer
            crs = opportunity_layer.crs()
            # Get dimensions and set XY coordinate to 0
            l = float(length / 2)
            w = float(width / 2)
            x = 0
            y = 0
            # Create memory layer to hold 2 rectangles and calculate minimum horizontal distance when rotated
            layer = QgsVectorLayer("Multipolygon?crs=epsg:" + unicode(crs.postgisSrid()) + "&field=id:integer&index=yes", 'poly' , "memory")
            layer.startEditing()
            prov = layer.dataProvider() 
            # First feature
            poly1 = QgsFeature()
            poly1.setGeometry(QgsGeometry.fromRect(QgsRectangle(x - w, y - l, x + w, y + l)))
            poly1.setAttributes([1])
            # Second feature
            poly2 = QgsFeature()
            poly2.setGeometry(QgsGeometry.fromRect(QgsRectangle(width - w, y - l, width + w, y + l)))
            poly2.setAttributes([2])
            # Add features
            prov.addFeatures([poly1, poly2])
            # Select both features and get their centroid position
            layer.selectAll()
            feats = [ feat for feat in layer.selectedFeatures() ]
            centroids = [ feat.geometry().centroid().asPoint() for feat in feats ]
            new_geom = []
            for feat in feats:
                geom = feat.geometry()
                # Rotate features
                geom.rotate(PV_orientation, feat.geometry().centroid().asPoint())
                new_geom.append(geom.asWkt())
            # Calculate intersection
            intersect1 = QgsGeometry.fromWkt(new_geom[0]).intersection(QgsGeometry.fromWkt(new_geom[1]))
            # Create line from centroids
            line = QgsGeometry.fromPolylineXY(centroids)
            # Calculate minimum horizontal distance
            distance = intersect1.intersection(line).length()
            # Ensure user-defined horizontal distance is not less than the calculated minimum horizontal distance
            if distance_x < distance:
                distance_x = distance
            # Remove memory layer
            del layer

        # Ensure polygons are not created 'within each other' if distance is zero;
        # Instead they will align on the bounding box
        if distance_x == 0:
            distance_x = (width)
            state_x = True
        if distance_y == 0:
            distance_y = (length)
            state_y = True

        return distance_x, state_x, distance_y, state_y

#-------------------------------Generate PV systems--------------------------------------------------------
    def generate_PV_panels(self, weather_data, module_length, module_width, module_area, module_orientation, tilt_angle, pstc, temp_coeff, horizontal_spacing, inter_row_distance, energy_output,
        x_state, vertical_distance, y_state, auto_custom_mode):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        information_group = self.General.identify_group_state('Additional information')
        scope_group = self.General.identify_group_state('Scope')

        # Define mode
        mode = auto_custom_mode

        # Define buttons and progress bar
        length = module_length
        width = module_width
        panel_area = module_area
        ground_reflectance = 0.2
        distance_x = horizontal_spacing
        inter_row_spacing = inter_row_distance

        if mode == 'custom_mode':
            Pstc = self.pv_generation_dockwidget.Pstc_spinbox.value()
            max_angle = tilt_angle
            power = float(energy_output)
            distance_y = vertical_distance
            state_x = x_state
            state_y = y_state
            PV_orientation = module_orientation
            # If rotation is 90 or 270 degrees, flip dimensions instead of calculating distance
            if PV_orientation in (90, 270):
                PV_orientation = 0
                panel_length = width * float(cos(radians(max_angle)))
                width = module_length
            else:
                panel_length = length * float(cos(radians(max_angle)))

        else:
            Pstc = pstc
            temp_coefficient = temp_coeff

        # Get weather data
        weather_data_frame = weather_data

        land_exclusion = float(self.land_availability_dockwidget.utilisation_green_spinBox.value())
        house_consumption = float(self.pv_generation_dockwidget.houseConsumption_spinBox.value())
        areaLayer_combobox = self.pv_generation_dockwidget.areaLayer_combobox
        areafield_combobox = self.pv_generation_dockwidget.areafield_combobox
        progress_bar = self.pv_generation_dockwidget.progressBar

        # Disconnect move_added_layer_to_information() function
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.General.move_added_layer_to_information)
        except TypeError:
            pass

        # Get name of current scope layer
        for layers in scope_group.children():
            if layers.isVisible():
                name = layers.name()

        # Define opportunity map layer
        opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        # Get opportunity map features
        features = self.TechFunctions.land_area('opportunity_features')

        # Only run when there is at least 1 feature
        if features:
            # Set memory layer the same CRS as the source layer
            crs = opportunity_layer.crs()
            memory_lyr = QgsVectorLayer("MultiPolygon?crs=epsg:" + unicode(crs.postgisSrid()) + "&index=yes", "PV panels for " + str(name), "memory")
            memory_lyr.startEditing()
            memory_lyr.addAttribute(QgsField("ID", QVariant.Int))
            memory_lyr.addAttribute(QgsField("Tilt Angle", QVariant.Int))
            memory_lyr.addAttribute(QgsField("Orientation", QVariant.Int))
            memory_lyr.addAttribute(QgsField("Energy (kWh)", QVariant.Double))
            memory_lyr.addAttribute(QgsField("Inter_row", QVariant.Double))
            #memory_lyr.addAttribute(QgsField("EnergyByID", QVariant.Double))
            provider = memory_lyr.dataProvider()

            # Specifying input/output crs to transform coordinates to lat/lon system
            crsSrc = QgsCoordinateReferenceSystem(crs) # source crs
            crsDest = QgsCoordinateReferenceSystem(4326) # destination crs
            transform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance()) 

            # Get land exclusion percentage
            land_exclusion_percentage = float(float(land_exclusion) / 100)

            # Set progress bar
            progress_bar.setMaximum(len(features))

            # Define variables
            start_x = 0
            start_y = 0

            # Store information in lists/dictionaries
            # Store PV panels as new features
            fts = []
            # Store site ID and energy output for each PV panel
            energySum_dict = {}
            # Store original PV panel geometry for rotation
            couples_id_geom = []
            # Store optimal tilt angle and energy output for each lat/lon coordinate
            angle_energy_at_coordinate = {}
            # Store optimal PV power output, tilt angle, orientation and inter-row spacing per feature
            optimal_PV_power_output_list = []
            optimal_PV_tilt_angle_list = []
            optimal_PV_orientation_list = []
            optimal_PV_inter_row_spacing_list = []
            #for f in features:
            for index, f in enumerate(features):

                if mode == 'automatic_mode':
                    geom = QgsGeometry(f.geometry())
                    output_geometry = geom.pointOnSurface()
                    # Clone feature to transform to new coordinates system
                    clone_geom = QgsGeometry(output_geometry)
                    # Transform feature's geometry
                    clone_geom.transform(transform) 
                    lat = round(clone_geom.asPoint().y(), 2)
                    lon = round(clone_geom.asPoint().x(), 2)
                    coord = lat, lon

                    if coord not in angle_energy_at_coordinate:

                        if lat < 180:
                            min_orientation = 90
                            max_orientation = 275
                        else:
                            min_orientation = 0
                            max_orientation = 90

                        # Run PV model and retrieve optimal PV orientation, tilt angle, energy and mean solar elevation to calculate inter row spacing
                        initial_PV_orientation, initial_max_angle, initial_max_energy = self.PV_model(lat, lon, weather_data_frame, ground_reflectance, min_orientation, max_orientation, 10, Pstc, temp_coefficient, length, width, panel_area, 0, 91, 10, False)
                        PV_orientation, max_angle, max_energy, inter_row_spacing = self.PV_model(lat, lon, weather_data_frame, ground_reflectance, initial_PV_orientation - 5, initial_PV_orientation + 5, 1, Pstc, temp_coefficient, length, width, panel_area, initial_max_angle -5, initial_max_angle + 5, 1, True)

                        distance_x, state_x, distance_y, state_y = self.check_horizontal_distance(length, width, PV_orientation, max_angle, horizontal_spacing, inter_row_spacing)                        
                        angle_energy_at_coordinate[coord] = [max_angle, max_energy]


                    # for top down view
                    panel_length = length * float(cos(radians(float(max_angle))))
                    power = float(max_energy) * float(panel_area)
                    inter_row_spacing = float(inter_row_spacing)
                    del clone_geom

                # Add optimal pv parameters to list
                optimal_PV_power_output_list.append(round(power, 1))
                optimal_PV_tilt_angle_list.append(max_angle)
                optimal_PV_orientation_list.append(PV_orientation)
                optimal_PV_inter_row_spacing_list.append(round(inter_row_spacing, 1))

                try:
                    land_area = f.geometry().area()
                    total_panel_area = 0
                    power_sum = 0
                    progress_bar.setValue(progress_bar.value() + 1)
                    bbox = f.geometry().boundingBox()
                    start_x = bbox.xMinimum() + float(distance_x / 2)
                    start_y = bbox.yMinimum() + float(distance_y / 2)
                    # Utilise area starting from top
                    utilised_bbox = float(bbox.yMaximum()) - (float(bbox.height()) * float(land_exclusion_percentage))
                    for row in range(0, int(ceil(bbox.height() / distance_y))):
                        for column in range(0, int(ceil(bbox.width() / distance_x))):
                            fet = QgsFeature()
                            geom_type = self.PV_panel_size(panel_length, width, start_x, start_y)
                            if f.geometry().contains(geom_type):
                                #if (total_panel_area > (float(land_area) * float(land_exclusion_percentage))) or (start_y < utilised_bbox):
                                # check above line as surface area of panels should be used as land optimsation vs surface area of land
                                if (total_panel_area > (float(land_area) * float(land_exclusion_percentage))):
                                    break
                                else:
                                    power_sum += power
                                    total_panel_area += geom_type.area()
                                    centroid = geom_type.centroid().asPoint()
                                    geom_type.rotate(PV_orientation, centroid)
                                    couples_id_geom.append([f.id(), geom_type])
                                    fet.setGeometry(geom_type)
                                    fet.setAttributes([f['ID'], int(max_angle), int(PV_orientation), round(power, 1), round(inter_row_spacing,1)])
                                    fts.append(fet)
                            if state_x == False:
                                start_x += distance_x + (width)
                            else:
                                start_x += distance_x
                        start_x = bbox.xMinimum() + float(distance_x / 2)
                        start_y += distance_y
                        '''
                        if state_y == False:
                            start_y += distance_y + (panel_length)
                        else:
                            start_y += distance_y
                        '''
                    energySum_dict[f['ID']] = power_sum
                    #energySum_dict = {'ID': power_sum}
                except AttributeError:
                    pass

            # Update features in memory layer
            memory_lyr.addFeatures(fts)
            memory_lyr.updateFields()
            # Add energy attributes
            #for feats in memory_lyr.getFeatures():
            #    if feats['ID'] in energySum_dict:
            #        memory_lyr.changeAttributeValue(feats.id(), 3, energySum_dict.get(feats['ID']))
            # Change geometry values to include rotation
            provider.changeGeometryValues({
              couple_id_geom[0]: couple_id_geom[1] for couple_id_geom in couples_id_geom
            })
            # Save memory layer
            memory_lyr.commitChanges()
            # Deselect all features
            memory_lyr.selectByIds([])
            # Get number of features (i.e. number of PV arrays)
            no_of_features = memory_lyr.featureCount()
            # If more than one optimal orientation, return range
            angle_list = self.optimal_PV_output_values(min(optimal_PV_tilt_angle_list), max(optimal_PV_tilt_angle_list))
            orientation_list = self.optimal_PV_output_values(min(optimal_PV_orientation_list), max(optimal_PV_orientation_list))
            inter_row_spacing_list = self.optimal_PV_output_values(min(optimal_PV_inter_row_spacing_list), max(optimal_PV_inter_row_spacing_list))
            power_list = self.optimal_PV_output_values(min(optimal_PV_power_output_list), max(optimal_PV_power_output_list))
            energy_sum = sum(energySum_dict.values())
            # Pass output parameters to solar energy calculator
            if mode == 'custom_mode':
                self.solarPV_eneryCalculation(length, width, Pstc, no_of_features, angle_list, orientation_list, inter_row_spacing_list, power_list, energy_sum, house_consumption, land_exclusion, 'custom_mode')
            else:
                
                self.solarPV_eneryCalculation(length, width, Pstc, no_of_features, angle_list, orientation_list, inter_row_spacing_list, power_list, energy_sum, house_consumption, land_exclusion, 'automatic_mode')

            # If summary by area option is checked
            if self.pv_generation_dockwidget.areaSummary_GroupBox.isChecked():
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

                join_layer = processing.run("native:joinbynearest", 
                                        {'INPUT':memory_lyr,
                                        'INPUT_2':area_layer,
                                        'FIELDS_TO_COPY':[area_field],
                                        'DISCARD_NONMATCHING':True,
                                        'PREFIX':'',
                                        'NEIGHBORS':1,
                                        'MAX_DISTANCE':None,
                                        'OUTPUT':'TEMPORARY_OUTPUT'},
                                        feedback = f)

                delete_dup_layer = processing.run("native:deleteduplicategeometries", 
                                            {'INPUT':join_layer['OUTPUT'],
                                            'OUTPUT':'TEMPORARY_OUTPUT'},
                                            feedback = f)

                delete_field_layer = processing.run("native:deletecolumn", 
                                                {'INPUT':delete_dup_layer['OUTPUT'],
                                                'COLUMN':['n','distance','feature_x','feature_y','nearest_x','nearest_y'],
                                                'OUTPUT':'TEMPORARY_OUTPUT'},
                                                feedback = f)

                energy_stats_layer = processing.run("qgis:statisticsbycategories", 
                                                {'INPUT':delete_field_layer['OUTPUT'],
                                                'VALUES_FIELD_NAME':'Energy (kWh)',
                                                'CATEGORIES_FIELD_NAME':[area_field],
                                                'OUTPUT':'TEMPORARY_OUTPUT'},
                                                feedback = f)
                
                pv_layer = delete_field_layer['OUTPUT']

                QgsProject.instance().addMapLayer(pv_layer, False)
                information_group.insertChildNode(0, QgsLayerTreeLayer(pv_layer))
                information_group.setExpanded(True)
                # Set pv_layer to go at top of layer order panel
                order = root.customLayerOrder()
                for i, o in enumerate(order):
                    if o.name() == pv_layer.name():
                        order.insert(0, order.pop(i))
                root.setCustomLayerOrder(order)

                # Set colour and refresh
                pv_layer.loadNamedStyle(self.plugin_dir + '/styles/pv_panel_style_2.qml')
                pv_layer.triggerRepaint()
                self.iface.layerTreeView().refreshLayerSymbology(pv_layer.id())
                self.iface.layerTreeView().setLayerVisible(pv_layer, True)
                pv_layer.setName("PV panels for " + str(name))
                self.iface.mapCanvas().refresh()
                
                energy_stats = {}
                for feats in energy_stats_layer['OUTPUT'].getFeatures():
                    # Retrieve energy statistics for each area_field {0 = area_field, 1 = count of pv panels, 6 = sum of energy}
                    energy_stats[feats.attributes()[0]] = [feats.attributes()[1], # count of pv panels
                                                        feats.attributes()[6] # sum of energy
                                                        ] 

                area_stats = {}
                for feats in area_stats_layer['OUTPUT'].getFeatures():
                    area_stats[feats[area_field]] = [float(feats[clip_layer_name + '_area'] * land_exclusion_percentage), # area utilised
                                                    float(feats.geometry().area()), # area of feature (e.g. ward)
                                                    float(round(float(feats[clip_layer_name + '_pc'] * land_exclusion_percentage), 1)) # area utilised in %
                                                    ]

                # Retrieve summary statistics {0. Area utilised, 1. Area of feature (e.g. ward), 2. % Area utilised, 3. no of panels, 4. tilt angle, 5. orientation, 6. energy output, 7. inter-row spacing}
                stats = {}
                for feats in pv_layer.getFeatures():
                    stats[feats[area_field]] = [area_stats[feats[area_field]][0], #area utilised
                                                area_stats[feats[area_field]][1], # area of feature (e.g. ward)
                                                area_stats[feats[area_field]][2], # area utilised in %
                                                int(feats['ID']), #ID 
                                                str(feats[area_field]), # Name
                                                int(feats['Tilt Angle']), # Tilt angle
                                                int(feats['Orientation']), # Orientation
                                                int(feats['Energy (kWh)']), # Energy output
                                                float(feats['Inter_row']) # Inter-row spacing
                                                ]
                
                # Get units
                units_dict = {u'm\u00B2': 'm<sup>2</sup>', u'km\u00B2': 'km<sup>2</sup>', 'acre': 'acre', 'ha': 'ha'}
                units = units_dict[self.land_availability_dockwidget.areaUnits_combo_2.currentText()]

                summary = ''

                if self.pv_generation_dockwidget.areaSummary_GroupBox.isChecked():
                    summary += str(
                    '---<br>' +
                    '<b>Output</b>' +
                    '<br>Number of dwellings equivalent: ' + str("<b>{:,.0f}".format(sum(item[1] for item in energy_stats.values()) / house_consumption)) + "</b>" +
                    '<br>Number of panels: ' + str("<b>{:,.0f}".format(no_of_features)) + "</b>"
                    )

                    total_power_generation = sum(item[1] for item in energy_stats.values())
                    if total_power_generation < 100000:
                        summary += str('<br>Total power generation (kWh): ' + str("<b>{:,.0f}".format(total_power_generation)) + "</b><br><br>")
                    else:
                        summary += str('<br>Total power generation (MWh): ' + str("<b>{:,.0f}".format(float(total_power_generation / 1000))) + "</b><br><br>")
                
                # Prepare text
                if mode == 'custom_mode':
                    summary += str(
                                '<b>ID ' +\
                                '| Name ' +\
                                '| Area utilised/Area of Ward (' + str(units) + ')' + \
                                '| No of dwellings' +\
                                '| No of panels ' +\
                                '| Energy yield (MWh)</b><br><br>'
                                )

                    for x in stats:
                        # 0 = area utilised, 1 = area of ward, 2 = percentage utilisaed, 3 = ID, 4 = area_field, 5 = tilt angle, 6 = orientation, 7 = energy, 8 = inter-row spacing
                        #print( str(stats[x][0]),  str(stats[x][1]),  str(stats[x][2]),  str(stats[x][3]), str(stats[x][4]), str(stats[x][5]), str(stats[x][6]), str(stats[x][7]))
                        summary += str(
                                    str(stats[x][3]) + \
                                    ' <b>|</b> ' + str(stats[x][4]) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(stats[x][0]))) + '/' + str("{:,.0f}".format(stats[x][1])) + ' (' + str(stats[x][2]) + ' %)' + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][1] / house_consumption))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][0]))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][1] / 1000))) + \
                                    '<br>'
                                    )
                else:
                    summary += str(
                                '<b>ID ' +\
                                '| Name ' +\
                                '| Area utilised/Area of Ward (m<sup>2</sup>) ' +\
                                '| Tilt angle ' +\
                                '| Orientation ' +\
                                '| No of dwellings ' +\
                                '| No of panels ' +\
                                '| Energy yield (MWh/y) '+\
                                '| Inter-row spacing</b><br><br>'
                                )

                    for x in stats:
                        summary += str(
                                    str(stats[x][3]) + \
                                    ' <b>|</b> ' + str(stats[x][4]) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(stats[x][0]))) + '/' + str("{:,.0f}".format(stats[x][1])) + ' (' + str(stats[x][2]) + ' %)' + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(stats[x][5]))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(stats[x][6]))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][1] / house_consumption))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][0]))) + \
                                    ' <b>|</b> ' + str("{:,.0f}".format(int(energy_stats[str(x)][1] / 1000))) + \
                                    ' <b>|</b> ' + str("{:,.1f}".format(float(stats[str(x)][8]))) + \
                                    '<br>'
                                    )

                summary += '<br><br>'
                # Output results to energy yield estimator textbox
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(summary)
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)

                # Remove temporary layers
                del memory_lyr
                del dissolve_layer
                del clip_layer
                del area_stats_layer
                del join_layer
                del delete_dup_layer

            else:
                QgsProject.instance().addMapLayer(memory_lyr, False)
                information_group.insertChildNode(0, QgsLayerTreeLayer(memory_lyr))
                information_group.setExpanded(True)
                # Set memory_lyr to go at top of layer order panel
                order = root.customLayerOrder()
                for i, o in enumerate(order):
                    if o.name() == memory_lyr.name():
                        order.insert(0, order.pop(i))
                root.setCustomLayerOrder(order)

                # Set colour and refresh
                memory_lyr.loadNamedStyle(self.plugin_dir + '/styles/pv_panel_style_2.qml')
                memory_lyr.triggerRepaint()
                self.iface.layerTreeView().refreshLayerSymbology(memory_lyr.id())
                self.iface.layerTreeView().setLayerVisible(memory_lyr, True)
                self.iface.mapCanvas().refresh()

            # Reconnect move_added_layer_to_information() function
            QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)
            
            # Close configuration
            self.pv_generation_dockwidget.close()
        # If no features are available, show warning message
        else:
            self.iface.messageBar().pushMessage("", 'No areas of opportunity available.', Qgis.Warning, 5)
            # Close configuration
            self.pv_generation_dockwidget.close()



#-------------------------------Return single/multiple optimal output paramters--------------------------------------------------------
    def optimal_PV_output_values(self, min_value, max_value):
        if min_value == max_value:
            return str(min_value)
        else:
            return str(min_value) + ' - ' + str(max_value)

#-------------------------------"Generate PV arrays" create panel arrays--------------------------------------------------------
    def PV_panel_size(self, length, width, x, y):
        # length & width measured in m; x & y measured in m
        l = float(length / 2)
        w = float(width / 2)
        return QgsGeometry.fromRect(QgsRectangle(x - w, y - l, x + w, y + l))


#-------------------------------Solar PV calculations-------------------------------------------
    def solarPV_eneryCalculation(self, length_value, width_value, pstc, no_of_features_value, tilt_angle, orientation_angle, inter_row_distance, energy_value, energy_sum, house_consumption_value, original_land_exclusion, mode):
        # Read energy parameters
        length = float(length_value)
        width = float(width_value)
        Pstc = pstc
        no_of_features = float(no_of_features_value)
        area_of_array = float(length) * float(width)
        optimal_tilt_angle = str(tilt_angle)
        orientation = str(orientation_angle)
        inter_row_spacing = str(inter_row_distance)
        energy = str(energy_value)
        total_power_generation = int(energy_sum)
        land_exclusion_for_report = int(original_land_exclusion)
        house_consumption = int(house_consumption_value)

        # Power
        #total_power_generation = no_of_features * power
        # House equivalent
        house_equivalent = int(total_power_generation / house_consumption)

        stats = str(
            '<b>PV specification (' + str(mode.capitalize().replace('_',' ')) + ')</b>' +
            '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(house_consumption)) +
            '<br>Power output (kWh/y): ' + energy +
            '<br>Length, Width (m): ' + str("{:,.1f}".format(length)) + ', ' + str("{:,.1f}".format(width)) +
            '<br>P<sub>STC</sub> (W): ' + str(Pstc) +
            '<br>Optimal tilt angle (<sup>o</sup>): ' + optimal_tilt_angle +
            '<br>Orientation (<sup>o</sup>): ' + orientation +
            '<br>Inter-row spacing (m): ' + inter_row_spacing +
            #'<br>Horizontal panel spacing (m): ' + str("{:,.1f}".format(self.pv_generation_dockwidget.distance_x_doubleSpinBox.value())) +
            '<br>'
            )

        if not self.pv_generation_dockwidget.areaSummary_GroupBox.isChecked():
            stats += str(
            '---<br>' +
            '<b>Output</b>' +
            '<br>Number of dwellings equivalent: ' + str("<b>{:,.0f}".format(house_equivalent)) + "</b>" +
            '<br>Number of panels: ' + str("<b>{:,.0f}".format(no_of_features)) + "</b>"
            )

            if total_power_generation < 100000:
                stats += str('<br>Total power generation (kWh): ' + str("<b>{:,.0f}".format(total_power_generation)) + "</b><br><br>")
            else:
                stats += str('<br>Total power generation (MWh): ' + str("<b>{:,.0f}".format(float(total_power_generation / 1000))) + "</b><br><br>")

        first_stats, second_stats = self.read_PV_model(None)
        area_of_panel = '<br>Area of panel (m<sup>2</sup>): ' + str(area_of_array)
        stats += first_stats + area_of_panel + second_stats

        # Output results to Report
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)


#-------------------------------"Generate N-S facing sites" options--------------------------------------------
    def generate_northerly_southerly_sites_configuration(self):
        # Define groups
        information_group = self.General.identify_group_state('Additional information')
        # Define comboboxes
        dsm_layer_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.dsmLayer_combobox
        site_layer_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.siteLayer_combobox
        orientation_selection = self.pv_generate_northerly_southerly_sites_dockwidget.orientation_combobox
        # Define buttons
        generate_button = self.pv_generate_northerly_southerly_sites_dockwidget.generate_pushButton
        close_button = self.pv_generate_northerly_southerly_sites_dockwidget.close_pushButton
        progress_bar = self.pv_generate_northerly_southerly_sites_dockwidget.progressBar
        # Set progress bar
        progress_bar.setValue(0)

        # Set orientation combobox
        orientation_selection.clear()
        orientation_selection.addItems(['Northerly', 'Southerly'])

        # Get relevant raster layers
        rLayers = [layer.name() for layer in QgsProject.instance().mapLayers().values() if layer.type() == QgsMapLayer.RasterLayer]

        # Get relevant vector layers
        layers_list = []
        for child in information_group.children():
            if isinstance(child, QgsLayerTreeLayer):
                try:
                    if child.layer().geometryType() == QgsWkbTypes.PolygonGeometry:
                        layers_list.append(child.name())
                except AttributeError:
                    pass

        # Disconnect signals/slots
        try:
            generate_button.clicked.disconnect(self.generate_northerly_southerly_sites)
        except TypeError:
            pass
        try:
            close_button.clicked.disconnect(self.close_northerly_southerly_sites_generation)
        except TypeError:
            pass
        try:
            site_layer_combobox.currentIndexChanged.disconnect(self.get_site_fields)
        except TypeError:
            pass

        # Populate dsm combobox
        dsm_layer_combobox.clear()
        dsm_layer_combobox.addItems(rLayers)
        # Populate building combobox
        site_layer_combobox.clear()
        site_layer_combobox.addItems(layers_list)

        index = site_layer_combobox.findText('building', QtCore.Qt.MatchFixedString | QtCore.Qt.MatchContains)
        if index >= 0:
            site_layer_combobox.setCurrentIndex(index)

        # Get building fields from layer
        self.get_site_fields()

        # Connect signals/slots
        generate_button.clicked.connect(self.generate_northerly_southerly_sites)
        close_button.clicked.connect(self.close_northerly_southerly_sites_generation)
        site_layer_combobox.currentIndexChanged.connect(self.get_site_fields) 

        self.pv_generate_northerly_southerly_sites_dockwidget.show()


#-------------------------------"Generate N-S facing Sites" close--------------------------------------------
    def close_northerly_southerly_sites_generation(self):
        self.pv_generate_northerly_southerly_sites_dockwidget.close()


#-------------------------------Get building layer--------------------------------------------
    def get_site_fields(self):
        selected_layer_name = self.pv_generate_northerly_southerly_sites_dockwidget.siteLayer_combobox.currentText()
        siteField_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.siteField_combobox
        try:
            selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]
            field_names = [field.name() for field in selectedLayer.fields()]
            siteField_combobox.clear()
            siteField_combobox.addItems(field_names)
            index = siteField_combobox.findText('id', QtCore.Qt.MatchFixedString | QtCore.Qt.MatchContains)
            if index >= 0:
                siteField_combobox.setCurrentIndex(index)
        except IndexError:
            self.pv_generate_northerly_southerly_sites_dockwidget.siteField_combobox.clear()


#-------------------------------Run "Generate N-S facing sites"--------------------------------------------
    def generate_northerly_southerly_sites(self):
        # Define root
        root = QgsProject.instance().layerTreeRoot()
        # Define groups     
        information_group = self.General.identify_group_state('Additional information')
        # Define comboboxes
        dsm_layer_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.dsmLayer_combobox
        site_layer_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.siteLayer_combobox
        field_combobox = self.pv_generate_northerly_southerly_sites_dockwidget.siteField_combobox
        progress_bar = self.pv_generate_northerly_southerly_sites_dockwidget.progressBar
        # Get orientation selection
        orientation_selection = self.pv_generate_northerly_southerly_sites_dockwidget.orientation_combobox.currentText()
        # Define rule paths
        rules = {
                'Northerly': [0,45,1,315,360,1],
                'Southerly': [135,225,1]
                }
        # Get selected rule path
        orientation = rules[orientation_selection]
        # Get Additional information path
        information_path = QgsProject.instance().readPath("./") + '/Additional information/'
        # Define output path
        output_path = str(information_path) + str(orientation_selection) + ' sites for ' + str(site_layer_combobox.currentText()) + '.shp'
        # Create error check and messages
        error_check = []
        error_messages = {1: 'Load DSM layer', 2: 'Load polygon site layer'}
        # Define and connect progress feedback from processing tool to interface
        f = QgsProcessingFeedback()
        f.progressChanged.connect(partial(self.General.progress_changed, progress_bar))
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Disconnect move_added_layer_to_information() function
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.General.move_added_layer_to_information)
        except TypeError:
            pass

        if len(dsm_layer_combobox) == 0:
            error_check.append(error_messages[1])
        if len(site_layer_combobox) == 0:
            error_check.append(error_messages[2])

        if error_check:
            self.iface.messageBar().pushMessage("", ' + '.join(error_check), Qgis.Warning, 3)
        else:
            progress_bar.setValue(0)
            progress_bar.setMaximum(10)
            # Define layers
            dsm_layer = QgsProject.instance().mapLayersByName( dsm_layer_combobox.currentText() )[0]
            site_layer = QgsProject.instance().mapLayersByName( site_layer_combobox.currentText() )[0]
            # Get building ID field
            # NOTE: MUST BE SINGLE WORD (i.e. "Primary ID" must be changed to "PrimaryID" before running tool)
            site_field = field_combobox.currentText()
            # Get dsm crs
            dsm_crs = dsm_layer.crs().toProj4()
            # Use CRS of city shapefile
            for fname in glob.glob(QgsProject.instance().readPath("./") + '/Processing scripts/Shapefile conversion/City/*.shp'):
                crs = QgsVectorLayer( fname, '', 'ogr' ).crs().authid()
            ###############
            # Begin process
            #
            # 1. Aspect
            output_aspect = processing.run("gdal:aspect", 
                                        {'INPUT':dsm_layer,
                                        'BAND':1,
                                        'TRIG_ANGLE':False,
                                        'ZERO_FLAT':True,
                                        'COMPUTE_EDGES':False,
                                        'ZEVENBERGEN':False,
                                        'OPTIONS':'',
                                        'EXTRA':'',
                                        'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 2. Get extent of aspect output
            aspect_raster = QgsVectorLayer(output_aspect['OUTPUT'], '', "ogr" )
            extent = aspect_raster.extent()
            xmin = extent.xMinimum()
            xmax = extent.xMaximum()
            ymin = extent.yMinimum()
            ymax = extent.yMaximum()
            aspect_extent = "%f,%f,%f,%f [%s]"% (xmin, xmax, ymin, ymax, crs)
            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 3. Reclass
            output_reclass = processing.run("native:reclassifybytable", 
                                        {'INPUT_RASTER':output_aspect['OUTPUT'],
                                        'RASTER_BAND':1,
                                        'TABLE':orientation,
                                        'NO_DATA':-9999,
                                        'RANGE_BOUNDARIES':0,
                                        'NODATA_FOR_MISSING':True,
                                        'DATA_TYPE':5,
                                        'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 4. Warp (Reproject)
            output_reproject = processing.run("gdal:warpreproject", 
                                        {'INPUT':output_reclass['OUTPUT'],
                                        'SOURCE_CRS':dsm_crs,
                                        'TARGET_CRS':crs,
                                        'RESAMPLING':0,
                                        'NODATA':-9999,
                                        'TARGET_RESOLUTION':None,
                                        'OPTIONS':'',
                                        'DATA_TYPE':0,
                                        'TARGET_EXTENT':aspect_extent,
                                        'TARGET_EXTENT_CRS':None,
                                        'MULTITHREADING':True,
                                        'EXTRA':'',
                                        'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 5. Field calculator - create new field with value of 1
            output_field_calculator = processing.run("qgis:fieldcalculator", 
                                                {'INPUT':site_layer,
                                                'FIELD_NAME':'diss_field',
                                                'FIELD_TYPE':1,
                                                'FIELD_LENGTH':1,
                                                'FIELD_PRECISION':0,
                                                'NEW_FIELD':True,
                                                'FORMULA':'1',
                                                'OUTPUT':'memory:'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 6. Dissolve site polygons - with value of 1
            output_dissolve = processing.run("native:dissolve", 
                        {'INPUT':output_field_calculator['OUTPUT'],
                        'FIELD':['diss_field'],
                        'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 7. Clip warped raster - with dissolved polygons
            output_clip = processing.run("gdal:cliprasterbymasklayer", 
                                    {'INPUT':output_reproject['OUTPUT'],
                                    'MASK':output_dissolve['OUTPUT'],
                                    'SOURCE_CRS':None,
                                    'TARGET_CRS':None,
                                    'NODATA':None,
                                    'ALPHA_BAND':False,
                                    'CROP_TO_CUTLINE':True,
                                    'KEEP_RESOLUTION':False,
                                    'SET_RESOLUTION':False,
                                    'X_RESOLUTION':None,
                                    'Y_RESOLUTION':None,
                                    'MULTITHREADING':True,
                                    'OPTIONS':'',
                                    'DATA_TYPE':0,
                                    'EXTRA':'',
                                    'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 8. Polygonise clipped raster
            output_polygonize = processing.run("gdal:polygonize", 
                                        {'INPUT':output_clip['OUTPUT'],
                                        'BAND':1,
                                        'FIELD':'DN',
                                        'EIGHT_CONNECTEDNESS':False,
                                        'EXTRA':'',
                                        'OUTPUT':'TEMPORARY_OUTPUT'})

            progress_bar.setValue(progress_bar.value() + 1)
            #
            # 9. Intersect new polygon layer with site layer
            output_intersect = processing.run("saga:intersect", 
                                        {'A':output_polygonize['OUTPUT'],
                                        'B':site_layer,
                                        'SPLIT':True,
                                        'RESULT':'TEMPORARY_OUTPUT'})
            
            #
            # 10. Repair and dissolve intersect layer - with value of chosen field            
            output_repair = processing.run("native:fixgeometries", 
                                        {'INPUT':output_intersect['RESULT'],
                                        'OUTPUT':'TEMPORARY_OUTPUT'})
            
            progress_bar.setValue(progress_bar.value() + 1)

            output_result = processing.run("native:dissolve", 
                        {'INPUT':output_repair['OUTPUT'],
                        'FIELD':[str(site_field)],
                        'OUTPUT':output_path})
            
            progress_bar.setValue(progress_bar.value() + 1)

            # Load output
            result = QgsVectorLayer(output_path, os.path.splitext(os.path.basename(output_path))[0], "ogr" )
            QgsProject.instance().addMapLayer(result, False)
            result.loadNamedStyle(self.plugin_dir + '/styles/sites.qml')
            information_group.insertChildNode(-1, QgsLayerTreeLayer(result))
            # Set output layer to go at top of layer order panel
            order = root.customLayerOrder()
            for i, o in enumerate(order):
                if o.name() == result.name():
                    order.insert(0, order.pop(i))
            root.setCustomLayerOrder(order)
            #
            #End process
            ###############

            # Delete temporary outputs
            del output_aspect
            del output_reclass
            del output_reproject
            del output_field_calculator
            del output_dissolve
            del output_clip
            del output_polygonize
            del output_intersect
            del output_repair
            del output_result
            # Close dockwidget
            self.pv_generate_northerly_southerly_sites_dockwidget.close()

        # Reconnect move_added_layer_to_information() function
        QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)
        QApplication.restoreOverrideCursor()