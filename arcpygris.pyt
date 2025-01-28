# -*- coding: utf-8 -*-

import arcpy, arcpy_helpers
import enumeration_units, tribal_native_areas, legislative_areas, metro_areas_places, nation, landmarks, transportation, water, fips

import importlib
importlib.reload(legislative_areas)

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "arcpygris"
        self.alias = "arcpygris"

        # List of tool classes associated with this toolbox
        self.tools = [EnumerationUnits, TribalNativeAreas, LegislativeAreas, MetroAreasPlaces, Nation, Landmarks, Transportation, Water]

class EnumerationUnits:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Enumeration Units"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["State", "County", "Tract", "Block Group", "Block", "ZCTA", "County Subdivision", "School District"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_geom_type = arcpy.Parameter(
            displayName = "Geometry Type",
            name = "GeometryType",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param_geom_type.filter.type = "ValueList"

        param_resolution = arcpy.Parameter(
            displayName = "Resolution",
            name = "Resolution",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_resolution.filter.type = "ValueList"
        param_resolution.enabled = False

        param_sd_type = arcpy.Parameter(
            displayName = "District Type",
            name = "DistrictType",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_sd_type.filter.type = "ValueList"
        param_sd_type.filter.list = ['Unified', 'Elementary', 'Secondary']
        param_sd_type.enabled = False

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())
        param_states.enabled = False

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_geom_type,
            param_resolution,
            param_sd_type,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_sd_type = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_sd_type = param_sd_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography 
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(enumeration_units, geo_mod).years
        
        # determine geo_type by geography and years
        geom_type_filtered = False
        if req_geography == "Block":
            geom_type_filtered = True
            param_geom_type.filter.list = ["TIGER"]
            param_geom_type.value = "TIGER"
        elif req_geography:
            if req_year:
                if req_year in getattr(enumeration_units, geo_mod).cb_years and req_year in getattr(enumeration_units, geo_mod).tg_years:
                    geom_type_filtered = True
                    param_geom_type.filter.list = ["TIGER", "Cartographic"]
                elif req_year in getattr(enumeration_units, geo_mod).cb_years:
                    geom_type_filtered = True
                    param_geom_type.filter.list = ["Cartographic"]
                    param_geom_type.value = "Cartographic"
                elif req_year in getattr(enumeration_units, geo_mod).tg_years:
                    geom_type_filtered = True
                    param_geom_type.filter.list = ["TIGER"]
                    param_geom_type.value = "TIGER"
        if not geom_type_filtered:
            param_geom_type.filter.list = []
            param_geom_type.value = None

        # resolution visibility
        resolution_needed = False
        req_year_int = int(req_year) if req_year else req_year
        if req_geom_type == "Cartographic" and req_year:
            if req_geography == "State":
                if req_year_int >= 2010:
                    resolution_needed = True
                    param_resolution.filter.list = ["500k", "5m", "20m"]
            elif req_geography == "County":
                if req_year_int >= 2010:
                    resolution_needed = True
                    param_resolution.filter.list = ["500k", "5m", "20m"]
            elif req_geography == "Tract":
                if req_year_int >= 2022 and req_states is None:
                    resolution_needed = True
                    param_resolution.filter.list = ["500k", "5m"]
        if resolution_needed:
            param_resolution.enabled = True
        else:
            param_resolution.enabled = False
            param_resolution.value = None

        # school district type visibility
        if req_geography == "School District":
            param_sd_type.enabled = True
        else:
            param_sd_type.enabled = False
            param_sd_type.value = None

        # state visibility
        by_state = True
        if req_geography is None or req_year is None:
            by_state = False
        elif req_geography == "ZCTA":
            if req_year_int not in [2000, 2010]:
                by_state = False
            elif req_year_int == 2010 and req_geom_type == "Cartographic":
                by_state = False
        if by_state:
            param_states.enabled = True
        else:
            param_states.enabled = False
            param_states.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_sd_type = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_sd_type = param_sd_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        req_year_int = int(req_year) if req_year else req_year
        if req_geom_type == "Cartographic" and req_year:
            if req_geography == "State":
                if req_year_int >= 2010:
                    arcpy_helpers.set_parameterRequired(param_resolution)
            elif req_geography == "County":
                if req_year_int >= 2010:
                    arcpy_helpers.set_parameterRequired(param_resolution)
            elif req_geography == "Tract":
                if req_year_int >= 2022 and req_states is None:
                    arcpy_helpers.set_parameterRequired(param_resolution)
        
        if req_geography == "School District":
            arcpy_helpers.set_parameterRequired(param_sd_type)

        if req_geography == "Tract":
            if req_year and not (req_year_int >= 2019 and req_geom_type == "Cartographic"):
                arcpy_helpers.set_parameterRequired(param_states)
        elif req_geography == "Block Group":
            if req_year and not (req_year_int >= 2019 and req_geom_type == "Cartographic"):
                arcpy_helpers.set_parameterRequired(param_states)
        elif req_geography == "Block":
            arcpy_helpers.set_parameterRequired(param_states)
        elif req_geography == "County Subdivision":
            arcpy_helpers.set_parameterRequired(param_states)
        
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_sd_type = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_sd_type = param_sd_type.valueAsText
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(enumeration_units, geo_mod).download(
            geom_type = req_geom_type,
            resolution = req_resolution,
            year = req_year,
            states = req_states,
            sd_type = req_sd_type,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return


class TribalNativeAreas:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tribal/Native Areas"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Tribal Tract", "Tribal Block Group", "Native Area", "Tribal Subdivision", "Alaska Native Regional Corporation"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_geom_type = arcpy.Parameter(
            displayName = "Geometry Type",
            name = "GeometryType",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param_geom_type.filter.type = "ValueList"

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_geom_type,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography 
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(tribal_native_areas, geo_mod).years
        
        # determine geo_type by geography and years
        geom_type_filtered = False
        if req_geography:
            if req_year in getattr(legislative_areas, geo_mod).cb_years and req_year in getattr(legislative_areas, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER", "Cartographic"]
            elif req_year in getattr(legislative_areas, geo_mod).cb_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["Cartographic"]
                param_geom_type.value = "Cartographic"
            elif req_year in getattr(legislative_areas, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER"]
                param_geom_type.value = "TIGER"
        if not geom_type_filtered:
            param_geom_type.filter.list = []
            param_geom_type.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_out_feature = param_out_feature.valueAsText
        
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(tribal_native_areas, geo_mod).download(
            geom_type = req_geom_type,
            year = req_year,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return

class LegislativeAreas:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Legislative Areas"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Congressional District", "State Legislative District", "Voting District"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_geom_type = arcpy.Parameter(
            displayName = "Geometry Type",
            name = "GeometryType",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param_geom_type.filter.type = "ValueList"

        param_resolution = arcpy.Parameter(
            displayName = "Resolution",
            name = "Resolution",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_resolution.filter.type = "ValueList"
        param_resolution.filter.list = ["500k", "5m", "20m"]
        param_resolution.enabled = False

        param_house = arcpy.Parameter(
            displayName = "House",
            name = "House",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_house.filter.type = "ValueList"
        param_house.filter.list = ["Lower", "Upper"]

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_geom_type,
            param_resolution,
            param_house,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_house = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_house = param_house.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(legislative_areas, geo_mod).years
        
        # determine geo_type by geography and years
        geom_type_filtered = False
        if req_geography:
            if req_year in getattr(legislative_areas, geo_mod).cb_years and req_year in getattr(legislative_areas, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER", "Cartographic"]
            elif req_year in getattr(legislative_areas, geo_mod).cb_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["Cartographic"]
                param_geom_type.value = "Cartographic"
            elif req_year in getattr(legislative_areas, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER"]
                param_geom_type.value = "TIGER"
        if not geom_type_filtered:
            param_geom_type.filter.list = []
            param_geom_type.value = None

        # resolution visibility
        resolution_needed = False
        if req_geom_type == "Cartographic":
            if req_geography == "Congressional District":
                resolution_needed = True
                param_resolution.filter.list = ["500k", "5m", "20m"]
        if resolution_needed:
            param_resolution.enabled = True
        else:
            param_resolution.enabled = False
            param_resolution.value = None

        # house visibility
        if req_geography == "State Legislative District":
            param_house.enabled = True
        else:
            param_house.enabled = False
            param_house.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_house = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_house = param_house.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        if req_geom_type == "Cartographic":
            if req_geography == "Congressional District":
                arcpy_helpers.set_parameterRequired(req_resolution)
        
        if req_geography == "State Legislative District":
            arcpy_helpers.set_parameterRequired(req_house)

        req_year_int = int(req_year) if req_year else req_year
        if req_geography == "Congressional District" and req_year:
            if req_geom_type == "TIGER" and req_year_int >= 2023:
                arcpy_helpers.set_parameterRequired(param_states)
        elif req_geography == "State Legislative District":
            if not (req_geom_type == "Cartographic" and req_year_int >= 2019):
                arcpy_helpers.set_parameterRequired(param_states)
        elif req_geography == "Voting District":
            if not (req_geom_type == "Cartographic" and req_year_int == 2020):
                arcpy_helpers.set_parameterRequired(param_states)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_house = parameters[3]
        param_states = parameters[4]
        param_out_feature = parameters[5]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_house = param_house.valueAsText
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        if req_house == "Lower":
            if not req_states:
                messages.AddWarningMessage("Nebraska has a unicameral legislature. No lower house exists.")
            else:
                if "Nebraska" in req_states:
                    messages.AddWarningMessage("Nebraska has a unicameral legislature. Requested upper house.")

        getattr(legislative_areas, geo_mod).download(
            geom_type = req_geom_type,
            resolution = req_resolution,
            year = req_year,
            house = req_house,
            states = req_states,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return

class MetroAreasPlaces:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Metro Areas/Places"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Core Based Statistical Area", "Combined Statistical Area", "Place", "Urban Area", "Metro Division", "New England"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_geom_type = arcpy.Parameter(
            displayName = "Geometry Type",
            name = "GeometryType",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param_geom_type.filter.type = "ValueList"

        param_resolution = arcpy.Parameter(
            displayName = "Resolution",
            name = "Resolution",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_resolution.filter.type = "ValueList"
        param_resolution.filter.list = ["500k", "5m", "20m"]
        param_resolution.enabled = False

        param_ua_criteria = arcpy.Parameter(
            displayName = "Urban Area Criteria",
            name = "UrbanAreaCriteria",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_ua_criteria.filter.type = "ValueList"
        param_ua_criteria.enabled = False

        param_necta_type = arcpy.Parameter(
            displayName = "New England City and Town Areas Type",
            name = "NewEnglandCityandTownAreasType",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_necta_type.filter.type = "ValueList"
        param_necta_type.filter.list = ["2010", "2020"]
        param_necta_type.enabled = False

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_geom_type,
            param_resolution,
            param_ua_criteria,
            param_necta_type,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_ua_criteria = parameters[3]
        param_necta_type = parameters[4]
        param_states = parameters[5]
        param_out_feature = parameters[6]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_ua_criteria = param_ua_criteria.valueAsText
        req_necta_type = param_necta_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(metro_areas_places, geo_mod).years
        
        # determine geo_type by geography and years
        geom_type_filtered = False
        if req_geography == "Metro Division":
            geom_type_filtered = True
            param_geom_type.filter.list = ["TIGER"]
            param_geom_type.value = "TIGER"
        elif req_geography:
            if req_year in getattr(metro_areas_places, geo_mod).cb_years and req_year in getattr(metro_areas_places, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER", "Cartographic"]
            elif req_year in getattr(metro_areas_places, geo_mod).cb_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["Cartographic"]
                param_geom_type.value = "Cartographic"
            elif req_year in getattr(metro_areas_places, geo_mod).tg_years:
                geom_type_filtered = True
                param_geom_type.filter.list = ["TIGER"]
                param_geom_type.value = "TIGER"
        if not geom_type_filtered:
            param_geom_type.filter.list = []
            param_geom_type.value = None

        # ua_criteria visibility
        if req_geography == "Urban Area":
            param_ua_criteria.enabled = True
        else:
            param_ua_criteria.enabled = False
            param_ua_criteria.value = None
        
        # determine ua_criteria by geography and years
        ua_criteria_filtered = False
        req_year_int = int(req_year) if req_year else req_year
        if req_geography == "Urban Area" and req_year:
            if req_geom_type == "Cartographic":
                if req_year_int == 2020:
                    ua_criteria_filtered = True
                    param_ua_criteria.filter.list = ["2020"]
                    param_ua_criteria.value = "2020"
                elif req_year_int >= 2013 and req_year_int <= 2019:
                    ua_criteria_filtered = True
                    param_ua_criteria.filter.list = ["2010"]
                    param_ua_criteria.value = "2010"
            elif req_geom_type == "TIGER":
                if req_year_int >= 2023:
                    ua_criteria_filtered = True
                    param_ua_criteria.filter.list = ["2020"]
                    param_ua_criteria.value = "2020"
                elif req_year_int in [2020, 2022]:
                    ua_criteria_filtered = True
                    param_ua_criteria.filter.list = ["2010", "2020"]
                elif req_year_int >= 2012:
                    ua_criteria_filtered = True
                    param_ua_criteria.filter.list = ["2010"]
                    param_ua_criteria.value = "2010"
        if not ua_criteria_filtered:
            param_ua_criteria.filter.list = []
            param_ua_criteria.value = None
        
        # determine necta_type by geography and years
        necta_type_filtered = False
        req_year_int = int(req_year) if req_year else req_year
        if req_geography == "New England" and req_year:
            if req_geom_type == "Cartographic":
                necta_type_filtered = True
                param_necta_type.filter.list = ["NECTA"]
                param_necta_type.value = "NECTA"
            elif req_geom_type == "TIGER":
                necta_type_filtered = True
                param_necta_type.filter.list = ["NECTA", "Combined NECTA", "NECTA Division"]
        if not necta_type_filtered:
            param_necta_type.filter.list = []
            param_necta_type.value = None
        
        # necta visibility
        if req_geography == "New England":
            param_necta_type.enabled = True
        else:
            param_necta_type.enabled = False
            param_necta_type.value = None

        # resolution visibility
        resolution_needed = False
        if req_geom_type == "Cartographic":
            if req_geography == "Core Based Statistical Area":
                resolution_needed = True
                param_resolution.filter.list = ["500k", "5m", "20m"]
            elif req_geography == "Combined Statistical Area":
                resolution_needed = True
                param_resolution.filter.list = ["500k", "5m", "20m"]
            elif req_year and req_year_int >= 2021 and req_geography == "New England":
                resolution_needed = True
                param_resolution.filter.list = ["500k", "5m", "20m"]
        if resolution_needed:
            param_resolution.enabled = True
        else:
            param_resolution.enabled = False
            param_resolution.value = None

        # state visibility
        if req_geography == "Place":
            param_states.enabled = True
        else:
            param_states.enabled = False
            param_states.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_ua_criteria = parameters[3]
        param_necta_type = parameters[4]
        param_states = parameters[5]
        param_out_feature = parameters[6]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_ua_criteria = param_ua_criteria.valueAsText
        req_necta_type = param_necta_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        req_year_int = int(req_year) if req_year else req_year
        if req_geom_type == "Cartographic":
            if req_geography == "Core Based Statistical Area":
                arcpy_helpers.set_parameterRequired(param_resolution)
            elif req_geography == "Combined Statistical Area":
                arcpy_helpers.set_parameterRequired(param_resolution)
            elif req_year and req_year_int >= 2021 and req_geography == "New England":
                arcpy_helpers.set_parameterRequired(param_resolution)

        if req_geography == "Urban Area":
            arcpy_helpers.set_parameterRequired(param_ua_criteria)

        if req_geography == "New England":
            arcpy_helpers.set_parameterRequired(param_necta_type)

        if req_geography == "Place":
            if req_year and not (req_year_int >= 2019 and req_geom_type == "Cartographic"):
                arcpy_helpers.set_parameterRequired(param_states)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_resolution = parameters[2]
        param_ua_criteria = parameters[3]
        param_necta_type = parameters[4]
        param_states = parameters[5]
        param_out_feature = parameters[6]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_resolution = param_resolution.valueAsText
        req_ua_criteria = param_ua_criteria.valueAsText
        req_necta_type = param_necta_type.valueAsText
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(metro_areas_places, geo_mod).download(
            geom_type = req_geom_type,
            resolution = req_resolution,
            year = req_year,
            ua_criteria = req_ua_criteria,
            necta_type = req_necta_type,
            states = req_states,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return

class Nation:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Nation"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Nation", "Region", "Division"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_resolution = arcpy.Parameter(
            displayName = "Resolution",
            name = "Resolution",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param_resolution.filter.type = "ValueList"

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_resolution,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_resolution = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_resolution = param_resolution.valueAsText
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography 
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(nation, geo_mod).years
        
        # determine resolution by geography
        if req_geography == "Nation":
            param_resolution.filter.list = ["5m", "20m"]
        elif req_geography == "Region":
            param_resolution.filter.list = ["500k", "5m", "20m"]
        elif req_geography == "Division":
            param_resolution.filter.list = ["500k", "5m", "20m"]
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_resolution = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_resolution = param_resolution.valueAsText
        req_out_feature = param_out_feature.valueAsText
        
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_resolution = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_resolution = param_resolution.valueAsText
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(nation, geo_mod).download(
            year = req_year,
            resolution = req_resolution,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return

class Landmarks:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Landmarks"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Landmark", "Military Installation"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_geom_type = arcpy.Parameter(
            displayName = "Geometry Type",
            name = "GeometryType",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param_geom_type.filter.type = "ValueList"
        param_geom_type.filter.list = ["Point", "Area"]
        param_geom_type.enabled = False

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_geom_type,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_states = parameters[2]
        param_out_feature = parameters[3]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(landmarks, geo_mod).years

        # geom_type visibility
        if req_geography == "Landmark":
            param_geom_type.enabled = True
        else:
            param_geom_type.enabled = False
            param_geom_type.value = None

        # state visibility
        if req_geography == "Landmark":
            param_states.enabled = True
        else:
            param_states.enabled = False
            param_states.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_states = parameters[2]
        param_out_feature = parameters[3]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        if req_geography == "Landmark":
            arcpy_helpers.set_parameterRequired(param_geom_type)

        if req_geography == "Landmark":
            arcpy_helpers.set_parameterRequired(param_states)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_geom_type = parameters[1]
        param_states = parameters[2]
        param_out_feature = parameters[3]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_geom_type = param_geom_type.valueAsText
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(landmarks, geo_mod).download(
            geom_type = req_geom_type,
            year = req_year,
            states = req_states,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return
    
class Transportation:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Transportation"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Road", "Primary Road", "Primary Secondary Road", "Rail", "Address Range"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(transportation, geo_mod).years

        # state visibility
        if req_geography == "Road":
            param_states.enabled = True
        elif req_geography == "Primary Secondary Road":
            param_states.enabled = True
        elif req_geography == "Address Range":
            param_states.enabled = True
        else:
            param_states.enabled = False
            param_states.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        if req_geography == "Road":
            arcpy_helpers.set_parameterRequired(param_states)
        if req_geography == "Primary Secondary Road":
            arcpy_helpers.set_parameterRequired(param_states)
        if req_geography == "Address Range":
            arcpy_helpers.set_parameterRequired(param_states)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(transportation, geo_mod).download(
            year = req_year,
            states = req_states,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return
    
class Water:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Water"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_req = arcpy.Parameter(
            displayName = "Request Parameters",
            name = "InputTableFields",
            datatype = "GPValueTable",
            parameterType = "Required",
            direction = "Input"
        )
        param_req.columns = [['String', 'Geography'], ['String', 'Year']]
        param_req.filters[0].type = "ValueList"
        param_req.filters[0].list = ["Area Water", "Linear Water", "Coastline"]
        param_req.filters[1].type = "ValueList"
        param_req.controlCLSID = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

        param_states = arcpy.Parameter(
            displayName = "States",
            name = "States",
            datatype = "GPValueTable",
            parameterType = "Optional",
            direction = "Input"
        )
        param_states.columns = [['String', 'States']]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(fips.state_to_fips.keys())

        param_out_feature = arcpy.Parameter(
            displayName="Output Feature",
            name="OutputFeature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )

        params = [
            param_req,
            param_states,
            param_out_feature
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        # determine years by geography
        if req_geography:
            geo_mod = req_geography.lower().replace(" ", "_")
            param_req.filters[1].list = getattr(water, geo_mod).years

        # state visibility
        if req_geography == "Area Water":
            param_states.enabled = True
        elif req_geography == "Linear Water":
            param_states.enabled = True
        else:
            param_states.enabled = False
            param_states.value = None
        
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        req_out_feature = param_out_feature.valueAsText

        if req_geography == "Area Water":
            arcpy_helpers.set_parameterRequired(param_states)
        if req_geography == "Linear Water":
            arcpy_helpers.set_parameterRequired(param_states)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_req = parameters[0]
        param_states = parameters[1]
        param_out_feature = parameters[2]

        req_vals = arcpy_helpers.get_valueTableValues(param_req)[0]
        req_geography = req_vals[0]
        req_year = req_vals[1]
        req_states = param_states.values
        if req_states:
            req_states = [state[0] for state in param_states.values]
        req_out_feature = param_out_feature.valueAsText

        geo_mod = req_geography.lower().replace(" ", "_")

        getattr(water, geo_mod).download(
            year = req_year,
            states = req_states,
            output_path = req_out_feature
        )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return