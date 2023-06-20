# GOMap

********************************************************************************************************
Copyright (c) 2014-2023 Energy Systems Research Unit, University of Strathclyde, All Rights Reserved.  
                                                                                                       
********************************************************************************************************

Contents
1. Getting Started
    a. GOMap v3.11
    b. Installation
    c. Running QGIS v3.28.1
    d. Extracting GOMap
    e. Setup
2. Running GOMap
    a. Load Glasgow project
    b. Toolbar
	 - GOMap
	 - Save project
	 - Identify/Select mode
	 - About
	 - Tools
    c. Focus selection
	 - Scope
	 - Aspects
	 - Scoring
	 - Weighting
    d. Updating factor with single score
    e. Updating factor with multiple scores
    f. Land availability
    g. Energy yield estimator
    h. Technology scripts
3. New GOMap project
4. Change resolution
5. Other useful plugins
6. Contact

********************************************************************************************************

1. Getting Started

1.a. GOMap v3.11

    GOMap - A geospatial opportunity map for identifying suitable areas for the deployment of energy systems.
    Takes into consideration policy and technical aspects, both of which consists of a number of comprehensive factors. 
    Each factor is superimposed on a high-resolution grid supported by a scoring and weighting system.
    The output maps allow users to determine the overall suitability of any given site and identify the specific policy or technical aspects that might impede a proposed deployment.
    
    For more information, see the ESRU Publication website:
    (http://www.esru.strath.ac.uk/publications.htm)


1.b. Installation

    Requires QGIS v3.28.1 using the Standalone Installer for Windows:
    (https://qgis.org/en/site/forusers/download.html)

    QGIS is an Open Source Geographic Information System (GIS) licensed under the GNU General Public License.


1.c. Running QGIS v3.28.1

    If QGIS has not been installed previously, run it. This will create the following directory:
    "C:/Users/user_name/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/"

    The "plugins/" directory will contain all plugins used by QGIS. Running QGIS will allow you to configure settings. 
    In order to use GOMap, macros must be enabled. This can be set from the menubar in the QGIS interface (Settings > Options > General)
    Set the "Enable macros" option to 'Always'.

    The following suggestions are also recommended to maximise performance:
    - Set the rendering settings to use the maximum CPU cores available (Settings > Options > Rendering)
    - Set the default output vector layer extension to be "shp" (Settings > Options > Processing > General > 

    When applied, close QGIS.


1.d. Extracting GOMap

    Extract all contents from the .zip file to the Desktop. There are 3 folders:

    "GOMap - enter_name".  A project template.
    "GOMap - Glasgow". A project based on Glasgow, Scotland (UK).
    "GOMap". The GOMap plugin.

    The plugin must be moved to the same directory mentioned above:
    "C:/Users/user_name/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/"

    If the "plugins" directory does not exist, create a new folder with the name "plugins" and insert the GOMap plugin.
    

1.e. Setup

    Run QGIS. From the menubar in QGIS, go to:
    Plugins > Manage and Install Plugins

    Search for "GOMap" and enable it by checking the box.


********************************************************************************************************


2. Running GOMap

2.a. Load Glasgow project.

    Inside the "GOMap - Glasgow" folder, load the "GOMap.qgs" project file. The project file will automatically initiate the plugin.


2.b. Toolbar

    The GOMap toolbar contains the following functions:

    "GOMap". 
     When set to ON enables the opportunity map and is continuously updated whenever a change is made.
     This allows the results from the acreage and energy yield estimator panels to be recalculated. 
     When set to OFF, the opportunity map is disabled and all underlying factors can be seen and examined.

    "Save project".
     Saves your current project.

    "Identify/Select mode"
     Toggle between retrieving information for features or selecting them to determine area and energy statistics. 

    "Tools"
	  Update - Checks for latest GOMap version.
      Settings - Select various options for scoring and interface (See #2c. "Scoring").
      Add/save layer - Adds an empty polygon layer where new polygons can be drawn. The layer can be saved as a new scope or factor.
      Scripts - Technology specific scripts which allow for the physical generation of energy systems on suitable land sites as shown on the opportunity map and returns energy statistics (See #2h. "Technology scripts").

    "About".
     Loads a description of the project which can be edited in the 'About.txt' file. Hyperlinks are supported.   


2.c. Focus selection

    "Scope". 
     A spatial filter to focus GOMap on specific parts of the opportunities map. Only one scope can be active at any time.
     Switching to another will update the land availability and energy yield statistics.
     New scopes can be added by checking 'New scope'. This allows to scope by specific attributes from a polygon layer (e.g. postcode from the 'Wards' shapefile).

    "Aspects". 
     Split into two: policy and technical, both of which contain relevant factors.
     These could be interactively switched on or off which updates the opportunities map.

     "Scoring"
     Each factor can be scored as 1, 2 or 3 where 1 is best and 3 is worst. A special score which designates the area as a 'Showstopper' is given as 4 and overrides all other scores.
     The 'Lenient' method is calculated by taking the mean (or median) score available from all factors in each aspect. The final policy/technical score is then calculated by taking the mean (or median) of all aspect scores.
     The 'Stringent' method uses the highest score of a factor in each aspect. The final policy/technical score for each grid cell is allocated the score of the aspect which possessed the highest.
     The lenient method is set as default and can be changed from the "Tools" menu.

    "Weighting".
     Split into two: Equal and user-defined. Takes into account two available scoring methods.

     'Equal' - The overall score can be calculated by either scoring method.
     For example, the lenient method; if 3 aspects from the 'Environmental' factor overlapped a grid cell and had scores of 1, 2 and 4, the 'Environmental' factor score for that cell would be 4. This is repeated for all other aspects.
     If 5 factors overlapped this same cell and had scores of (1, 1, 2, 2, 3), the final policy score would be (2 = 'Intermediate').
     If 3/5 factors overlapped this same cell and had scores of (NULL, NULL, 1, 1, 2), the NULL factors are excluded and the final policy score would be (1 = 'Possible').
     If 5 factors overlapped this same cell and had scores of (1, 1, 2, 3, 4), the final policy score would be 4 due to a factor being a 'Showstopper'.

     'User-defined' - The overall score is calculated by using only the lenient method.
     Uses the highest weighting given for each factor. The overall score for each grid cell is allocated the score of the factor which possessed the higher weighting. 
     For example, if three factors overlap a grid cell and had scores of (1, 2, 3) with weighting: (0.2, 0.5, 0.3), the cell would be allocated the score of the factor which had the highest weighting (in this case, 2).
     The total weighting must equal 1 for policy, similarly for technical. Default values are set when this method is chosen.
     In contrast to the equal weighting method, each factor could be weighted to encourage or mitigate development.
     This method could be more suited to policy makers or planners as they can decide which factor has greater importance in regards to other factors.
     The "AHP" (Analytical Hierarchy Process) function is a mathematical technique where each criterion is assigned a scale to determine the ideal weighting of each criterion in a given scenario. The AHP technique is based on the pairwise comparisons method. The decision-maker forms a hierarchical decision tree and determines the importance of each individual criteria in comparison to all other criteria by using a 9-point scale system.
     The "Search" function automatically searches for the best weighting combination which provides the maximum ideal area.

    "Opportunities". 
     The policy/technical opportunity map showing the final result.

    "Additional Information". 
     Provides visual references, tabular data or any other miscellaneous information. Does not affect the any results.


2.d. Updating factor with single score

    Right-click a factor and chose the "Open Attribute Table" option. Click the "Edit" button (pencil icon) and select the 'Score' field.
    Enter a score (1-4 for policy; 1-3 for technical) then save the edits. The opportunities map will be refreshed.


2.e. Updating factor with multiple scores

    Right-click a factor and chose the "Open Attribute Table" option. Click the "Edit" button (pencil icon) and select the 'Score' field.
    Enter an expression in order to determine which feature is allocated a specific score. Save the edits by clicking the "Edit" button again.
    The technical aspect "Connection distance" is one example using multiple scores based on distance. The expression used was:

    CASE
    WHEN "HubDist" <= 100 THEN 1
    WHEN "HubDist" > 100 AND "HubDist" <= 200 THEN 2 
    ELSE 3
    END

    It is highly recommended to use a "Virtual field" to store multiple scores for factors which overlap significantly large areas as this can increase performance.
    Note that this field is NOT saved in the shapefile but within the project file.
    This be can accomplished by right-clicking a factor and choosing the "Open Attribute Table" option. Click the "Edit" button (pencil icon).
    If there is a 'Score' field, select the "Delete field" button and delete it. Select the "Field Calculator" button and check the 'Create a new field' and 'Create virtual field' options.
    Add name, type and length details ('Score', Whole number (integer), 10) and enter the expression to calculate multiple scores. When done, click OK and save the edits by clicking the "Edit" button again.


2.f. Land availability

    Calculates area of available opportunity. Different units can be selected.
    The utilisation factor allows a percentage of green, amber and/or red areas of opportunity to be included in the calculations.
    A factor of 1.00 is the equivalent of 100 %; 0.2 is 20 % etc.


2.g. Energy yield estimator
  
    Users can select a technology in order to see an estimated energy yield based on current opportunities.
    Each time the map has changed, the estimator is refreshed. The user can configure the options for each technology.
    The report button creates a PDF report which will contain the opportunity map, parameters used, calculated energy yield, number of buildings equivalent and other information.


2.h. Technology scripts

    There are 3 technologies which are currently supported.

    "PV"
    Generate PV panels - Creates polygons representing PV arrays within opportunity areas based on parameters such as length/width of PV array, tilt angle, orientation, inter-row spacing, and energy yield. Two modes are available: "Custom mode" uses user-defined parameters to create PV arrays; "Automatic mode" which uses weather information (ambient temperature, direct and diffuse solar radiation) to calculate optimal parameters.  PV spreadsheet model can be loaded to calculate annual average energy generation per m^2 which are fed into the energy and solar parameters of the script. Energy statistics is provided with an optional summary by area with the chosen polygon layer.
    Generate northerly/southerly sites - Creates polygon sites which face either northerly (from 315 deg to 45 deg clockwise) or southerly (135 deg to 225 deg clockwise). Requires a Digital Surface Model (DSM) and a polygon site layer. The output layer is saved in the "Additional information" directory which can be used as a new scope layer (See #2c. "Scope").

    "Wind"
    Generate wind turbines - Creates points with a buffer of user-defined dimensions within opportunity areas. Physical parameters can be set to determine spacing between turbines and the average energy generated.

    "District heating"
    Generate district heating - Creates points representing the district heating network source within opportunity areas. A building polygon layer is required to determine how much energy (from the energy parameters given) is available and the nearest buildings that can be supplied. Creates an additional polygon layer representing building polygons in green (supplied) and red (not supplied) within a user-defined proximity parameter.


********************************************************************************************************


3. New GOMap project

    The "GOMap - enter_name" directory is a project template. This can be renamed to a chosen town/city (e.g. "GOMap - Tokyo").
    Shapefiles can be imported into GOMap where these are converted to a grid system. Each cell is given a unique ID.
    Once the script has finished, both the original and processed shapefiles are moved to their respective folders within the GOMap directory. 
    
    To begin, locate the "Processing scripts" directory inside the "GOMap - enter_name" folder. 
    There are 2 folders and 2 executable files.
    The "Script" folder can be ignored as this contains the source code for the conversion process.
    The "Shapefile conversion" folder is where shapefiles are placed.
    The "Run project conversion script" is used for changing the grid resolution for the entire project (See #4. Change resolution).
    The "Run shapefile conversion script" is used for converting shapefiles into a grid.

    Ensure the shapefiles do not contain geometric errors (tools such as "Fix Geometry" in QGIS can solve this). 
    Inside the "Shapefile conversion" directory, there are 3 folders.
    The "City" folder must contain a polygon shapefile covering the entire extent of the desired area (e.g. the boundaries of Tokyo).
    The "Scope" folder is optional but can contain a polygon shapefile which covers specific areas within the city shapefile.
    The "Factors" folder should contain all factors for ONE ASPECT AT A TIME. Polygon, point and line shapefiles can be used.
    For line shapefiles, ensure there is a "Width" field (e.g. to represent motorways, pipes etc.); for point shapefiles, ensure there is a "Name" field (e.g. to represent the name of a substation etc.).
    These shapefiles should be placed in the relevant scoring folders where "Score 1" means all shapefiles will be given a score of 1; "Score 2" for a score of 2 etc.
    The "Existing score" folder should contain shapefiles which either already possess a score or given a score at a later stage.

    Once all the required shapefiles are placed accordingly, the 'Run shapefile conversion script' tool can be executed.
    When the script is executed, the user is prompted to enter required information.
    This includes whether the shapefiles are for SCOPE, POLICY or TECHNICAL. 
    If SCOPE is chosen, then grid cell size is required (e.g. "100" will make 100m x 100m cells).
    An overlap rule can be specified where sites are excluded if the % of area is less than the resolution (e.g. "10" will exclude sites which are <= 10% of the area of a grid cell).
    IF POLICY or TECHNICAL is chosen, the name of the aspect and the grid resolution are required.
    Each grid cell will have a unique ID attribute which is used to map all factors within the project.
    This process should be repeated for other aspect groups. Once finished, the GOMap project can be opened.
    
    **CAUTION**
    If a shapefile contains a large number of geometries, it is highly recommended to place the shapefile in the "Existing score" folder and remove any unnecessary fields. 
    When GOMap is loaded, add a new virtual "Score" field with the relevant score or expression as this can boost performance when dealing with large shapefiles. Save the GOMap project and restart it.
    A copy of the shapefile containing all attributes could be added to the "Additional information" directory and can be used as reference.
    

********************************************************************************************************

4. Change resolution

    The 'Run project conversion script' in the "Processing scripts" directory allows existing projects to be rebuilt at a user-defined resolution. 
    This script reprocesses the original factors to a new cellsize using the existing scores used.
    The script can be found in the "Processing scripts" directory.
    The "City" folder must contain a polygon shapefile covering the entire extent of the desired area (e.g. the boundaries of Tokyo).
    The project must not be loaded in QGIS when running this script and it is recommended that QGIS be closed.


********************************************************************************************************

5. Other useful plugins

    QuickMapServices - Provides satellite imagery to be used as basemaps.
    go2streetview - In combination with the QuickMapServices plugin, Google or Bing basemaps are used to open Google Streetview or Bing BirdsEye.


********************************************************************************************************

6. Contact

    Enquiries relating to GOMap should be sent to esru@strath.ac.uk.
