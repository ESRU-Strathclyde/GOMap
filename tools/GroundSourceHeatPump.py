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
from qgis.utils import iface
from qgis.PyQt import QtGui

# Import resources from dockwidgets
from ..dockwidgets.configure_gshp_dockwidget import configure_gshp

from .General import General
from .TechnologyFunctions import TechFunctions


class GSHP:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.configure_gshp_dockwidget = configure_gshp()

        # Reference General class
        self.General = General(None)

        # Reference TechFunctions class
        self.TechFunctions = TechFunctions(self.land_availability_dockwidget)

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')


#-------------------------------"Configure" options-------------------------------------------------------
    def configure_GSHP_tools(self):
        ok_button = self.configure_gshp_dockwidget.ok_pushButton
        reset_button = self.configure_gshp_dockwidget.reset_pushButton

        try:
            ok_button.clicked.disconnect(self.configure_GSHP_tools_OK)
        except TypeError:
            pass
        try:
            reset_button.clicked.disconnect(self.configure_GSHP_tools_reset)
        except TypeError:
            pass

        self.configure_gshp_dockwidget.energy_label.setText(str(u'Heat density (kW/m<sup>2</sup>)'))

        ok_button.clicked.connect(self.configure_GSHP_tools_OK)
        reset_button.clicked.connect(self.configure_GSHP_tools_reset)
        
        self.configure_gshp_dockwidget.show()


#-------------------------------"Configure" OK button-------------------------------------------------------
    def configure_GSHP_tools_OK(self):
        self.configure_gshp_dockwidget.close()
        self.TechFunctions.populate_EnergyYieldEstimator()
        # Output specification from configure dockwidget
        stats = str(
            '<b>Ground source heat pump specification</b>' +
            '<br>Dwelling consumption (kWh/yr): ' + str("{:,.0f}".format(self.configure_gshp_dockwidget.houseConsumption_spinBox.value())) +
            '<br>' + str(u'Heat density (kW/m<sup>2</sup>): ') + str(int(self.configure_gshp_dockwidget.energy_spinBox.value())) +
            '<br>Heat loss (%): ' + str(int(self.configure_gshp_dockwidget.heatLoss_spinBox.value())) +
            '<br><br>'
            )
        # Output stats to energy yield estimator textbox
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.moveCursor(QtGui.QTextCursor.End)


#-------------------------------"Configure" Reset button-------------------------------------------------------
    def configure_GSHP_tools_reset(self):
        # Reset to default settings
        self.configure_gshp_dockwidget.energy_spinBox.setValue(20.0)
        self.configure_gshp_dockwidget.heatLoss_spinBox.setValue(10)
        self.configure_gshp_dockwidget.houseConsumption_spinBox.setValue(9500)