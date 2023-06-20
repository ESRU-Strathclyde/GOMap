<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" simplifyDrawingTol="1" minScale="100000000" version="3.12.3-București" simplifyDrawingHints="1" styleCategories="AllStyleCategories" maxScale="100000" labelsEnabled="0" simplifyLocal="1" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" type="RuleRenderer" forceraster="0" symbollevels="0">
    <rules key="{12e28496-b9fa-4813-8238-ff51f38d197d}">
      <rule symbol="0" key="{5010aba9-1dc8-41aa-ada2-2e6c8f500168}" label="Possible" filter="&quot;Policy_Category&quot; = 'Possible'"/>
      <rule symbol="1" key="{447a744b-26e7-4a77-88aa-c8da98b81645}" label="Intermediate" filter="&quot;Policy_Category&quot; = 'Intermediate'"/>
      <rule symbol="2" key="{047fdae9-f7b2-43b2-8945-5e64669b8177}" label="Sensitive" filter="&quot;Policy_Category&quot; = 'Sensitive'"/>
      <rule symbol="3" key="{dc4a9460-d166-437b-9f4a-94fc3d954dc5}" label="Showstopper" filter="&quot;Policy_Category&quot; = 'Showstopper'"/>
    </rules>
    <symbols>
      <symbol type="fill" alpha="1" force_rhr="0" clip_to_extent="1" name="0">
        <layer enabled="1" pass="1" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="0,255,0,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,255,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="outlineColor">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="if(@map_scale &lt; 13000, '0, 0, 0', color_rgb( color_part(@symbol_color, 'red'), color_part(@symbol_color, 'green'), color_part(@symbol_color, 'blue')))" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" alpha="1" force_rhr="0" clip_to_extent="1" name="1">
        <layer enabled="1" pass="2" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="240,171,100,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="240,171,100,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="outlineColor">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="if(@map_scale &lt; 13000, '0, 0, 0', color_rgb( color_part(@symbol_color, 'red'), color_part(@symbol_color, 'green'), color_part(@symbol_color, 'blue')))" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" alpha="1" force_rhr="0" clip_to_extent="1" name="2">
        <layer enabled="1" pass="3" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="150,54,52,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="150,54,52,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="outlineColor">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="if(@map_scale &lt; 13000, '0, 0, 0', color_rgb( color_part(@symbol_color, 'red'), color_part(@symbol_color, 'green'), color_part(@symbol_color, 'blue')))" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" alpha="1" force_rhr="0" clip_to_extent="1" name="3">
        <layer enabled="1" pass="4" class="SimpleFill" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="29,27,16,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="29,27,16,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option type="Map" name="properties">
                <Option type="Map" name="outlineColor">
                  <Option type="bool" value="true" name="active"/>
                  <Option type="QString" value="if(@map_scale &lt; 13000, '0, 0, 0', color_rgb( color_part(@symbol_color, 'red'), color_part(@symbol_color, 'green'), color_part(@symbol_color, 'blue')))" name="expression"/>
                  <Option type="int" value="3" name="type"/>
                </Option>
              </Option>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Pie" attributeLegend="1">
    <DiagramCategory backgroundColor="#ffffff" minimumSize="0" minScaleDenominator="100000" barWidth="5" penWidth="0" spacing="0" maxScaleDenominator="1e+08" direction="1" sizeScale="3x:0,0,0,0,0,0" enabled="0" height="15" lineSizeScale="3x:0,0,0,0,0,0" scaleDependency="Area" width="15" sizeType="MM" lineSizeType="MM" rotationOffset="270" showAxis="0" opacity="1" labelPlacementMethod="XHeight" spacingUnitScale="3x:0,0,0,0,0,0" spacingUnit="MM" penAlpha="255" backgroundAlpha="255" scaleBasedVisibility="0" diagramOrientation="Up" penColor="#000000">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" field="" label=""/>
      <axisSymbol>
        <symbol type="line" alpha="1" force_rhr="0" clip_to_extent="1" name="">
          <layer enabled="1" pass="0" class="SimpleLine" locked="0">
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" obstacle="0" priority="0" dist="0" showAll="1" placement="0" linePlacementFlags="2">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option type="Map" name="properties">
          <Option type="Map" name="show">
            <Option type="bool" value="true" name="active"/>
            <Option type="QString" value="ID" name="field"/>
            <Option type="int" value="2" name="type"/>
          </Option>
        </Option>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option type="Map" name="QgsGeometryGapCheck">
        <Option type="double" value="0" name="allowedGapsBuffer"/>
        <Option type="bool" value="false" name="allowedGapsEnabled"/>
        <Option type="QString" value="" name="allowedGapsLayer"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <referencedLayers/>
  <referencingLayers/>
  <fieldConfiguration>
    <field name="ID">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="Policy_Category">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="ID" index="0" name=""/>
    <alias field="Policy_Category" index="1" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="ID"/>
    <default expression="" applyOnUpdate="0" field="Policy_Category"/>
  </defaults>
  <constraints>
    <constraint constraints="0" field="ID" notnull_strength="0" unique_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="Policy_Category" notnull_strength="0" unique_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="ID" desc="" exp=""/>
    <constraint field="Policy_Category" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column type="field" width="-1" hidden="0" name="ID"/>
      <column type="actions" width="-1" hidden="1"/>
      <column type="field" width="-1" hidden="0" name="Policy_Category"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>../qgis test project_2</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from PyQt4.QtGui import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="ID"/>
    <field editable="0" name="Policy_Category"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="ID"/>
    <field labelOnTop="0" name="Policy_Category"/>
  </labelOnTop>
  <widgets>
    <widget name="Access_Category">
      <config/>
    </widget>
    <widget name="CDP_HYPERL">
      <config/>
    </widget>
    <widget name="CONFIRMED">
      <config/>
    </widget>
    <widget name="Combined access_Category">
      <config/>
    </widget>
    <widget name="Combined energy_Category">
      <config/>
    </widget>
    <widget name="Combined policy_Category">
      <config/>
    </widget>
    <widget name="Combined policy_Score">
      <config/>
    </widget>
    <widget name="Combined technical_Category">
      <config/>
    </widget>
    <widget name="Combined technical_Score">
      <config/>
    </widget>
    <widget name="Energy_Category">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Community growth masterplan area (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Community growth masterplan area (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Community growth masterplan area (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Community growth masterplan area (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Community growth masterplan area (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Economic policy areas (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Economic policy areas (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Economic policy areas (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Economic policy areas (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Feasibility study - Summerston (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Feasibility study - Summerston (P)_LDP_Ref">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Feasibility study - Summerston (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Feasibility study - Summerston (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green belt (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green belt (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green belt (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green belt (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green belt (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Green network opportunity areas (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - consented (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - consented (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - consented (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - consented (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - potential (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - potential (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - potential (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Housing land supply - potential (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Industrial/business marketable land supply (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Industrial/business marketable land supply (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Local development framework (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Local development framework (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Local development framework (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Master plan area (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Master plan area (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Master plan area (P)_Proposal">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Master plan area (P)_Proposer">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Master plan area (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Network of centres (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Network of centres (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Network of centres (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Network of centres (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_PolScore">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic development framework - river (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic economic investment locations (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic economic investment locations (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Strategic economic investment locations (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Transformational regeneration areas (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Transformational regeneration areas (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-DE - Developmental policy, citywide_Transformational regeneration areas (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Conservation areas (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Green corridors_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Green corridors (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Historic gardens designed landscapes (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Listed buildings (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Local nature reserves (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_ANTIQUITY">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Old wood (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_PolScore">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Proposed conservation area (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Scheduled ancient monuments (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of importance for nature conservation (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special landscape importance (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_EVNUMBER">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Sites of special scientific interest (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_AREACODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_AREANAME">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_Tree Preservation Order (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall buffer (P)_HYPERLINK">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall buffer (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall buffer (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall buffer (P)_OLCPCODE">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-EN - Environmental policy, citywide_World heritage site - Antonine Wall buffer (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_Radius">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_Type">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Airport, helipad and motorway (P)_length">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Helipad inner radius (P)_LINKTEXT">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Helipad inner radius (P)_OBJECTID">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Helipad inner radius (P)_Radius">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Helipad inner radius (P)_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Helipad inner radius (P)_Type">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_PolScore">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_P-VN - Visual intrusion, citywide_Score">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_PolScore">
      <config/>
    </widget>
    <widget name="H-PO - Combined policy score by hybrid method, citywide_S">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_11kV fault">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_11kV score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_33kV fault">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Area score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Capacity">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Circuits">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Comb_score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Gen Cap">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_HubDist">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_HubName">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Reverse">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Tot_fault">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Trans_cons">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Type">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Voltage">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_X">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_Grid congestion points (P)_Y">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GC - Grid congestion, citywide_TechScore">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GD - Grid connection distance, citywide_Distance from grid to primary substation (P)_HubDist">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GD - Grid connection distance, citywide_Distance from grid to primary substation (P)_HubName">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GD - Grid connection distance, citywide_Distance from grid to primary substation (P)_Score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-GD - Grid connection distance, citywide_TechScore">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-OS - Overshadowing, citywide_Merged annual shade (P)_Score">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-OS - Overshadowing, citywide_Merged annual shade (P)_TOID">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_T-OS - Overshadowing, citywide_TechScore">
      <config/>
    </widget>
    <widget name="H-TE - Combined technical score by hybrid method, citywide_TechScore">
      <config/>
    </widget>
    <widget name="LOCATION">
      <config/>
    </widget>
    <widget name="OBJECTID">
      <config/>
    </widget>
    <widget name="Policy_Category">
      <config/>
    </widget>
    <widget name="Policy_Score">
      <config/>
    </widget>
    <widget name="Score">
      <config/>
    </widget>
    <widget name="Technical_Category">
      <config/>
    </widget>
    <widget name="Technical_Score">
      <config/>
    </widget>
  </widgets>
  <previewExpression>ID</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
