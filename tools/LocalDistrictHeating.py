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
from time import sleep
from math import ceil
from qgis.core import QgsProject, QgsField, QgsVectorLayer, edit, Qgis, QgsFeature, QgsSvgMarkerSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsLayerTreeLayer, \
QgsWkbTypes, QgsProcessingFeatureSourceDefinition
from qgis.utils import iface
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import QVariant

# Import resources from dockwidgets
from ..dockwidgets.ldh_generation_dockwidget import ldh_generation

from .General import General
from .TechnologyFunctions import TechFunctions


class LDH:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.ldh_generation_dockwidget = ldh_generation()

        # Reference General class
        self.General = General(None)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')


#-------------------------------"Generate local district heating" options-------------------------------------------------------
    def generate_LDH_configuration(self):
        # Define groups
        information_group = self.General.identify_group_state('Additional information')
        # Define comboboxes
        building_layer_combobox = self.ldh_generation_dockwidget.buildingLayer_combobox
        # Define buttons
        generate_button = self.ldh_generation_dockwidget.generate_pushButton
        close_button = self.ldh_generation_dockwidget.close_pushButton
        progress_bar = self.ldh_generation_dockwidget.progressBar

        # Set local district heating generation settings
        self.ldh_generation_dockwidget.proximity_spinBox.setValue(5.0)
        self.ldh_generation_dockwidget.capacity_spinBox.setValue(200.0)
        self.ldh_generation_dockwidget.capacity_spinBox.setValue(3)
        self.ldh_generation_dockwidget.heatLoss_spinBox.setValue(10)

        # Set progress bar
        progress_bar.setValue(0)

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
            generate_button.clicked.disconnect(self.generate_LDH)
        except TypeError:
            pass
        try:
            close_button.clicked.disconnect(self.close_LDH_generation)
        except TypeError:
            pass
        try:
            building_layer_combobox.currentIndexChanged.disconnect()
        except TypeError:
            pass

        # Populate building combobox
        building_layer_combobox.clear()
        building_layer_combobox.addItems(layers_list)

        index = building_layer_combobox.findText('building', QtCore.Qt.MatchFixedString | QtCore.Qt.MatchContains)
        if index >= 0:
            building_layer_combobox.setCurrentIndex(index)

        # Get building fields from layer
        self.get_building_fields()

        # Connect signals/slots
        generate_button.clicked.connect(self.generate_LDH)
        close_button.clicked.connect(self.close_LDH_generation)
        building_layer_combobox.currentIndexChanged.connect(self.get_building_fields)

        self.ldh_generation_dockwidget.show()


#-------------------------------"Generate local district heating" close--------------------------------------------
    def close_LDH_generation(self):
        self.ldh_generation_dockwidget.close()


#-------------------------------Get building layer--------------------------------------------
    def get_building_fields(self):
        selected_layer_name = self.ldh_generation_dockwidget.buildingLayer_combobox.currentText()
        buildingfield_combobox = self.ldh_generation_dockwidget.buildingfield_combobox
        try:
            selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]
            field_names = [field.name() for field in selectedLayer.fields()]
            buildingfield_combobox.clear()
            buildingfield_combobox.addItems(field_names)
            index = buildingfield_combobox.findText('heat', QtCore.Qt.MatchFixedString | QtCore.Qt.MatchContains)
            if index >= 0:
                buildingfield_combobox.setCurrentIndex(index)
        except IndexError:
            self.ldh_generation_dockwidget.buildingfield_combobox.clear()


#-------------------------------Run "Generate local district heating"--------------------------------------------
    def generate_LDH(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        information_group = root.findGroup('Additional information')
        scope_group = root.findGroup('Scope')

        # Define textboxes and buttons
        proximity = float(self.ldh_generation_dockwidget.proximity_spinBox.value() * 1000)
        capacity = float(self.ldh_generation_dockwidget.capacity_spinBox.value() * 1000)
        cop = float(self.ldh_generation_dockwidget.cop_spinBox.value())
        heat_loss = float(self.ldh_generation_dockwidget.heatLoss_spinBox.value())

        energy_loss = float((float(100) - heat_loss) / 100)
        energy_generation = float(capacity * (365 * 24) * energy_loss)

        # Define buttons and label
        generate_button = self.ldh_generation_dockwidget.generate_pushButton
        close_button = self.ldh_generation_dockwidget.close_pushButton
        progress_bar = self.ldh_generation_dockwidget.progressBar

        # Disconnect move_added_layer_to_information() function
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.General.move_added_layer_to_information)
        except TypeError:
            pass

        # Get building fields from layer
        #self.generate_LDH_configuration()
        #self.close_LDH_generation()
        # Define opportunity map layer
        opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        # Get opportunity map features
        features = self.TechFunctions.land_area('opportunity_features')
        # Set progress bar
        progress_bar.setMaximum(100)

        # Set memory layer the same CRS as the source layer
        crs = opportunity_layer.crs()

        # Define variables
        feat = [f.id() for f in features]
        areas = [f.geometry().area() for f in features]
        max_area = max(areas)
        value = ceil(float(max_area) / float(3.14 * (proximity / 2)**2))
        opportunity_layer.selectByIds(feat)

        selected_layer_name = self.ldh_generation_dockwidget.buildingLayer_combobox.currentText()
        building_layer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]
        building_field = self.ldh_generation_dockwidget.buildingfield_combobox.currentText()

        # Create points
        result = processing.run("qgis:randompointsinsidepolygons", 
            {'INPUT':QgsProcessingFeatureSourceDefinition(opportunity_layer.id(), True),
            'STRATEGY': 0,
            'VALUE': value,
            'MIN_DISTANCE': float(proximity * 2),
            'OUTPUT': 'TEMPORARY_OUTPUT'})

        opportunity_layer.selectByIds([])
        point_layer = result['OUTPUT']
        with edit(point_layer):            
            point_layer.addAttribute(QgsField("ID", QVariant.Int))
            point_layer.deleteAttributes([0])
            point_layer.updateExtents()
            point_layer.updateFields()

        progress_bar.setValue(33)
        sleep(5)

        # Create buffer
        buffer_layer = QgsVectorLayer("MultiPolygon?crs=epsg:" + unicode(crs.postgisSrid()), 'Buffers' , "memory")
        with edit(buffer_layer):
            buffer_layer.addAttribute(QgsField('ID', QVariant.Int))
            feat_list = []
            for f in point_layer.getFeatures():
                poly = QgsFeature()
                f_buffer = f.geometry().buffer((proximity / 2), 99)
                poly.setAttributes([1])
                poly.setGeometry(f_buffer)
                feat_list.append(poly)
            buffer_layer.addFeatures(feat_list)
        buffer_layer.updateExtents()
        buffer_layer.updateFields()

        # Get pairs of intersecting buffer features
        features = [feat for feat in buffer_layer.getFeatures()]
        ids = []
        for feat in buffer_layer.getFeatures():
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
        with edit(buffer_layer):
            buffer_layer.deleteFeatures(final_list)

        # Create new point layer and get centroids from buffers
        # (using final_list to delete the original features may not delete those points where the buffer interesects
        # so best to obtain the centroid of the buffers and output this as a new file)
        result_layer = QgsVectorLayer('Point?crs=epsg:' + unicode(crs.postgisSrid()) + '&field=id:string&index=yes', 'Local district heating network' , 'memory')
        result_layer.startEditing()
        for feat in buffer_layer.getFeatures():
            centroid = feat.geometry().centroid()
            name = feat.attribute("ID")
            centroid_feature = QgsFeature(buffer_layer.fields())
            centroid_feature.setGeometry(centroid)
            centroid_feature['ID'] = name
            result_layer.addFeature(centroid_feature)

        result_layer.commitChanges()

        # Intersect with polygon
        #features = [feat for feat in building_layer.getFeatures()]
        ids = []
        for buffers in buffer_layer.getFeatures():
            for polygons in building_layer.getFeatures():
                if buffers.geometry().intersects(polygons.geometry()):
                    ids.append(polygons)

        del buffer_layer
        del point_layer
        progress_bar.setValue(66)
        sleep(5)

        # Get intersection
        intersect_layer = QgsVectorLayer("MultiPolygon?crs=epsg:" + unicode(crs.postgisSrid()) + "&index=yes", 'Buildings within heating network', "memory")
        # Copy fields
        with edit(intersect_layer):
            for field in building_layer.fields():
                intersect_layer.addAttribute(field)
        # Set field name
        field_name = 'Supply'
        # Set status message to notify user of NULL values in field
        status_message = 0

        with edit(intersect_layer):
            for feat in ids:
                feature = QgsFeature()
                feature.setGeometry(feat.geometry())
                feature.setAttributes(feat.attributes())
                intersect_layer.addFeature(feature)
            intersect_layer.addAttribute(QgsField(field_name, QVariant.Int))
            # Get result
            for point in result_layer.getFeatures():
                heat_generation = energy_generation
                distance_dict = {}
                for polygon in intersect_layer.getFeatures():
                    distance = point.geometry().distance(polygon.geometry())
                    if distance < proximity:
                        distance_dict[polygon] = distance
                distance_list = sorted(distance_dict.keys(), key=(lambda key: distance_dict[key]))
                for feat in distance_list:
                    if feat[building_field]:
                        heat_generation -= float(feat[building_field])
                        if heat_generation >= 0:
                            feat[field_name] = 1
                            intersect_layer.updateFeature(feat)
                        else:
                            feat[field_name] = 0
                            intersect_layer.updateFeature(feat)
                    else:
                        status_message = 1


        # Deselect all features
        intersect_layer.selectByIds([])

        progress_bar.setValue(99)
        sleep(5)

        QgsProject.instance().addMapLayer(intersect_layer, False)
        QgsProject.instance().addMapLayer(result_layer, False)
        result_layer.setName('Local district heating networks')
        information_group.insertChildNode(0, QgsLayerTreeLayer(intersect_layer))
        information_group.insertChildNode(0, QgsLayerTreeLayer(result_layer))
        information_group.setExpanded(True)
        # Set layer to go at top of layer order panel
        order = root.customLayerOrder()
        for i, o in enumerate(order):
            if o.name() == intersect_layer.name():
                order.insert(0, order.pop(i))
            if o.name() == result_layer.name():
                order.insert(0, order.pop(i))
        root.setCustomLayerOrder(order)
        intersect_layer.loadNamedStyle(self.plugin_dir + '/styles/buildings_within_heating_network_style.qml')
        self.apply_LDH__style(result_layer, proximity)
        self.iface.layerTreeView().setLayerVisible(intersect_layer, True)
        self.iface.layerTreeView().setLayerVisible(result_layer, True)
        #iface.layerTreeView().setLayerExpanded(intersect_layer, True)
        root.findLayer(intersect_layer.id()).setExpanded(True)

        progress_bar.setValue(100)
        sleep(1)
        self.iface.mapCanvas().refresh()
        self.ldh_generation_dockwidget.close()

        no_of_networks = result_layer.featureCount()
        no_of_buildings_within_network = intersect_layer.featureCount()
        buildings_suitable_list = []
        for buildings in intersect_layer.getFeatures():
            if buildings[field_name] == 1:
                buildings_suitable_list.append(1)

        no_of_buildings_suitable = len(buildings_suitable_list)

        self.LDH_turbine_eneryCalculation(proximity, no_of_networks, no_of_buildings_within_network, no_of_buildings_suitable, capacity, cop, heat_loss)

        # Reconnect move_added_layer_to_information() function
        QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)

        if status_message == 1:
            self.iface.messageBar().pushMessage("", 'NULL values were found and ignored.', Qgis.Warning, -1)

#-------------------------------Local district heating calculations-------------------------------------------
    def LDH_turbine_eneryCalculation(self, proximity_value, no_of_networks_value, no_of_buildings_network_value, no_of_buildings_suitable_value, 
                                    capacity_value, cop_value, heat_loss_value):
        # Read energy parameters
        buildingLayer = str(self.ldh_generation_dockwidget.buildingLayer_combobox.currentText())
        demandField = str(self.ldh_generation_dockwidget.buildingfield_combobox.currentText())
        proximity = float(proximity_value / 1000)
        no_of_networks = int(no_of_networks_value)
        no_of_buildings_within_network = int(no_of_buildings_network_value)
        no_of_buildings_suitable = int(no_of_buildings_suitable_value)
        capacity = float(capacity_value)
        cop = float(cop_value)
        heat_loss_value = float(heat_loss_value)

        energy_loss = float((float(100) - heat_loss_value) / 100)
        output_energy_generation_kWh = float(no_of_networks * capacity * (365 * 24) * energy_loss)
        output_energy_generation_MWh = float(output_energy_generation_kWh / 1000)
        input_energy_kWh = float(output_energy_generation_kWh / cop)
        input_energy_MWh = float(input_energy_kWh / 1000)

        stats = str(
            '<b>Local district heating network specification</b>' +
            '<br>Building layer: ' + buildingLayer +
            '<br>Demand field: ' + demandField +
            '<br>Proximity (km): ' + str("{:,.1f}".format(proximity)) +
            '<br>Capacity (MW): ' + str(int(capacity / 1000)) +
            '<br>Coefficient of performance (COP): ' + str(int(cop)) +
            '<br>Heat loss (%): ' + str(int(heat_loss_value)) +
            '<br>' +
            '<br>Number of local district heating networks: ' + str("<b>{:,.0f}".format(no_of_networks)) + "</b>" +
            '<br>Energy input (MWh/yr): ' + str("<b>{:,.0f}".format(input_energy_MWh)) + "</b>" +
            '<br>Energy yield (MWh/yr): ' + str("<b>{:,.0f}".format(output_energy_generation_MWh)) + "</b>" +
            '<br>Number of buildings within heating networks: ' + str("<b>{:,.0f}".format(no_of_buildings_within_network)) + "</b>" +
            '<br>Number of buildings supplied: ' + str("<b><font color=\"#21d314\">{:,}".format(no_of_buildings_suitable)) + "</font></b>" +
            '<br>Number of buildings not supplied: ' + str("<b><font color=\"#ff0000\">{:,}".format(no_of_buildings_within_network - no_of_buildings_suitable)) + "</font></b>" +            
            '<br><br>'
            )

        # Output results to Report
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)


#-------------------------------Apply local district heating marker + svg style-------------------------------------------------------
    def apply_LDH__style(self, input_layer, proximity):
        layer = input_layer
        # Create local district heating marker symbol
        svgStyle = {'name': str(self.plugin_dir) + '/styles/local_district_heating.svg',
                     'size': str(12),
                     'size_unit': 'Millimeter'}
        svg_symbol = QgsSvgMarkerSymbolLayer.create(svgStyle)
        symbol = layer.renderer().symbol()
        symbol.changeSymbolLayer(0, svg_symbol)

        # Create boundary marker symbol (Note: this is affected by Projection CRS)
        properties = {'size': str(proximity),
                      'size_unit': 'MapUnit', 
                      'color': '0,0,0,0', 
                      'outline': '255,255,255,255'}
        symbol_layer = QgsSimpleMarkerSymbolLayer.create(properties)

        lineSym = layer.renderer().symbol()
        lineSym.appendSymbolLayer(symbol_layer)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())