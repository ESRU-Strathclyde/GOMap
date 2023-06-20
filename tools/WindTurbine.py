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
import os, processing
from qgis.core import QgsProject, QgsField, QgsVectorLayer, edit, QgsFeature, QgsGeometry, QgsProcessingFeedback, QgsSvgMarkerSymbolLayer, \
QgsSimpleMarkerSymbolLayer, QgsLayerTreeLayer, QgsProcessingFeatureSourceDefinition
from qgis.utils import iface
from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import QVariant
from math import ceil
from functools import partial

# Import resources from dockwidgets
from ..dockwidgets.configure_wind_dockwidget import configure_wind
from ..dockwidgets.wind_generation_dockwidget import wind_generation

from .General import General
from .TechnologyFunctions import TechFunctions


class WIND:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.configure_wind_dockwidget = configure_wind()
        self.wind_generation_dockwidget = wind_generation()

        # Reference General class
        self.General = General(None)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')



#-------------------------------"Configure" options-------------------------------------------------------
    def configure_WIND_tools(self):
        ok_button = self.configure_wind_dockwidget.ok_pushButton
        reset_button = self.configure_wind_dockwidget.reset_pushButton

        try:
            ok_button.clicked.disconnect(self.configure_WIND_tools_OK)
        except TypeError:
            pass
        try:
            reset_button.clicked.disconnect(self.configure_WIND_tools_reset)
        except TypeError:
            pass

        ok_button.clicked.connect(self.configure_WIND_tools_OK)
        reset_button.clicked.connect(self.configure_WIND_tools_reset)
        
        self.configure_wind_dockwidget.show()


#-------------------------------"Configure" OK button-------------------------------------------------------
    def configure_WIND_tools_OK(self):
        self.configure_wind_dockwidget.close()
        self.TechFunctions.populate_EnergyYieldEstimator()
        # Output specification from configure dockwidget

        # Read energy parameters
        house_consumption = float(self.configure_wind_dockwidget.houseConsumption_spinBox.value())
        wind_speed = float(self.configure_wind_dockwidget.windSpeed_spinBox.value())
        turbine_efficiency = float(self.configure_wind_dockwidget.turbineEfficiency_spinBox.value())
        
        # Energy Yield
        # Rotor is set to a constant as we are calculating wind power density, the swept area value cancels out in the power and power_density equations
        rotor = 1
        air_density = 1.23
        swept_area = float(3.14 * (rotor / 2)**2)
        efficiency_percentage = float(turbine_efficiency) / float(100)        
        power = float(0.5 * float(air_density) * float(swept_area) * (wind_speed**3) * efficiency_percentage)
        # Convert power (W) into energy (kWh)
        energy_generation = float(power * (24 * 365)) / float(1000)

        # Power density
        power_density = float(energy_generation) / float(swept_area)
        
        stats = str(
            '<b>Wind specification</b>' +
            '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(house_consumption)) +
            '<br>Average wind speed (m/s): ' + str(int(wind_speed)) +
            '<br>Turbine efficiency (%): ' + str("{:,.1f}".format(turbine_efficiency)) +
            '<br>Power density kW/m<sup>2</sup>: ' + str("{:,.1f}".format(power_density)) +
            '<br><br>'
            )
        # Output stats to energy yield estimator textbox
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)


#-------------------------------"Configure" Reset button-------------------------------------------------------
    def configure_WIND_tools_reset(self):
        # Reset to default settings
        self.configure_wind_dockwidget.windSpeed_spinBox.setValue(5)
        self.configure_wind_dockwidget.turbineEfficiency_spinBox.setValue(30)
        self.configure_wind_dockwidget.houseConsumption_spinBox.setValue(9500)


#-------------------------------"Generate wind turbines" options-------------------------------------------------------
    def generate_WIND_turbines_configuration(self):
        # Define buttons and label
        generate_button = self.wind_generation_dockwidget.generate_pushButton
        close_button = self.wind_generation_dockwidget.close_pushButton
        progress_bar = self.wind_generation_dockwidget.progressBar

        # Define parameters from configuration
        house_consumption = self.configure_wind_dockwidget.houseConsumption_spinBox.value()
        wind_speed = self.configure_wind_dockwidget.windSpeed_spinBox.value()
        turbine_efficiency = self.configure_wind_dockwidget.turbineEfficiency_spinBox.value()

        # Set wind turbine generation settings
        self.wind_generation_dockwidget.houseConsumption_spinBox.setValue(house_consumption)
        self.wind_generation_dockwidget.windSpeed_spinBox.setValue(wind_speed)
        self.wind_generation_dockwidget.turbineEfficiency_spinBox.setValue(turbine_efficiency)

        # Set progress bar
        progress_bar.setValue(0)

        try:
            generate_button.clicked.disconnect(self.generate_WIND_turbines)
        except TypeError:
            pass
        try:
            close_button.clicked.disconnect(self.close_WIND_generation)
        except TypeError:
            pass

        generate_button.clicked.connect(self.generate_WIND_turbines)
        close_button.clicked.connect(self.close_WIND_generation)

        self.wind_generation_dockwidget.show()


#-------------------------------"Generate wind turbines" Cancel button-------------------------------------------------------
    def close_WIND_generation(self):
        # Close wind turbine generation interface when clicked on Close
        self.wind_generation_dockwidget.close()


#-------------------------------Run "Generate wind turbines"-------------------------------------------------------
    def generate_WIND_turbines(self):
        # Define textboxes and buttons
        rotor = int(self.wind_generation_dockwidget.rotor_spinbox.value())
        spacing = int(self.wind_generation_dockwidget.spacing_spinbox.value())
        wind_speed = float(self.wind_generation_dockwidget.windSpeed_spinBox.value())
        turbine_efficiency = float(self.wind_generation_dockwidget.turbineEfficiency_spinBox.value())
        house_consumption = float(self.wind_generation_dockwidget.houseConsumption_spinBox.value())

        # Define buttons and progress bar
        generate_button = self.wind_generation_dockwidget.generate_pushButton
        close_button = self.wind_generation_dockwidget.close_pushButton
        progress_bar = self.wind_generation_dockwidget.progressBar

        # Disconnect move_added_layer_to_information() function
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.General.move_added_layer_to_information)
        except TypeError:
            pass

        # Define opportunity map layer
        opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        # Get opportunity map features
        features = self.TechFunctions.land_area('opportunity_features')
        feat = [f.id() for f in features]
        areas = [f.geometry().area() for f in features]
        max_area = max(areas)
        value = ceil(float(max_area) / float(3.14 * (spacing / 2)**2))
        opportunity_layer.selectByIds(feat)

        # Define and connect progress feedback from processing tool to interface
        f = QgsProcessingFeedback()
        f.progressChanged.connect(partial(self.General.progress_changed, progress_bar))

        result = processing.run("qgis:randompointsinsidepolygons", 
            {'INPUT':QgsProcessingFeatureSourceDefinition(opportunity_layer.id(), True),
            'STRATEGY': 0,
            'VALUE': value,
            'MIN_DISTANCE': float(spacing * 2),
            'OUTPUT': 'TEMPORARY_OUTPUT'},
            feedback = f)

        opportunity_layer.selectByIds([])
        memory_lyr = result['OUTPUT']
        self.wind_turbine_spacing_checker(memory_lyr, rotor, spacing, wind_speed, turbine_efficiency, house_consumption)

#-------------------------------Wind spacing checker-------------------------------------------
    def wind_turbine_spacing_checker(self, layer, rotor, spacing, wind_speed, turbine_efficiency, house_consumption):
        # Define root
        root = QgsProject.instance().layerTreeRoot()
        opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        crs = opportunity_layer.crs()

        # Define scope group
        scope_group = self.General.identify_group_state('Scope')
        
        # Create buffers for points
        poly_layer = QgsVectorLayer("Polygon?crs=epsg:" + unicode(crs.postgisSrid()), 'Buffers' , "memory")
        pr = poly_layer.dataProvider() 
        pr.addAttributes([QgsField("ID", QVariant.Int)])
        feat_list = []
        for f in layer.getFeatures():
            poly = QgsFeature()
            f_buffer = f.geometry().buffer((spacing), 99)
            f_poly = poly.setGeometry(QgsGeometry.fromPolygonXY(f_buffer.asPolygon()))
            poly.setAttributes([1])
            poly.setGeometry(f_buffer)
            feat_list.append(poly)

        pr.addFeatures(feat_list)
        poly_layer.updateExtents()
        poly_layer.updateFields()

        # Get pairs of intersecting buffer features
        features = [feat for feat in poly_layer.getFeatures()]
        ids = []
        for feat in poly_layer.getFeatures():
            for geat in features:
                if feat.id() != geat.id():
                    if geat.geometry().intersects(feat.geometry()):
                        ids.append([feat.id(), geat.id()])

        # Set/sort list and get id of intersecting feature(s)
        for x in ids:
            x.sort()

        ids_sort = set(tuple(x) for x in ids)
        ids_list = [list(x) for x in ids_sort]
        ids_firstItem = [item[0] for item in ids_list]
        final_list = list(set(ids_firstItem))

        # Use ids from final_list to remove intersecting buffer features
        with edit(poly_layer):
            poly_layer.deleteFeatures(final_list)

        # Get name of current scope layer
        for layers in scope_group.children():
            if layers.isVisible():
                name = layers.name()

        # Create new point layer and get centroids from buffers
        # (using final_list to delete the original features may not delete those points where the buffer interesects
        # so best to obtain the centroid of the buffers and output this as a new file)
        result_layer = QgsVectorLayer('Point?crs=epsg:' + unicode(crs.postgisSrid()) + '&field=id:string&index=yes', "Wind turbines for " + str(name) , 'memory')
        result_layer.startEditing()
        for feat in poly_layer.getFeatures():
            centroid = feat.geometry().centroid()
            attribute_name = feat.attribute("ID")
            centroid_feature = QgsFeature(poly_layer.fields())
            centroid_feature.setGeometry(centroid)
            centroid_feature['ID'] = attribute_name
            result_layer.addFeature(centroid_feature)

        result_layer.commitChanges()
        del layer
        del poly_layer

        QgsProject.instance().addMapLayer(result_layer, False)
        information_group = self.General.identify_group_state('Additional information')
        information_group.insertChildNode(0, QgsLayerTreeLayer(result_layer))
        information_group.setExpanded(True)
        # Set result_layer to go at top of layer order panel
        order = root.customLayerOrder()
        for i, o in enumerate(order):
            if o.name() == result_layer.name():
                order.insert(0, order.pop(i))
        root.setCustomLayerOrder(order)
        self.apply_WIND_turbine_style(result_layer, spacing)
        self.iface.layerTreeView().setLayerVisible(result_layer, True)

        self.iface.mapCanvas().refresh()
        self.wind_generation_dockwidget.close()

        no_of_features = result_layer.featureCount()

        self.WIND_turbine_eneryCalculation(rotor, spacing, no_of_features, wind_speed, turbine_efficiency, house_consumption)

        # Reconnect move_added_layer_to_information() function
        QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)


#-------------------------------Wind Turbine calculations-------------------------------------------
    def WIND_turbine_eneryCalculation(self, rotor_value, spacing_value, no_of_features_value, wind_speed_value, turbine_efficiency_value, house_consumption_value):
        # Read energy parameters
        rotor = float(rotor_value)
        spacing = float(spacing_value)
        no_of_features = int(no_of_features_value)
        wind_speed = float(wind_speed_value)
        turbine_efficiency = float(turbine_efficiency_value)
        house_consumption = float(house_consumption_value)

        # Energy Yield
        air_density = 1.23
        swept_area = float(3.14 * (rotor / 2)**2)
        efficiency_percentage = float(turbine_efficiency) / float(100)        
        power = float(0.5 * air_density * swept_area * (wind_speed**3) * efficiency_percentage)
        energy_generation = float(power * (24 * 365)) / float(1000000)
        power_density = float(energy_generation) / float(swept_area)
        total_energy_generation = float(no_of_features * energy_generation)

        # House equivalent
        house_equivalent = int((total_energy_generation * 1000) / house_consumption)

        stats = str(
            '<b>Wind specification</b>' +
            '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(self.wind_generation_dockwidget.houseConsumption_spinBox.value())) +
            '<br>Rotor diameter (m): ' + str(int(rotor)) +
            '<br>Spacing between turbines (m): ' + str(int(spacing)) +
            '<br>Wind speed (m/s): ' + str(int(wind_speed)) +
            '<br>Turbine efficiency (%): ' + str(int(turbine_efficiency)) +
            '<br>Power density kW/m<sup>2</sup>: ' + str("{:,.1f}".format(power_density * 1000)) +
            '<br>' +
            '---<br>' +
            '<b>Output</b>' +
            '<br>Number of turbines: ' + str("<b>{:,.0f}".format(no_of_features)) + "</b>" +
            '<br>Energy yield (MWh/yr): ' + str("<b>{:,.0f}".format(total_energy_generation)) + "</b>" +
            '<br>Number of dwellings equivalent: ' + str("<b>{:,}".format(house_equivalent)) + "</b>" +
            '<br><br>'
            )

        # Output results to Report
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)


#-------------------------------Apply wind turbine marker + svg style-------------------------------------------------------
    def apply_WIND_turbine_style(self, input_layer, spacing):
        layer = input_layer
        # Create wind turbine marker symbol
        svgStyle = {'name': str(self.plugin_dir) + '/styles/wind_turbine.svg',
                     'size': str(100),
                     'size_unit': 'MapUnit'}
        svg_symbol = QgsSvgMarkerSymbolLayer.create(svgStyle)
        symbol = layer.renderer().symbol()
        symbol.changeSymbolLayer(0, svg_symbol)

        # Create boundary marker symbol
        properties = {'size': str(float(spacing) * float(2)),
                      'size_unit': 'MapUnit', 
                      'color': '0,0,0,0', 
                      'outline': '255,255,255,255'}
        symbol_layer = QgsSimpleMarkerSymbolLayer.create(properties)

        lineSym = layer.renderer().symbol()
        lineSym.appendSymbolLayer(symbol_layer)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())
