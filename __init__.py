# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GOMap
                                 A QGIS plugin
 For examining renewable energy systems deployment opportunities in cities.
                             -------------------
        begin                : 2016-12-07
        copyright            : (C) 2016 by ESRU, University of Strathclyde
        email                : esru@strath.ac.uk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GOMap class from file GOMap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GOMap import GOMap
    return GOMap(iface)
