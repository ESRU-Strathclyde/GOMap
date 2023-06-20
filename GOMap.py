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
from .resources import *
# Import required modules
import glob, os, sys, operator, processing, datetime, subprocess, re
import numpy as np
from time import sleep
from itertools import permutations
from functools import partial
from qgis.core import QgsProject, QgsVectorLayerJoinInfo, QgsLayerTree, QgsField, Qgis, QgsFeatureRequest, QgsVectorFileWriter, QgsLayoutItemPage, \
QgsSymbol, QgsRuleBasedRenderer, QgsLayerTreeLayer, QgsVectorLayer, QgsLayerTreeGroup, edit, QgsExpression, QgsLayout, QgsLayoutExporter, QgsPrintLayout, \
QgsRasterLayer, qgsfunction, QgsWkbTypes, QgsProcessingFeedback, QgsSingleSymbolRenderer, QgsReadWriteContext
from qgis.utils import iface
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant, QFileInfo
from qgis.PyQt.QtGui import QIcon, QColor, QFont
from qgis.PyQt.QtWidgets import QAction, QApplication, QToolButton, QMenu, QMenuBar, QHeaderView, QTreeWidgetItem, QTreeWidgetItemIterator, QListWidgetItem
from qgis.PyQt.QtXml import QDomDocument

# Import resources from dockwidgets
from .dockwidgets.GOMap_dockwidget import GOMapDockWidget
from .dockwidgets.policy_dockwidget import policy_dockwidget
from .dockwidgets.technical_dockwidget import technical_dockwidget
from .dockwidgets.land_availability_dockwidget import land_availability
from .dockwidgets.about_dockwidget import about
from .dockwidgets.confirm_weighting_dockwidget import confirm_weighting

# Import resources for General
from .dockwidgets.create_scope_dockwidget import create_scope
from .dockwidgets.settings_dockwidget import settings
from .dockwidgets.save_report_dockwidget import save_report

# Import resources for PV
from .dockwidgets.configure_pv_dockwidget import configure_pv
# Import resources for PV canopy
from .dockwidgets.configure_pv_canopy_dockwidget import configure_pv_canopy
# Import resources for Wind
from .dockwidgets.configure_wind_dockwidget import configure_wind
# Import resources for Ground source heat pumps
from .dockwidgets.configure_gshp_dockwidget import configure_gshp
# Import resources for AHP
from .dockwidgets.ahp_dockwidget import ahp

# Reference technology classes
from .tools.General import General
from .tools.solarPV import PV
from .tools.PV_Canopy import PV_Canopy
from .tools.WindTurbine import WIND
from .tools.GroundSourceHeatPump import GSHP
from .tools.LocalDistrictHeating import LDH
from .tools.TechnologyFunctions import TechFunctions
from .tools.Statistics import Statistics


class GOMap:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GOMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GOMap')
        
        self.toolbar = self.iface.addToolBar(u'GOMap')
        self.toolbar.setObjectName(u'GOMap Toolbar')
        self.toolbar.setToolTip(u'GOMap Toolbar')

        self.pluginIsActive = False
        #self.dockwidget = None
        self.dockwidget = GOMapDockWidget()
        self.policy_dockwidget = policy_dockwidget()
        self.technical_dockwidget = technical_dockwidget()
        self.land_availability_dockwidget = land_availability()
        self.about_dockwidget = about()
        self.confirm_weighting_dockwidget = confirm_weighting()
        self.create_scope_dockwidget = create_scope()
        self.ahp_dockwidget = ahp()

        self.settings_dockwidget = settings()
        self.save_report_dockwidget = save_report()
        self.configure_pv_dockwidget = configure_pv()
        self.configure_pv_canopy_dockwidget = configure_pv_canopy()
        self.configure_wind_dockwidget = configure_wind()
        self.configure_gshp_dockwidget = configure_gshp()

        # Reference General class
        self.General = General(self.settings_dockwidget)

        # Reference PV class
        self.PV = PV(self.land_availability_dockwidget)

        # Reference PV canopy class
        self.PV_Canopy = PV_Canopy(self.land_availability_dockwidget)

        # Reference WIND class
        self.WIND = WIND(self.land_availability_dockwidget)

        # Reference WIND class
        self.GSHP = GSHP(self.land_availability_dockwidget)

        # Reference LDH class
        self.LDH = LDH(self.land_availability_dockwidget)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # Reference Statistics class
        self.Statistics = Statistics(self.land_availability_dockwidget,
                                    self.ahp_dockwidget)

        self.General.update_GOMap_plugin(True)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GOMap', message)


    def add_action(
        self,
        toolbar,
        icon_path,
        text,
        callback,
        checkable=False,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action


#-------------------------------Add buttons/menus to toolbar/menubar-------------------------------------------
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # GOMap Live icon
        icon = QIcon()
        icon.addFile( ':/plugins/GOMap/icons/GOMapLive_Off.png', state=QIcon.Off )
        icon.addFile( ':/plugins/GOMap/icons/GOMapLive_On.png', state=QIcon.On )
        self.GOMapLive_button = self.add_action(
            self.toolbar,
            icon,
            text=self.tr(u'GOMap'),
            callback=self.GOMap_Live,
            checkable=True,
            enabled_flag=False,
            parent=self.iface.mainWindow())
        self.GOMapLive_button.setObjectName('GOMap Live')

        # Save GOMap icon
        save_icon_path = ':/plugins/GOMap/icons/Save_Constraint.png'
        self.save_button = self.add_action(
            self.toolbar,
            save_icon_path,
            text=self.tr(u'Save project'),
            callback=self.save_GOMap,
            checkable=False,
            enabled_flag=False,
            parent=self.iface.mainWindow())
        self.save_button.setObjectName('Save GOMap')

        # Identify/Select mode
        Identify_Selelection_icon = QIcon()
        Identify_Selelection_icon.addFile( ':/plugins/GOMap/icons/Identify_Features.png', state=QIcon.Off )
        Identify_Selelection_icon.addFile( ':/plugins/GOMap/icons/Select_Features.png', state=QIcon.On )
        self.Identify_Selection_button = self.add_action(
            self.toolbar,
            Identify_Selelection_icon,
            text=self.tr(u'Identify/Select mode'),
            callback=self.TechFunctions.selectingFeatures,
            checkable=True,
            enabled_flag=False,
            parent=self.iface.mainWindow())
        self.Identify_Selection_button.setObjectName('Identify/Select')

        # GOMap Update icon (invisible, only used once when project is loaded)
        GOMap_icon_path = ':/plugins/GOMap/icons/GOMap_Update.png'
        self.GOMapUpdate_button = self.add_action(
            self.toolbar,
            GOMap_icon_path,
            text=self.tr(u'Update'),
            callback=self.update_GOMapProject,
            checkable=False,
            enabled_flag=False,
            parent=self.iface.mainWindow())
        self.GOMapUpdate_button.setObjectName('GOMap Update')
        self.GOMapUpdate_button.setVisible(False)       

        # GOMap Run icon (invisible, only used once when project is loaded)
        GOMap_run = ''
        self.run_button = self.add_action(
            self.toolbar,
            GOMap_run,
            text=self.tr(u''),
            callback=self.run,
            checkable=False,
            parent=self.iface.mainWindow())
        self.run_button.setObjectName('GOMap')
        self.run_button.setVisible(False)

        # Close GOMap icon (invisible, only used once when project is closed)
        GOMap_close = ''
        self.close_button = self.add_action(
            self.toolbar,
            GOMap_close,
            text=self.tr(u''),
            callback=self.onClosePlugin,
            checkable=False,
            parent=self.iface.mainWindow())
        self.close_button.setObjectName('GOMap Close')
        self.close_button.setVisible(False)

        # Add/remove opportunity maps icon (invisible)
        opp_maps = ''
        self.opp_maps_button = self.add_action(
            self.toolbar,
            opp_maps,
            text=self.tr(u''),
            callback=self.add_remove_opportunityMaps,
            checkable=False,
            parent=self.iface.mainWindow())
        self.opp_maps_button.setObjectName('Opp maps')
        self.opp_maps_button.setVisible(False)

        # Show tool_buttons (invisible)
        show_tools = ''
        self.show_tool_buttons = self.add_action(
            self.toolbar,
            show_tools,
            text=self.tr(u''),
            callback=self.show_tools,
            checkable=False,
            parent=self.iface.mainWindow())
        self.show_tool_buttons.setObjectName('Show tools')
        self.show_tool_buttons.setVisible(False)

        
        # Dummy icon to connect to new functions for testing
        # Can connect to functions from other scripts (e.g. callback=self.TechFunctions.selectingFeatures,)
        # To update icons, use "compile" bat file
        test_icon_path = ':/plugins/GOMap/icons/test.png'
        self.test_button = self.add_action(
            self.toolbar,
            test_icon_path,
            text=self.tr(u'Test'),
            callback=self.test_function,
            checkable=True,
            enabled_flag=True,
            parent=self.iface.mainWindow())
        self.test_button.setObjectName('Test')
        self.test_button.setVisible(False)
        

        # Create main menu to hold tools
        self.mainMenu = QMenu()

        # Connect and update
        self.update_menu = QAction((QIcon(":/plugins/GOMap/icons/GOMap_Update.png")), "Check for updates", self.iface.mainWindow())
        self.update_menu.triggered.connect(partial(self.General.update_GOMap_plugin, None))
        self.mainMenu.addAction(self.update_menu)

        # Settings
        self.settings_menu = QAction((QIcon(":/plugins/GOMap/icons/GOMap.png")), "Settings", self.iface.mainWindow())
        self.settings_menu.triggered.connect(self.General.scoring_method_options)
        self.mainMenu.addAction(self.settings_menu)

        # Add/save layer
        self.GENERAL_create_polygon_layer = QAction((QIcon(':/plugins/GOMap/icons/Create_polygon.png')), "Create polygon layer", self.iface.mainWindow())
        self.GENERAL_save_layer_constraint = QAction((QIcon(':/plugins/GOMap/icons/Save_Constraint.png')), "Save layer as factor", self.iface.mainWindow())

        self.GENERAL_create_polygon_layer.triggered.connect(self.General.add_layer)
        self.GENERAL_save_layer_constraint.triggered.connect(self.General.save_constraint)

        GENERAL_menu = self.mainMenu.addMenu(QIcon(":/plugins/GOMap/icons/Add_Layer.png"), "Add/save layer")
        GENERAL_menu.addAction(self.GENERAL_create_polygon_layer)
        GENERAL_menu.addAction(self.GENERAL_save_layer_constraint)

        # Define script menu to hold scripts for various technologies
        SCRIPT_menu = self.mainMenu.addMenu(QIcon(":/plugins/GOMap/icons/Developer_tools.png"), "Scripts")

        # Statistics
        self.stats_tool_1 = QAction((QIcon(':/plugins/GOMap/icons/Developer_tools.png')), "Area statistics", self.iface.mainWindow())
        self.stats_tool_1.triggered.connect(self.Statistics.area_statistics_configuration)

        stats_menu = SCRIPT_menu.addMenu(QIcon(":/plugins/GOMap/icons/Developer_tools.png"), "Statistics")
        stats_menu.addAction(self.stats_tool_1)

        # PV
        self.PV_tool_1 = QAction((QIcon(':/plugins/GOMap/icons/PV_Panel.png')), "Generate PV panels", self.iface.mainWindow())
        self.PV_tool_1.triggered.connect(self.PV.generate_PV_panels_configuration)

        self.PV_tool_2 = QAction((QIcon(':/plugins/GOMap/icons/PV_rooftop.png')), "Generate northerly/southerly sites", self.iface.mainWindow())         
        self.PV_tool_2.triggered.connect(self.PV.generate_northerly_southerly_sites_configuration)

        PV_menu = SCRIPT_menu.addMenu(QIcon(":/plugins/GOMap/icons/PV_Panel.png"), "PV")
        PV_menu.addAction(self.PV_tool_1)
        PV_menu.addAction(self.PV_tool_2)

        # WIND
        self.WIND_tool_1 = QAction((QIcon(':/plugins/GOMap/icons/Wind_Turbine.png')), "Generate wind turbines", self.iface.mainWindow())
        self.WIND_tool_1.triggered.connect(self.WIND.generate_WIND_turbines_configuration)

        WIND_menu = SCRIPT_menu.addMenu(QIcon(":/plugins/GOMap/icons/Wind_Turbine.png"), "Wind")
        WIND_menu.addAction(self.WIND_tool_1)

        # LDH
        self.LDH_tool_1 = QAction((QIcon(':/plugins/GOMap/icons/Local_District_Heating.png')), "Generate district heating network", self.iface.mainWindow())
        self.LDH_tool_1.triggered.connect(self.LDH.generate_LDH_configuration)

        LDH_menu = SCRIPT_menu.addMenu(QIcon(":/plugins/GOMap/icons/Local_District_Heating.png"), "District heating")
        LDH_menu.addAction(self.LDH_tool_1)            

        # Set main menu properties
        self.mainToolButton = QToolButton()
        self.mainToolButton.setIcon(QIcon(':/plugins/GOMap/icons/Developer_tools.png'))
        self.mainToolButton.setToolTip("Tools")
        self.mainToolButton.setMenu(self.mainMenu)
        self.mainToolButton.setObjectName('GOMap tools')
        self.mainToolButton.setPopupMode(QToolButton.InstantPopup)
        self.mainToolButton.setEnabled(False)
        self.toolbar.addWidget(self.mainToolButton)


        # About GOMap icon (placed last to reflect last position in toolbar)
        about_icon_path = ':/plugins/GOMap/icons/About.png'
        self.about_button = self.add_action(
            self.toolbar,
            about_icon_path,
            text=self.tr(u'About GOMap project'),
            callback=self.about_GOMap_project,
            checkable=False,
            enabled_flag=False,
            parent=self.iface.mainWindow())
        self.about_button.setObjectName('About GOMap project')


#-------------------------------Test function-------------------------------------------
    # Test function to connection to buttons and signals 
    def test_function(self):
        iface.messageBar().pushMessage("", 'This is just a test', Qgis.Info, 5)


#-------------------------------Show tools when GOMap project loaded-------------------------------------------
    # Enable tools/scripts when project is loaded 
    def show_tools(self):
        self.GOMapLive_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.about_button.setEnabled(True)
        self.mainToolButton.setEnabled(True)
        self.Identify_Selection_button.setEnabled(True)

        
#-------------------------------Closing GOMap-------------------------------------------
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        # Close interfaces and disable tools/scripts
        self.policy_dockwidget.close()
        self.technical_dockwidget.close()
        self.dockwidget.close()
        self.land_availability_dockwidget.close()
        self.about_dockwidget.close()
        self.pluginIsActive = False

        self.GOMapLive_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.about_button.setEnabled(False)
        self.mainToolButton.setEnabled(False)
        self.Identify_Selection_button.setEnabled(False)

        '''
        # Following code closes all loaded dockwidgets and actions but seems slow?
        # Need to import QDockWidget to qgis.PyQt.QtWidgets
        items = vars(self)
        for i in items:
            item = items[i]
            if isinstance(item, QDockWidget):
                item.close()
            if isinstance(item, QAction):
                print(item.objectName())
                item.disconnect()
        '''

        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Disconnect signals from layers, interface, buttons etc. from their connected functions. 
        # Try method is used in the unlikelyhood that the signals were already disconnected.
        try:
            for pol_groups in policy_group.children():
                for layers in pol_groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layers.visibilityChanged.disconnect(self.refresh_weighting_aspect_list_main_aspects)
                    layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)          
        except TypeError:
            pass

        try:
            for tech_groups in technical_group.children():
                for layers in tech_groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layers.visibilityChanged.disconnect(self.refresh_weighting_aspect_list_main_aspects)
                    layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)
        except TypeError:
            pass

        try:
            self.policy_dockwidget.policyApply_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.technical_dockwidget.technicalApply_pushButton.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.land_availability_dockwidget.utilisation_green_spinBox.valueChanged.disconnect()
        except TypeError:
            pass
        try:
            self.land_availability_dockwidget.utilisation_amber_spinBox.valueChanged.disconnect()
        except TypeError:
            pass
        try:
            self.land_availability_dockwidget.utilisation_red_spinBox.valueChanged.disconnect()
        except TypeError:
            pass
        try:
            self.land_availability_dockwidget.utilisation_black_spinBox.valueChanged.disconnect()
        except TypeError:
            pass
        try:
            self.land_availability_dockwidget.report_pushButton.clicked.disconnect()
        except:
            pass
        try:
            self.land_availability_dockwidget.technology_comboBox.currentIndexChanged.disconnect()
        except TypeError:
            pass
        try:
            iface.currentLayerChanged.disconnect()
        except TypeError:
            pass
        try:
            QgsProject.instance().legendLayersAdded.disconnect()
        except TypeError:
            pass


#-------------------------------Unload GOMap-------------------------------------------
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GOMap'),
                action)
            self.iface.removeToolBarIcon(action)
        # Remove the toolbar
        del self.toolbar


#-------------------------------GOMap Custom Field Calculator Expressions -------------------------------------------
    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def categorisation_func(name, feature, parent):
        root = QgsProject.instance().layerTreeRoot()
        def categorisations(lst, name):
            policy_categories = {1: 'Possible', 2: 'Intermediate', 3: 'Sensitive', 4: 'Showstopper'}
            technical_categories = {1: 'Favourable', 2: 'Likely', 3: 'Unlikely'}
            if lst:
                if name == 'Policy':
                    return policy_categories[lst[0]]
                else:
                    return technical_categories[lst[0]]
            else:
                if name == 'Policy':
                    return policy_categories[1]
                else:
                    return technical_categories[1]
        layer = QgsProject.instance().mapLayersByName('Combined ' + name.lower())[0]
        aspect_list = []
        group = root.findGroup(name)
        for aspect in group.children():
            aspect_list.append(aspect.name())
        field_names = ['Score']
        text = []
        for fields in field_names:
            if (1 <= feature[fields] <= 4):
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(categorisations(results, name))

    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def median_func_factors(name, rounding, feature, parent):
        def median_value_factors(lst, score_rounding):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    lst.sort()
                    half = len(lst)//2  # integer division
                    b = lst[half]
                    c = lst[-half-1]  # for odd lengths, b == c
                    if score_rounding == 'optimistic':
                        return int(round((float(b) + float(c)) / float(2)))
                    else:
                        return int((float(b) + float(c)) / float(2) + 0.5)
            else:
                return None
        layer = QgsProject.instance().mapLayersByName(name)[0]
        field_names = [field.name() for field in layer.fields() if '_Score' in field.name()]
        text = []
        for fields in field_names:
            if str(feature[fields]) != 'None':
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(median_value_factors(results, rounding))

    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def median_func_aspects(name, rounding, feature, parent):
        root = QgsProject.instance().layerTreeRoot()
        def median_value_aspects(lst, score_rounding):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    lst.sort()
                    half = len(lst)//2  # integer division
                    b = lst[half]
                    c = lst[-half-1]  # for odd lengths, b == c
                    if score_rounding == 'optimistic':
                        return int(round((float(b) + float(c)) / float(2)))
                    else:
                        return int((float(b) + float(c)) / float(2) + 0.5)
            else:
                return None
        layer = QgsProject.instance().mapLayersByName('Combined ' + name.lower())[0]
        aspect_list = []
        group = root.findGroup(name)
        for aspect in group.children():
            aspect_list.append(aspect.name())
        field_names = [field.name() for field in layer.fields() for aspect in aspect_list if str(aspect) + '_Score' in field.name()]
        text = []
        for fields in field_names:
            if (1 <= feature[fields] <= 4):
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(median_value_aspects(results, rounding))


    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def mean_func_factors(name, rounding, feature, parent):
        from statistics import mean
        def mean_value_factors(lst, score_rounding):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    if score_rounding == 'optimistic':
                        return int(mean(lst))
                    else:
                        return int(mean(lst) + 0.5)
            else:
                return None
        layer = QgsProject.instance().mapLayersByName(name)[0]
        field_names = [field.name() for field in layer.fields() if '_Score' in field.name()]
        text = []
        for fields in field_names:
            if str(feature[fields]) != 'None':
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(mean_value_factors(results, rounding))


    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def mean_func_aspects(name, rounding, feature, parent):
        from statistics import mean
        root = QgsProject.instance().layerTreeRoot()
        def mean_value_aspects(lst, score_rounding):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    if score_rounding == 'optimistic':
                        return int(mean(lst))
                    else:
                        return int(mean(lst) + 0.5)
            else:
                return None
        layer = QgsProject.instance().mapLayersByName('Combined ' + name.lower())[0]
        aspect_list = []
        group = root.findGroup(name)
        for aspect in group.children():
            aspect_list.append(aspect.name())
        field_names = [field.name() for field in layer.fields() for aspect in aspect_list if str(aspect) + '_Score' in field.name()]
        text = []
        for fields in field_names:
            if (1 <= feature[fields] <= 4):
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(mean_value_aspects(results, rounding))


    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def sum_func_factors(name, feature, parent):
        from statistics import mean
        def sum_value_factors(lst):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    return int(max(lst))
            else:
                return None
        layer = QgsProject.instance().mapLayersByName(name)[0]
        field_names = [field.name() for field in layer.fields() if '_Score' in field.name()]
        text = []
        for fields in field_names:
            if str(feature[fields]) != 'None':
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(sum_value_factors(results))


    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def sum_func_aspects(name, feature, parent):
        from statistics import mean
        root = QgsProject.instance().layerTreeRoot()
        def sum_value_aspects(lst):
            if lst:
                if 4 in lst:
                    return int(4)
                else:
                    lst = [x for x in lst if x != 0]
                    return int(max(lst))
            else:
                return None
        layer = QgsProject.instance().mapLayersByName('Combined ' + name.lower())[0]
        aspect_list = []
        group = root.findGroup(name)
        for aspect in group.children():
            aspect_list.append(aspect.name())
        field_names = [field.name() for field in layer.fields() for aspect in aspect_list if str(aspect) + '_Score' in field.name()]
        text = []
        for fields in field_names:
            if (1 <= feature[fields] <= 4):
                text.append(str(feature[fields]))
        results = sorted(map(int, text))
        return str(sum_value_aspects(results))


    @qgsfunction(args='auto', group='Custom', usesGeometry=False)
    def weight_func_aspects(name, rounding, weightings, feature, parent):
        import ast, math
        from statistics import mean
        root = QgsProject.instance().layerTreeRoot()
        
        def weight_value_aspects(lst, score_rounding, weightings):
            if lst:
                if 4 in lst:
                    return int(4)
                
                else:
                    # If only one aspect is active, final score is the same as the aspect
                    lst = [x for x in lst if x != 0]
                    if len(lst) == 1:
                        return int(max(lst))
                    
                    else:
                        final_score = sum(map(math.prod, weightings.values()))
                        if score_rounding == 'optimistic':
                            return int(final_score)
                        else:
                            return int(final_score) + 0.5
            else:
                return None
        
        layer = QgsProject.instance().mapLayersByName('Combined ' + name.lower())[0]
        aspect_list = []
        aspect_scores = {}
        weighting_dict = {}
        group = root.findGroup(name)
        for aspect in group.children():
            aspect_list.append(aspect.name())
            weighting_dict[aspect.name()] = ''
        field_names = [field.name() for field in layer.fields() for aspect in aspect_list if str(aspect) + '_Score' in field.name()]
        text = []
        for fields in field_names:
            if (1 <= feature[fields] <= 4):
                text.append(int(feature[fields]))
                aspect_scores[fields.replace('_Score', '')] = int(feature[fields])
        results = sorted(map(int, text))
        for key, value in aspect_scores.items():
            weighting_dict[key] = value
            
        weightings_to_dict = ast.literal_eval(weightings)
        for key, value in weightings_to_dict.items():
            weighting_dict[key] = value
            
        ds = [aspect_scores, weightings_to_dict]
        d = {}
        for k in aspect_scores.keys():
            d[k] = tuple(d[k] for d in ds)
        #print(d)
        return str(weight_value_aspects(results, rounding, d))


#-------------------------------Save GOMap---------------------------------------------------
    def save_GOMap(self):
        #print('save_GOMap')
        iface.mainWindow().findChild( QAction, 'mActionSaveProject' ).trigger()


#-------------------------------About GOMap---------------------------------------------------
    def about_GOMap_project(self):
        #print('about_GOMap')
        # Define text browser
        about_project_textBrowser = self.about_dockwidget.about_project_textBrowser

        # Get path to "About.txt" file
        try:
            about_file_path = QgsProject.instance().readPath("./") + '/About.txt'
            f = open(about_file_path, 'r')
            # Read file
            text = f.read()
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

            for x in urls:
                if x in text:
                    text = text.replace(x, x.replace('http', '<a href="http').replace(')', '">') + x + '</a>')

            # Set text to text browser
            about_text = '<b>Project information:</b><br><br>'
            about_text += '<br>'.join(text.splitlines())
            about_project_textBrowser.setHtml(about_text)
            about_project_textBrowser.setOpenExternalLinks(True)
        except FileNotFoundError:
            text = 'No Project information found: missing "About.txt" file.'
            about_project_textBrowser.setHtml(text)

        self.about_dockwidget.show()


#-------------------------------Create scope layer---------- ---------------------------------
    def create_scope_layer(self, layer):
        #print('create_scope_layer')
        # Define root, New scope layer and User-defined layer
        root = QgsProject.instance().layerTreeRoot()
        new_scope_layer = QgsProject.instance().mapLayersByName( "New scope" )[0]
        new_scope_layer_node = root.findLayer(new_scope_layer.id())
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id())

        # If New scope layer is checked
        if new_scope_layer_node.isVisible():
            # Define comboboxes, list views and buttons
            drawScope_radioButton = self.create_scope_dockwidget.drawScope_radioButton
            generateScope_radioButton = self.create_scope_dockwidget.generateScope_radioButton
            addPolygonLayer_pushButton = self.create_scope_dockwidget.addPolygonLayer_pushButton
            scope_combobox = self.create_scope_dockwidget.scope_combobox
            field_combobox = self.create_scope_dockwidget.field_combobox
            fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
            toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget
            select_pushButton = self.create_scope_dockwidget.select_pushButton        
            selectAll_pushButton = self.create_scope_dockwidget.selectAll_pushButton
            remove_pushButton = self.create_scope_dockwidget.remove_pushButton
            removeAll_pushButton = self.create_scope_dockwidget.removeAll_pushButton
            scope_name_lineEdit = self.create_scope_dockwidget.scope_name_lineEdit
            ok_button = self.create_scope_dockwidget.ok_pushButton

            # Disconnect function
            try:
                drawScope_radioButton.clicked.disconnect(self.enable_scope_options)
            except TypeError:
                pass
            try:
                generateScope_radioButton.clicked.disconnect(self.enable_scope_options)
            except TypeError:
                pass
            try:
                addPolygonLayer_pushButton.clicked.disconnect(self.General.add_layer)
            except TypeError:
                pass
            try:
                scope_combobox.currentIndexChanged.disconnect(self.get_scope_layer_fields)
            except TypeError:
                pass
            try:
                field_combobox.currentIndexChanged.disconnect(self.get_scope_values)
            except TypeError:
                pass
            try:
                select_pushButton.clicked.disconnect(self.move_selected_scope_fields)
            except TypeError:
                pass
            try:
                selectAll_pushButton.clicked.disconnect(self.move_all_scope_fields)
            except TypeError:
                pass
            try:
                remove_pushButton.clicked.disconnect(self.remove_selected_scope_fields)
            except TypeError:
                pass
            try:
                removeAll_pushButton.clicked.disconnect(self.remove_all_scope_fields)
            except TypeError:
                pass
            try:
                ok_button.clicked.disconnect(self.create_scope_layer_ok)
            except TypeError:
                pass

            # Define groups
            information_group = self.General.identify_group_state('Additional information')

            # Get relevant vector layers
            layers_list = []
            for child in information_group.children():
                if isinstance(child, QgsLayerTreeLayer):
                    try:
                        if child.layer().geometryType() == QgsWkbTypes.PolygonGeometry:
                            layers_list.append(child.name())
                    except AttributeError:
                        pass

            # Populate scope combobox
            scope_combobox.clear()
            scope_combobox.addItems(layers_list)

            # Set default scope name
            scope_name_lineEdit.setText('Scope name')

            # Get selected layer
            selected_layer_name = self.create_scope_dockwidget.scope_combobox.currentText()
            selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]

            # Get fields from selected layer and populate combobox
            field_names = [field.name() for field in selectedLayer.fields()]
            field_combobox.clear()
            field_combobox.addItems(field_names)

            # Get values
            self.get_scope_values()
            # Run scope option function
            self.enable_scope_options()
            
            # Connect functions
            drawScope_radioButton.clicked.connect(self.enable_scope_options)
            generateScope_radioButton.clicked.connect(self.enable_scope_options)
            addPolygonLayer_pushButton.clicked.connect(self.General.add_layer)
            scope_combobox.currentIndexChanged.connect(self.get_scope_layer_fields)
            field_combobox.currentIndexChanged.connect(self.get_scope_values)
            select_pushButton.clicked.connect(self.move_selected_scope_fields)
            selectAll_pushButton.clicked.connect(self.move_all_scope_fields)
            remove_pushButton.clicked.connect(self.remove_selected_scope_fields)
            removeAll_pushButton.clicked.connect(self.remove_all_scope_fields)

            ok_button.clicked.connect(self.create_scope_layer_ok)
            self.create_scope_dockwidget.show()

        if userDefined_node.isVisible():
            self.create_scope_dockwidget.show()
            self.policy_dockwidget.hide()
            self.technical_dockwidget.hide()
            #self.dockwidget.hide()

        if not new_scope_layer_node.isVisible():
            self.create_scope_dockwidget.hide()

        if not new_scope_layer_node.isVisible() and userDefined_node.isVisible():
            self.create_scope_dockwidget.hide()
            self.policy_dockwidget.show()
            self.technical_dockwidget.show()
            #self.dockwidget.show()


#-------------------------------Enable scope options-------------------------------------------
    def enable_scope_options(self):
        # Define buttons and group boxes
        drawScope_radioButton = self.create_scope_dockwidget.drawScope_radioButton
        generateScope_radioButton = self.create_scope_dockwidget.generateScope_radioButton
        addPolygonLayer_pushButton = self.create_scope_dockwidget.addPolygonLayer_pushButton
        layerField_groupBox = self.create_scope_dockwidget.layerField_groupBox
        existingAttributes_groupBox = self.create_scope_dockwidget.existingAttributes_groupBox
        selectedAttributes_groupBox = self.create_scope_dockwidget.selectedAttributes_groupBox

        if drawScope_radioButton.isChecked():
            layerField_groupBox.hide()
            existingAttributes_groupBox.hide()
            selectedAttributes_groupBox.hide()
            addPolygonLayer_pushButton.setEnabled(True)
            
        else:
            layerField_groupBox.show()
            existingAttributes_groupBox.show()
            selectedAttributes_groupBox.show()
            addPolygonLayer_pushButton.setEnabled(False)

#-------------------------------Get fields from chosen scope layer-------------------------------------------
    def get_scope_layer_fields(self):
        #print('get_scope_layer_fields')
        # Define comboboxes, list views and buttons
        scope_combobox = self.create_scope_dockwidget.scope_combobox
        field_combobox = self.create_scope_dockwidget.field_combobox
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        # Disconnect function
        try:
            field_combobox.currentIndexChanged.disconnect(self.get_scope_values)
        except TypeError:
            pass            

        # Get selected layer
        selected_layer_name = self.create_scope_dockwidget.scope_combobox.currentText()
        selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]

        # Get fields from selected layer and populate combobox
        field_names = [field.name() for field in selectedLayer.fields()]
        field_combobox.clear()
        field_combobox.addItems(field_names)

        # Clear list widgets
        fromLayer_listWidget.clear()
        toLayer_listWidget.clear()

        # Get unique values from selected field and populate widgets
        selected_field = self.create_scope_dockwidget.field_combobox.currentText()
        idx = selectedLayer.fields().indexFromName(selected_field)
        unique_values = selectedLayer.uniqueValues(idx)
        for values in unique_values:
            item = QListWidgetItem(str(values))
            fromLayer_listWidget.addItem(item)

        # Connect function
        field_combobox.currentIndexChanged.connect(self.get_scope_values)

#-------------------------------Get values from chosen scope layer field-------------------------------------------
    def get_scope_values(self):
        #print('get_scope_values')
        # Define comboboxes, list views and buttons
        scope_combobox = self.create_scope_dockwidget.scope_combobox
        field_combobox = self.create_scope_dockwidget.field_combobox
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        # Get selected layer
        selected_layer_name = self.create_scope_dockwidget.scope_combobox.currentText()
        selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]

        # Clear list widgets
        fromLayer_listWidget.clear()
        toLayer_listWidget.clear()

        # Get unique values from selected field and populate widgets
        selected_field = self.create_scope_dockwidget.field_combobox.currentText()
        idx = selectedLayer.fields().indexFromName(selected_field)
        unique_values = selectedLayer.uniqueValues(idx)
        for values in unique_values:
            item = QListWidgetItem(str(values))
            fromLayer_listWidget.addItem(item)


#-------------------------------Move selected scope field-------------------------------------------
    def move_selected_scope_fields(self):
        #print('move_selected_scope_fields')
        # Define list views
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        # Sort rows in descending order to compensate shifting due to takeItem()
        rows = sorted([index.row() for index in fromLayer_listWidget.selectedIndexes()], reverse=True)
        for row in rows:
            toLayer_listWidget.addItem(fromLayer_listWidget.takeItem(row))


#-------------------------------Move all scope field-------------------------------------------
    def move_all_scope_fields(self):
        #print('move_all_scope_fields')
        # Define list views
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        for row in reversed(range(fromLayer_listWidget.count())):
            toLayer_listWidget.addItem(fromLayer_listWidget.takeItem(row))


#-------------------------------Remove selected scope field-------------------------------------------
    def remove_selected_scope_fields(self):
        #print('remove_selected_scope_fields')
        # Define list views
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        # Sort rows in descending order to compensate shifting due to takeItem()
        rows = sorted([index.row() for index in toLayer_listWidget.selectedIndexes()], reverse=True)
        for row in rows:
            fromLayer_listWidget.addItem(toLayer_listWidget.takeItem(row))


#-------------------------------Remove all scope field-------------------------------------------
    def remove_all_scope_fields(self):
        #print('remove_all_scope_fields')
        # Define list views
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget

        for row in reversed(range(toLayer_listWidget.count())):
            fromLayer_listWidget.addItem(toLayer_listWidget.takeItem(row))


#-------------------------------Confirm saving scope-------------------------------------------
    def create_scope_layer_ok(self):
        # Define root and New scope layer
        root = QgsProject.instance().layerTreeRoot()
        new_scope_layer = QgsProject.instance().mapLayersByName( "New scope" )[0]
        new_scope_layer_node = root.findLayer(new_scope_layer.id()) 

        # Define comboboxes, list views and buttons
        drawScope_radioButton = self.create_scope_dockwidget.drawScope_radioButton
        generateScope_radioButton = self.create_scope_dockwidget.generateScope_radioButton
        scope_combobox = self.create_scope_dockwidget.scope_combobox
        field_combobox = self.create_scope_dockwidget.field_combobox
        fromLayer_listWidget = self.create_scope_dockwidget.fromLayer_listWidget
        toLayer_listWidget = self.create_scope_dockwidget.toLayer_listWidget
        output_scope_name = self.create_scope_dockwidget.scope_name_lineEdit
        progress_bar = self.create_scope_dockwidget.progressBar


        # Define groups
        scope_group = self.General.identify_group_state('Scope')
        information_group = self.General.identify_group_state('Additional information')
        

        if drawScope_radioButton.isChecked():

            # Set layer as active
            memory_layer = self.iface.activeLayer()
            # Get name from textbox
            name = str(output_scope_name.text())
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

            # Define and connect progress feedback from processing tool to interface
            f = QgsProcessingFeedback()
            f.progressChanged.connect(partial(self.General.progress_changed, progress_bar))

            # Run clip tool on original layer with largest area
            processing.run("native:clip", {'INPUT': layer.layer(),
                                            'OVERLAY':memory_layer,
                                            'OUTPUT': scope_path + name + '.shp'
                                            },
                                            feedback = f)
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

        else:
            # Get selected layer
            selected_layer_name = self.create_scope_dockwidget.scope_combobox.currentText()
            selectedLayer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]

            
            provider = selectedLayer.dataProvider()
            selected_field = self.create_scope_dockwidget.field_combobox.currentText()

            # Get items in list widget
            itemsTextList = [str(toLayer_listWidget.item(i).text()) for i in range(toLayer_listWidget.count())]        
            if len(itemsTextList) == 1:
                itemTuple = "('" + str(itemsTextList[0]) + "')"
            else:
                itemTuple = tuple(itemsTextList)

            # Get path to '/Scope/'
            original_data_scope_path = QgsProject.instance().readPath("./") + '/Original data/Scope/'
            scope_path = QgsProject.instance().readPath("./") + '/Scope/'
            # Output name
            output_name = str(output_scope_name.text())
            if output_name != 'New scope':
                # Define opportunity layer and CRS
                opportunity_layer = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
                crs = opportunity_layer.crs()
                # Define memory layer and copy fields
                memory_lyr = QgsVectorLayer("Polygon?crs=epsg:" + unicode(crs.postgisSrid()) + "&index=yes", "memory_lyr", "memory")
                memory_lyr_data = memory_lyr.dataProvider()
                attr = selectedLayer.fields().toList()
                memory_lyr_data.addAttributes(attr)
                memory_lyr.updateFields()

                # Define expression to filter features
                expr = QgsExpression( '"' + selected_field + '" IN ' + str(itemTuple))
                request = QgsFeatureRequest(expr)
                # Get features and add to memory layer
                feats = [f for i, f in enumerate(selectedLayer.getFeatures(request))]
                memory_lyr_data.addFeatures(feats)
                # Add memory layer to "Additional Information" group temporarily (needed for tool)
                QgsProject.instance().addMapLayer(memory_lyr, False)
                #information_group.insertChildNode(-1, QgsLayerTreeLayer(memory_lyr))
                information_group.addLayer(memory_lyr)

                # Determine layer in Scope group which has largest area, use this to clip original layer into
                area_dict = {}
                for layer in scope_group.children():
                    if layer.name() != 'New scope':
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
                    if layers.name() != 'New scope':
                        if layers.name() == layer_name:
                            layer = QgsProject.instance().mapLayersByName(layers.name())[0]

                # Define and connect progress feedback from processing tool to interface
                f = QgsProcessingFeedback()
                f.progressChanged.connect(partial(self.General.progress_changed, progress_bar))

                # Run clip tool to create scope layer
                processing.run("native:clip", {'INPUT': layer,
                                                'OVERLAY':memory_lyr,
                                                'OUTPUT':scope_path + output_name + '.shp'
                                                },
                                                feedback = f)
                # Save as original scope layer
                QgsVectorFileWriter.writeAsVectorFormat(memory_lyr, original_data_scope_path + output_name + '.shp', "utf-8", memory_lyr.crs(), "ESRI Shapefile")
                # Remove memory layer from "Additional Information" group
                QgsProject.instance().removeMapLayers([memory_lyr.id()])
                # Update GOMap to load newly created layers safely
                iface.mainWindow().findChild( QAction, 'GOMap Update' ).trigger()
                # Delete reference to memory layer
                del memory_lyr
                # Select new scope layer
                new_scope = QgsProject.instance().mapLayersByName(output_name)[0]
                iface.layerTreeView().setLayerVisible(new_scope, True)

            else:
                iface.messageBar().pushMessage("", 'Type another name', Qgis.Warning, 5)

        # Switch New scope layer off
        new_scope_layer_node.setItemVisibilityChecked(False)



#-------------------------------Update GOMap----------------------------------------------------------------------
    def apply_style(self, input_vector, aspect_type):
        #print('apply_style')
        root = QgsProject.instance().layerTreeRoot()
        # Define colours dictionary
        color_mapping = { 1: "00ff00", 2: "f0ab64", 3: "963634", 4: "1d1b10" }
        # Define layer and field
        layer = input_vector
        idx = layer.fields().indexFromName("Score")
        # Set up layer symbology corresponding to saved score
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        if idx != -1:                  
            if layer.minimumValue(idx) == layer.maximumValue(idx):
                color = color_mapping.get(layer.minimumValue(idx), "default color")
                symbol.setColor(QColor('#{color}'.format(color=color)))
                renderer = QgsSingleSymbolRenderer(symbol)
                layer.setRenderer(renderer)
                iface.layerTreeView().refreshLayerSymbology(layer.id())
            elif layer.minimumValue(idx) != layer.maximumValue(idx):
                if aspect_type == 'Policy':
                    style_rules = (
                        ('Possible', """""Score" = 1""", '#00ff00'),
                        ('Intermediate', """"Score" = 2""", '#f0ab64'),
                        ('Sensitive', """"Score" = 3""", '#963634'),
                        ('Showstopper', """"Score" = 4""", '#1d1b10'),
                    )
                else:
                   style_rules = (
                        ('Favourable', """""Score" = 1""", '#00ff00'),
                        ('Likely', """"Score" = 2""", '#f0ab64'),
                        ('Unlikely', """"Score" = 3""", '#963634'),
                    )    
                # Create a new rule-based renderer
                renderer = QgsRuleBasedRenderer(symbol)
                # Get the "root" rule
                root_rule = renderer.rootRule()
                for label, expression, color_name in style_rules:
                    # Set outline colour to match that of polygon fill colour
                    # Create a clone (i.e. a copy) of the default rule
                    rule = root_rule.children()[0].clone()
                    # Set the label, expression and color
                    rule.setLabel(label)
                    rule.setFilterExpression(expression)
                    rule.symbol().setColor(QColor(color_name))
                    # Append the rule to the list of rules
                    root_rule.appendChild(rule)
                # Delete the default rule
                root_rule.removeChildAt(0)
                # Apply the renderer to the layer
                layer.setRenderer(renderer)
                root.findLayer(layer.id()).setExpanded(False)
            if self.GOMapLive_button.isChecked():
                layer.setOpacity(0)
            else:
                layer.setOpacity(100)
                layer.triggerRepaint()



#-------------------------------Add new groups----------------------------------------------------------------------
    def add_new_layer_groups(self, aspect_type, apply_crs):
        #print('add_new_layer_groups')
        # Define root, group and message level
        root = QgsProject.instance().layerTreeRoot()
        groups = root.findGroup(aspect_type)
        message_level = 1

        dirs = []
        if aspect_type in ('Policy', 'Technical'):
            roots = [x[0] for x in os.walk(os.path.join(QgsProject.instance().readPath("./"), "Aspects", aspect_type + " aspects"))][0]
            dirs = [x[1] for x in os.walk(os.path.join(QgsProject.instance().readPath("./"), "Aspects", aspect_type + " aspects"))][0]
        for group in groups.children():
            if group.name() in dirs:
                dirs.remove(group.name())
        if dirs:
            for folder_name in dirs:
                # Before adding group and its shapefiles, check if folder is empty
                # If folder contains shapefiles
                if glob.glob(os.path.join(roots, folder_name, "*.shp")):
                    group = groups.addGroup(folder_name)
                    message_level = 1
                else:
                    message_level = 2

        return message_level


#-------------------------------Update existing groups----------------------------------------------------------------
    def update_existing_layer_groups(self, aspect_type, apply_crs):
        #print('update_existing_layer_groups')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        # Disable function to automatically insert added layers to Additional information group
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.General.move_added_layer_to_information)
        except TypeError:
            pass

        if aspect_type == 'Additional information':
            groups = self.General.identify_group_state('Additional information')
        elif aspect_type == 'Scope':
            groups = self.General.identify_group_state('Scope')
            # Select New scope layer to add new scopes
            new_scope_layer = QgsProject.instance().mapLayersByName("New scope")[0]
        else:
            groups = root.findGroup(aspect_type)

        if aspect_type in ('Policy', 'Technical'):
            roots = [x[0] for x in os.walk(os.path.join(QgsProject.instance().readPath("./"), "Aspects", aspect_type + " aspects"))][0]
            dirs = [x[1] for x in os.walk(os.path.join(QgsProject.instance().readPath("./"), "Aspects", aspect_type + " aspects"))][0]
            # Create empty list
            aspect_list = []
            # Find all layers loaded in QGIS
            for group in groups.children():
                for aspect_layer in group.children():
                    aspect_list.append(aspect_layer.layer().source())
            new_aspect_list = [x.encode() for x in aspect_list]
            second_aspect_list = [l.decode().replace("b'", "'") for l in new_aspect_list]
            # Create empty list
            dir_list = []
            # Find all layers in aspect directories
            for folder_name in dirs:
                for shapefile in glob.glob(os.path.join(roots, folder_name, "*.shp")):
                    dir_list.append(shapefile)
            second_dir_list = [l.replace('\\','/') for l in dir_list]

            # Find paths of shapefiles in directories which are not loaded in QGIS
            missing_shapefiles = [x for x in second_dir_list if x not in second_aspect_list]
            # For all shapefiles not loaded in QGIS, add them to relevant group with symbology
            if missing_shapefiles:
                for shapefile in missing_shapefiles:
                    paths = os.path.dirname(shapefile)
                    group_name = paths.rsplit('/', -1)[-1]
                    group = root.findGroup(group_name)
                    layer = QgsVectorLayer(shapefile, os.path.splitext(os.path.basename(shapefile))[0], "ogr" )
                    idx = layer.fields().indexFromName("Score")
                    crs = layer.crs()
                    #crs.createFromId(apply_crs)
                    layer.setCrs(crs)
                    QgsProject.instance().addMapLayer(layer, False)
                    #group.insertChildNode(-1, QgsLayerTreeLayer(layer))
                    group.addLayer(layer)
                    self.apply_style(layer, aspect_type)
                    iface.layerTreeView().refreshLayerSymbology(layer.id())
                    iface.layerTreeView().setLayerVisible(layer, True)

        if aspect_type in ('Additional information', 'Scope'):  
            roots = [x[0] for x in os.walk(os.path.join(QgsProject.instance().readPath("./"), aspect_type))][0]
            # Create empty list
            geospatial_list = []
            # Find all layers loaded in QGIS
            for geospatial_layer in groups.children():
                if isinstance(geospatial_layer, QgsLayerTreeLayer):
                    geospatial_list.append(geospatial_layer.layer().source())
            new_geospatial_list = [x.encode() for x in geospatial_list]
            second_geospatial_list = [l.decode().replace("b'", "'") for l in new_geospatial_list]
            # Create empty list
            geospatial_dir_list = []
            # Find all layers in information directory
            if aspect_type == 'Additional information':
                for geospatial_file in glob.glob(roots + "/*tif"):
                    geospatial_dir_list.append(geospatial_file)
            for geospatial_file in glob.glob(roots + "/*shp"):
                geospatial_dir_list.append(geospatial_file)
            new_geospatial_dir_list = [x.encode() for x in geospatial_dir_list]
            second_geospatial_dir_list = [l.decode().replace("b'", "'").replace('\\','/') for l in new_geospatial_dir_list]

            # Find paths of shapefiles in directories which are not loaded in QGIS
            missing_geospatial_files = [x for x in second_geospatial_dir_list if x not in second_geospatial_list]
            # For all shapefiles not loaded in QGIS, add them to relevant group with symbology
            if aspect_type == 'Additional information':
                if missing_geospatial_files:
                    for file in missing_geospatial_files:
                        if file.lower().endswith('.shp'):
                            vlayer = QgsVectorLayer(file, os.path.splitext(os.path.basename(file))[0], "ogr" )
                            crs = vlayer.crs()
                            #crs.createFromId(apply_crs)
                            vlayer.setCrs(crs)
                            QgsProject.instance().addMapLayer(vlayer, False)
                            #groups.insertChildNode(-1, QgsLayerTreeLayer(vlayer))
                            groups.addLayer(vlayer)
                            iface.layerTreeView().setLayerVisible(vlayer, False)
                            order = root.customLayerOrder()
                            #order.insert( 0, order.pop(order.index(vlayer.id())))
                            root.setCustomLayerOrder(order) 
                        if file.lower().endswith('.tif'):
                            fileName = file
                            fileInfo = QFileInfo(fileName)
                            baseName = fileInfo.baseName()
                            rlayer = QgsRasterLayer(fileName, baseName)
                            crs = rlayer.crs()
                            #crs.createFromId(apply_crs)
                            rlayer.setCrs(crs)
                            QgsProject.instance().addMapLayer(rlayer, False)                        
                            #groups.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                            groups.addLayer(rlayer)
                            iface.layerTreeView().setLayerVisible(rlayer, False)
                            order = root.customLayerOrder()
                            #order.insert( 0, order.pop(order.index(rlayer.id())))
                            root.setCustomLayerOrder(order) 
            else:
                if missing_geospatial_files:
                    for file in missing_geospatial_files:
                        layer = QgsVectorLayer(file, os.path.splitext(os.path.basename(file))[0], "ogr" )
                        crs = layer.crs()
                        #crs.createFromId(apply_crs)
                        layer.setCrs(crs)
                        QgsProject.instance().addMapLayer(layer, False)
                        groups.addLayer(layer)
                        layer.loadNamedStyle(self.plugin_dir + '/styles/scope_style.qml')
                        iface.layerTreeView().refreshLayerSymbology(layer.id())
                        iface.layerTreeView().setLayerVisible(layer, False)

        # Re-ennable function to automatically insert added layers to Additional information group
        QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)


#-------------------------------Update GOMap----------------------------------------------------------------------
    def update_GOMapProject(self):
        #print('update_GOMapProject')
        # Use CRS of city shapefile
        for fname in glob.glob(QgsProject.instance().readPath("./") + '/Processing scripts/Shapefile conversion/City/*.shp'):
            initial_crs = QgsVectorLayer( fname, '', 'ogr' ).crs().authid()
            get_crs = int(initial_crs.split(":",1)[-1].split()[0])

        # If GOMap Live is toggled, untoggle it (switch to OFF)
        if iface.mainWindow().findChild( QAction, 'GOMap Live' ).isChecked() == True:
            self.GOMapLive_button.trigger()
        
        message_level_for_policy = self.add_new_layer_groups('Policy', get_crs)
        message_level_for_technical = self.add_new_layer_groups('Technical', get_crs)
        self.update_existing_layer_groups('Policy', get_crs)
        self.update_existing_layer_groups('Technical', get_crs)
        self.update_existing_layer_groups('Additional information', get_crs)
        self.update_existing_layer_groups('Scope', get_crs)

        # Run add_remove_opportunityMaps() function   
        self.add_remove_opportunityMaps()

        # Show messages based on level        
        iface.messageBar().clearWidgets()
        if (message_level_for_policy == 2) or (message_level_for_technical == 2):
            iface.messageBar().pushMessage("",  u'GOMap loaded but some aspect(s) were not added due to empty directory', Qgis.Warning, 5)
        else:
            iface.messageBar().pushMessage("",  u'GOMap project loaded', Qgis.Success, 5)
            self.General.update_GOMap_plugin(True)



#-------------------------------Add/remove hidden scoring layers-------------------------------------------
    def create_query_for_scoringLayers_and_opportunity_map(self):
        #print('create_query_for_scoringLayers_and_opportunity_map')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        scope_group = self.General.identify_group_state('Scope')

        # Determine layer in Scope group which has largest area, use this to clip original layer into        
        area_dict = {}
        for layers in scope_group.children():
            if layers.name() != 'New scope':
                try:
                    area = 0
                    for feat in layers.layer().getFeatures():
                        area += feat.geometry().area()
                    area_dict[layers.name()] = area
                except AttributeError:
                    pass

        layer_name = max(area_dict.keys(), key=(lambda key: area_dict[key]))

        for layers in scope_group.children():
            if layers.name() != 'New scope':
                if layers.name() == layer_name:
                    layer = layers

        # Get list of all layers enabled (i.e. they are ticked) and store in list
        display_list = []
        for layers in scope_group.children():
            if layers.name() != 'New scope':
                if layers.isVisible() == 2:
                    display_list.append(layers.layer())

        # If no layers in list (i.e. no layers are ticked), enable largest area
        if not len(display_list) > 0:
            iface.layerTreeView().setLayerVisible(layer.layer(), True)

        # Set query to select from largest layer
        query = """SELECT * FROM '""" + layer.layer().name() + """'"""
        return query


#-------------------------------Add scoring layers and opportunity map--------------------------------------------------------------
    def add_combinedScoringLayers_and_opportunity_map(self, aspect_type, query):
        #print('add_combinedScoringLayers_and_opportunity_map')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        scoring_group = root.findGroup('Combined maps')

        try:
            # Define Combined policy map (hidden scoring layer)
            oppPol_weightedMap = QgsProject.instance().mapLayersByName( "Combined " + aspect_type )[0]
        except IndexError:
            # If Combined policy map does not exist, create it, stlye it and add it to Table of Contents
            oppPol_weightedMap = QgsVectorLayer( "?query={}&nogeometry".format(query), "Combined " + aspect_type, "virtual" )
            QgsProject.instance().addMapLayer(oppPol_weightedMap, False)
            #scoring_group.insertChildNode(-1, QgsLayerTreeLayer(oppPol_weightedMap))
            scoring_group.addLayer(oppPol_weightedMap)
            iface.layerTreeView().setLayerVisible(oppPol_weightedMap, False)
            scoring_group.setExpanded(False)

        try:
            # Define Opportunity map (hidden scoring layer)
            oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        except IndexError:   
        # If Opportunity map does not exist, create it, stlye it and add it to Table of Contents         
            oppPolTech_weightedMap = QgsVectorLayer( "?query={}".format(query), "Opportunities", "virtual" )
            QgsProject.instance().addMapLayer(oppPolTech_weightedMap, False)
            for child in root.children():
                if isinstance(child, QgsLayerTreeGroup):
                    main_group = child
            #main_group.insertChildNode(-1, QgsLayerTreeLayer(oppPolTech_weightedMap))
            main_group.addLayer(oppPolTech_weightedMap)
            abstract = str('Rated in the format: Policy / Technical.'
                        '\nThe legend colours denote the following in terms of the likelihood in receiving planning permission:\n' +
                        '\nGreen - High chance' +
                        '\nAmber - Medium chance' +
                        '\nRed - Low chance' +
                        '\nBlack - Showstopper\n' +
                        '\nCurrent scope:')
            oppPolTech_weightedMap.setAbstract(abstract)


#-------------------------------Add scoring layers-------------------------------------------------------------------
    def add_scoringLayers(self, aspect_type, query):
        #print('add_scoringLayers')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        groups = root.findGroup(aspect_type)
        mapGroups = root.findGroup(aspect_type + " maps")

        mapLayers = [x.name() for x in mapGroups.children()]
        mapGroupsNames = [y.name() for y in groups.children()]

        for group in groups.children():
            if group.name() not in mapLayers:
                vlayer = QgsVectorLayer( "?query={}&nogeometry".format(query), group.name(), "virtual" )
                QgsProject.instance().addMapLayer(vlayer, False)
                #mapGroups.insertChildNode(-1, QgsLayerTreeLayer(vlayer))
                mapGroups.addLayer(vlayer)
                group.setExpanded(False)
                
                for layer in group.children():
                    iface.layerTreeView().setLayerVisible(layer.layer(), True)        
        # If a aspect group does not exist for an existing Opportunity, the map is removed
        for layer in mapGroups.children():
            if layer.name() not in mapGroupsNames:
                QgsProject.instance().removeMapLayers( [layer.layer().id()] )
            layer.setExpanded(False)


#-------------------------------Add/remove opportunity map GOMap----------------------------------------------------------------------
    def add_remove_opportunityMaps(self):
        #print('add_remove_opportunityMaps')
        # Get query
        query = self.create_query_for_scoringLayers_and_opportunity_map()

        # Run following functions
        self.add_combinedScoringLayers_and_opportunity_map('policy', query)
        self.add_combinedScoringLayers_and_opportunity_map('technical', query)
        self.add_scoringLayers('Policy', query)
        self.add_scoringLayers('Technical', query)

        self.update_policy_or_technical_oppMaps_with_GOMap_update('Policy')
        self.update_policy_or_technical_oppMaps_with_GOMap_update('Technical')
        self.refresh_weighting_aspect_list_main_aspects('Policy')
        self.refresh_weighting_aspect_list_main_aspects('Technical')
        self.update_weighted_maps('Both')
        
    
#-------------------------------Refresh weighting aspect application for main aspects-------------------------------------------
    def refresh_weighting_aspect_list_main_aspects(self, aspect_type):
        #print('refresh_weighting_aspect_list_main_aspects')
        # Define root and groups
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        main_group = root.findGroup(aspect_type)

        # Define button and table
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
            totalWeighting_lineEdit = self.dockwidget.policyTotalWeighting_lineEdit
            apply_pushButton = self.policy_dockwidget.policyApply_pushButton
            search_pushButton = self.policy_dockwidget.policySearch_pushButton
            progress_bar = self.policy_dockwidget.progressBar
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget
            totalWeighting_lineEdit = self.dockwidget.technicalTotalWeighting_lineEdit
            apply_pushButton = self.technical_dockwidget.technicalApply_pushButton
            search_pushButton = self.technical_dockwidget.technicalSearch_pushButton
            progress_bar = self.technical_dockwidget.progressBar

        # Define bold font
        font = QFont()
        font.setBold(True)

        try:
            qTree.itemDoubleClicked.disconnect()
        except TypeError:
            pass
        try:
            qTree.itemChanged.disconnect()
        except TypeError:
            pass

        # Reset progress bar
        progress_bar.setValue(0)

        # Define parameters for QTreeWidget
        visible_groups = []
        weighting_dict = {}

        # Fetch layers and store in layer_data list, also count number of layers per aspect group
        for group in main_group.children():
            weighting_dict[group.name()] = ''
            aspect_group = root.findGroup(str(group.name()))
            if aspect_group.isVisible():
                visible_groups.append(group.name())

        if len(visible_groups) != 0:
            # Layer weighting
            layer_weighting = float(1) / float(len(visible_groups))
            # Calculate remainder
            remainder = 1 - (layer_weighting * float(len(visible_groups)))
            allocations = []

            # Assign remainder to some weightings where total equals 1
            for i in range(len(visible_groups), 0, -1):
                allocation = int(remainder/i)
                remainder -= allocation
                allocations.append(allocation)

            # Add percentage value and remainder if necessary
            for key, value in weighting_dict.items():
                if key in visible_groups:
                    if allocations:
                        weighting_dict[key] = round(layer_weighting + allocations.pop(), 3)
                    else:
                        weighting_dict[key] = round(layer_weighting, 3)

            #qTree.clear()
            header = QTreeWidgetItem(["Aspects", "Weightings"])
            qTree.setHeaderItem(header)

            # Set groups and their weightings
            for x in range(len(visible_groups)):
                group = QTreeWidgetItem(qTree, [str(visible_groups[x]), str(weighting_dict[str(visible_groups[x])])])
                group.setFont(0, font)
                #group.setTextAlignment(1, Qt.AlignHCenter)
            
            # Resize to fit contents
            qTree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
            qTree.expandAll()
            # Connect signal when double clicking item to self.qtree_check_item_clicked() function
            qTree.itemChanged.connect(partial(self.qtree_item_string_checker, aspect_type))
            qTree.itemDoubleClicked.connect(partial(self.qtree_check_item_clicked, aspect_type))
            #self.qtree_total_weighting(aspect_type)
            if len(visible_groups) > 1:
                apply_pushButton.setEnabled(True)
                search_pushButton.setEnabled(True)
            else:
                apply_pushButton.setEnabled(False)
                search_pushButton.setEnabled(False)                
        else:
            #qTree.clear()
            totalWeighting_lineEdit.setText('0')
            totalWeighting_lineEdit.setStyleSheet("color: rgb(255, 0, 0);font-weight: bold;")
            apply_pushButton.setEnabled(False)
            search_pushButton.setEnabled(False)

        self.refresh_weighting_aspect_list_sub_aspects(aspect_type)


#-------------------------------Refresh weighting aspect application for sub aspects-------------------------------------------
    def refresh_weighting_aspect_list_sub_aspects(self, aspect_type):
        #print('refresh_weighting_aspect_list_sub_aspects')
        # Define root and groups
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        main_group = root.findGroup(aspect_type)

        # Define button and table
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget

        # Define bold font
        font = QFont()
        font.setBold(True)

        # Define parameters for QTreeWidget
        layer_data = []  
        layer_count = []
        visible_groups = []

        # Fetch layers and store in layer_data list, also count number of layers per aspect group
        for group in main_group.children():
            layer_list = []
            for child in group.children():
                if child.isVisible():
                    layer_data.append(child.name())
                    layer_list.append(child.name())            
            aspect_group = root.findGroup(str(group.name()))
            if aspect_group.isVisible():
                layer_count.append(len(layer_list))
                visible_groups.append(group.name())


        aspects_weighting_dict = {}
        iterator = QTreeWidgetItemIterator(qTree)
        while iterator.value():
            item = iterator.value()
            try:
                if "." in item.text(1):
                    aspects_weighting_dict[str(item.text(0))] = float(item.text(1))
                else:
                    aspects_weighting_dict[str(item.text(0))] = int(item.text(1))
            except ValueError:
                pass                
            iterator += 1

        qTree.clear()
        header = QTreeWidgetItem(["Aspects", "Weightings"])
        qTree.setHeaderItem(header)

        # Define range by using number of layers in each aspect group with number of aspect groups
        top = list(np.cumsum(layer_count))
        bottom = list(np.subtract(np.cumsum(layer_count),layer_count))
        pairs = zip(bottom,top)
        ranges = iter([range(x[0], x[1]) for x in pairs])

        for x in range(len(visible_groups)):
            group = QTreeWidgetItem(qTree, [str(visible_groups[x]), str(aspects_weighting_dict[visible_groups[x]])])
            group.setFont(0, font)
            #group.setTextAlignment(1, Qt.AlignHCenter)
            for row in next(ranges):
                item = QTreeWidgetItem(group, [str(layer_data[row])])

        # Resize to fit contents
        qTree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        qTree.expandAll()
        self.qtree_total_weighting(aspect_type)


#-------------------------------QTree check when item is clicked--------------------------------------------------------
    def qtree_check_item_clicked(self, aspect_type, item, column):
        #print('qtree_check_item_clicked')
        # Define qTree
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget

        try:
            qTree.itemChanged.disconnect()
        except TypeError:
            pass

        item.setFlags(QtCore.Qt.ItemIsEnabled)
        if item.text(1) != '0' and item.text(1) != '':
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        qTree.itemChanged.connect(partial(self.qtree_total_weighting, aspect_type))
        qTree.itemChanged.connect(partial(self.qtree_item_string_checker, aspect_type))


#-------------------------------QTree check if string is entered-----------------------------------------------------
    def qtree_item_string_checker(self, aspect_type, item, column):
        #print('qtree_item_string_checker')
        # Define qTree
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget

        try:
            qTree.itemChanged.disconnect()
        except TypeError:
            pass

        if column == 1:
            new_item = item.text(1).replace('.', '')
            if new_item.isnumeric():
                item.setForeground(1, QtGui.QBrush(QtGui.QColor("black")))
            else:
                item.setForeground(1, QtGui.QBrush(QtGui.QColor("red")))                

        qTree.itemChanged.connect(partial(self.qtree_item_string_checker, aspect_type))


#-------------------------------QTree total weighting--------------------------------------------------------
    def qtree_total_weighting(self, aspect_type):
        #print('qtree_total_weighting')
        # Define qTree and line edit
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
            totalWeighting_lineEdit = self.dockwidget.policyTotalWeighting_lineEdit
            apply_pushButton = self.policy_dockwidget.policyApply_pushButton
            search_pushButton = self.policy_dockwidget.policySearch_pushButton
            progress_bar = self.policy_dockwidget.progressBar
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget
            totalWeighting_lineEdit = self.dockwidget.technicalTotalWeighting_lineEdit
            apply_pushButton = self.technical_dockwidget.technicalApply_pushButton
            search_pushButton = self.technical_dockwidget.technicalSearch_pushButton
            progress_bar = self.technical_dockwidget.progressBar
        try:
            qTree.itemChanged.disconnect(self.qtree_total_weighting)
        except TypeError:
            pass

        # Define root and groups
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        main_group = root.findGroup(aspect_type)

        visible_groups = []

        # Fetch layers and store in layer_data list, also count number of layers per aspect group
        for group in main_group.children():
            aspect_group = root.findGroup(str(group.name()))
            if aspect_group.isVisible():
                visible_groups.append(group.name())

        # Define parameters for QTreeWidget
        weighting_list = []
        string_check_list = []

        iterator = QTreeWidgetItemIterator(qTree)
        while iterator.value():
            item = iterator.value()
            try:
                weighting_list.append(float(item.text(1)))
            except ValueError:
                string_check_list.append(item.text(1))
            iterator += 1

        # Check if a string is used as weighting; False (check fails) if string is found, True if check passes
        new_string_check_list = list(filter(None, string_check_list))
        string_check = False if len(new_string_check_list) > 0 else True

        total_weighting = sum(weighting_list)

        if string_check == True:
            if float(total_weighting) == 1.0:
                totalWeighting_lineEdit.setStyleSheet("color: rgb(0, 210, 0);font-weight: bold;")
                totalWeighting_lineEdit.setText('1')                
            else:
                totalWeighting_lineEdit.setText(str(total_weighting))
                if float(total_weighting) == 0.0:
                    apply_pushButton.setEnabled(False)
                    search_pushButton.setEnabled(False)
                else:
                    if len(visible_groups) > 1:
                        apply_pushButton.setEnabled(True)
                        search_pushButton.setEnabled(True)
                    else:
                        apply_pushButton.setEnabled(False)
                        search_pushButton.setEnabled(False)
        else:
            totalWeighting_lineEdit.setText('error, non-numeric found')
            totalWeighting_lineEdit.setStyleSheet("color: rgb(255, 0, 0);font-weight: bold;")


#-------------------------------Energy yield estimator-------------------------------------------
    def technical_configuration(self):
        #print('technical_configuration')
        # Define textboxes and buttons
        technology_comboBox = self.land_availability_dockwidget.technology_comboBox

        # Technology tools icon
        technology_toolButton = self.land_availability_dockwidget.technology_toolButton

        if technology_comboBox.currentText() == 'Technology':
            technology_toolButton.setEnabled(False)

        if technology_comboBox.currentText() != 'Technology':
            try:
                technology_toolButton.clicked.disconnect(self.PV.configure_PV_tools)
            except TypeError:
                pass
            try:
                technology_toolButton.clicked.disconnect(self.PV_Canopy.configure_PV_canopy_tools)
            except TypeError:
                pass
            try:
                technology_toolButton.clicked.disconnect(self.WIND.configure_WIND_tools)
            except TypeError:
                pass
            try:
                technology_toolButton.clicked.disconnect(self.GSHP.configure_GSHP_tools)
            except TypeError:
                pass
            # Add PV tool menus
            if technology_comboBox.currentText() == 'PV':
                technology_toolButton.clicked.connect(self.PV.configure_PV_tools)
            # Add PV canopy tool menus
            if technology_comboBox.currentText() == 'PV canopy':
                technology_toolButton.clicked.connect(self.PV_Canopy.configure_PV_canopy_tools)
            # Add Wind tool menus
            if technology_comboBox.currentText() == 'Wind':
                technology_toolButton.clicked.connect(self.WIND.configure_WIND_tools)
            # Add Ground source heat pump tool menus
            if technology_comboBox.currentText() == 'GSHP':
                technology_toolButton.clicked.connect(self.GSHP.configure_GSHP_tools)

            # Set icon properties
            technology_toolButton.setEnabled(True)

        # Run following function
        self.TechFunctions.land_areaUnits()
        self.TechFunctions.populate_EnergyYieldEstimator()
        


#-------------------------------Join policy/technical layers when recalculating opportunity map----------------------------------------
    def policy_or_technical_joins_for_update_weighted_maps(self, aspect_type):
        #print('policy_or_technical_joins_for_update_weighted_maps')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(aspect_type)
        scoring_layers_group = root.findGroup('Scoring layers')

        # Define aspect_type parameter
        lower_case = str(aspect_type).lower()

         # Define layer
        weighted_map = QgsProject.instance().mapLayersByName( "Combined " + lower_case )[0]

        # Define fields
        childField = 'ID'
        opp_mapField = 'ID'

        if aspect_type == 'Policy':
            try:                    
                # Perform joining policy aspect groups to Combined policy by first removing then rejoining them
                # In terms of attributes, only carry over the Score field for improved optimisation
                for pol_group in scoring_layers_group.children():
                    if pol_group.name() == "Policy maps":   
                        for child in pol_group.children():
                            layer = QgsProject.instance().mapLayersByName(child.name())[0]
                            root.findLayer(layer.id())
                            weighted_map.removeJoin(layer.id())
                for aspect_group in group.children():
                    for child in aspect_group.children():
                        if child.isVisible():
                            layer = QgsProject.instance().mapLayersByName(child.name())[0]
                            root.findLayer(layer.id())
                            weighted_map.removeJoin(layer.id())
                for pol_group in scoring_layers_group.children():
                    if pol_group.name() == "Policy maps":   
                        for child in pol_group.children():
                            aspect_group = root.findGroup(str(child.name()))
                            if aspect_group.isVisible():
                                joinObject = QgsVectorLayerJoinInfo()
                                joinObject.setJoinFieldName(childField)
                                joinObject.setTargetFieldName(opp_mapField)
                                joinObject.setJoinLayerId(child.layer().id())
                                joinObject.setJoinFieldNamesSubset([child.name(), 'Score'])
                                joinObject.setUsingMemoryCache(True)
                                joinObject.setJoinLayer(child.layer())
                                weighted_map.addJoin(joinObject)
            except IndexError:
                pass

        if aspect_type == 'Technical':
            try:                    
                # Perform joining technical aspect groups to Combined technical by first removing then rejoining them
                # In terms of attributes, only carry over the Score field for improved optimisation
                for tech_group in scoring_layers_group.children():
                    if tech_group.name() == "Technical maps":   
                        for child in tech_group.children():
                            layer = QgsProject.instance().mapLayersByName(child.name())[0]
                            root.findLayer(layer.id())
                            weighted_map.removeJoin(layer.id())
                for aspect_group in group.children():
                    for child in aspect_group.children():
                        if child.isVisible():
                            layer = QgsProject.instance().mapLayersByName(child.name())[0]
                            root.findLayer(layer.id())
                            weighted_map.removeJoin(layer.id())
                for tech_group in scoring_layers_group.children():
                    if tech_group.name() == "Technical maps":   
                        for child in tech_group.children():
                            aspect_group = root.findGroup(str(child.name()))
                            if aspect_group.isVisible():
                                joinObject = QgsVectorLayerJoinInfo()
                                joinObject.setJoinFieldName(childField)
                                joinObject.setTargetFieldName(opp_mapField)
                                joinObject.setJoinLayerId(child.layer().id())
                                joinObject.setJoinFieldNamesSubset([child.name(), 'Score'])
                                joinObject.setUsingMemoryCache(True)
                                joinObject.setJoinLayer(child.layer())
                                weighted_map.addJoin(joinObject)
            except IndexError:
                pass


#------------------------------- Update opportunity map -------------------------------------------
    def update_weighted_maps(self, aspect_type):
        #print('update_weighted_maps')
        # Define root and groups   
        root = QgsProject.instance().layerTreeRoot()

        # Define User-defined weighting layer
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id())

        # Define constant parameters for formula
        delim1 = ' OR '
        delim2 = ' + '
        delim3 = '||\',\'+'

        # Get scoring settings
        score_method, score_rounding, score_system = self.General.scoring_method_ok(None)
        
        try:
            # For policy or during startup
            if aspect_type in ('Policy', 'Both'):
                policy_group = root.findGroup('Policy')
                for group in policy_group.children():
                    # Match Opportunity layer with group aspects name
                    policy_oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                    # Loop until Score field is completely deleted 
                    while True:
                        score_index = policy_oppMap.fields().indexFromName('Score')
                        if score_index != -1:
                            policy_oppMap.removeExpressionField(score_index)
                        else:
                            break
                    # Define equal weighting formula
                    layers = [g.name() for g in group.children()]

                    if score_system == 'lenient':
                        formula = score_method + "_func_factors('" + policy_oppMap.name() + "', '" + score_rounding + "')"
                        '''
                        fscorestrs = {k:delim1.join('"{layer}_Score" = {N}\n'.format(
                            layer = l, N = k) for l in layers) for k in range(1, 5)}

                        coalesce_function = {k:delim2.join('coalesce(("{layer}_Score" / "{layer}_Score"), 0)'.format(
                                        layer = l, N = k) for l in layers) for k in range(1, 5)}

                        division_function = ' / ('+ coalesce_function[1] + ')'

                        average_fscorestrs = {k:delim2.join('coalesce("{layer}_Score", 0)'.format(
                                        layer = l, N = k) for l in layers) for k in range(1, 5)}
                        average_formula = '(' + (average_fscorestrs[1]) + ') ' + division_function
                        
                        if score_rounding == 'optimistic':
                            formula = str("""CASE """ +
                                    """\nWHEN """ + fscorestrs[4] + """ THEN 4 """ +
                                    """\nWHEN """ + average_formula + """ >= 2 AND """ + average_formula +  """ < 3 THEN 2 """ +
                                    """\nWHEN """ + average_formula + """ >= 1 AND """ + average_formula +  """ < 2 THEN 1 """ +
                                    """\nWHEN """ + average_formula + """ < 1 THEN 1 END """)
                        else:
                            formula = str("""CASE """ +
                                """\nWHEN """ + fscorestrs[4] + """ THEN 4 """ +
                                """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                                """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                                """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)
                        '''
                    if score_system == 'stringent':
                        formula = "sum_func_factors('" + policy_oppMap.name() + "')"
                        '''
                        fscorestrs = {k:delim1.join('"{layer}_Score" = {N}\n'.format(
                            layer = l, N = k) for l in layers) for k in range(1, 5)}

                        formula = ("CASE WHEN " +
                                fscorestrs[4] + " THEN 4 WHEN " +
                                fscorestrs[3] + " THEN 3 WHEN " +
                                fscorestrs[2] + " THEN 2 WHEN " +
                                fscorestrs[1] + " THEN 1 ELSE 1 END")
                        '''
                    # "Score" field is created and formula applied
                    field = QgsField( 'Score', QVariant.Int )
                    policy_oppMap.addExpressionField( formula, field )

            # For technical or during startup
            if aspect_type in ('Technical', 'Both'):
                technical_group = root.findGroup('Technical')
                for group in technical_group.children():
                    # Match Opportunity layer with group aspects name
                    technical_oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                    # Loop until Score field is completely deleted 
                    while True:
                        score_index = technical_oppMap.fields().indexFromName('Score') 
                        if score_index != -1:
                            technical_oppMap.removeExpressionField(score_index)
                        else:
                            break
                    # Define equal weighting formula
                    layers = [g.name() for g in group.children()]

                    if score_system == 'lenient':
                        formula = score_method + "_func_factors('" + technical_oppMap.name() + "', '" + score_rounding + "')"
                        '''
                        coalesce_function = {k:delim2.join('coalesce(("{layer}_Score" / "{layer}_Score"), 0)'.format(
                                        layer = l, N = k) for l in layers) for k in range(1, 5)}

                        division_function = ' / ('+ coalesce_function[1] + ')'

                        average_fscorestrs = {k:delim2.join('coalesce("{layer}_Score", 0)'.format(
                                        layer = l, N = k) for l in layers) for k in range(1, 5)}
                        
                        average_formula = '(' + (average_fscorestrs[1]) + ') ' + division_function
                        
                        if score_rounding == 'optimistic':
                            formula = str("""CASE """ +
                                    """\nWHEN """ + average_formula + """ >= 2 AND """ + average_formula +  """ < 3 THEN 2 """ +
                                    """\nWHEN """ + average_formula + """ >= 1 AND """ + average_formula +  """ < 2 THEN 1 """ +
                                    """\nWHEN """ + average_formula + """ < 1 THEN 1 END """)
                        else:
                            formula = str("""CASE """ +
                                """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                                """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                                """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)
                            '''
                    if score_system == 'stringent':
                        formula = "sum_func_factors('" + technical_oppMap.name() + "')"
                        '''
                        fscorestrs = {k:delim1.join('"{layer}_Score" = {N}\n'.format(
                                layer = l, N = k) for l in layers) for k in range(1, 5)}

                        formula = ("CASE WHEN " +
                                fscorestrs[3] + " THEN 3 WHEN " +
                                fscorestrs[2] + " THEN 2 WHEN " +
                                fscorestrs[1] + " THEN 1 ELSE 1 END")
                        '''
                    # "Score" field is created and formula applied
                    field = QgsField( 'Score', QVariant.Int )
                    technical_oppMap.addExpressionField( formula, field )

            # If user-defined weighting layer is not checked
            if userDefined_node.itemVisibilityChecked() == False:
                # Run following functions
                QApplication.setOverrideCursor(Qt.WaitCursor)
                if aspect_type in ('Policy', 'Both'):
                    self.policy_or_technical_joins_for_update_weighted_maps('Policy')
                    self.live_update_combined_map('Policy')
                if aspect_type in ('Technical', 'Both'):
                    self.policy_or_technical_joins_for_update_weighted_maps('Technical')
                    self.live_update_combined_map('Technical')
                self.connect_PolTech('final')
                self.calculate_area_2()
                if not self.GOMapLive_button.isChecked():
                    self.GOMapLive_button.trigger()
                QApplication.restoreOverrideCursor()
            else:                 
                # If user-defined weighting is checked
                # Run following functions
                state = False
                QApplication.setOverrideCursor(Qt.WaitCursor)
                if aspect_type in ('Policy', 'Both'):
                    policyTotalWeighting_lineEdit = self.dockwidget.policyTotalWeighting_lineEdit
                    #if policyTotalWeighting_lineEdit.text() == '1':
                    if (0.99 <= float(policyTotalWeighting_lineEdit.text()) <= 1.01):
                        self.policy_or_technical_joins_for_update_weighted_maps('Policy')
                        self.live_update_combined_map('Policy')
                        state = True
                    else:
                        if policy_group:
                            iface.messageBar().pushMessage("", 'Policy weighting must equal 1 (current weighting = ' + 
                                policyTotalWeighting_lineEdit.text() + ').', Qgis.Warning, 7)

                if aspect_type in ('Technical', 'Both'):
                    technicalTotalWeighting_lineEdit = self.dockwidget.technicalTotalWeighting_lineEdit
                    #if technicalTotalWeighting_lineEdit.text() == '1':
                    if (0.99 <= float(technicalTotalWeighting_lineEdit.text()) <= 1.01):
                        self.policy_or_technical_joins_for_update_weighted_maps('Technical')
                        self.live_update_combined_map('Technical')
                        state = True
                    else:
                        if technical_group:
                            iface.messageBar().pushMessage("", 'Technical weighting must equal 1 (current weighting = ' + 
                                technicalTotalWeighting_lineEdit.text() + ').', Qgis.Warning, 7)

                if state == True:
                    self.connect_PolTech('search')
                    self.calculate_area_2()
                    if not self.GOMapLive_button.isChecked():
                        self.GOMapLive_button.trigger()
                QApplication.restoreOverrideCursor()
        except TypeError:
            pass

        if aspect_type == 'Policy':
            progress_bar = self.policy_dockwidget.progressBar
            progress_bar.setValue(100)
        if aspect_type == 'Technical':
            progress_bar = self.technical_dockwidget.progressBar
            progress_bar.setValue(100)

#-------------------------------"Configure" Report-------------------------------------------------------
    def configure_report(self):
        #print('configure_report')
        ok_button = self.save_report_dockwidget.ok_pushButton
        cancel_button = self.save_report_dockwidget.cancel_pushButton

        try:
            ok_button.clicked.disconnect(self.report_ok)
        except TypeError:
            pass
        try:
            cancel_button.clicked.disconnect(self.report_cancel)
        except TypeError:
            pass

        self.save_report_dockwidget.report_name_lineEdit.setText(str('Name'))

        ok_button.clicked.connect(self.report_ok)
        cancel_button.clicked.connect(self.report_cancel)
        
        self.save_report_dockwidget.show()


#-------------------------------Report "OK" button-------------------------------------------
    def report_ok(self):
        #print('report_ok')
        self.save_report_dockwidget.close()
        self.report()


#-------------------------------Report "Cancel" button-------------------------------------------
    def report_cancel(self):
        #print('report_cancel')
        self.save_report_dockwidget.close()


#------------------------------- Load PdfFileMerger module-------------------------------------------
    def pdf_merger(self):
        # Import PyPDF2
        sys.path.append(self.plugin_dir + '/modules')
        from PyPDF2 import PdfFileMerger
        
        merger = PdfFileMerger()
        return merger


#-------------------------------Create report for opportunity map-------------------------------------------
    def report(self):
        #print('report')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')
        scope_group = root.findGroup('Scope')

        # Define scoring methods
        lenient_radioButton = self.settings_dockwidget.lenient_radioButton
        stringent_radioButton = self.settings_dockwidget.stringent_radioButton
        if lenient_radioButton.isChecked():
            score_system = 'Lenient'
        if stringent_radioButton.isChecked():
            score_system = 'Stringent'

        # Get project name    
        for child in root.children():
            if isinstance(child, QgsLayerTreeGroup):
                city_name = child.name()

        # Get scope layer
        for layer in scope_group.children():
            if layer.isVisible() and layer.name() != 'New scope':
                scope = layer.name()

        # Set waiting cursor
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create lists for parameters and aspects
        report_first_column = []
        report_second_column = ['<Div style="margin-top:-40px"/>']
        report_third_column = ['<Div style="margin-top:-40px"/>']

        # Define technology combo box
        technology_comboBox = self.land_availability_dockwidget.technology_comboBox

        units_dict = {u'm\u00B2': 'm<sup>2</sup>', u'km\u00B2': 'km<sup>2</sup>', 'acre': 'acre', 'ha': 'ha'}
        units = units_dict[self.land_availability_dockwidget.areaUnits_combo_2.currentText()]

        # Define weighting layer
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id()) 

        if userDefined_node.itemVisibilityChecked() == False:
            weighting_aspect = 'Equal'
        else:
            weighting_aspect = 'User-defined'

        # Define utilistion aspect and check boxes for green, amber, red score categories
        utilisation_green_spinBox = self.land_availability_dockwidget.utilisation_green_spinBox.text()
        utilisation_amber_spinBox = self.land_availability_dockwidget.utilisation_amber_spinBox.text()
        utilisation_red_spinBox = self.land_availability_dockwidget.utilisation_red_spinBox.text()
        utilisation_black_spinBox = self.land_availability_dockwidget.utilisation_black_spinBox.text()

        area1 = 0
        area2 = 0
        area3 = 0
        area4 = 0

        area1 = float(self.land_availability_dockwidget.area_Score1_lineEdit.text().replace(',',''))
        area2 = float(self.land_availability_dockwidget.area_Score2_lineEdit.text().replace(',',''))
        area3 = float(self.land_availability_dockwidget.area_Score3_lineEdit.text().replace(',',''))
        area4 = float(self.land_availability_dockwidget.area_Score4_lineEdit.text().replace(',',''))

        total_area = float(area1 + area2 + area3 + area4)

        # Units
        units_m = u'm\u00B2'
        units_km = u'km\u00B2'
        units_acre = 'acre'
        units_ha = 'ha'

        if self.land_availability_dockwidget.areaUnits_combo.currentText() == units_m:
            final_area = total_area
        if self.land_availability_dockwidget.areaUnits_combo.currentText() == units_km:
            final_area = total_area * 1000
        if self.land_availability_dockwidget.areaUnits_combo.currentText() == units_acre:
            final_area = total_area / 0.000247105
        if self.land_availability_dockwidget.areaUnits_combo.currentText() == units_ha:
            final_area = total_area / 0.0001

        # Begin Report
        report_file_name = self.save_report_dockwidget.report_name_lineEdit.text()
        report_title = 'Opportunity report for ' + str(report_file_name)

        land_info = str(
            '<b>Input</b>'
            '<br>Scope: ' + str(scope) +
            '<br>Weighting: ' + weighting_aspect +
            '<br>Scoring: ' + str(score_system) +                
            '<br>Land availability (' + units + "): {:,.1f}".format(total_area) +
            '<br>Utilisation factor: ' +
            '<br>&emsp;Green - ' + str(utilisation_green_spinBox) +
            '<br>&emsp;Amber - ' + str(utilisation_amber_spinBox) +
            '<br>&emsp;Red - ' + str(utilisation_red_spinBox) +
            '<br>&emsp;Black - ' + str(utilisation_black_spinBox)
            )

        report_first_column.append(land_info)
    
        ### PV ###
        if technology_comboBox.currentText() == 'PV':
            # Get data to calculate energy yield and house equivalent
            ouput_energy = float(self.configure_pv_dockwidget.energy_spinBox.value())
            house_consumption = float(self.configure_pv_dockwidget.houseConsumption_spinBox.value())

            # Populate report
            report_first_column.append(
                '<br>Average dwelling consumption (kWh/yr): ' + str(int(house_consumption)) +
                '<br>' + u'Output energy (kWh/m<sup>2</sup>yr): ' + str(ouput_energy))

        ### PV canopy ###
        if technology_comboBox.currentText() == 'PV canopy':
            ouput_energy = int(self.configure_pv_canopy_dockwidget.energy_spinBox.value())        
            ev_consumption = float(self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value())

            # Populate report
            report_first_column.append(
                '<br>Average electric vehicle consumption (kWh/yr): ' + str(int(ev_consumption)) +
                '<br>' + u'Output energy (kWh/m<sup>2</sup>yr): ' + str(ouput_energy))

        ### Wind ###
        if technology_comboBox.currentText() == 'Wind':
            speed = int(self.configure_wind_dockwidget.windSpeed_spinBox.value())
            efficiency = int(self.configure_wind_dockwidget.turbineEfficiency_spinBox.value())
            house_consumption = float(self.configure_wind_dockwidget.houseConsumption_spinBox.value())

            rotor = 1
            air_density = 1.23
            swept_area = float(3.14 * (rotor / 2)**2)
            efficiency_percentage = float(efficiency) / float(100)        
            power = float(0.5 * float(air_density) * float(swept_area) * (speed**3) * efficiency_percentage)
            # Convert power (W) into energy (kWh)
            energy_generation = float(power * (24 * 365)) / float(1000)

            # Power density
            power_density = float(energy_generation) / float(swept_area)

            # Populate report
            report_first_column.append(
                '<br>Average dwelling consumption (kWh/yr): ' + str(int(house_consumption)) +
                '<br>Wind speed (m/s): ' + str(speed) +
                '<br>Turbine efficiency (%): ' + str(efficiency) +
                '<br>Power density kW/m<sup>2</sup>: ' + str("{:,.1f}".format(power_density)))

        ### Ground Source Heat Pumps ###
        if technology_comboBox.currentText() == 'GSHP':
            ouput_energy = int(self.configure_gshp_dockwidget.energy_spinBox.value())
            heat_loss = int(self.configure_gshp_dockwidget.heatLoss_spinBox.value())
            house_consumption = float(self.configure_gshp_dockwidget.houseConsumption_spinBox.value())

            # Populate report
            report_first_column.append(
                '<br>Average dwelling consumption (kWh/yr): ' + str(int(house_consumption)) +
                '<br>' + u'Heat density (kW/m<sup>2</sup>): ' + str(ouput_energy) +
                '<br>Heat loss (%): ' + str(heat_loss))

        # Get energy yield and dwelling/EV equivalent values from summary message box
        try:
            msgBar = self.TechFunctions.return_messageBar()
            energy_yield = str(msgBar.children()[7].children()[2].toPlainText().split()[8])
            dwelling_ev_equivalent = str(msgBar.children()[7].children()[2].toPlainText().split()[13])

            report_first_column.append(
                '<br><br><b>Output</b>' +
                '<br>Technology: ' +  technology_comboBox.currentText() + 
                '<br>Energy yield (MWh/yr): ' + energy_yield +
                '<br>Number of dwellings equivalent: ' + dwelling_ev_equivalent)
        except IndexError:
            pass

        ### Equal weighting ###
        if weighting_aspect == 'Equal':
            # Get all policy layers and colour them (green if on, red if off)
            for aspects in policy_group.children():
                report_second_column.append('<br><br><b>' + aspects.name() + '</b>')
                for layers in aspects.children():
                    score_index = layers.layer().fields().indexFromName('Score')
                    scores_list = layers.layer().uniqueValues(score_index)
                    #scores_list.sort()
                    score = str(scores_list).replace('[', '').replace(']', '').replace('L', '')
                    if layers.isVisible():
                        report_second_column.append('<br><font color=\"#21d314\">{}'.format(layers.name() + ' - ' + score) + '</font>')
                    else:
                        report_second_column.append('<br><font color=\"#ff0000\">{}'.format(layers.name() + ' - ' + score) + '</font>')
            # Get all technical layers and colour them (green if on, red if off)
            for aspects in technical_group.children():
                report_third_column.append('<br><br><b>' + aspects.name() + '</b>')
                for layers in aspects.children():
                    score_index = layers.layer().fields().indexFromName('Score')
                    scores_list = layers.layer().uniqueValues(score_index)
                    #scores_list.sort()
                    score = str(scores_list).replace('[', '').replace(']', '').replace('L', '')
                    if layers.isVisible():
                        report_third_column.append('<br><font color=\"#21d314\">{}'.format(layers.name() + ' - ' + score) + '</font>')
                    else:
                        report_third_column.append('<br><font color=\"#ff0000\">{}'.format(layers.name() + ' - ' + score) + '</font>')

        ### User-defined weighting ###
        if weighting_aspect == 'User-defined':
            policy_group = root.findGroup('Policy')
            technical_group = root.findGroup('Technical')

            policy_weighting_aspect_treeWidget = self.policy_dockwidget.policy_weighting_aspect_treeWidget
            technical_weighting_aspect_treeWidget = self.technical_dockwidget.technical_weighting_aspect_treeWidget

            qTrees = [policy_weighting_aspect_treeWidget, technical_weighting_aspect_treeWidget]

            policy_aspects = [groups.name() for groups in policy_group.children()]
            technical_aspects = [groups.name() for groups in technical_group.children()]
            all_aspects = policy_aspects + technical_aspects
            # Store all policy and layer aspects with weightings in dictionary
            weighting_dict = {}

            for qTree in qTrees:
                iterator = QTreeWidgetItemIterator(qTree)
                while iterator.value():
                    item = iterator.value()
                    try:
                        if str(item.text(0)) in all_aspects:
                            weighting_dict[str(item.text(0))] = str(item.text(1))
                    except ValueError:
                        pass
                    iterator += 1

            for aspects in policy_group.children():
                report_second_column.append('<br><br><b>' + aspects.name() + ' - ' + weighting_dict[aspects.name()] + '</b>')
                for layers in aspects.children():
                    score_index = layers.layer().fields().indexFromName('Score')
                    scores_list = layers.layer().uniqueValues(score_index)
                    #scores_list.sort()
                    score = str(scores_list).replace('[', '').replace(']', '').replace('L', '')
                    if layers.isVisible():
                        report_second_column.append('<br><font color=\"#21d314\">{}'.format(layers.name() + ' - ' + score) + '</font>')
                    else:
                        report_second_column.append('<br><font color=\"#ff0000\">{}'.format(layers.name() + ' - ' + score) + '</font>')
            for aspects in technical_group.children():
                report_third_column.append('<br><br><b>' + aspects.name() + ' - ' + weighting_dict[aspects.name()] + '</b>')
                for layers in aspects.children():
                    score_index = layers.layer().fields().indexFromName('Score')
                    scores_list = layers.layer().uniqueValues(score_index)
                    #scores_list.sort()
                    score = str(scores_list).replace('[', '').replace(']', '').replace('L', '')
                    if layers.isVisible():
                        report_third_column.append('<br><font color=\"#21d314\">{}'.format(layers.name() + ' - ' + score) + '</font>')
                    else:
                        report_third_column.append('<br><font color=\"#ff0000\">{}'.format(layers.name() + ' - ' + score) + '</font>')

        ### Set up main report in #print Layout ###
        canvas = iface.mapCanvas()
        template_path = str(self.plugin_dir) + '/report/layout_main.qpt'
        template_file = open(template_path)
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)
        composition = QgsPrintLayout(QgsProject.instance())
        composition.loadFromTemplate(document, QgsReadWriteContext())

        # Set page orientation
        composition.pageCollection().page(0).setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)

        # html frames
        results_frame = composition.itemById('results_frame') 
        composer_results = results_frame.multiFrame()

        # Append html tag (as we are formatting in HTML)
        final_string_results = ''.join(report_first_column)

        # Set html frames
        composer_results.setHtml(final_string_results)
        composer_results.loadHtml()

        # Set title
        title_item = composition.itemById('title')
        title_item.setText(report_title)

        # Set map
        map_item = composition.itemById('map')
        #map_item.setExtent(canvas.extent())
        map_item.zoomToExtent(canvas.extent())

        # Set tag
        if self.save_report_dockwidget.tag_checkBox.isChecked():
            tag_item = composition.itemById('tag')
            tag = str("Tag: " + timestamp + "_" + city_name + "_" + weighting_aspect + ' weightings_' + score_system + " scoring")
            tag_item.setText(tag)

        # Set legend
        legend_item = composition.itemById('legend')
        #print(dir(legend_item))
        legend_item.updateLegend()
        #legend_item.update()

        # Set North Arrow
        arrow = composition.itemById('north_arrow')
        arrow.setPicturePath(str(self.plugin_dir) + '/report/north_arrow.svg')

        # Refresh
        composition.refresh()

        # Export Report to PDF        
        exporter = QgsLayoutExporter(composition)
        output_path_main = QgsProject.instance().readPath("./") + '/Reports/' + report_file_name + '_main.pdf'

        sleep(5)
        # Settings to output map as raster for quality and size
        dpi = self.save_report_dockwidget.dpi_spinBox.value()
        settings = QgsLayoutExporter.PdfExportSettings()
        settings.dpi = int(dpi)
        settings.rasterizeWholeImage = True
        exporter.exportToPdf(output_path_main, settings)
        sleep(5)
        
        ### Set up parameter report in #print Layout ###
        template_path_parameters = str(self.plugin_dir) + '/report/layout_parameters.qpt'
        template_file_parameters = open(template_path_parameters)
        template_content_parameters = template_file_parameters.read()
        template_file_parameters.close()
        document_parameters = QDomDocument()
        document_parameters.setContent(template_content_parameters)
        composition_parameters = QgsPrintLayout(QgsProject.instance())
        composition_parameters.loadFromTemplate(document_parameters, QgsReadWriteContext())

        # Set page orientation
        composition_parameters.pageCollection().page(0).setPageSize('A4', QgsLayoutItemPage.Orientation.Portrait)
        # html frames
        policy_frame = composition_parameters.itemById('policy_frame')
        technical_frame = composition_parameters.itemById('technical_frame')
        composer_policy = policy_frame.multiFrame()
        composer_technical = technical_frame.multiFrame()
        # Append html tag (as we are formatting in HTML)
        report_second_column.append('</Div>')
        report_third_column.append('</Div>')
        final_string_policy = ''.join(report_second_column)
        final_string_technical = ''.join(report_third_column)
        # Set html frames
        composer_policy.setHtml(final_string_policy)
        composer_technical.setHtml(final_string_technical)
        composer_policy.loadHtml()
        composer_technical.loadHtml()
        # Refresh
        composition_parameters.refresh()

        exporter = QgsLayoutExporter(composition_parameters)
        output_path_parameters = QgsProject.instance().readPath("./") + '/Reports/' + report_file_name + '_parameters.pdf'

        exporter.exportToPdf(output_path_parameters, QgsLayoutExporter.PdfExportSettings())
        sleep(5)

        ### Set up information report in #print Layout if not empty ###
        info_page_check = False
        if self.land_availability_dockwidget.energyYieldEstimator_textBrowser.toPlainText() != '':
            info_page_check = True
            template_path_info = str(self.plugin_dir) + '/report/layout_info.qpt'
            template_file_info = open(template_path_info)
            template_content_info = template_file_info.read()
            template_file_info.close()
            document_info = QDomDocument()
            document_info.setContent(template_content_info)
            composition_info = QgsPrintLayout(QgsProject.instance())
            composition_info.loadFromTemplate(document_info, QgsReadWriteContext())

            # Set page orientation
            composition_info.pageCollection().page(0).setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)
            # html frames
            info_frame = composition_info.itemById('info_frame')
            composer_info = info_frame.multiFrame()
            # Set html frames
            composer_info.setHtml('<font size=2.5px>' + self.land_availability_dockwidget.energyYieldEstimator_textBrowser.toHtml() + '</font>')
            composer_info.loadHtml()
            # Refresh
            composition_info.refresh()

            exporter = QgsLayoutExporter(composition_info)
            output_path_info = QgsProject.instance().readPath("./") + '/Reports/' + report_file_name + '_info.pdf'

            exporter.exportToPdf(output_path_info, QgsLayoutExporter.PdfExportSettings())
            sleep(5)
        
        # Merge main and parameter reports
        merger = self.pdf_merger()
        main_report = open(output_path_main, "rb")
        parameters_report = open(output_path_parameters, "rb")
        merger.append(main_report)
        merger.append(parameters_report)
        if info_page_check == True:
            info_report = open(output_path_info, "rb")
            merger.append(info_report)

        # Export final report
        final_output_path = QgsProject.instance().readPath("./") + '/Reports/' + report_file_name + '.pdf'
        try:
            output = open(final_output_path, "wb")        
            merger.write(output)
            sleep(5)
            main_report.close()
            parameters_report.close()
            output.close()
            merger.close()
            del main_report
            del parameters_report
            del merger
            del output
            # Delete initial reports
            os.remove(output_path_main)
            os.remove(output_path_parameters)
            if info_page_check == True:
                info_report.close()
                del info_report
                os.remove(output_path_info)
            # Set cursor to default and load Report
            QApplication.restoreOverrideCursor()
            iface.messageBar().pushMessage("",  u'Report generated', Qgis.Success, 5)
            subprocess.Popen([final_output_path], shell=True)
        except IOError:
            main_report.close()
            parameters_report.close()
            output.close()
            merger.close()
            del main_report
            del parameters_report
            del merger
            del output
            # Delete initial reports
            os.remove(output_path_main)
            os.remove(output_path_parameters)
            if info_page_check == True:
                info_report.close()
                del info_report
                os.remove(output_path_info)

            iface.messageBar().pushMessage("", '"' + report_file_name + '" is already opened. Close the report or type another name', Qgis.Critical, 10)

            QApplication.restoreOverrideCursor()
        

#-------------------------------Update policy/technical aspect symbology when aspect score is modified-----------------------------
    def update_layer_symbology(self):
        #print('update_layer_symbology')
        # Define root, groups and layer
        layer = iface.activeLayer()
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        for groups in policy_group.children():
            for layers in groups.children():
                if layer.name() == layers.name():
                    aspect_type = 'Policy'

        for groups in technical_group.children():
            for layers in groups.children():
                if layer.name() == layers.name():
                    aspect_type = 'Technical'

        # Define field and symbology
        idx = layer.fields().indexFromName("Score")   
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())

        # If Score field exists, style it
        if idx != -1:        
            if aspect_type == 'Policy':                          
                if layer.minimumValue(idx) == 1 and layer.maximumValue(idx) == 1:
                    symbol.setColor(QColor('#00ff00'))
                if layer.minimumValue(idx) == 2 and layer.maximumValue(idx) == 2:
                    symbol.setColor(QColor('#f0ab64'))
                if layer.minimumValue(idx) == 3 and layer.maximumValue(idx) == 3:
                    symbol.setColor(QColor('#963634'))
                if layer.minimumValue(idx) == 4 and layer.maximumValue(idx) == 4:
                    symbol.setColor(QColor('#1d1b10'))
                elif layer.minimumValue(idx) != layer.maximumValue(idx):
                    style_rules = (
                        ('Possible', """""Score" = 1""", '#00ff00'),
                        ('Intermediate', """"Score" = 2""", '#f0ab64'),
                        ('Sensitive', """"Score" = 3""", '#963634'),
                        ('Showstopper', """"Score" = 4""", '#1d1b10'),
                    )
                    # Create a new rule-based renderer
                    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                    renderer = QgsRuleBasedRenderer(symbol)
                    # Get the "root" rule
                    root_rule = renderer.rootRule()
                    for label, expression, color_name in style_rules:
                        # Set outline colour to match that of polygon fill colour
                        # Create a clone (i.e. a copy) of the default rule
                        rule = root_rule.children()[0].clone()
                        # Set the label, expression and color
                        rule.setLabel(label)
                        rule.setFilterExpression(expression)
                        rule.symbol().setColor(QColor(color_name))
                        # Append the rule to the list of rules
                        root_rule.appendChild(rule)
                    # Delete the default rule
                    root_rule.removeChildAt(0)
                    # Apply the renderer to the layer
                    layer.setRenderer(renderer)
                    root.findLayer(layer.id()).setExpanded(False)

            if aspect_type == 'Technical':
                if layer.minimumValue(idx) == 1 and layer.maximumValue(idx) == 1:
                    symbol.setColor(QColor('#00ff00'))
                if layer.minimumValue(idx) == 2 and layer.maximumValue(idx) == 2:
                    symbol.setColor(QColor('#f0ab64'))
                if layer.minimumValue(idx) == 3 and layer.maximumValue(idx) == 3:
                    symbol.setColor(QColor('#963634'))
                elif layer.minimumValue(idx) != layer.maximumValue(idx):
                    style_rules = (
                        ('Favourable', """""Score" = 1""", '#00ff00'),
                        ('Likely', """"Score" = 2""", '#f0ab64'),
                        ('Unlikely', """"Score" = 3""", '#963634'),
                    )
                    # Create a new rule-based renderer
                    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                    renderer = QgsRuleBasedRenderer(symbol)
                    # Get the "root" rule
                    root_rule = renderer.rootRule()
                    for label, expression, color_name in style_rules:
                        # Set outline colour to match that of polygon fill colour
                        # Create a clone (i.e. a copy) of the default rule
                        rule = root_rule.children()[0].clone()
                        # Set the label, expression and color
                        rule.setLabel(label)
                        rule.setFilterExpression(expression)
                        rule.symbol().setColor(QColor(color_name))
                        # Append the rule to the list of rules
                        root_rule.appendChild(rule)
                    # Delete the default rule
                    root_rule.removeChildAt(0)
                    # Apply the renderer to the layer
                    layer.setRenderer(renderer)
                    root.findLayer(layer.id()).setExpanded(False)
            # If GOMap Live is activated, make all layers 100% transparent
            if self.GOMapLive_button.isChecked():
                layer.setOpacity(0)
            else:
                # Otherwise show them
                layer.setOpacity(100)
            # Refresh layers
            layer.triggerRepaint()
            iface.layerTreeView().refreshLayerSymbology(layer.id())

        # Run update_weighted_maps() function
        self.update_weighted_maps('Both')



#------------------------------- Toggle policy weighting aspect Interface-------------------------------------------
    def toggle_GOMap_Interface(self, checked):
        #print('toggle_GOMap_Interface')
        if checked:
            policyTotalWeighting_lineEdit = self.dockwidget.policyTotalWeighting_lineEdit
            technicalTotalWeighting_lineEdit = self.dockwidget.technicalTotalWeighting_lineEdit

            policyTotalWeighting_lineEdit.setVisible(False)
            technicalTotalWeighting_lineEdit.setVisible(False)
            self.policy_dockwidget.show()
            self.technical_dockwidget.show()
            #self.dockwidget.show()
        # If unchecked, hide interface
        else:
            self.policy_dockwidget.hide()
            self.technical_dockwidget.hide()
            #self.dockwidget.hide()


#-------------------------------Connect opportunity map layer to GOMap Live function-----------------------------------------
    def opportunity_GOMapLive_connection(self):
        #print('opportunity_GOMapLive_connection')
        # Connect opportunity map to GOMap Live button when its visibility is clicked
        self.GOMapLive_button.trigger()


#-------------------------------Create GOMap Interface-------------------------------------------
    def run(self):
        #print('run')
        #################################################################################
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True
            '''
            # Create the dockwidget (after translation) and keep reference
            if self.dockwidget == None:
            '''

            # Set the dockwidgets
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.policy_dockwidget)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.technical_dockwidget)            
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.create_scope_dockwidget)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

            #################################################################################
            # Create timestamp
            global timestamp
            date = datetime.datetime.now()
            timestamp = date.strftime('%d/%m/%Y')

             # Define root and groups
            root = QgsProject.instance().layerTreeRoot()
            policy_group = root.findGroup('Policy')
            technical_group = root.findGroup('Technical')

            # Connect all policy layers to refresh_weighting_aspect_list_sub_aspects() function when ticked/unticked
            for pol_groups in policy_group.children():
                for layers in pol_groups.children():
                    layers.visibilityChanged.connect(partial(self.refresh_weighting_aspect_list_main_aspects, 'Policy'))

            # Connect all technical layers to refresh_weighting_aspect_list_sub_aspects() function when ticked/unticked
            for tech_group in technical_group.children():
                for layers in tech_group.children():
                    layers.visibilityChanged.connect(partial(self.refresh_weighting_aspect_list_main_aspects, 'Technical'))

            # When save aspect options interface is open and user clicks on another layer, close interface
            iface.currentLayerChanged.connect(self.General.save_constraint_cancel)

            # Update opportunity map when Apply button is clicked by running update_weighted_maps() function
            policyApply_pushButton = self.policy_dockwidget.policyApply_pushButton
            policyApply_pushButton.clicked.connect(partial(self.update_weighted_maps, 'Policy'))
            policyApply_pushButton.setToolTip('Apply policy weightings')

            technicalApply_pushButton = self.technical_dockwidget.technicalApply_pushButton
            technicalApply_pushButton.clicked.connect(partial(self.update_weighted_maps, 'Technical'))
            technicalApply_pushButton.setToolTip('Apply technical weightings')

            # AHP
            policyAHP_pushButton = self.policy_dockwidget.policyAHP_pushButton
            policyAHP_pushButton.clicked.connect(partial(self.Statistics.show_AHP, 'Policy'))
            policyAHP_pushButton.setToolTip('Perform Analytical Hierarchy Process (AHP) on policy aspects')

            technicalAHP_pushButton = self.technical_dockwidget.technicalAHP_pushButton
            technicalAHP_pushButton.clicked.connect(partial(self.Statistics.show_AHP, 'Technical'))
            technicalAHP_pushButton.setToolTip('Perform Analytical Hierarchy Process (AHP) on techincal aspects')

            AHPWeightingsApply_pushButton = self.ahp_dockwidget.AHPWeightingsApply_pushButton
            AHPWeightingsApply_pushButton.clicked.connect(self.ahp_weightings_applied_to_opportunity_map)
            AHPWeightingsApply_pushButton.setToolTip('Apply AHP weightings to current opportunity map')

            # Search
            policySearch_pushButton = self.policy_dockwidget.policySearch_pushButton
            #policySearch_pushButton.clicked.connect(partial(self.weighting_search, 'Policy'))
            policySearch_pushButton.clicked.connect(partial(self.confirm_weighting_search, 'Policy'))
            policySearch_pushButton.setToolTip('Search for best policy weighting combination')

            technicalSearch_pushButton = self.technical_dockwidget.technicalSearch_pushButton
            #technicalSearch_pushButton.clicked.connect(partial(self.weighting_search, 'Technical'))
            technicalSearch_pushButton.clicked.connect(partial(self.confirm_weighting_search, 'Technical'))
            technicalSearch_pushButton.setToolTip('Search for best technical weighting combination')

            # Load report
            report_button = self.land_availability_dockwidget.report_pushButton
            report_button.clicked.connect(self.configure_report)
            report_button.setToolTip('Generate report including all text below')

            # Area
            self.land_availability_dockwidget.area_label.setToolTip('Available land measured in selected units.')
            # Define squared units combobox for land availability
            oppMap_units = [u'm\u00B2', u'km\u00B2', 'acre', 'ha']
            # Clear units combobox
            self.land_availability_dockwidget.areaUnits_combo.clear()
            # Add units to units combobox
            self.land_availability_dockwidget.areaUnits_combo.addItems(oppMap_units)
            self.land_availability_dockwidget.areaUnits_combo.setToolTip('Units')

            # Clear units combobox
            self.land_availability_dockwidget.areaUnits_combo_2.clear()
            # Add units to units combobox
            self.land_availability_dockwidget.areaUnits_combo_2.addItems(oppMap_units)
            self.land_availability_dockwidget.areaUnits_combo_2.setToolTip('Units')

            # Connect utilisation factor spinbox to function
            self.land_availability_dockwidget.utilisation_label.setToolTip('Utilisation factor:' +
                                                                                 '\nPercentage of available land to be used for development')
            self.land_availability_dockwidget.utilisation_green_spinBox.setToolTip('Utilisation factor:' +
                                                                                 '\nPercentage of available land to be used for development')
            self.land_availability_dockwidget.utilisation_green_spinBox.setKeyboardTracking(False)
            self.land_availability_dockwidget.utilisation_green_spinBox.valueChanged.connect(self.calculate_area_2)

            self.land_availability_dockwidget.utilisation_amber_spinBox.setToolTip('Utilisation factor:' +
                                                                                 '\nPercentage of available land to be used for development')
            self.land_availability_dockwidget.utilisation_amber_spinBox.setKeyboardTracking(False)
            self.land_availability_dockwidget.utilisation_amber_spinBox.valueChanged.connect(self.calculate_area_2)

            self.land_availability_dockwidget.utilisation_red_spinBox.setToolTip('Utilisation factor:' +
                                                                                 '\nPercentage of available land to be used for development')
            self.land_availability_dockwidget.utilisation_red_spinBox.setKeyboardTracking(False)
            self.land_availability_dockwidget.utilisation_red_spinBox.valueChanged.connect(self.calculate_area_2)

            self.land_availability_dockwidget.utilisation_black_spinBox.setToolTip('Utilisation factor:' +
                                                                                 '\nPercentage of available land to be used for development')
            self.land_availability_dockwidget.utilisation_black_spinBox.setKeyboardTracking(False)
            self.land_availability_dockwidget.utilisation_black_spinBox.valueChanged.connect(self.calculate_area_2)

            # Define technologies 
            technology_comboBox = self.land_availability_dockwidget.technology_comboBox
            technologies = ['Technology', 'PV', 'PV canopy', 'Wind', 'GSHP']
            technology_comboBox.clear()
            technology_comboBox.addItems(technologies)
            technology_comboBox.setToolTip('Select from available technologies')
            technology_comboBox.setItemData(1, "Photovoltaic", Qt.ToolTipRole)
            technology_comboBox.setItemData(2, "Photovoltaic on canopy", Qt.ToolTipRole)
            technology_comboBox.setItemData(3, "Wind", Qt.ToolTipRole)
            technology_comboBox.setItemData(4, "Ground source heat pumps", Qt.ToolTipRole)
            technology_comboBox.currentIndexChanged.connect(self.technical_configuration)

            # Technology tools icon
            technology_toolButton = self.land_availability_dockwidget.technology_toolButton
            technology_toolButton.setIcon(QIcon(':/plugins/GOMap/icons/Configure.png'))
            technology_toolButton.setEnabled(False)
            technology_toolButton.setToolTip("Configure")
            technology_toolButton.setPopupMode(QToolButton.InstantPopup)

            # Set Land availability interface at left of GOMap interface and set size if GOMap Interface is checked
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.land_availability_dockwidget)

            # Any layers manually added will be moved to "Additional information" group
            QgsProject.instance().legendLayersAdded.connect(self.General.move_added_layer_to_information)

            # Hide Interface
            self.policy_dockwidget.hide()
            self.technical_dockwidget.hide()
            self.dockwidget.hide()
            self.create_scope_dockwidget.hide()

            # Load messageBar to hold utilised area, energy yield and dwelling/EV equivalent values
            self.TechFunctions.load_messageBar()


#-------------------------------Weighting selection-------------------------------------------
    def weighting_selection(self, layer):
        #print('weighting_selection')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()

        # Define New scope layer
        new_scope_layer = QgsProject.instance().mapLayersByName( "New scope" )[0]
        new_scope_layer_node = root.findLayer(new_scope_layer.id())

        # Define user-defined weighting layer
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id())

        # Disconnect weighting layer to function
        try:
            userDefined_node.visibilityChanged.disconnect(self.weighting_selection)
        except TypeError:
            pass

        # Define scoring method button
        lenient_radioButton = self.settings_dockwidget.lenient_radioButton
        stringent_radioButton = self.settings_dockwidget.stringent_radioButton

        # If 'Equal' weighting selected, set 'User-defined' visible to False and hide weighting dockwidget
        if userDefined_node.itemVisibilityChecked() == False:
            if stringent_radioButton.isEnabled() == False:
                stringent_radioButton.setEnabled(True)
            self.toggle_GOMap_Interface(0)

        # If 'User-defined' weighting selected, set 'Equal' visible to False and show weighting dockwidget
        else:
            lenient_radioButton.setChecked(True)
            stringent_radioButton.setEnabled(False)
            self.toggle_GOMap_Interface(1)
            self.refresh_weighting_aspect_list_main_aspects('Policy')
            self.refresh_weighting_aspect_list_main_aspects('Technical')

        if not userDefined_node.isVisible() and new_scope_layer_node.isVisible():
            self.create_scope_dockwidget.show()

        if userDefined_node.isVisible() and new_scope_layer_node.isVisible():
            self.create_scope_dockwidget.hide()

        # Reconnect weighting layer to function
        userDefined_node.visibilityChanged.connect(self.weighting_selection)

        #self.update_weighted_maps('Both')


#-------------------------------Scope-------------------------------------------
    def scope(self, layer):
        #print('scope')
        ##print(layer.name())
        ##print(layer.layer())
        # Define groups
        scope_group = self.General.identify_group_state('Scope')

        # Define layer and deselect any features
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        oppPolTech_weightedMap.selectByIds([])
        # Define source and SQL query of currently activated layer in Scope group
        # As only one layer in this group can be active when GOMap Live is on 
        #scope_layerPath = layer.layer().source()
        SQL_layer = str(layer.layer().name())
        query = """SELECT * FROM '""" + SQL_layer + """' """
        layer_list = []
        # Get active layer and save into list
        layer_list.append(layer.name())
        # Disconnect all scope layers to scope() and land_area() functions
        for layers in scope_group.children():
            if layers.name() != 'New scope':
                try:
                    layers.visibilityChanged.disconnect()
                except TypeError:
                    pass
        # Set active layer as visible
        iface.layerTreeView().setLayerVisible(layer.layer(), True)
        # Set all other layers as not visible
        for layers in scope_group.children():
            if layers.name() != 'New scope':
                if layers.name() not in layer_list:
                    layer = QgsProject.instance().mapLayersByName( layers.name() )[0]
                    iface.layerTreeView().setLayerVisible(layer, False) 
                # Reconnect all scope layers to scope() and land_area() functions
                layers.visibilityChanged.connect(self.scope)
                layers.visibilityChanged.connect(partial(self.TechFunctions.land_area, None))

        # Set opportunity map to match source of selected scope layer (this acts as a spatial filter)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        oppPolTech_weightedMap.setDataSource(
        "?query={}".format(query),
        oppPolTech_weightedMap.name(), 
        "virtual" )
        # Run connect_PolTech() function to join relevant fields
        self.connect_PolTech('final')
        # Refresh opportunity map
        oppPolTech_weightedMap.triggerRepaint()
        # Update land availability
        self.TechFunctions.land_area(None)
        self.TechFunctions.land_areaUnits()
        self.TechFunctions.populate_EnergyYieldEstimator()
        
        QApplication.restoreOverrideCursor()


#-------------------------------Show/hide unique tag------------------------------------------
    def refresh_canvas(self):
        iface.mapCanvas().refresh()


#-------------------------------Update policy/technical scoring layers with GOMap update--------------------------------
    def update_policy_or_technical_oppMaps_with_GOMap_update(self, aspect_type):
        #print('update_policy_or_technical_oppMaps_with_GOMap_update')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()

        # Define constriant_type parameter
        group = root.findGroup(aspect_type)

        # Define field
        opp_mapField = 'ID'

        # Find all visible layers in aspect groups, remove and rejoin them to each aspect group scoring layer
        for aspect_group in group.children():
            if group.isVisible():                    
                for child in aspect_group.children():
                    if child.isVisible():
                        # Match Opportunity layer with group aspects name
                        oppMap = QgsProject.instance().mapLayersByName( aspect_group.name() )[-1]
                        layer = QgsProject.instance().mapLayersByName(child.name())[0]
                        oppMap.removeJoin(layer.id())
                        childField = 'ID'
                        joinObject = QgsVectorLayerJoinInfo()
                        joinObject.setJoinFieldName(childField)
                        joinObject.setTargetFieldName(opp_mapField)
                        joinObject.setJoinLayerId(layer.id())
                        joinObject.setJoinFieldNamesSubset([layer.name(), 'Score'])
                        joinObject.setUsingMemoryCache(True)
                        joinObject.setJoinLayer(layer)
                        oppMap.addJoin(joinObject)
                    else:
                        # If layer is not visible, remove them
                        #for child in aspect_group.children():
                        oppMap = QgsProject.instance().mapLayersByName( aspect_group.name() )[-1]
                        layer = QgsProject.instance().mapLayersByName(child.name())[0]
                        oppMap.removeJoin(layer.id())
            else:
                # If aspect group is not visible, remove all layers in group from scoring layer
                for child in aspect_group.children():
                    oppMap = QgsProject.instance().mapLayersByName( aspect_group.name() )[-1]
                    layer = QgsProject.instance().mapLayersByName(child.name())[0]
                    oppMap.removeJoin(layer.id())


#-------------------------------Update scoring layers with GOMap Live-------------------------------------------
    def update_scoring_oppMaps(self, layer):
        #print('update_scoring_oppMaps')
        # Define  root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Define field
        opp_mapField = 'ID'

        node_layer = QgsProject.instance().mapLayersByName(str(layer.name()))[-1]
        node = root.findLayer(node_layer.id())

        # Define policy aspect layers
        policy_aspect_layers = [layer.name() for groups in policy_group.children() for layer in groups.children()]
        technical_aspect_layers = [layer.name() for groups in technical_group.children() for layer in groups.children()]

        if node_layer.name() in policy_aspect_layers:
            aspect_type = 'Policy'
            main_group = root.findGroup(aspect_type)
        if node_layer.name() in technical_aspect_layers:
            aspect_type = 'Technical'
            main_group = root.findGroup(aspect_type)

        # Find all visible layers in policy  groups, remove and rejoin them to each policy group scoring layer
        for group in main_group.children():
            if main_group.isVisible():
                if node.isVisible():
                    for child in group.children():
                        if node.name() == child.name():
                            # Match Opportunity layer with group aspects name
                            oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                            oppMap.removeJoin(node.layer().id())
                            childField = 'ID'
                            joinObject = QgsVectorLayerJoinInfo()
                            joinObject.setJoinFieldName(childField)
                            joinObject.setTargetFieldName(opp_mapField)
                            joinObject.setJoinLayerId(node.layer().id())
                            joinObject.setJoinFieldNamesSubset([node.name(), 'Score'])
                            joinObject.setUsingMemoryCache(True)
                            joinObject.setJoinLayer(node.layer())
                            oppMap.addJoin(joinObject)
                else:
                    # If layer is not visible, remove them
                    for child in group.children():
                        if node.name() == child.name():
                            oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                            oppMap.removeJoin(node.layer().id())
            else:
                # If policy group is not visible, remove all layers in group from scoring layer
                for child in group.children():
                    oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                    oppMap.removeJoin(child.layer().id())

        # Run following functions
        QApplication.setOverrideCursor(Qt.WaitCursor)    
        self.connect_policy_or_technical(aspect_type)
        self.live_update_combined_map(aspect_type)
        self.connect_PolTech('final')
        self.calculate_area_2()
        QApplication.restoreOverrideCursor()



#-------------------------------Join policy layers to combined policy map-------------------------------------------
    def connect_policy_or_technical(self, aspect_type):
        #print('connect_policy_or_technical')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        opportunity_group = root.findGroup('Scoring layers')

        # Define aspect_type parameter
        lower_case = str(aspect_type).lower()

        # Define layer
        weighted_map = QgsProject.instance().mapLayersByName( "Combined " + lower_case )[0]

        # Define fields
        childField = 'ID'
        opp_mapField = 'ID'

        try:                    
            # Perform joining policy layers for Combined policy
            for group in opportunity_group.children():
                if group.name() == aspect_type + " maps":   
                    for child in group.children():
                        weighted_map.removeJoin(child.layer().id())                    
            for group in opportunity_group.children():
                if group.name() == aspect_type + " maps":   
                    for child in group.children():
                        aspect_group = root.findGroup(str(child.name()))
                        if aspect_group.isVisible():
                            joinObject = QgsVectorLayerJoinInfo()
                            joinObject.setJoinFieldName(childField)
                            joinObject.setTargetFieldName(opp_mapField)
                            joinObject.setJoinLayerId(child.layer().id())
                            joinObject.setJoinFieldNamesSubset([child.name(), 'Score'])
                            joinObject.setUsingMemoryCache(True)
                            joinObject.setJoinLayer(child.layer())
                            weighted_map.addJoin(joinObject)
        except IndexError:
            pass


#-------------------------------Hide attribute fields-------------------------------------------
    def setColumnVisibility(self, layer, columnName, visible):
        #print('setColumnVisibility')
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name == columnName:
                column.hidden = not visible
                break
        config.setColumns( columns )
        layer.setAttributeTableConfig( config )


#-------------------------------Join combined scoring layers to final opportunity map-------------------------------------------
    def connect_PolTech(self, output):
        #print('connect_PolTech')
        # Define GOMap plugin directory
        plugin_dir = os.path.dirname(__file__)

        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Define layers
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        oppPol_weightedMap = QgsProject.instance().mapLayersByName( "Combined policy" )[0]
        oppTech_weightedMap = QgsProject.instance().mapLayersByName( "Combined technical" )[0]

        # Get opacity level
        opacity = oppPolTech_weightedMap.opacity()
        
        # Define fields
        childField = 'ID'
        opp_mapField = 'ID'

        # Remove and rejoin combined policy scoring layer from opportunity map
        oppPolTech_weightedMap.removeJoin(oppPol_weightedMap.id())
        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName(childField)
        joinObject.setTargetFieldName(opp_mapField)
        joinObject.setJoinLayerId(oppPol_weightedMap.id())
        joinObject.setPrefix('Policy_')
        joinObject.setJoinFieldNamesSubset(['Category'])
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(oppPol_weightedMap)
        oppPolTech_weightedMap.addJoin(joinObject) 

        # Remove and rejoin combined technical scoring layer from opportunity map
        oppPolTech_weightedMap.removeJoin(oppTech_weightedMap.id())
        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName(childField)
        joinObject.setTargetFieldName(opp_mapField)
        joinObject.setJoinLayerId(oppTech_weightedMap.id())
        joinObject.setPrefix('Technical_')
        joinObject.setJoinFieldNamesSubset(['Category'])
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(oppTech_weightedMap)
        oppPolTech_weightedMap.addJoin(joinObject)

        # If user-defined weighting search is used, pass as the function "weighting_search()" will continue
        if output == 'search':
            pass
        # Else show final result
        if output == 'final':
            # Update style for opportunity map
            # Policy + techincal
            if policy_group.isVisible() and technical_group.isVisible():
                oppPolTech_weightedMap.loadNamedStyle(plugin_dir + '/styles/opportunities_style.qml')
            # Policy
            if policy_group.isVisible() and technical_group.isVisible() == False:
                oppPolTech_weightedMap.loadNamedStyle(plugin_dir + '/styles/policy_only_style.qml')
            # Techincal
            if policy_group.isVisible() == False and technical_group.isVisible():
                oppPolTech_weightedMap.loadNamedStyle(plugin_dir + '/styles/technical_only_style.qml')
            # None
            if policy_group.isVisible() == False and technical_group.isVisible() == False:
                oppPolTech_weightedMap.loadNamedStyle(plugin_dir + '/styles/no_aspect_style.qml')

            # Set opacity and refresh opportunity map
            oppPolTech_weightedMap.setOpacity(opacity)
            oppPolTech_weightedMap.triggerRepaint()
            root.findLayer(oppPolTech_weightedMap.id()).setExpanded(True)
            iface.layerTreeView().refreshLayerSymbology(oppPolTech_weightedMap.id())

            ltl = QgsProject.instance().layerTreeRoot().findLayer(oppPolTech_weightedMap.id())
            ltm = iface.layerTreeView().layerTreeModel()
            legendNodes = ltm.layerLegendNodes(ltl)

            try:
                for ln in legendNodes:
                    ln.dataChanged.disconnect()
            except TypeError:
                pass

            for ln in legendNodes:
                ln.dataChanged.connect(partial(self.TechFunctions.land_area, ln))
                ln.dataChanged.connect(self.TechFunctions.land_areaUnits)
                ln.dataChanged.connect(self.TechFunctions.populate_EnergyYieldEstimator)


#-------------------------------Update combined map-------------------------------------------
    def live_update_combined_map(self, aspect_type):
        #print('live_update_combined_map')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        main_group = root.findGroup(aspect_type)

        # Define aspect_type parameter
        lower_case = str(aspect_type).lower()

         # Define layer
        weighted_map = QgsProject.instance().mapLayersByName( "Combined " + lower_case )[0]

        # Define user-defined weighting layer
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id())

        # Define constant parameters for formula
        delim1 = ' OR '
        delim2 = ' + '
        delim3 = ' AND '
        # Define score and category fields
        score_field = QgsField( 'Score', QVariant.Int )
        category_field = QgsField( 'Category', QVariant.String )

        # Loop until Score field is completely deleted
        while True:
            score_idx = weighted_map.fields().indexFromName("Score")
            if score_idx != -1:
                weighted_map.removeExpressionField(score_idx)
            else:
                break

        # Loop until Category field is completely deleted 
        while True:
            category_idx = weighted_map.fields().indexFromName("Category")
            if category_idx != -1:       
                weighted_map.removeExpressionField(category_idx)
            else:
                break
        
        try:
            groups = []
            for group in main_group.children():
                if group.isVisible():
                    groups.append(group.name())

            # Get scoring settings
            score_method, score_rounding, score_system = self.General.scoring_method_ok(None)

            # Define lenient formula
            if score_system == 'lenient':
                formula = score_method + "_func_aspects('" + aspect_type + "', '" + score_rounding + "')"
                category_expression = "categorisation_func('" + aspect_type + "')"
                '''
                coalesce_function = {k:delim2.join('coalesce(("{group}_Score" / "{group}_Score"), 0)'.format(
                                group = l, N = k) for l in groups) for k in range(1, 5)}

                division_function = ' / ('+ coalesce_function[1] + ')'

                fscorestrs = {k:delim2.join('coalesce("{group}_Score", 0)'.format(
                                group = l, N = k) for l in groups) for k in range(1, 5)}
                average_formula = '(' + (fscorestrs[1]) + ') ' + division_function


                # Define lenient formula for showstopper
                if aspect_type == 'Policy':
                    fscorestrs_2  = {k:delim1.join('"{group}_Score" = 4'.format(
                                    group = l, N = k) for l in groups) for k in range(1, 5)}
                    lenient_formula_showstopper = (fscorestrs_2[1])

                    if score_rounding == 'optimistic':
                        formula = str("""CASE """ +
                                """\nWHEN """ + lenient_formula_showstopper + """ THEN 4 """ +
                                """\nWHEN """ + average_formula + """ >= 2 AND """ + average_formula +  """ < 3 THEN 2 """ +
                                """\nWHEN """ + average_formula + """ >= 1 AND """ + average_formula +  """ < 2 THEN 1 """ +
                                """\nWHEN """ + average_formula + """ < 1 THEN 1 END """)
                    else:
                        formula = str("""CASE """ +
                            """\nWHEN """ + lenient_formula_showstopper + """ THEN 4 """ +
                            """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                            """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                            """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)

                    # Set lenient category expression
                    lenient_categoryExpression = ("CASE" + "\nWHEN" + ' "Score" = 4 THEN ' + "'Showstopper'" + \
                                        "\nWHEN" + ' "Score" = 3 THEN' + " 'Sensitive'" + \
                                        "\nWHEN" + ' "Score" = 2 THEN' + " 'Intermediate'" + \
                                        "\nWHEN" + ' "Score" = 1 THEN' + " 'Possible'" + \
                                        "\nELSE 'Possible' END")

                if aspect_type == 'Technical':
                    if score_rounding == 'optimistic':
                        formula = str("""CASE """ +
                                """\nWHEN """ + average_formula + """ >= 2 AND """ + average_formula +  """ < 3 THEN 2 """ +
                                """\nWHEN """ + average_formula + """ >= 1 AND """ + average_formula +  """ < 2 THEN 1 """ +
                                """\nWHEN """ + average_formula + """ < 1 THEN 1 END """)
                    else:
                        formula = str("""CASE """ +
                            """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                            """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                            """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)

                    # Set lenient category expression
                    lenient_categoryExpression = ("CASE" + \
                                        "\nWHEN" + ' "Score" = 3 THEN' + " 'Unlikely'" + \
                                        "\nWHEN" + ' "Score" = 2 THEN' + " 'Likely'" + \
                                        "\nWHEN" + ' "Score" = 1 THEN' + " 'Favourable'" + \
                                        "\nELSE 'Favourable' END")
                '''    
            if score_system == 'stringent':
                formula = "sum_func_aspects('" + aspect_type + "')"
                category_expression = "categorisation_func('" + aspect_type + "')"
                '''
                fscorestrs = {k:delim1.join('"{group}_Score" = {N}\n'.format(
                        group = l, N = k) for l in groups) for k in range(1, 5)}

                if aspect_type == 'Policy':
                    formula = ("CASE WHEN " +
                            fscorestrs[4] + " THEN 4 WHEN " +
                            fscorestrs[3] + " THEN 3 WHEN " +
                            fscorestrs[2] + " THEN 2 WHEN " +
                            fscorestrs[1] + " THEN 1 ELSE 1 END")

                    # Set lenient category expression
                    lenient_categoryExpression = ("CASE" + "\nWHEN" + ' "Score" = 4 THEN ' + "'Showstopper'" + \
                                        "\nWHEN" + ' "Score" = 3 THEN' + " 'Sensitive'" + \
                                        "\nWHEN" + ' "Score" = 2 THEN' + " 'Intermediate'" + \
                                        "\nWHEN" + ' "Score" = 1 THEN' + " 'Possible'" + \
                                        "\nELSE 'Possible' END")

                if aspect_type == 'Technical':
                    formula = ("CASE WHEN " +
                            fscorestrs[3] + " THEN 3 WHEN " +
                            fscorestrs[2] + " THEN 2 WHEN " +
                            fscorestrs[1] + " THEN 1 ELSE 1 END")

                    # Set lenient category expression
                    lenient_categoryExpression = ("CASE" + \
                                        "\nWHEN" + ' "Score" = 3 THEN' + " 'Unlikely'" + \
                                        "\nWHEN" + ' "Score" = 2 THEN' + " 'Likely'" + \
                                        "\nWHEN" + ' "Score" = 1 THEN' + " 'Favourable'" + \
                                        "\nELSE 'Favourable' END")
                '''

            # If user-defined weighting layer is not checked
            if userDefined_node.itemVisibilityChecked() == False:
                try:
                    aspect_list = []
                    for group in main_group.children():
                        if group.isVisible():
                            aspect_list.append(group.name())

                    # If only one group is active
                    if len(aspect_list) == 1:
                        formula = str('CASE WHEN "' + aspect_list[0] + '_Score" IS NOT NULL THEN "' + aspect_list[0] + '_Score" ' + 'END')
                        if aspect_type == 'Policy':
                            category = str('CASE WHEN "' + aspect_list[0] + '_Score" = 4 THEN ' + "'Showstopper'" +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 3 THEN ' + "'Sensitive'" +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 2 THEN ' + "'Intermediate'" +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 1 THEN ' + "'Possible' ELSE 'Possible' END")
                        if aspect_type == 'Technical':
                            category = str('CASE ' +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 3 THEN ' + "'Unlikely'" +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 2 THEN ' + "'Likely'" +
                                           ' WHEN "' + aspect_list[0] + '_Score" = 1 THEN ' + "'Favourable' ELSE 'Favourable' END")

                        # If "Score" field does not exist, one is created
                        weighted_map.addExpressionField( formula, score_field )
                        # If "Category" field does not exist, one is created
                        weighted_map.addExpressionField( category, category_field )

                    # If more than one policy group is active
                    if len(aspect_list) > 1:
                        weighted_map.addExpressionField( formula, score_field )
                        weighted_map.addExpressionField( category_expression, category_field )
                except UnboundLocalError:
                    pass
            else:
                self.update_weighted_maps_for_user_defined_weighting(aspect_type)
        except IndexError:
            pass  

 
#-------------------------------Update groups and/or layers-------------------------------------------
    def update_oppMaps_by_groups_or_layers(self, layerTreeNode):
        # layerTreeNode.type(): 0 for group; 1 for layer
        #print('update_oppMaps_by_groups_or_layers')
        #print(layerTreeNode.name())
        # Define root
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Disconnect functions
        try:
            policy_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
        except TypeError:
            pass
        try:
            technical_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
        except TypeError:
            pass

        for groups in policy_group.children():
            groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            for layers in groups.children():
                try:
                    layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                except TypeError:
                    pass

        for groups in technical_group.children():
            groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            for layers in groups.children():
                try:
                    layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                except TypeError:
                    pass

        try:
            iface.mapCanvas().renderComplete.disconnect(self.General.unique_tag_reference)
        except TypeError:
            pass

        # If Policy or Technical main groups toggled
        if layerTreeNode.name() in ('Policy', 'Technical'):
            aspect_type = layerTreeNode.name()
            aspect_group = root.findGroup(aspect_type)

            # Define field
            opp_mapField = 'ID'

            # Get aspects
            aspect_groups = [groups for groups in aspect_group.children()]

            # Find all visible layers in policy  groups, remove and rejoin them to each policy group scoring layer
            #itemVisibilityChecked
            aspect_group.setItemVisibilityChecked(True)
            if aspect_group.isItemVisibilityCheckedRecursive() == False:
                #print('checked')
                aspect_group.setItemVisibilityCheckedRecursive(True)
                for groups in aspect_groups:
                    for layer in groups.children():                    
                        # Match Opportunity layer with group aspects name
                        policy_oppMap = QgsProject.instance().mapLayersByName( groups.name() )[-1]
                        policy_oppMap.removeJoin(layer.layer().id())
                        childField = 'ID'
                        joinObject = QgsVectorLayerJoinInfo()
                        joinObject.setJoinFieldName(childField)
                        joinObject.setTargetFieldName(opp_mapField)
                        joinObject.setJoinLayerId(layer.layer().id())
                        joinObject.setJoinFieldNamesSubset([layer.name(), 'Score'])
                        joinObject.setUsingMemoryCache(True)
                        joinObject.setJoinLayer(layer.layer())
                        policy_oppMap.addJoin(joinObject)
            elif aspect_group.isItemVisibilityCheckedRecursive() == True:
                #print('unchecked')
                aspect_group.setItemVisibilityCheckedRecursive(False)
                for groups in aspect_groups:
                    # If policy group is not visible, remove all layers in group from scoring layer
                    policy_oppMap = QgsProject.instance().mapLayersByName( groups.name() )[-1]
                    for layer in groups.children():
                        policy_oppMap.removeJoin(layer.layer().id())

            # Run following functions
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.connect_policy_or_technical(aspect_type)
            self.live_update_combined_map(aspect_type)
            self.connect_PolTech('final')
            self.calculate_area_2()
            QApplication.restoreOverrideCursor()

        # If group is toggled
        if layerTreeNode.name() not in ('Policy', 'Technical') and layerTreeNode.nodeType() == 0:
            #print('group')
            #layerTreeNode.setItemVisibilityCheckedParentRecursive(True)
            # Define field
            opp_mapField = 'ID'

            # Get aspects
            policy_aspect_groups = [group.name() for group in policy_group.children()]
            technical_aspect_groups = [group.name() for group in technical_group.children()]

            # Find all visible layers in policy  groups, remove and rejoin them to each policy group scoring layer
            group = QgsProject.instance().layerTreeRoot().findGroup(layerTreeNode.name())
            aspect_group = group.parent()
            if not aspect_group.isVisible():
                aspect_group.setItemVisibilityChecked(True)
            if layerTreeNode.isVisible():
                for layer in group.children():
                    iface.layerTreeView().setLayerVisible(layer.layer(), True)
                    # Match Opportunity layer with group aspects name
                    policy_oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                    policy_oppMap.removeJoin(layer.layer().id())
                    childField = 'ID'
                    joinObject = QgsVectorLayerJoinInfo()
                    joinObject.setJoinFieldName(childField)
                    joinObject.setTargetFieldName(opp_mapField)
                    joinObject.setJoinLayerId(layer.layer().id())
                    joinObject.setJoinFieldNamesSubset([layer.name(), 'Score'])
                    joinObject.setUsingMemoryCache(True)
                    joinObject.setJoinLayer(layer.layer())
                    policy_oppMap.addJoin(joinObject)
            else:
                # If policy group is not visible, remove all layers in group from scoring layer
                for layer in group.children():
                    iface.layerTreeView().setLayerVisible(layer.layer(), False)
                    policy_oppMap = QgsProject.instance().mapLayersByName( group.name() )[-1]
                    policy_oppMap.removeJoin(layer.layer().id())

            groups_visible = [groups.isVisible() for groups in aspect_group.children()]
            if True in groups_visible:
                aspect_group.setItemVisibilityChecked(True)
            else:
                aspect_group.setItemVisibilityChecked(False)

            # Run following functions
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if group.name() in policy_aspect_groups:
                self.connect_policy_or_technical('Policy')
                self.live_update_combined_map('Policy')
            if group.name() in technical_aspect_groups:
                self.connect_policy_or_technical('Technical')
                self.live_update_combined_map('Technical')
            self.connect_PolTech('final')
            self.calculate_area_2()
            QApplication.restoreOverrideCursor()

        # If layer is toggled
        if layerTreeNode.nodeType() == 1:
            #print('layer')

            #layerTreeNode.setItemVisibilityCheckedParentRecursive(True)
            node_layer = QgsProject.instance().mapLayersByName(str(layerTreeNode.name()))[-1]
            node = root.findLayer(node_layer.id())
            group = node.parent()
            aspect_group = group.parent()
            # put logic here to find visible and not visibile groups
            #aspect_groups = [groups.name() for groups in aspect_group.children()]
            if not group.isVisible():
                group.setItemVisibilityChecked(True)
            if not aspect_group.isVisible():
                aspect_group.setItemVisibilityChecked(True)

            layers_visible = [layer.isVisible() for groups in aspect_group.children() for layer in groups.children()]
            clicked_group_layers_visible = [layer.isVisible() for layer in group.children()]
            if True in layers_visible:
                group.setItemVisibilityChecked(True)
                aspect_group.setItemVisibilityChecked(True)
            else:
                group.setItemVisibilityChecked(False)
                aspect_group.setItemVisibilityChecked(False)
            if any(clicked_group_layers_visible) == False:
                group.setItemVisibilityChecked(False)

            self.update_scoring_oppMaps(node)

        # Connect functions
        policy_group.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
        technical_group.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)

        for groups in policy_group.children():
            groups.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
            for layers in groups.children():
                layers.visibilityChanged.connect(self.update_scoring_oppMaps)

        for groups in technical_group.children():
            groups.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
            for layers in groups.children():
                layers.visibilityChanged.connect(self.update_scoring_oppMaps)
        
        iface.mapCanvas().renderComplete.connect(self.General.unique_tag_reference)



#-------------------------------Iterator for weighting list------------------------------------
    def iterator_for_weighting_list(self, aspect_type):
        #print('iterator_for_weighting_list')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        main_group = root.findGroup(aspect_type)

        # Define opportunities map
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]

        # Define aspect_type parameter
        lower_case = str(aspect_type).lower()

         # Define layer
        weighted_map = QgsProject.instance().mapLayersByName( "Combined " + lower_case )[0]

        # Get scoring settings
        score_method, score_rounding, score_system = self.General.scoring_method_ok(None)

        # Define button and table
        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget

        weighting_dict = {}
        weightings = []
        iterator = QTreeWidgetItemIterator(qTree)
        while iterator.value():
            item = iterator.value()
            try:
                if item.text(1) != '0' and item.text(1) != '0.0':
                    if "." in item.text(1):
                        weighting_dict[str(item.text(0))] = float(item.text(1))
                        weightings.append(float(item.text(1)))
                    else:
                        weighting_dict[str(item.text(0))] = int(item.text(1))
                        weightings.append(int(item.text(1)))                    
            except ValueError:
                pass
            iterator += 1

        delim = 'WHEN '
        delim2 = ' + '
        delim3 = ' OR '

        # Check if main aspect weighting have equal values
        weighting_list_check = [x for x in weightings if x != 0]

        if len(weighting_list_check) > 1:
            weighting_check = all(weightings[0] == item for item in weightings)
        else:
            weighting_check = False

        # Sort dictionary in reverse order (so it matches the order as shown in interface)
        sorted_weighting_dict = sorted(weighting_dict.items(), key=operator.itemgetter(1), reverse=True)

        # Get visible groups
        groups = []
        for group in main_group.children():
            if group.isVisible():
                groups.append(group.name())

        # If main weighting values are equal, use selected score method
        if weighting_check == True:
            formula = score_method + "_func_aspects('" + aspect_type + "', '" + score_rounding + "')"
            '''
            coalesce_function = {k:delim2.join('coalesce(("{group}_Score" / "{group}_Score"), 0)'.format(
                            group = l, N = k) for l in groups) for k in range(1, 5)}

            division_function = ' / (' + coalesce_function[1] + ')'


            fscorestrs = {k:delim2.join('coalesce("{group}_Score", 0)'.format(
                            group = l, N = k) for l in groups) for k in range(1, 5)}

            average_formula = '(' + (fscorestrs[1]) + ') ' + division_function

            if aspect_type == 'Policy':
                # Define lenient formula for showstopper
                fscorestrs_2  = {k:delim3.join('"{group}_Score" = 4'.format(
                                group = l, N = k) for l in groups) for k in range(1, 5)}
                lenient_formula_showstopper = (fscorestrs_2[1])
                formula = str("""CASE """ +
                        """\nWHEN """ + lenient_formula_showstopper + """ THEN 4 """ +
                        """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                        """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                        """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)
            if aspect_type == 'Technical':
                formula = str("""CASE """ +
                        """\nWHEN """ + average_formula + """ >= 2.5 THEN 3 """ +
                        """\nWHEN """ + average_formula + """ >= 1.5 THEN 2 """ +
                        """\nWHEN """ + average_formula + """ < 1.5 THEN 1 END """)
            
            '''
        # Else apply weightings to main aspect type groups
        # Weighted Overlay Analysis is used where weightings are multiplied by aspect score.
        # The sum of all weighted aspect scores results in the final score for each grid cell.
        if weighting_check == False:
            # Replace single quotes with double as the latter is used for field names in the QGIS native field calculator
            weighting_dict_to_string = str(weighting_dict).replace("'", '"')
            formula = str("weight_func_aspects('" + aspect_type + "', '" + score_rounding + "', '" + weighting_dict_to_string + "')")
            '''
            fscorestrs = delim2.join('coalesce("{group}_Score", 1.5) * {weight}\n'.format(
                        group = sorted_weighting_dict[w][0], weight = float(sorted_weighting_dict[w][1])) for w in range(0, len(weighting_dict)))
            
            if aspect_type == 'Policy':
                fscorestrs_2  = {k:delim.join('"{group}_Score" = 4 THEN 4\n'.format(
                                group = l, N = k) for l in groups) for k in range(1, 5)}            
                lenient_formula_showstopper = (fscorestrs_2[1]) 
                formula = ("CASE" + "\nWHEN " + lenient_formula_showstopper + 
                    """\nWHEN """ + fscorestrs + """ >= 2.5 THEN 3 """ +
                    """\nWHEN """ + fscorestrs + """ >= 1.5 THEN 2 """ +
                    """\nWHEN """ + fscorestrs + """ < 1.5 THEN 1 END """)

            if aspect_type == 'Technical':
                formula = ("CASE" + """\nWHEN """ + fscorestrs + """ >= 2.5 THEN 3 """ +
                    """\nWHEN """ + fscorestrs + """ >= 1.5 THEN 2 """ +
                    """\nWHEN """ + fscorestrs + """ < 1.5 THEN 1 END """)
            '''

        category_expression = "categorisation_func('" + aspect_type + "')"
        '''
        if aspect_type == 'Policy':
            category_expression = ("CASE" + "\nWHEN" + ' "Score" = 4 THEN ' + "'Showstopper'" + \
                                    "\nWHEN" + ' "Score" = 3 THEN' + " 'Sensitive'" + \
                                    "\nWHEN" + ' "Score" = 2 THEN' + " 'Intermediate'" + \
                                    "\nWHEN" + ' "Score" = 1 THEN' + " 'Possible'" + \
                                    "\nELSE 'Possible' END")

        if aspect_type == 'Technical':
            category_expression = ("CASE" + \
                                    "\nWHEN" + ' "Score" = 3 THEN' + " 'Unlikely'" + \
                                    "\nWHEN" + ' "Score" = 2 THEN' + " 'Likely'" + \
                                    "\nWHEN" + ' "Score" = 1 THEN' + " 'Favourable'" + \
                                    "\nELSE 'Favourable' END")
        '''
        # Loop until Score field is completely deleted 
        while True:
            score_index = weighted_map.fields().indexFromName('Score') 
            if score_index != -1:
                weighted_map.removeExpressionField(score_index)
            else:
                break
        # Add new Score field
        field = QgsField( 'Score', QVariant.Int )
        weighted_map.addExpressionField( formula, field )

        # Loop until Category field is completely deleted 
        while True:
            category_index = weighted_map.fields().indexFromName('Category') 
            if category_index != -1:
                weighted_map.removeExpressionField(category_index)
            else:
                break
        # Add new category field
        field = QgsField( 'Category', QVariant.String )
        weighted_map.addExpressionField( category_expression, field )

        # Refresh opportunities map
        oppPolTech_weightedMap.triggerRepaint()



#-------------------------------Create weightings-----------------------------------------
    def set_weightings(self, n):
        #print('set_weightings')
        weightings = {1: [100], 
                      2: [60, 40],
                      3: [50, 30, 20],
                      4: [40, 30, 20, 10],
                      5: [40, 25, 20, 10, 5],
                      6: [30, 25, 20, 15, 6, 4],
                      7: [30, 25, 20, 15, 7, 2, 1],
                      8: [30, 25, 20, 10, 5, 7, 2, 1],
                      9: [30, 25, 20, 7, 6, 5, 4, 2, 1],
                      10: [30, 25, 12, 8, 7, 6, 5, 4, 2, 1],
                      11: [30, 13, 12, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                      12: [18, 14, 12, 11, 9, 8, 7, 6, 5, 4, 3, 2, 1]
                      }

        return weightings[n]


#-------------------------------Confirm weighting search---------------------------------------------
    def confirm_weighting_search(self, aspect_type):

        # Disconnect signals
        try:
            self.confirm_weighting_dockwidget.confirmWeightings_pushButton.clicked.disconnect()
        except:
            pass
        try:
            self.confirm_weighting_dockwidget.closeWeightings_pushButton.clicked.disconnect()
        except:
            pass

        # Connect signals
        self.confirm_weighting_dockwidget.confirmWeightings_pushButton.clicked.connect(partial(self.weighting_search, aspect_type))
        self.confirm_weighting_dockwidget.closeWeightings_pushButton.clicked.connect(self.cancel_weighting_search)

        # Show interface
        self.confirm_weighting_dockwidget.show()


#-------------------------------Cancel weighting search---------------------------------------------
    def cancel_weighting_search(self):
        self.confirm_weighting_dockwidget.close()


#-------------------------------Perform weighting search using random weightings-----------------------------------------
    def weighting_search(self, aspect_type):
        #print('weighting_search')
        # Define root and groups
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        if aspect_type == 'Policy':
            main_group = root.findGroup('Policy')
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
            progress_bar = self.policy_dockwidget.progressBar
        if aspect_type == 'Technical':
            main_group = root.findGroup('Technical')
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget
            progress_bar = self.technical_dockwidget.progressBar

        qTree.clear()
        header = QTreeWidgetItem(["Aspects", "Weightings"])
        qTree.setHeaderItem(header)

        # Define bold font
        font = QFont()
        font.setBold(True)

        # Define parameters for QTreeWidget
        layer_data = []  
        layer_count = []
        visible_groups = []

        # Fetch layers and store in layer_data list, also count number of layers per aspect group
        for group in main_group.children():
            layer_list = []
            for child in group.children():
                if child.isVisible():
                    layer_data.append(child.name())
                    layer_list.append(child.name())            
            aspect_group = root.findGroup(str(group.name()))
            if aspect_group.isVisible():
                layer_count.append(len(layer_list))
                visible_groups.append(group.name())

        # Define range by using number of layers in each aspect group with number of aspect groups
        top = list(np.cumsum(layer_count))
        bottom = list(np.subtract(np.cumsum(layer_count),layer_count))
        pairs = zip(bottom,top)
        ranges = iter([range(x[0], x[1]) for x in pairs])

        # Get x amount of random weightings which match visible number of groups
        #new_weightings = self.random_weightings(len(visible_groups), 100)
        new_weightings = self.set_weightings(len(visible_groups))
        # Place the random weightings inside a dictionary
        weights = dict(zip(visible_groups, new_weightings))
        # Find all possible combinations by rearranding the weightings
        weightings = [dict(zip(weights.keys(), values)) for values in permutations(weights.values())]

        # If number of visible groups can have equal weighting (i.e. no remainder which divisible by 100), add this combination (e.g.)
        # 2 visible groups = 50 weighting each --- added to list of possible combinations
        # 3 visible groups = 33 weighting each plus remainder --- not added to list of possible combinations
        if 1%len(visible_groups) == 0:
            duplicate_weightings = {}
            for x in weights:
                duplicate_weightings[x] = (1 / len(visible_groups))
            weightings.append(duplicate_weightings)

        # Final list to hold weightings
        final_weightings_list = []

        # Define progress bar
        progress_bar.setMaximum(len(weightings))
        progress_bar.setValue(0)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        # Counter used to identify the last iteration
        z = 0
        for y in weightings:
            final_weightings = {}
            qTree.clear()
            z = z + 1
            for x in range(len(visible_groups)):
                # Set main aspects only for all iterations excluding the last
                group = QTreeWidgetItem(qTree, [str(visible_groups[x]), str(y[visible_groups[x]])])
                group.setFont(0, font)
                # Store group names and weightings in dictionary
                final_weightings[str(visible_groups[x])] = y[visible_groups[x]]
                # When the last iteration occurs, set the subaspects
                if z == len(weightings):
                    for row in next(ranges):
                        item = QTreeWidgetItem(group, [str(layer_data[row])])

            # Update opportunity map
            self.update_weighted_maps(aspect_type)
            # Fetch green area per weighting iteration
            final_weightings['Area'] = self.TechFunctions.land_area_green_only(aspect_type)
            # Add result to list
            final_weightings_list.append(final_weightings)
            progress_bar.setValue(progress_bar.value() + 1)
            
        # Resize to fit contents
        qTree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        qTree.expandAll()
        QApplication.restoreOverrideCursor()

        # Find best weighting combination from list of dictionaries in terms of maximum possible or favourable area
        best_weighting = max(final_weightings_list, key=lambda x:x['Area'])

        # Set groups with their best weightings
        for x in range(len(visible_groups)):
            group = QTreeWidgetItem(qTree, [str(visible_groups[x]), str(best_weighting[str(visible_groups[x])])])

        # Refresh aspects and subaspects
        self.refresh_weighting_aspect_list_sub_aspects(aspect_type)
        # Update opportunity map
        self.update_weighted_maps(aspect_type)
        # Close confirm weighting window
        self.confirm_weighting_dockwidget.close()


#-------------------------------Update Opportunity map live when user defined weighting is checked------------------------------------
    def update_weighted_maps_for_user_defined_weighting(self, aspect_type): 
        #print('update_weighted_maps_for_user_defined_weighting')
        # Define weighting algorithms
        try:
            # If user-defined weighting is checked
            if aspect_type == 'Policy':
                policyTotalWeighting_lineEdit = self.dockwidget.policyTotalWeighting_lineEdit
                #if policyTotalWeighting_lineEdit.text() == '1':
                if (0.99 <= float(policyTotalWeighting_lineEdit.text()) <= 1.01):
                    self.iterator_for_weighting_list(aspect_type)
            if aspect_type == 'Technical':
                technicalTotalWeighting_lineEdit = self.dockwidget.technicalTotalWeighting_lineEdit
                #if technicalTotalWeighting_lineEdit.text() == '1':
                if (0.99 <= float(technicalTotalWeighting_lineEdit.text()) <= 1.01):
                    self.iterator_for_weighting_list(aspect_type)
        except TypeError:
            pass


#-------------------------------Update Opportunity map with AHP weightings------------------------------------
    def ahp_weightings_applied_to_opportunity_map(self): 
        #print('update_weighted_maps_for_user_defined_weighting')
        # Define weighting algorithms
        try:
            root = QgsProject.instance().layerTreeRoot()
        except AttributeError:
            pass
        policy_group = root.findGroup('Policy')

        ahp_dict = self.Statistics.get_ahp_results()

        try:
            for group in policy_group.children():
                if ahp_dict[group.name()]:
                    aspect_type = 'Policy'
        except KeyError:
            aspect_type = 'Technical'

        if aspect_type == 'Policy':
            qTree = self.policy_dockwidget.policy_weighting_aspect_treeWidget
            progress_bar = self.policy_dockwidget.progressBar
        if aspect_type == 'Technical':
            qTree = self.technical_dockwidget.technical_weighting_aspect_treeWidget
            progress_bar = self.technical_dockwidget.progressBar

        qTree.clear()
        header = QTreeWidgetItem(["Aspects", "Weightings"])
        qTree.setHeaderItem(header)
        # Define bold font
        font = QFont()
        font.setBold(True)

        for x in range(len(ahp_dict)):
            group = QTreeWidgetItem(qTree, [str(list(ahp_dict.keys())[x]), str(list(ahp_dict.values())[x])])
            group.setFont(0, font)

        # Resize to fit contents
        qTree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        qTree.expandAll()
        
        # Refresh aspects and subaspects
        self.refresh_weighting_aspect_list_sub_aspects(aspect_type)
        # Update opportunity map
        self.update_weighted_maps(aspect_type)
        # Close confirm weighting window
        self.ahp_dockwidget.close()
        

#-------------------------------Calculate area when Opportunity Map layer is clicked-------------------------------------------
    def calculate_area(self):
        #print('calculate_area')
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Define root
        root = QgsProject.instance().layerTreeRoot()

        # Define layer
        for node in root.children():
            for child in node.children():
                if child.name() == "Opportunities":
                    layer = child  

        # If GOMap Live is active, calculate land availability and solar energy            
        if self.GOMapLive_button.isChecked():               
            #set_category_areas(self)   
            if layer.isVisible() == 0:
                self.TechFunctions.land_area(None)
                self.TechFunctions.land_areaUnits()
                self.TechFunctions.populate_EnergyYieldEstimator()
                
        # Disconnect visibilityChanged signal to layer
        else:
            try:
                layer.visibilityChanged.disconnect(self.calculate_area)
            except TypeError:
                pass
        QApplication.restoreOverrideCursor()


#-------------------------------Calculate area when policy/technical aspects are clicked-------------------------------------------
    def calculate_area_2(self):
        #print('calculate_area_2')
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # If GOMap Live is active
        if self.GOMapLive_button.isChecked():
            #set_category_areas(self)
            self.TechFunctions.land_area(None)
            self.TechFunctions.land_areaUnits()
            self.TechFunctions.populate_EnergyYieldEstimator()
        QApplication.restoreOverrideCursor()



#-------------------------------Hide opportunity map -------------------------------------------
    def hideNode(self, node, bHide):
        #print('hideNode')
        # Define root
        root = QgsProject.instance().layerTreeRoot()
        ltv = iface.layerTreeView()
        if type( node ) in ( QgsLayerTreeLayer, QgsLayerTreeGroup ):
            index = ltv.node2index( node )
            ltv.setRowHidden( index.row(), index.parent(), bHide )
            node.setCustomProperty( 'nodeHidden', 'True' if bHide else 'False' )
            ltv.setCurrentIndex( ltv.node2index( root ) )


#-------------------------------GOMap Live button-------------------------------------------
    def GOMap_Live(self, checked):
        #print('GOMap_Live')
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')
        scope_group = self.General.identify_group_state('Scope')

        # Define main menubar
        menubar = iface.mainWindow().findChild(QMenuBar)

        # Define layer
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]  

        # Define User-defined weighting layer
        userDefined_layer = QgsProject.instance().mapLayersByName( "User-defined weightings" )[0]
        userDefined_node = root.findLayer(userDefined_layer.id())
        
        # Get child of opportunity layermenubar = iface.mainWindow().findChild(QMenuBar)
        for node in root.children():
            for child in node.children():
                if child.name() == "Opportunities":
                    opportunity_layer = child

        # Run calculate_area_2() function
        self.calculate_area_2()        

        # If GOMap Live is ON
        if checked:
            # Set GOMap icon message
            self.GOMapLive_button.setText('GOMap ON')
            # Hide main menubar
            menubar.hide()
            # Disconnect functions
            try:
                iface.mapCanvas().renderComplete.disconnect(self.General.unique_tag_reference)
            except TypeError:
                pass
            for layers in scope_group.children():
                if layers.name() != 'New scope':
                    try:
                        layers.visibilityChanged.disconnect()
                    except TypeError:
                        pass

            try:
                policy_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            except TypeError:
                pass
            try:
                technical_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            except TypeError:
                pass

            # Set policy layers to have 0% transparency and disconnect to the following functions
            for groups in policy_group.children():
                try:
                    groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
                except TypeError:
                    pass
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    try:
                        layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                    except TypeError:
                        pass
                    try:
                        layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)
                    except TypeError:
                        pass
            # Set technical layers to have 0% transparency and disconnect to the following functions
            for groups in technical_group.children():
                try:
                    groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
                except TypeError:
                    pass
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    try:
                        layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                    except TypeError:
                        pass
                    try:
                        layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)
                    except TypeError:
                        pass
            # Disconnect user-defined weighting layer from function
            try:
                userDefined_node.visibilityChanged.disconnect(self.weighting_selection)
            except TypeError:
                pass
            # Make opportunity_layer visible and connect it to calculate_area() function and units combobox to land_area() function
            self.hideNode(opportunity_layer, False)             
            iface.layerTreeView().setLayerVisible(oppPolTech_weightedMap, True)
            opportunity_layer.visibilityChanged.connect(self.calculate_area)
            self.land_availability_dockwidget.areaUnits_combo.currentIndexChanged.connect(self.TechFunctions.land_areaUnits)
            self.land_availability_dockwidget.areaUnits_combo_2.currentIndexChanged.connect(self.TechFunctions.land_areaUnits)
            self.land_availability_dockwidget.areaUnits_combo_2.currentIndexChanged.connect(self.TechFunctions.populate_EnergyYieldEstimator)
            # Connect unique_tag_reference() function to renderComplete() method
            iface.mapCanvas().renderComplete.connect(self.General.unique_tag_reference)
            # Connect layers in group to scope() function
            for layers in scope_group.children():
                if layers.name() != 'New scope':
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layer.setOpacity(0)
                    layer.triggerRepaint()
                    layers.visibilityChanged.connect(self.scope)
                if layers.name() == 'New scope':
                    layers.visibilityChanged.connect(self.create_scope_layer)
            # Connect Policy and Technical groups to functions
            policy_group.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
            technical_group.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
            # Set policy layers to have 100% transparency and connect to the following functions
            for groups in policy_group.children():
                groups.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layer.setOpacity(0)
                    layer.triggerRepaint()
                    layer.committedAttributeValuesChanges.connect(self.update_layer_symbology)
                    layers.visibilityChanged.connect(self.update_scoring_oppMaps)
            # Set technical layers to have 100% transparency and connect to the following functions
            for groups in technical_group.children():
                groups.visibilityChanged.connect(self.update_oppMaps_by_groups_or_layers)
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layer.setOpacity(0)
                    layer.triggerRepaint()
                    layer.committedAttributeValuesChanges.connect(self.update_layer_symbology)
                    layers.visibilityChanged.connect(self.update_scoring_oppMaps)
            # Connect user-defined weighting layer to function
            userDefined_node.visibilityChanged.connect(self.weighting_selection)

            # Show interface            
            self.land_availability_dockwidget.show()

            # Enable GOMap tools button
            self.mainToolButton.setEnabled(True)

            # If user-defined weighting is enabled, hide dockwidgets
            if userDefined_node.isVisible():
                self.policy_dockwidget.show()
                self.technical_dockwidget.show()

            # Show message when GOMap Live is ON
            iface.messageBar().pushMessage("", 'GOMap ON', Qgis.Info, 3)

        # When GOMap Live is OFF
        else:   
            # Set GOMap icon message
            self.GOMapLive_button.setText('GOMap OFF')
            # Show main menubar 
            menubar.show()
            # Make opportunity_layer invisible and disconnect it to calculate_area() function and units combobox to land_area() function
            self.hideNode(opportunity_layer, True)            
            opportunity_layer.visibilityChanged.disconnect(self.calculate_area)
            iface.layerTreeView().setLayerVisible(oppPolTech_weightedMap, False)
            self.land_availability_dockwidget.areaUnits_combo.currentIndexChanged.disconnect()
            self.land_availability_dockwidget.areaUnits_combo_2.currentIndexChanged.disconnect()
            # Disconnect unique_tag_reference() function to renderComplete() method
            try:
                iface.mapCanvas().renderComplete.disconnect(self.General.unique_tag_reference)
            except TypeError:
                pass
            # Disconnect layers in group to Check function (WARNING: ORDER MATTERS!!!)
            for layers in scope_group.children():
                if layers.name() != 'New scope':
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    layer.setOpacity(100)
                    layer.triggerRepaint()
                    layers.visibilityChanged.disconnect()
                if layers.name() == 'New scope':
                    layers.visibilityChanged.disconnect(self.create_scope_layer)

            # Disconnect Policy and Technical group functions
            try:
                policy_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            except TypeError:
                pass
            try:
                technical_group.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
            except TypeError:
                pass

            # Set policy layers to have 0% transparency and disconnect to the following functions
            for groups in policy_group.children():
                try:
                    groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
                except TypeError:
                    pass
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    try:
                        layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                    except TypeError:
                        pass
                    layer.setOpacity(100)
                    layer.triggerRepaint()
                    try:
                        layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)
                    except TypeError:
                        pass
                    try:
                        layers.visibilityChanged.disconnect(self.refresh_weighting_aspect_list_main_aspects)
                    except TypeError:
                        pass

            # Set technical layers to have 0% transparency and disconnect to the following functions
            for groups in technical_group.children():
                try:
                    groups.visibilityChanged.disconnect(self.update_oppMaps_by_groups_or_layers)
                except TypeError:
                    pass
                for layers in groups.children():
                    layer = QgsProject.instance().mapLayersByName(layers.name())[0]
                    try:
                        layers.visibilityChanged.disconnect(self.update_scoring_oppMaps)
                    except TypeError:
                        pass
                    layer.setOpacity(100)
                    layer.triggerRepaint()
                    try:
                        layer.committedAttributeValuesChanges.disconnect(self.update_layer_symbology)
                    except TypeError:
                        pass
                    try:
                        layers.visibilityChanged.disconnect(self.refresh_weighting_aspect_list_main_aspects)
                    except TypeError:
                        pass
            # Disconnect user-defined weighting layer from function
            userDefined_node.visibilityChanged.disconnect(self.weighting_selection)

            # Set technology combobox to default value
            technology_comboBox = self.land_availability_dockwidget.technology_comboBox
            technology_comboBox.setCurrentIndex(0)

            # Hide interface            
            self.land_availability_dockwidget.hide()        

            # Show message when GOMap Live is OFF
            iface.messageBar().pushMessage("", 'GOMap OFF', Qgis.Info, 3)

            # Disable GOMap tools button
            self.mainToolButton.setEnabled(False)

            # If user-defined weighting is enabled, hide dockwidgets
            if userDefined_node.isVisible():
                self.policy_dockwidget.hide()
                self.technical_dockwidget.hide()

        # Connect opportunity map layer to opportunity_GOMapLive_connection() function
        #opportunity_layer.visibilityChanged.connect(self.opportunity_GOMapLive_connection)


