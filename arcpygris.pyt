# -*- coding: utf-8 -*-

import arcpy
import asyncio
import re
import tigerweb


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "arcpygris"
        self.alias = "arcpygris"

        self.tools = [EnumerationUnits, CBSAs, Schools, AIANNHA]


class ArcpygrisTool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Arcpygris Tool"
        self.description = ""

        self.geography_list = []

    def getParameterInfo(self):
        """Define the tool parameters."""

        param_geography = arcpy.Parameter(
            displayName="Geography",
            name="Geography",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        param_geography.filter.type = "ValueList"
        param_geography.filter.list = self.geography_list

        param_type = arcpy.Parameter(
            displayName="Boundary Type",
            name="BoundaryType",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        param_type.filter.type = "ValueList"
        param_type.filter.list = ["TIGER/Line", "Cartographic"]

        param_year = arcpy.Parameter(
            displayName="Year",
            name="Year",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        param_year.filter.type = "ValueList"
        param_year.enabled = False

        param_resolution = arcpy.Parameter(
            displayName="Resolution",
            name="Resolution",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
        )
        param_resolution.filter.type = "ValueList"
        param_resolution.enabled = False

        param_states = arcpy.Parameter(
            displayName="States",
            name="States",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input",
        )
        param_states.columns = [["String", "States"]]
        param_states.filters[0].type = "ValueList"
        param_states.filters[0].list = list(tigerweb.state_to_fips.keys())
        param_states.enabled = False

        params = [
            param_geography,
            param_type,
            param_year,
            param_resolution,
            param_states,
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        param_geography = parameters[0]
        param_type = parameters[1]
        param_year = parameters[2]
        param_resolution = parameters[3]
        param_states = parameters[4]

        req_geography = param_geography.valueAsText
        req_type = param_type.valueAsText
        req_cb = param_type.valueAsText == "Cartographic"
        req_year = param_year.valueAsText

        if (
            req_geography in param_geography.filter.list
            and req_type in param_type.filter.list
        ):
            if req_cb and req_geography not in tigerweb.cb_server_dict.keys():
                param_year.filter.list = []
                param_year.enabled = False
            else:
                server_layers = asyncio.run(
                    tigerweb.available_year_services(req_geography, req_cb)
                )

                map_servers = list(server_layers.keys())
                years = [re.search(r".*(\d{4})", s).group(1) for s in map_servers]
                years.sort(reverse=True)
                param_year.filter.list = years
                param_year.enabled = True

            if req_cb and req_year in param_year.filter.list:
                param_resolution.enabled = True
                map_server = map_servers[years.index(req_year)]
                map_server_layers = server_layers[map_server]

                param_resolution.filter.list = [
                    layer_name.rsplit(" ", 1)[1]
                    for layer_name in map_server_layers.keys()
                ]
            else:
                param_resolution.enabled = False

            if req_geography in tigerweb.is_state_subsettable:
                param_states.enabled = True
            else:
                param_states.enabled = False
        else:
            param_year.enabled = False
            param_resolution.enabled = False
            param_states.enabled = False

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""

        param_geography = parameters[0]
        param_type = parameters[1]

        req_geography = param_geography.valueAsText
        req_type = param_type.valueAsText
        req_cb = param_type.valueAsText == "Cartographic"

        if (
            req_geography in param_geography.filter.list
            and req_type in param_type.filter.list
        ):
            if req_cb and req_geography not in tigerweb.cb_server_dict.keys():
                param_type.setErrorMessage(
                    f"{req_geography} cartographic boundaries are not available."
                )

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param_geography = parameters[0]
        param_type = parameters[1]
        param_year = parameters[2]
        param_resolution = parameters[3]
        param_states = parameters[4]

        req_geography = param_geography.valueAsText
        req_type = param_type.valueAsText
        req_cb = req_type == "Cartographic"
        req_year = param_year.valueAsText
        req_resolution = param_resolution.valueAsText
        req_states = param_states.values

        server_layers = asyncio.run(
            tigerweb.available_year_services(req_geography, req_cb)
        )

        map_servers = list(server_layers.keys())
        years = [re.search(r".*(\d{4})", s).group(1) for s in map_servers]
        map_server = map_servers[years.index(req_year)]
        map_server_layers = server_layers[map_server]

        layer_name = f"{req_geography} {req_resolution}" if req_cb else req_geography
        layer_id = map_server_layers[layer_name]

        arc_project = arcpy.mp.ArcGISProject("Current")
        cur_map = arc_project.activeMap

        new_layer = cur_map.addDataFromPath(
            f"{tigerweb.base_url}{map_server}/MapServer/{layer_id}"
        )
        new_layer.minThreshold = 0
        new_layer.maxThreshold = 0

        if req_states:
            fips = [f"'{tigerweb.state_to_fips[state[0]]}'" for state in req_states]
            new_layer.definitionQuery = f"STATE IN ({', '.join(fips)})"

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""

        return


class EnumerationUnits(ArcpygrisTool):
    def __init__(self):
        super().__init__()
        self.label = "Enumeration Units"
        self.geography_list = [
            "Census Divisions",
            "Census Regions",
            "States",
            "Counties",
            "Census Tracts",
            "Census Block Groups",
            "Census Blocks",
            "Zip Code Tabulation Areas",
        ]


class CBSAs(ArcpygrisTool):
    def __init__(self):
        super().__init__()
        self.label = "Core-Based Statistical Areas"
        self.geography_list = [
            "Metropolitan New England City and Town Areas",
            "Micropolitan New England City and Town Areas",
            "Combined Statistical Areas",
            "Metropolitan Statistical Areas",
            "Micropolitan Statistical Areas",
        ]


class Schools(ArcpygrisTool):
    def __init__(self):
        super().__init__()
        self.label = "Schools"
        self.geography_list = [
            "Unified School Districts",
            "Secondary School Districts",
            "Elementary School Districts",
        ]


class Places(ArcpygrisTool):
    def __init__(self):
        super().__init__()
        self.label = "Places"
        self.geography_list = [
            "Subbarrios",
            "Consolidated Cities",
            "Incorporated Places",
            "Census Designated Places",
        ]


class AIANNHA(ArcpygrisTool):
    def __init__(self):
        super().__init__()
        self.label = "American Indian, Alaska Native, and Native Hawaiian Areas"
        self.geography_list = [
            "Tribal Census Tracts",
            "Tribal Block Groups",
            "Tribal Subdivisions",
            "Tribal Designated Statistical Areas",
            "State Designated Tribal Statistical Areas",
            "Oklahoma Tribal Statistical Areas",
            "Federal American Indian Reservations",
            "State American Indian Reservations",
            "American Indian Joint-Use Areas ",
            "Off-Reservation Trust Lands",
            "Alaska Native Regional Corporations",
            "Alaska Native Village Statistical Areas",
            "Hawaiian Home Lands",
        ]
