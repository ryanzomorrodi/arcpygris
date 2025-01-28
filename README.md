# arcpygris

`arcpygris` is an ArcGIS Pro python toolbox that allows users to directly download TIGER/Line or cartographic boundaries from the US Census Bureau into an ArcGIS Pro project.

Designed as a port of the [`tigris`](https://github.com/walkerke/tigris) R package and [`pygris`](https://github.com/walkerke/pygris) Python package for ArcGIS Pro, `arcpygris` aims to make the process of working with Census geographies within ArcGIS Pro more seamless. Layers downloaded into a geodatabase are also attached with metadata detailing the layer's provenance and query parameters used to generate it, thereby improving the reproducibility of the project.

| Tool                | Geography                          | Boundaries available                           | Years available       |
|------------------|------------------|-------------------|------------------|
| Nation              | Nation                             | cartographic (1:5m; 1:20m)                     | 2013-2023             |
| Nation              | Division                           | cartographic (1:500k; 1:5m; 1:20m)             | 2013-2023             |
| Nation              | Region                             | cartographic (1:500k; 1:5m; 1:20m)             | 2013-2023             |
| Enumeration Units   | States                             | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 1990, 2000, 2010-2024 |
| Enumeration Units   | Counties                           | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 1990, 2000, 2010-2024 |
| Enumeration Units   | Tracts                             | TIGER/Line; cartographic (1:500k)              | 1990, 2000, 2010-2024 |
| Enumeration Units   | Block Groups                       | TIGER/Line; cartographic (1:500k)              | 1990, 2000, 2010-2024 |
| Enumeration Units   | Blocks                             | TIGER/Line                                     | 2000, 2010-2024       |
| Enumeration Units   | ZCTA                               | TIGER/Line; cartographic (1:500k)              | 2000, 2010, 2012-2024 |
| Enumeration Units   | County Subdivision                 | TIGER/Line; cartographic (1:500k)              | 2010-2024             |
| Enumeration Units   | School District                    | TIGER/Line; cartographic                       | 2011-2024             |
| Legislative         | Congressional District             | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 2010-2024             |
| Legislative         | State Legislative District         | TIGER/Line; cartographic (1:500k)              | 2010-2024             |
| Legislative         | Voting District                    | TIGER/Line                                     | 2012, 2020            |
| Metro Area/Places   | Core Based Statistical Area        | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 2011-2021, 2023-2024  |
| Metro Area/Places   | Combined Statistical Area          | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 2010-2024             |
| Metro Area/Places   | Place                              | TIGER/Line; cartographic (1:500k)              | 2011-2024             |
| Metro Area/Places   | Urban Area                         | TIGER/Line; cartographic (1:500k)              | 2012-2024             |
| Metro Area/Places   | Metro Division                     | TIGER/Line                                     | 2011-2024             |
| Metro Area/Places   | New England                        | TIGER/Line; cartographic (1:500k; 1:5m; 1:20m) | 2010-2021             |
| Tribal/Native Areas | Tribal Tract                       | TIGER/Line                                     | 2011-2024             |
| Tribal/Native Areas | Tribal Block Group                 | TIGER/Line                                     | 2011-2024             |
| Tribal/Native Areas | Native Area                        | TIGER/Line; cartographic (1:500k)              | 2011-2024             |
| Tribal/Native Areas | Tribal Subdivision                 | TIGER/Line                                     | 2011-2024             |
| Tribal/Native Areas | Alaska Native Regional Corporation | TIGER/Line; cartographic (1:500k)              | 2011-2024             |
| Transportation      | Road                               | TIGER/Line                                     | 2011-2024             |
| Transportation      | Primary Road                       | TIGER/Line                                     | 2011-2024             |
| Transportation      | Primary Secondary Road             | TIGER/Line                                     | 2011-2024             |
| Transportation      | Rail                               | TIGER/Line                                     | 2011-2024             |
| Transportation      | Address Range                      | TIGER/Line                                     | 2011-2024             |
| Water               | Area Water                         | TIGER/Line                                     | 2011-2024             |
| Water               | Linear Water                       | TIGER/Line                                     | 2011-2024             |
| Water               | Coastline                          | TIGER/Line                                     | 2011-2024             |
| Landmarks           | Landmark                           | TIGER/Line                                     | 2012-2024             |
| Landmarks           | Military Installation              | TIGER/Line                                     | 2010-2024             |