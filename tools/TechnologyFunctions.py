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
from qgis.core import QgsProject, QgsFeatureRequest, QgsFeature, Qgis
from qgis.utils import iface
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QToolButton
from math import sin, cos, tan, radians

# Import resources from dockwidgets
from ..dockwidgets.configure_pv_dockwidget import configure_pv
from ..dockwidgets.configure_pv_canopy_dockwidget import configure_pv_canopy
from ..dockwidgets.configure_wind_dockwidget import configure_wind
from ..dockwidgets.configure_gshp_dockwidget import configure_gshp


class TechFunctions:
    def __init__(self,
                 land_availability_dockwidget):

        # Save reference to the QGIS interface
        self.iface = iface
        self.land_availability_dockwidget = land_availability_dockwidget
        self.configure_pv_dockwidget = configure_pv()
        self.configure_pv_canopy_dockwidget = configure_pv_canopy()
        self.configure_wind_dockwidget = configure_wind()
        self.configure_gshp_dockwidget = configure_gshp()

        # initialize plugin directory
        self.plugin_dir = os.path.join(os.path.dirname( __file__ ), '..')


#-------------------------------Populate Energy Yield Estimator-------------------------------------------
    def populate_EnergyYieldEstimator(self):
        technology_comboBox = self.land_availability_dockwidget.technology_comboBox

        # Get area
        try:
            #utilisation_factor = float(self.land_availability_dockwidget.UF_spinBox.text())
        
            area1 = float(self.land_availability_dockwidget.area_Score1_lineEdit.text().replace(',',''))
            area2 = float(self.land_availability_dockwidget.area_Score2_lineEdit.text().replace(',',''))
            area3 = float(self.land_availability_dockwidget.area_Score3_lineEdit.text().replace(',',''))
            area4 = float(self.land_availability_dockwidget.area_Score4_lineEdit.text().replace(',',''))
            #total_area = float(area1) * float(utilisation_factor)
            total_area = float(area1 + area2 + area3 + area4)

            # Convert area back into metres for energy yield calculations
            units_dict = {u'm\u00B2': 'm<sup>2</sup>', u'km\u00B2': 'km<sup>2</sup>', 'acre': 'acre', 'ha': 'ha'}
            units = units_dict[self.land_availability_dockwidget.areaUnits_combo_2.currentText()]

            green_area = 0
            amber_area = 0
            red_area = 0
            black_area = 0
            utilisation_green = self.land_availability_dockwidget.utilisation_green_spinBox.value()
            utilisation_amber = self.land_availability_dockwidget.utilisation_amber_spinBox.value()
            utilisation_red = self.land_availability_dockwidget.utilisation_red_spinBox.value()
            utilisation_black = self.land_availability_dockwidget.utilisation_black_spinBox.value()

            if utilisation_green != 0:
                green_area = float(areaScore1) * float(utilisation_green / 100)
            if utilisation_amber != 0:
                amber_area = float(areaScore2) * float(utilisation_amber / 100)
            if utilisation_red != 0:
                red_area = float(areaScore3) * float(utilisation_red / 100)
            if utilisation_black != 0:
                black_area = float(areaScore4) * float(utilisation_black / 100)
            
            total_energy_area = float(green_area + amber_area + red_area + black_area)

            '''
            ### For no technology ###
            if technology_comboBox.currentText() == 'Technology':
                self.clear_EnergyYieldEstimator()
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(str(
                    'Total area (' + units + '): ' + str("{:,.1f}".format(total_area))))
            '''
    
            ### PV ###
            if technology_comboBox.currentText() == 'PV':
                # Get data to calculate energy yield and house equivalent
                ouput_energy = float(self.configure_pv_dockwidget.energy_spinBox.value())
                house_consumption = float(self.configure_pv_dockwidget.houseConsumption_spinBox.value())
                pv_length = float(self.configure_pv_dockwidget.length_spinbox.value())
                pv_width = float(self.configure_pv_dockwidget.width_spinbox.value())
                pv_angle = float(self.configure_pv_dockwidget.pv_angle_spinbox.value())
                inter_row_spacing = float(self.configure_pv_dockwidget.inter_row_spinbox.value())

                # Area of panel
                panel_area = float(pv_length) * float(pv_width)

                # Area of shade created by panel
                shade_area = float(inter_row_spacing) * float(pv_width)
                no_of_panels = float(total_energy_area) / float(shade_area)
                total_area_of_panels = float(no_of_panels) * float(panel_area)

                # Energy Yield
                total_energy_generation = float(total_area_of_panels) * float(ouput_energy)

                # House equivalent
                house_equivalent = int(float(total_energy_generation) / float(house_consumption))

                stats = str(
                    'Total area (' + units + '): ' + str("{:,.1f}".format(total_area)) + str("&nbsp;" * 15) +
                    'Energy yield (MWh/y): ' + str("{:,.0f}".format(int(total_energy_generation) / 1000)) + str("&nbsp;" * 15) +
                    'Number of dwellings equivalent: ' + str("{:,}".format(house_equivalent))
                    )
                '''
                # Clear Energy Yield Estimator
                self.clear_EnergyYieldEstimator()
                # Populate Energy Yield Estimator
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
                '''

            ### PV Canopy ###
            if technology_comboBox.currentText() == 'PV canopy':
                # Get data to calculate energy yield and EV equivalent                
                ouput_energy = float(self.configure_pv_canopy_dockwidget.energy_spinBox.value())
                EV_consumption = float(self.configure_pv_canopy_dockwidget.EVConsumption_spinBox.value())
                pv_length = float(self.configure_pv_canopy_dockwidget.length_spinbox.value())
                pv_width = float(self.configure_pv_canopy_dockwidget.width_spinbox.value())
                pv_angle = float(self.configure_pv_canopy_dockwidget.pv_angle_spinbox.value())
                inter_row_spacing = float(self.configure_pv_canopy_dockwidget.inter_row_spinbox.value())

                # Area of panel
                panel_area = float(pv_length) * float(pv_width)

                # Area of shade created by panel
                shade_area = float(inter_row_spacing) * float(pv_width)
                no_of_panels = float(total_energy_area) / float(shade_area)
                total_area_of_panels = float(no_of_panels) * float(panel_area)

                # Energy Yield
                total_energy_generation = float(total_area_of_panels) * float(ouput_energy)

                # EV equivalent
                EV_equivalent = int(float(total_energy_generation) / float(EV_consumption))

                stats = str(
                    'Total area (' + units + '): ' + str("{:,.1f}".format(total_area)) + str("&nbsp;" * 15) +
                    'Energy yield (MWh/y): ' + str("{:,.0f}".format(int(total_energy_generation) / 1000)) + str("&nbsp;" * 15) +
                    'Number of EVs equivalent: ' + str("{:,}".format(EV_equivalent)))
                '''
                # Clear Energy Yield Estimator
                self.clear_EnergyYieldEstimator()
                # Populate Energy Yield Estimator
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
                '''

            ### Wind ###
            if technology_comboBox.currentText() == 'Wind':
                # Read energy parameters
                wind_speed = float(self.configure_wind_dockwidget.windSpeed_spinBox.value())
                turbine_efficiency = float(self.configure_wind_dockwidget.turbineEfficiency_spinBox.value())
                house_consumption = float(self.configure_wind_dockwidget.houseConsumption_spinBox.value())
                
                # Energy Yield
                # Rotor is set to a constant as we are calculating wind power density, the swept area value cancels out in the power and wind_energy_density equations
                # i.e. the wind_energy_density is directly proportional to the power, therefore if swept_area decreases, energy_generation decreases and is divided by a lower value
                # resulting an a proportionate wind_energy_density
                rotor = 1
                air_density = 1.23
                swept_area = float(3.14 * (rotor / 2)**2)
                efficiency_percentage = float(turbine_efficiency) / float(100)        
                power = float(0.5 * float(air_density) * float(swept_area) * (wind_speed**3) * efficiency_percentage)
                # Convert power (W) into energy (kWh)
                energy_generation = float(power * (24 * 365)) / float(1000)

                # Energy yield
                wind_energy_density = float(energy_generation) / float(swept_area)
                total_energy_generation = float(total_energy_area * float(wind_energy_density))

                # House equivalent
                house_equivalent = int(float(total_energy_generation) / float(house_consumption))

                stats = str(
                    'Total area (' + units + '): ' + str("{:,.1f}".format(total_area)) + str("&nbsp;" * 15) +
                    'Energy yield (MWh/y): ' + str("{:,.0f}".format(int(round(total_energy_generation / 1000)))) + str("&nbsp;" * 15) +
                    'Number of dwellings equivalent: ' + str("{:,}".format(house_equivalent))
                    )
                '''
                # Clear Energy Yield Estimator
                self.clear_EnergyYieldEstimator()
                # Populate Energy Yield Estimator
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
                '''

            ### For Ground source heat pump ###
            if technology_comboBox.currentText() == 'GSHP':
                ouput_energy = int(self.configure_gshp_dockwidget.energy_spinBox.value())
                heat_loss = int(self.configure_gshp_dockwidget.heatLoss_spinBox.value())
                house_consumption = float(self.configure_gshp_dockwidget.houseConsumption_spinBox.value())

                # Energy Yield
                heat_loss_percentage = float((float(100) - heat_loss) / 100)
                energy_generation = float(total_energy_area * ouput_energy * heat_loss_percentage)
                # Convert energy generation from kWh to MWh
                total_energy_generation = float(energy_generation) / float(1000)

                # House equivalent
                house_equivalent = int(float(energy_generation) / float(house_consumption))

                stats = str(
                    'Total area (' + units + '): ' + str("{:,.1f}".format(total_area)) + str("&nbsp;" * 15) +
                    'Energy yield (MWh/y): ' + str("{:,.0f}".format(int(total_energy_generation))) + str("&nbsp;" * 15) +
                    'Number of dwellings equivalent: ' + str("{:,}".format(house_equivalent))
                    )
                '''
                # Clear Energy Yield Estimator
                self.clear_EnergyYieldEstimator()
                # Populate Energy Yield Estimator
                self.land_availability_dockwidget.energyYieldEstimator_textBrowser.insertHtml(stats)
                '''

            self.iface.messageBar().clearWidgets()
            if technology_comboBox.currentText() != 'Technology':
                #iface.messageBar().pushMessage("", stats, Qgis.Info, -1)
                msgBar.pushMessage("Estimator", str("&nbsp;" * 15) + stats, Qgis.Info, 0)
                # Hide the close button in messagebar
                msgBar.findChildren(QToolButton)[0].setHidden(True)

        except ValueError:
            pass

        self.iface.mapCanvas().refresh()


#-------------------------------Create message bar as global variable-------------------------------------------
    def load_messageBar(self):
        global msgBar
        msgBar = self.iface.messageBar()
        

#-------------------------------Return msgBar to report-------------------------------------------
    def return_messageBar(self):
        return msgBar


#------------------------------Clear Populate Energy Yield Estimator------------------------------------------
    def clear_EnergyYieldEstimator(self):
        self.land_availability_dockwidget.energyYieldEstimator_textBrowser.clear()


#-------------------------------Minimum distance checker--------------------------------------------
    def checkMinDistance(self, point, index, distance, points):
        if distance == 0:
            return True
        neighbors = index.nearestNeighbor(point, 1)
        if len(neighbors) == 0:
            return True
        if neighbors[0] in points:
            np = points[neighbors[0]]
            if np.sqrDist(point) < (distance * distance):
                return False
        return True


#-------------------------------Land availability-----------------------------------------------------
    def land_area(self, parameter):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        policy_group = root.findGroup('Policy')
        technical_group = root.findGroup('Technical')

        # Set global variables
        global areaScore1, areaScore2, areaScore3, areaScore4

        # Define layer
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]

        state = False

        if parameter == 'opportunity_features':
            state = True
            features = []

        opportunity_legend = []

        ltl = QgsProject.instance().layerTreeRoot().findLayer(oppPolTech_weightedMap.id())
        ltm = self.iface.layerTreeView().layerTreeModel()
        legendNodes = ltm.layerLegendNodes(ltl)
        for ln in legendNodes:
            opportunity_legend.append(ln.data(Qt.DisplayRole))
        for ln in legendNodes:
            if ln.data( Qt.CheckStateRole ) != 2:
                try:
                    opportunity_legend.remove(ln.data( Qt.DisplayRole))
                except ValueError:
                    pass

        ##################### Calculate available land availability from opportunity map ######################
        # Check if any features are selected and return these
        if oppPolTech_weightedMap.selectedFeatures():
            if state == True:
                for f in oppPolTech_weightedMap.selectedFeatures():
                    features.append(f)
            else:
                selected_area = []
                sum_green_area = []
                sum_amber_area = []
                sum_red_area = []
                sum_black_area = []
                areaScore1 = 0
                areaScore2 = 0
                areaScore3 = 0
                areaScore4 = 0

                for f in oppPolTech_weightedMap.selectedFeatures():
                    selected_area.append(f)


                for features in selected_area:
                    if (features['Policy_Category'] == 'Possible' and features['Technical_Category'] == 'Favourable') or \
                    (features['Policy_Category'] == 'Possible' and features['Technical_Category'] == 'Likely') or \
                    (features['Policy_Category'] == 'Intermediate' and features['Technical_Category'] == 'Favourable'):
                        sum_green_area.append(features.geometry().area())

                    if (features['Policy_Category'] == 'Possible' and features['Technical_Category'] == 'Unlikely') or \
                    (features['Policy_Category'] == 'Intermediate' and features['Technical_Category'] == 'Likely') or \
                    (features['Policy_Category'] == 'Sensitive' and features['Technical_Category'] == 'Favourable'):
                        sum_amber_area.append(features.geometry().area())

                    if (features['Policy_Category'] == 'Intermediate' and features['Technical_Category'] == 'Unlikely') or \
                    (features['Policy_Category'] == 'Sensitive' and features['Technical_Category'] == 'Likely') or \
                    (features['Policy_Category'] == 'Sensitive' and features['Technical_Category'] == 'Unlikely'):
                        sum_red_area.append(features.geometry().area())

                    if features['Policy_Category'] == 'Showstopper':
                        sum_black_area.append(features.geometry().area())

                areaScore1 = sum(sum_green_area)
                areaScore2 = sum(sum_amber_area)
                areaScore3 = sum(sum_red_area)
                areaScore4 = sum(sum_black_area)


        # Else get features based on legend of opportunities map layer
        else:
            if policy_group.isVisible() != 0 and technical_group.isVisible() != 0: 
                # For Score = NULL or Possible and Favourable
                pos_fav_area = 0
                if 'Possible/ Favourable' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Possible' AND "Technical_Category" = 'Favourable' """ )
                        pos_fav_feat = oppPolTech_weightedMap.getFeatures( request )
                        pos_fav_ids = [i for i in pos_fav_feat]
                        for f in pos_fav_ids:
                            if f.geometry() is not None:
                                if state == True:
                                    features.append(f)
                                else:
                                    pos_fav_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Possible and Likely
                pos_like_area = 0
                if 'Possible/ Likely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Possible' AND "Technical_Category" = 'Likely' """ )
                        pos_like_feat = oppPolTech_weightedMap.getFeatures( request )
                        pos_like_ids = [i for i in pos_like_feat]
                        for f in pos_like_ids:
                            if f.geometry() is not None:
                                if state == True:
                                    features.append(f)
                                else:
                                    pos_like_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Intermediate and Favourable
                int_fav_area = 0
                if 'Intermediate/ Favourable' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Intermediate' AND "Technical_Category" = 'Favourable' """ )
                        int_fav_feat = oppPolTech_weightedMap.getFeatures( request )
                        int_fav_ids = [i for i in int_fav_feat]
                        for f in int_fav_ids:
                            if f.geometry() is not None:
                                if state == True:
                                    features.append(f)
                                else:
                                    int_fav_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Possible and Unlikely
                pos_unlike_area = 0
                if 'Possible/ Unlikely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Possible' AND  "Technical_Category" = 'Unlikely' """ )
                        pos_unlike_feat = oppPolTech_weightedMap.getFeatures( request )
                        pos_unlike_ids = [i for i in pos_unlike_feat]
                        for f in pos_unlike_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    pos_unlike_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Intermediate and Likely
                int_like_area = 0
                if 'Intermediate/ Likely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Intermediate' AND "Technical_Category" = 'Likely' """ )
                        int_like_feat = oppPolTech_weightedMap.getFeatures( request )
                        int_like_ids = [i for i in int_like_feat]
                        for f in int_like_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    int_like_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Sensitive and Favourable
                sen_fav_area = 0
                if 'Sensitive/ Favourable' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Sensitive' AND "Technical_Category" = 'Favourable' """ )
                        sen_fav_feat = oppPolTech_weightedMap.getFeatures( request )
                        sen_fav_ids = [i for i in sen_fav_feat]
                        for f in sen_fav_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    sen_fav_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Intermediate and Unlikely
                int_unlike_area = 0
                if 'Intermediate/ Unlikely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Intermediate' AND "Technical_Category" = 'Unlikely' """ )
                        int_unlike_feat = oppPolTech_weightedMap.getFeatures( request )
                        int_unlike_ids = [i for i in int_unlike_feat]
                        for f in int_unlike_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    int_unlike_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Sensitive and Likely
                sen_like_area = 0
                if 'Sensitive/ Likely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Sensitive' AND "Technical_Category" = 'Likely' """ )
                        sen_like_feat = oppPolTech_weightedMap.getFeatures( request )
                        sen_like_ids = [i for i in sen_like_feat]
                        for f in sen_like_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    sen_like_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Sensitive and Unlikely
                sen_unlike_area = 0
                if 'Sensitive/ Unlikely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Sensitive' AND "Technical_Category" = 'Unlikely' """ )
                        sen_unlike_feat = oppPolTech_weightedMap.getFeatures( request )
                        sen_unlike_ids = [i for i in sen_unlike_feat]
                        for f in sen_unlike_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    sen_unlike_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                # For Score = Showstopper
                show_feat_area = 0
                if 'Showstopper' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Showstopper' """ )
                        show_feat = oppPolTech_weightedMap.getFeatures( request )
                        show_ids = [i for i in show_feat]
                        for f in show_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    show_feat_area += f.geometry().area()
                    except AttributeError:
                        pass

                if state != True:
                    areaScore1 = float(pos_fav_area) + float(pos_like_area) + float(int_fav_area)
                    areaScore2 = float(pos_unlike_area) + float(int_like_area) + float(sen_fav_area)
                    areaScore3 = float(int_unlike_area) + float(sen_like_area) + float(sen_unlike_area)
                    areaScore4 = float(show_feat_area)
                    ########################

            if policy_group.isVisible() in (1, 2) and technical_group.isVisible() == 0:
                pos_area = 0
                if 'Possible' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Possible' """ )
                        pos_feat = oppPolTech_weightedMap.getFeatures( request )
                        pos_ids = [i for i in pos_feat]
                        for f in pos_ids:
                            if f.geometry() is not None:
                                if state == True:
                                    features.append(f)
                                else:
                                    pos_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                inter_area = 0
                if 'Intermediate' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Intermediate' """ )
                        inter_feat = oppPolTech_weightedMap.getFeatures( request )
                        inter_ids = [i for i in inter_feat]
                        for f in inter_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    inter_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                sen_area = 0
                if 'Sensitive' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Sensitive' """ )
                        sens_feat = oppPolTech_weightedMap.getFeatures( request )
                        sens_ids = [i for i in sens_feat]
                        for f in sens_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    sen_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                show_feat_area = 0
                if 'Showstopper' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Policy_Category" = 'Showstopper' """ )
                        show_feat = oppPolTech_weightedMap.getFeatures( request )
                        show_ids = [i for i in show_feat]
                        for f in show_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    show_feat_area += f.geometry().area()
                    except AttributeError:
                        pass

                if state != True:
                    areaScore1 = float(pos_area)
                    areaScore2 = float(inter_area)
                    areaScore3 = float(sen_area)
                    areaScore4 = float(show_feat_area)
            ########################

            if technical_group.isVisible() in (1, 2) and policy_group.isVisible() == 0:
                fav_area = 0
                if 'Favourable' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Technical_Category" = 'Favourable' """ )
                        fav_feat = oppPolTech_weightedMap.getFeatures( request )
                        fav_ids = [i for i in fav_feat]
                        for f in fav_ids:
                            if f.geometry() is not None:
                                if state == True:
                                    features.append(f)
                                else:
                                    fav_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                like_area = 0
                if 'Likely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Technical_Category" = 'Likely' """ )
                        like_feat = oppPolTech_weightedMap.getFeatures( request )
                        like_ids = [i for i in like_feat]
                        for f in like_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    like_area += f.geometry().area()
                    except AttributeError:
                        pass
                ########################
                unlike_area = 0
                if 'Unlikely' in opportunity_legend:
                    try:
                        request = QgsFeatureRequest().setFilterExpression( """ "Technical_Category" = 'Unlikely' """ )
                        unlike_feat = oppPolTech_weightedMap.getFeatures( request )
                        unlike_ids = [i for i in unlike_feat]
                        for f in unlike_ids:
                            if f.geometry() is not None:
                                if state == False:
                                    unlike_area += f.geometry().area()
                    except AttributeError:
                        pass


            if policy_group.isVisible() == 0 and technical_group.isVisible() == 0:
                fav_area = 0
                try:
                    fav_feat = oppPolTech_weightedMap.getFeatures()
                    fav_ids = [i for i in fav_feat]
                    for f in fav_ids:
                        if f.geometry() is not None:
                            if state == True:
                                features.append(f)
                            else:
                                fav_area += f.geometry().area()
                except AttributeError:
                    pass

                if state != True:
                    areaScore1 = float(fav_area)
                    areaScore2 = 0
                    areaScore3 = 0
                    areaScore4 = 0
                ########################

        if state == True:
            return features


#-------------------------------Land availability area units-----------------------------------------------------
    def land_areaUnits(self):
        try:
            # Output area results to interface depending on unit selection
            utilisation_green = float(self.land_availability_dockwidget.utilisation_green_spinBox.text())
            utilisation_amber = float(self.land_availability_dockwidget.utilisation_amber_spinBox.text())
            utilisation_red = float(self.land_availability_dockwidget.utilisation_red_spinBox.text())
            utilisation_black = float(self.land_availability_dockwidget.utilisation_black_spinBox.text())

            # If metres are selected
            if self.land_availability_dockwidget.areaUnits_combo.currentText() == u'm\u00B2':
                self.land_availability_dockwidget.area_green_lineEdit.setText("{:,.1f}".format(areaScore1))
                self.land_availability_dockwidget.area_amber_lineEdit.setText("{:,.1f}".format(areaScore2))
                self.land_availability_dockwidget.area_red_lineEdit.setText("{:,.1f}".format(areaScore3))
                self.land_availability_dockwidget.area_black_lineEdit.setText("{:,.1f}".format(areaScore4))


            if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == u'm\u00B2':
                self.land_availability_dockwidget.area_Score1_lineEdit.setText("{:,.1f}".format(float(areaScore1) * (float(utilisation_green) / float(100))))
                self.land_availability_dockwidget.area_Score2_lineEdit.setText("{:,.1f}".format(float(areaScore2) * (float(utilisation_amber) / float(100))))
                self.land_availability_dockwidget.area_Score3_lineEdit.setText("{:,.1f}".format(float(areaScore3) * (float(utilisation_red) / float(100))))
                self.land_availability_dockwidget.area_Score4_lineEdit.setText("{:,.1f}".format(float(areaScore4) * (float(utilisation_black) / float(100))))

            # If km is selected
            if self.land_availability_dockwidget.areaUnits_combo.currentText() == u'km\u00B2':
                new_areaScore1 = float(areaScore1) / 1000000
                new_areaScore2 = float(areaScore2) / 1000000
                new_areaScore3 = float(areaScore3) / 1000000
                new_areaScore4 = float(areaScore4) / 1000000

                self.land_availability_dockwidget.area_green_lineEdit.setText("{:,.1f}".format(new_areaScore1))
                self.land_availability_dockwidget.area_amber_lineEdit.setText("{:,.1f}".format(new_areaScore2))
                self.land_availability_dockwidget.area_red_lineEdit.setText("{:,.1f}".format(new_areaScore3))
                self.land_availability_dockwidget.area_black_lineEdit.setText("{:,.1f}".format(new_areaScore4))

            if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == u'km\u00B2':
                new_areaScore1 = float(areaScore1) / 1000000
                new_areaScore2 = float(areaScore2) / 1000000
                new_areaScore3 = float(areaScore3) / 1000000
                new_areaScore4 = float(areaScore4) / 1000000

                self.land_availability_dockwidget.area_Score1_lineEdit.setText("{:,.1f}".format(float(new_areaScore1) * (float(utilisation_green) / float(100))))
                self.land_availability_dockwidget.area_Score2_lineEdit.setText("{:,.1f}".format(float(new_areaScore2) * (float(utilisation_amber) / float(100))))
                self.land_availability_dockwidget.area_Score3_lineEdit.setText("{:,.1f}".format(float(new_areaScore3) * (float(utilisation_red) / float(100))))
                self.land_availability_dockwidget.area_Score4_lineEdit.setText("{:,.1f}".format(float(new_areaScore4) * (float(utilisation_black) / float(100))))

            # If acre is selected
            if self.land_availability_dockwidget.areaUnits_combo.currentText() == 'acre':
                new_areaScore1 = float(areaScore1) / 4046.86
                new_areaScore2 = float(areaScore2) / 4046.86
                new_areaScore3 = float(areaScore3) / 4046.86
                new_areaScore4 = float(areaScore4) / 4046.86

                self.land_availability_dockwidget.area_green_lineEdit.setText("{:,.1f}".format(new_areaScore1))
                self.land_availability_dockwidget.area_amber_lineEdit.setText("{:,.1f}".format(new_areaScore2))
                self.land_availability_dockwidget.area_red_lineEdit.setText("{:,.1f}".format(new_areaScore3))
                self.land_availability_dockwidget.area_black_lineEdit.setText("{:,.1f}".format(new_areaScore4))

            if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == 'acre':
                new_areaScore1 = float(areaScore1) / 4046.86
                new_areaScore2 = float(areaScore2) / 4046.86
                new_areaScore3 = float(areaScore3) / 4046.86
                new_areaScore4 = float(areaScore4) / 4046.86

                self.land_availability_dockwidget.area_Score1_lineEdit.setText("{:,.1f}".format(float(new_areaScore1) * (float(utilisation_green) / float(100))))
                self.land_availability_dockwidget.area_Score2_lineEdit.setText("{:,.1f}".format(float(new_areaScore2) * (float(utilisation_amber) / float(100))))
                self.land_availability_dockwidget.area_Score3_lineEdit.setText("{:,.1f}".format(float(new_areaScore3) * (float(utilisation_red) / float(100))))
                self.land_availability_dockwidget.area_Score4_lineEdit.setText("{:,.1f}".format(float(new_areaScore4) * (float(utilisation_black) / float(100))))

            # If ha is selected
            if self.land_availability_dockwidget.areaUnits_combo.currentText() == 'ha':
                new_areaScore1 = float(areaScore1) / 10000
                new_areaScore2 = float(areaScore2) / 10000
                new_areaScore3 = float(areaScore3) / 10000
                new_areaScore4 = float(areaScore4) / 10000

                self.land_availability_dockwidget.area_green_lineEdit.setText("{:,.1f}".format(new_areaScore1))
                self.land_availability_dockwidget.area_amber_lineEdit.setText("{:,.1f}".format(new_areaScore2))
                self.land_availability_dockwidget.area_red_lineEdit.setText("{:,.1f}".format(new_areaScore3))
                self.land_availability_dockwidget.area_black_lineEdit.setText("{:,.1f}".format(new_areaScore4))

            if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == 'ha':
                new_areaScore1 = float(areaScore1) / 10000
                new_areaScore2 = float(areaScore2) / 10000
                new_areaScore3 = float(areaScore3) / 10000
                new_areaScore4 = float(areaScore4) / 10000

                self.land_availability_dockwidget.area_Score1_lineEdit.setText("{:,.1f}".format(float(new_areaScore1) * (float(utilisation_green) / float(100))))
                self.land_availability_dockwidget.area_Score2_lineEdit.setText("{:,.1f}".format(float(new_areaScore2) * (float(utilisation_amber) / float(100))))
                self.land_availability_dockwidget.area_Score3_lineEdit.setText("{:,.1f}".format(float(new_areaScore3) * (float(utilisation_red) / float(100))))
                self.land_availability_dockwidget.area_Score4_lineEdit.setText("{:,.1f}".format(float(new_areaScore4) * (float(utilisation_black) / float(100))))
        except UnboundLocalError:
            pass


#-------------------------------Convert land units-----------------------------------------------------
    def convert_land_units_to_textBroswer(self, values):
        # If metres are selected
        if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == u'm\u00B2':
            area = round(values, 1)

        # If km is selected
        if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == u'km\u00B2':
            area = round(values / 1000000, 2)

        # If acre is selected
        if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == 'acre':
            area = round(values / 4046.86, 2)

        # If ha is selected
        if self.land_availability_dockwidget.areaUnits_combo_2.currentText() == 'ha':
            area = round(values / 10000, 2)

        return area


#-------------------------------Land availability for user-defined weighting search-----------------------------------------------------
    def land_area_green_only(self, factor_type):
        # Define root and groups
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(factor_type)
        if factor_type == 'Policy':
            expression = """ "Policy_Category" = 'Possible' """
        if factor_type == 'Technical':
            expression = """ "Technical_Category" = 'Favourable' """

        # Define layer
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]

        if group.isVisible() in (1, 2):
            green_area = 0
            try:
                request = QgsFeatureRequest().setFilterExpression( expression )
                features = oppPolTech_weightedMap.getFeatures( request )
                ids = [i for i in features]
                for f in ids:
                    if f.geometry() is not None:
                        green_area += f.geometry().area()
            except AttributeError:
                pass

        return green_area


#-------------------------------Update available land and energy yield by selecting features-----------------------------------------------------
    def selectingFeatures(self, checked):
        oppPolTech_weightedMap = QgsProject.instance().mapLayersByName( "Opportunities" )[0]
        if checked:
            # Show message when Selection mode is ON
            iface.messageBar().clearWidgets()
            iface.messageBar().pushMessage("", 'Selection mode', Qgis.Info, 3)
            self.iface.actionSelect().trigger()
            self.iface.setActiveLayer(oppPolTech_weightedMap)
            try:
                oppPolTech_weightedMap.selectionChanged.disconnect(self.update_available_land)
            except TypeError:
                pass

            oppPolTech_weightedMap.selectionChanged.connect(self.update_available_land)
            
        else:
            # Show message when Identify mode is ON
            iface.messageBar().clearWidgets()
            iface.messageBar().pushMessage("", 'Identify mode', Qgis.Info, 3)
            self.iface.actionIdentify().trigger()
            oppPolTech_weightedMap.removeSelection()
            try:
                oppPolTech_weightedMap.selectionChanged.disconnect(self.update_available_land)
            except TypeError:
                pass

    def update_available_land(self, selFeatures):
        self.land_area(None)
        self.land_areaUnits()
        self.populate_EnergyYieldEstimator()