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

import datetime, glob, os, processing, re, requests
from requests.exceptions import HTTPError, Timeout
from ..resources import *
from functools import partial
from qgis.core import QgsProject, QgsLayerTree, QgsField, QgsLayerTreeLayer, QgsVectorLayer, QgsVectorFileWriter, edit, QgsMapLayer, QgsLayerTreeGroup, Qgis
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QTextDocument, QFont
from qgis.PyQt.QtWidgets import QAction

# Import resources from dockwidgets
from ..dockwidgets.save_constraint_dockwidget import save_constraint
from ..dockwidgets.save_scope_dockwidget import save_scope
from ..dockwidgets.settings_dockwidget import settings


class General:
    def __init__(self, 
                 settings_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.settings_dockwidget = settings_dockwidget
        self.save_constraint_dockwidget = save_constraint()
        self.save_scope_dockwidget = save_scope()
        
        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')



#-------------------------------Connect and update--------------------------------------
    def update_GOMap_plugin(self, startup):
        #self.iface.messageBar().clearWidgets()
        #self.iface.messageBar().pushMessage("", 'Checking for updates...', Qgis.Info, 0)

        url = 'https://www.esru.strath.ac.uk/Downloads/downloads.htm'
        message_timer = 0

        current_version_file = self.plugin_dir + '/VERSION.py'
        current_version = ''
        with open(current_version_file) as f:
            for line in f:
                line = line.strip()
                if '__VERSION__' in line:
                    _, current_version = line.split('=', maxsplit=1)
                    current_version = current_version.strip()
                    break

        #print('Current version is:', current_version)

        try:
            response = requests.get(url, timeout=(5, 5))
            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            response.encoding = 'utf-8'
            response.text
            var_string = re.search(r'GOMap_.*?zip', response.text)[0]
            latest_version = var_string[7:11]
            #print('Latest version is:', latest_version)

            if float(latest_version) > float(current_version):
                iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage(
                    'GOMap v' + latest_version + ' available', '<a href="https://www.esru.strath.ac.uk/Downloads/GOMap/' + var_string + '"> Click here to download the latest version.</a>',
                Qgis.Success, message_timer)

            if not startup:
                if float(latest_version) == float(current_version):
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage('The latest GOMap version is already installed.', Qgis.Success, message_timer)

                if float(latest_version) < float(current_version):
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage('This version of GOMap differs with the online version. If this is a developer\'s version, make sure ' \
                        + 'to upload it to the relevant repository', Qgis.Critical, message_timer)

        except Timeout:
            if not startup:
                iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("",'The request timed out', Qgis.Warning, message_timer)
        except HTTPError as http_err:
            if not startup:
                iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("",f'HTTP error occurred: {http_err}', Qgis.Warning, message_timer)
        except Exception as err:
            if not startup:
                iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("",f'Other error occurred: {err}', Qgis.Warning, message_timer)



#-------------------------------Add empty memory layer-------------------------------------------
    def add_layer(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()        
        information_group = self.identify_group_state('Additional information')
        
        # Use CRS of city shapefile
        for fname in glob.glob(QgsProject.instance().readPath("./") + '/Processing scripts/Shapefile conversion/City/*.shp'):
            crs = QgsVectorLayer( fname, '', 'ogr' ).crs().authid()

        # Disconnect move_added_layer_to_information() function
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.move_added_layer_to_information)
        except TypeError:
            pass

        # Create memory layer and add to Additional information group
        memory_layer = QgsVectorLayer('Polygon?crs=' + crs, 'New scope layer', 'memory')
        QgsProject.instance().addMapLayer(memory_layer, False)
        information_group.insertChildNode(-1, QgsLayerTreeLayer(memory_layer))
        self.iface.setActiveLayer(memory_layer)
        # Set memory layer to go at top of layer order panel
        order = root.customLayerOrder()
        #order.insert( 0, order.pop(order.index(memory_layer.id())))
        root.setCustomLayerOrder(order) 
        # Set layer to edit mode and trigger "Add Feature" icon
        memory_layer.startEditing()
        self.iface.actionAddFeature().trigger()

        # Reconnect move_added_layer_to_information() function
        QgsProject.instance().legendLayersAdded.connect(self.move_added_layer_to_information)



#-------------------------------Confirm saving selected layer as scope-------------------------------------------
    def save_scope_ok(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        scope_group = self.identify_group_state('Scope')

        # Define textboxes and buttons
        scope_name = self.save_scope_dockwidget.scope_name_lineEdit

        # Set layer as active
        memory_layer = self.iface.activeLayer()
        # Get name from textbox
        name = str(scope_name.text())
        # Get path to '/Original data/Scope/'
        original_data_scope_path = QgsProject.instance().readPath("./") + '/Original data/Scope/'
        # Get path to '/Scope/'
        scope_path = QgsProject.instance().readPath("./") + '/Scope/'
        # Save changes to layer
        memory_layer.commitChanges()

        # Determine layer in Scope group which has largest area, use this to clip original layer into
        area_dict = {}
        for layer in scope_group.children():
            try:
                area = 0
                for feat in layer.layer().getFeatures():
                    area += feat.geometry().area()
                area_dict[layer.name()] = area
            except AttributeError:
                pass
        # Identify largest layer by name
        layer_name = max(area_dict.keys(), key=(lambda key: area_dict[key]))
        # Call and define largest layer
        for layers in scope_group.children():
            if layers.name() == layer_name:
                layer = layers
        
        # Run clip tool on original layer with largest area
        processing.run("native:clip", {'INPUT': layer.layer(),
                                        'OVERLAY':memory_layer,
                                        'OUTPUT': scope_path + name + '.shp'
                                        })
        # Write memory layer to disk in '/Original data/Scope/'
        QgsVectorFileWriter.writeAsVectorFormat(memory_layer, original_data_scope_path + name + '.shp', "utf-8", memory_layer.crs(), "ESRI Shapefile")
        #output = processing.runalg("qgis:clip", layer.layer(), original_layer, scope_path + name + '.shp')
        # Remove active layer from Table of Contents
        QgsProject.instance().removeMapLayer(memory_layer.id())

        self.iface.mainWindow().findChild( QAction, 'GOMap Update' ).trigger()

        #self.iface.mainWindow().findChild( QAction, 'Opp maps' ).trigger()

        new_scope = QgsProject.instance().mapLayersByName(name)[0]
        self.iface.layerTreeView().setLayerVisible(new_scope, True)
        del memory_layer
        self.save_scope_dockwidget.close()

#-------------------------------Cancel saving selected layer as scope-------------------------------------------
    def save_scope_cancel(self):
        # Close scope interface when clicked on Cancel
        self.save_scope_dockwidget.close()
        

#-------------------------------Interface options to save selected layer as constraint-------------------------------------------
    def save_constraint(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')
        information_group = self.identify_group_state('Additional information')

        # Define textboxes and buttons
        constraint_name = self.save_constraint_dockwidget.constraint_name_lineEdit
        existing_constraint_button = self.save_constraint_dockwidget.existingConstraint_radioButton
        new_constraint_button = self.save_constraint_dockwidget.addNewConstraint_radioButton
        existing_constraint_combobox = self.save_constraint_dockwidget.existingConstraint_combobox
        add_new_constraint = self.save_constraint_dockwidget.addNewConstraint_lineEdit
        policy_checkBox = self.save_constraint_dockwidget.policy_checkBox
        technical_checkBox = self.save_constraint_dockwidget.technical_checkBox
        ok_button = self.save_constraint_dockwidget.ok_pushButton
        cancel_button = self.save_constraint_dockwidget.cancel_pushButton

        # Set layer as active
        memory_layer = self.iface.activeLayer()

        information_list = []
        try:
            # Find all layers in information group and store in list
            for information_layer in information_group.children():
                information_list.append(information_layer.name())

            # Check to see if layer is in Additional information group
            if memory_layer.name() in information_list:
                # Check if layer is vector type
                if memory_layer.type() == QgsMapLayer.VectorLayer:
                    constraint_name.setText(str(memory_layer.name()))
                    constraint_name.selectAll()
                    add_new_constraint.clear()                
                    # Make sure buttons only trigger function once by disconnecting then reconnecting
                    try:
                        existing_constraint_button.clicked.disconnect(self.save_constraint_options)
                    except TypeError:
                        pass
                    try:
                        existing_constraint_button.clicked.disconnect(self.save_constraint_score)
                    except TypeError:
                        pass
                    try:
                        existing_constraint_combobox.currentIndexChanged.disconnect(self.save_constraint_score)
                    except TypeError:
                        pass
                    try:
                        new_constraint_button.clicked.disconnect(self.save_constraint_options)
                    except TypeError:
                        pass
                    try:
                        new_constraint_button.clicked.disconnect(self.save_constraint_score)
                    except TypeError:
                        pass
                    try:
                        policy_checkBox.stateChanged.disconnect(self.save_constraint_score)
                    except TypeError:
                        pass

                    existing_constraint_button.clicked.connect(self.save_constraint_options)
                    existing_constraint_button.clicked.connect(self.save_constraint_score)
                    existing_constraint_combobox.currentIndexChanged.connect(self.save_constraint_score)        
                    new_constraint_button.clicked.connect(self.save_constraint_options)
                    new_constraint_button.clicked.connect(self.save_constraint_score)
                    policy_checkBox.stateChanged.connect(self.save_constraint_score)

                    # If save constraint interface is not shown, show it
                    if self.save_constraint_dockwidget.isVisible() == True:
                        pass
                    else:                
                        self.save_constraint_dockwidget.show()
                    # Set default radiobutton
                    existing_constraint_button.setChecked(True)
                    # Store all constraint group names in list
                    policy_constraint_list = []
                    for group in policy_group.children():
                        policy_constraint_list.append(group.name())

                    # Add constraint group names into combobox
                    existing_constraint_combobox.clear()
                    existing_constraint_combobox.addItem('Policy')
                    existing_constraint_combobox.model().item(0).setEnabled(False)
                    existing_constraint_combobox.addItems(policy_constraint_list)
                    existing_constraint_combobox.setCurrentIndex(1)

                    technical_constraint_list = []
                    for group in technical_group.children():
                        technical_constraint_list.append(group.name())

                    no_of_policy_aspects = len(policy_constraint_list)
                    existing_constraint_combobox.addItem('---------')
                    existing_constraint_combobox.model().item(int(no_of_policy_aspects) + 1).setEnabled(False)
                    existing_constraint_combobox.addItem('Technical')
                    existing_constraint_combobox.model().item(int(no_of_policy_aspects) + 2).setEnabled(False)
                    existing_constraint_combobox.addItems(technical_constraint_list)

                    try:
                        ok_button.clicked.disconnect(self.save_constraint_ok)
                    except TypeError:
                        pass
                    try:
                        cancel_button.clicked.disconnect(self.save_constraint_cancel)
                    except TypeError:
                        pass
                    
                    ok_button.clicked.connect(self.save_constraint_ok)
                    cancel_button.clicked.connect(self.save_constraint_cancel)
                    self.save_constraint_options()        
                else:
                    # Layer must be a vector otherwise message is shown
                    self.iface.messageBar().pushMessage("", 'Select vector layer', Qgis.Warning, 3)
            else:
                # Layer must be in Additional information group otherwise message is shown
                self.iface.messageBar().pushMessage("", 'Select information layer', Qgis.Warning, 3)
        except AttributeError:
            self.iface.messageBar().pushMessage("", 'Select information layer', Qgis.Warning, 3)


#-------------------------------Policy/technical options to save selected layer as constraint-------------------------------------------
    def save_constraint_options(self):
        # Define textboxes and buttons
        policy_checkBox = self.save_constraint_dockwidget.policy_checkBox
        technical_checkBox = self.save_constraint_dockwidget.technical_checkBox
        existing_constraint_button = self.save_constraint_dockwidget.existingConstraint_radioButton
        new_constraint_button = self.save_constraint_dockwidget.addNewConstraint_radioButton
        existing_constraint_combobox = self.save_constraint_dockwidget.existingConstraint_combobox
        add_new_constraint = self.save_constraint_dockwidget.addNewConstraint_lineEdit

        # Set default checkbox
        policy_checkBox.setChecked(True)
        # Enable/disable options depending on user's choice
        if existing_constraint_button.isChecked():
            existing_constraint_combobox.setEnabled(True)
            add_new_constraint.setEnabled(False)
            policy_checkBox.setEnabled(False)
            technical_checkBox.setEnabled(False)
        else:
            existing_constraint_combobox.setEnabled(False)
            add_new_constraint.setEnabled(True)
            policy_checkBox.setEnabled(True)
            technical_checkBox.setEnabled(True)


#-------------------------------Score options to save selected layer as constraint-------------------------------------------
    def save_constraint_score(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Define textboxes and buttons
        score_comboBox = self.save_constraint_dockwidget.score_comboBox
        policy_checkBox = self.save_constraint_dockwidget.policy_checkBox
        technical_checkBox = self.save_constraint_dockwidget.technical_checkBox
        existing_constraint_button = self.save_constraint_dockwidget.existingConstraint_radioButton
        existing_constraint_combobox = self.save_constraint_dockwidget.existingConstraint_combobox

        # Find all constraint groups and store in list
        policy_constraint_list = []
        for group in policy_group.children():
            policy_constraint_list.append(group.name())

        technical_constraint_list = []
        for group in technical_group.children():
            technical_constraint_list.append(group.name())

        policy_constraint_score = ['1','2','3','4']
        technical_constraint_score = ['1','2','3']
        
        # Clear score combobox
        score_comboBox.clear()

        # Add relevant scores whenever user selects policy or technical
        if existing_constraint_button.isChecked():
            if existing_constraint_combobox.currentText() in policy_constraint_list:
                score_comboBox.addItems(policy_constraint_score)
            else:
                score_comboBox.addItems(technical_constraint_score)
        else:
            if policy_checkBox.isChecked():
                score_comboBox.addItems(policy_constraint_score)
            else:
                score_comboBox.addItems(technical_constraint_score)


#-------------------------------Confirm saving selected layer as constraint-------------------------------------------
    def save_constraint_ok(self):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        scope_group = self.identify_group_state('Scope')
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Define textboxes and buttons
        constraint_name = self.save_constraint_dockwidget.constraint_name_lineEdit
        score_comboBox = self.save_constraint_dockwidget.score_comboBox
        policy_checkBox = self.save_constraint_dockwidget.policy_checkBox
        technical_checkBox = self.save_constraint_dockwidget.technical_checkBox
        existing_constraint_button = self.save_constraint_dockwidget.existingConstraint_radioButton
        existing_constraint_combobox = self.save_constraint_dockwidget.existingConstraint_combobox
        new_constraint_button = self.save_constraint_dockwidget.addNewConstraint_radioButton
        add_new_constraint = self.save_constraint_dockwidget.addNewConstraint_lineEdit

        # Find all constraint groups and store in list
        policy_constraint_list = []
        for group in policy_group.children():
            policy_constraint_list.append(group.name())

        technical_constraint_list = []
        for group in technical_group.children():
            technical_constraint_list.append(group.name())

        # Get information regarding user's choice when selecting policy or technical constraint
        if existing_constraint_button.isChecked():
            if existing_constraint_combobox.currentText() in policy_constraint_list:
                constraint_type = 'Policy aspects'
                constraint_group = existing_constraint_combobox.currentText()
            else:
                constraint_type = 'Technical aspects'
                constraint_group = existing_constraint_combobox.currentText()
        else:
            if policy_checkBox.isChecked():
                constraint_type = 'Policy aspects'
                constraint_group = add_new_constraint.text()
            else:
                constraint_type = 'Technical aspects'
                constraint_group = add_new_constraint.text()

        # Set layer as active layer
        memory_layer = self.iface.activeLayer()
        # Get name
        name = str(constraint_name.text())
        # Get score
        score = score_comboBox.currentText()
        # Define path to original layer saved
        original_data_constraint_path = QgsProject.instance().readPath("./") + '/Original data/' + str(constraint_type) + '/' + constraint_group + '/'
        # Create new directories if '/Original data/' or '/aspects/' if constraint group does not exist
        if not os.path.exists(QgsProject.instance().readPath("./") + '/Original data/' + str(constraint_type) + '/' + constraint_group):
            os.makedirs(QgsProject.instance().readPath("./") + '/Original data/' + str(constraint_type) + '/' + constraint_group)
        if not os.path.exists(QgsProject.instance().readPath("./") + '/Aspects/' + str(constraint_type) + '/' + constraint_group):
            os.makedirs(QgsProject.instance().readPath("./") + '/Aspects/' + str(constraint_type) + '/' + constraint_group)
        # Define constraint path to save  layer
        constraint_path = QgsProject.instance().readPath("./") + '/Aspects/' + str(constraint_type) + '/' + constraint_group + '/'
        # Save changes
        memory_layer.commitChanges()
        # Write memory layer to disk in '/Original data/Scope/'
        QgsVectorFileWriter.writeAsVectorFormat(memory_layer, original_data_constraint_path + name + '.shp', "utf-8", memory_layer.crs(), "ESRI Shapefile")
        # Remove active layer from Table of Contents
        QgsProject.instance().removeMapLayer(memory_layer.id())
        # Define original layer
        original_layer = QgsVectorLayer(original_data_constraint_path + name + '.shp', name, 'ogr')

        # Add Score field and score 
        with edit(original_layer):
            original_layer.addAttribute(QgsField("Score", QVariant.Int))
            original_layer.updateFields()
            for feat in original_layer.getFeatures():
                original_layer.changeAttributeValue(feat.id(), original_layer.fields().indexFromName('Score'), score) 
        
        # Determine layer in Scope group which has largest area, use this to clip original layer into        
        area_dict = {}
        for layer in scope_group.children():
            try:
                area = 0
                for feat in layer.layer().getFeatures():
                    area += feat.geometry().area()
                area_dict[layer.name()] = area
            except AttributeError:
                pass

        # Identify largest layer by name
        layer_name = max(area_dict.keys(), key=(lambda key: area_dict[key]))
        # Call and define largest layer
        for layers in scope_group.children():
            if layers.name() == layer_name:
                layer = layers
        
        # Run processing algorithm to clip original layer with largest area
        output = processing.run("native:clip", {'INPUT': layer.layer(),
                                        'OVERLAY':original_layer,
                                        'OUTPUT':constraint_path + name + '.shp'
                                        })

        output_layer = QgsVectorLayer(output['OUTPUT'], name, 'ogr')

        with edit(output_layer):
            output_layer.addAttribute(QgsField("Score", QVariant.Int))
            output_layer.updateFields()
            for feat in output_layer.getFeatures():
                output_layer.changeAttributeValue(feat.id(), output_layer.fields().indexFromName('Score'), score) 
        # Close save options interface and update GOMap
        self.save_constraint_dockwidget.close()
        self.iface.mainWindow().findChild( QAction, 'GOMap Update' ).trigger()
        #self.iface.mainWindow().findChild( QAction, 'Opp maps' ).trigger()
        #del original_layer

        
#-------------------------------Cancel saving selected layer as constraint-------------------------------------------
    def save_constraint_cancel(self):
        # Close save constraint interface when clicked on Cancel
        self.save_constraint_dockwidget.close()


#-------------------------------Show GOMap settings---------------------------------------------------------
    def scoring_method_options(self):
        ###### Main settigs ######
        # Define buttons
        tag_checkBox = self.settings_dockwidget.tag_checkBox
        tag_comboBox = self.settings_dockwidget.tag_comboBox
        #positions = ['Top left', 'Top middle', 'Top right', 'Bottom left', 'Bottom middle', 'Bottom right']
        #tag_comboBox.clear()
        #tag_comboBox.addItems(positions)
        #tag_comboBox.setCurrentIndex(0)

        # Make sure buttons only trigger function once by disconnecting then reconnecting
        try:
            tag_checkBox.clicked.disconnect()
        except TypeError:
            pass
        try:
            tag_comboBox.currentIndexChanged.disconnect()
        except TypeError:
            pass

        tag_checkBox.clicked.connect(self.tag_position)
        tag_comboBox.currentIndexChanged.connect(self.refresh_canvas)

        ###### Score settings #######
        # Define buttons
        ok_button = self.settings_dockwidget.ok_pushButton
        cancel_button = self.settings_dockwidget.close_pushButton
        lenient_radioButton = self.settings_dockwidget.lenient_radioButton
        stringent_radioButton = self.settings_dockwidget.stringent_radioButton

        # Make sure buttons only trigger function once by disconnecting then reconnecting
        try:
            ok_button.clicked.disconnect()
        except TypeError:
            pass
        try:
            cancel_button.clicked.disconnect()
        except TypeError:
            pass
        try:
            lenient_radioButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            stringent_radioButton.clicked.disconnect()
        except TypeError:
            pass
        
        ok_button.clicked.connect(partial(self.scoring_method_ok, 'True'))
        cancel_button.clicked.connect(self.scoring_method_cancel)
        lenient_radioButton.clicked.connect(self.stringent_disable_options)
        stringent_radioButton.clicked.connect(self.stringent_disable_options)

        # Show scoring method interface
        self.settings_dockwidget.show()


#-------------------------------Enable/disable tag setting-------------------------------------------
    def tag_position(self):
        # Define buttons
        tag_checkBox = self.settings_dockwidget.tag_checkBox
        tag_comboBox = self.settings_dockwidget.tag_comboBox

        if tag_checkBox.isChecked():
            tag_comboBox.setEnabled(True)
        else:
            tag_comboBox.setEnabled(False)

        self.refresh_canvas()

#-------------------------------Create unique tag in 'copyright' label-------------------------------------------
    def unique_tag_reference(self, p):
        if self.settings_dockwidget.tag_checkBox.isChecked():
            # Define root and groups
            root = QgsProject.instance().layerTreeRoot()

            # Define user-defined weighting layer
            userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
            userDefined_node = root.findLayer(userDefined_layer.id())

            if userDefined_node.itemVisibilityChecked() == False:
                weighting = 'Equal'
            else:
                weighting = 'User-defined'

            # Define scoring methods
            lenient_radioButton = self.settings_dockwidget.lenient_radioButton
            stringent_radioButton = self.settings_dockwidget.stringent_radioButton
            if lenient_radioButton.isChecked():
                score_method = 'Lenient'
            if stringent_radioButton.isChecked():
                score_method = 'Stringent'

            # Get project name    
            for child in root.children():
                if isinstance(child, QgsLayerTreeGroup):
                    city_name = child.name()

            # Create timestamp
            date = datetime.datetime.now()
            timestamp = date.strftime('%d/%m/%Y')

            # Set style for tag
            text = QTextDocument()
            font = QFont()
            font.setFamily("Sans Serif")
            font.setPointSize(int(8))
            #font.setBold(True)
            font.setItalic(True)
            text.setDefaultFont(font)
            style = "<style type=\"text/css\"> p {color: #8a8a8a}</style>"

            # Set up full tag
            tag = str("Tag: " + timestamp + "_" + city_name + "_" + weighting + ' weightings_' + score_method + " scoring")

            # Apply style to tag and set position
            text.setHtml(style + tag)
            size = text.size()
            # Get width and height
            myWidth = p.device().width()
            myHeight = p.device().height()
            # Set height of top position tag if messageBar is active
            if iface.messageBar().isVisible():
                topHeight = 30
            else:
                topHeight = 0
            
            positions = {'Top left': [topHeight, 5], 'Top middle': [topHeight, (myWidth / 2) - (size.width() / 2)], 'Top right': [topHeight,  myWidth - size.width()], \
                         'Bottom left': [myHeight - size.height(), 5], 'Bottom middle': [myHeight - size.height(), (myWidth / 2) - (size.width() / 2)], \
                         'Bottom right': [myHeight - size.height(), myWidth - size.width()]}

            myYOffset = positions[self.settings_dockwidget.tag_comboBox.currentText()][0]
            myXOffset = positions[self.settings_dockwidget.tag_comboBox.currentText()][1]
            '''
            ### Top left ###
            #myYOffset = p.device().width() + p.device().height()
            #myYOffset = 0
            #myXOffset = 5
            ### Top middle ###
            myYOffset = 0
            myXOffset = (myWidth / 2) - (size.width() / 2)
            ### Bottom right ###
            myYOffset = myHeight - size.height()
            myXOffset = myWidth - size.width()
            ### Bottom left ###
            myYOffset = myHeight - size.height()
            myXOffset = 5
            ### Top right
            myYOffset = 0
            myXOffset = myWidth - size.width()
            '''
            p.translate( myXOffset, myYOffset )
            text.drawContents(p)
            p.setWorldTransform( p.worldTransform() )




#-------------------------------Show/hide unique tag------------------------------------------
    def refresh_canvas(self):
        self.iface.mapCanvas().refresh()

#-------------------------------Set scoring system--------------------------------------------------------------
    def scoring_method_ok(self, update):
        # Define buttons
        median_radioButton = self.settings_dockwidget.median_radioButton
        pessimistic_radioButton = self.settings_dockwidget.pessimistic_radioButton
        lenient_radioButton = self.settings_dockwidget.lenient_radioButton
        ############################################ add buttons to define mean or median usage and connect to forumula in gomap.py
        
        # Define score settings
        scoring_method = None
        score_rounding = None
        score_system = None

        # Define score method
        if median_radioButton.isChecked():
            scoring_method = 'median'
        else:
            scoring_method = 'mean'
        # Define score rounding
        if pessimistic_radioButton.isChecked():
            score_rounding = 'pessimistic'
        else:
            score_rounding = 'optimistic'
        # Define score system
        if lenient_radioButton.isChecked():
            score_system = 'lenient'
        else:
            score_system = 'stringent'

        self.settings_dockwidget.close()

        if update == 'True':
            #self.iface.mainWindow().findChild( QAction, 'GOMap Update' ).trigger()
            self.iface.mainWindow().findChild( QAction, 'Opp maps' ).trigger()

        return scoring_method, score_rounding, score_system


#-------------------------------Cancel scoring system-------------------------------------------
    def scoring_method_cancel(self):
        # Close scoring interface when clicked on Cancel
        self.settings_dockwidget.close()


#-------------------------------Stringent disable options -------------------------------------------
    def stringent_disable_options(self):
        # Define buttons        
        median_radioButton = self.settings_dockwidget.median_radioButton
        mean_radioButton = self.settings_dockwidget.mean_radioButton
        pessimistic_radioButton = self.settings_dockwidget.pessimistic_radioButton
        optimistic_radioButton = self.settings_dockwidget.optimistic_radioButton
        stringent_radioButton = self.settings_dockwidget.stringent_radioButton

        if stringent_radioButton.isChecked():
            median_radioButton.setEnabled(False)
            mean_radioButton.setEnabled(False)
            pessimistic_radioButton.setEnabled(False)
            optimistic_radioButton.setEnabled(False)
        else:
            median_radioButton.setEnabled(True)
            mean_radioButton.setEnabled(True)
            pessimistic_radioButton.setEnabled(True)
            optimistic_radioButton.setEnabled(True)


#-------------------------------Identify full name of current groupr-------------------------------------------
    def identify_group_state(self, group_name):
        root = QgsProject.instance().layerTreeRoot()
        for groups in root.children():
            for child in groups.children():
                if isinstance(child, QgsLayerTreeGroup):
                    if group_name in child.name():
                        group = child

        return group


#-------------------------------Move current layer to "Additional information" group--------------------------------------
    def move_added_layer_to_information(self, layers):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        information_group = self.identify_group_state('Additional information')

        # Move added layer to Additional information group by cloning, moving and removing the original from its position
        for layer in layers:
            new_layer = QgsProject.instance().mapLayersByName(layer.name())[-1]
            new_layer_parent = root.findLayer(new_layer.id())
            parent = new_layer_parent.parent()
            information_group.insertChildNode(-1, QgsLayerTreeLayer(new_layer))
            # Rename layer by adding underscore suffix to avoid potential errors
            new_layer.setName(layer.name() + '*')
            parent.removeChildNode(new_layer_parent)
            # Set layer to go at top of layer order panel
            order = root.customLayerOrder()
            for i, o in enumerate(order):
                if o.name() == layer.name():
                    order.insert(0, order.pop(i))
            root.setCustomLayerOrder(order)


#-------------------------------Find median score--------------------------------------
    def median(self, lst):
        if lst:
            lst.sort()
            half = len(lst)//2  # integer division
            b = lst[half]
            c = lst[-half-1]  # for odd lengths, b == c
            return int((b + c) / 2)


#-------------------------------Get processing feedback from internal processing algorithm-------------------------------------------------------
    def progress_changed(self, progress_bar, progress):
        progress_bar.setValue(progress) 

