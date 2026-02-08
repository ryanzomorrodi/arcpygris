# arcpygris

`arcpygris` is an ArcGIS Pro python toolbox that allows users to directly download TIGER/Line or cartographic boundaries from the US Census Bureau into an ArcGIS Pro project.

Inspired by the [`tigris`](https://github.com/walkerke/tigris) R package and [`pygris`](https://github.com/walkerke/pygris) Python package, `arcpygris` aims to make the process of working with Census geographies within ArcGIS Pro more seamless. Layers are added straight from the Census TIGERweb servers.


![](preview.png)

## Currently Supported Geographies

Since `arcpygris` relies on the Census TIGERweb servers, new years of Census geographies will be added as soon as they uploaded to TIGERweb. These are the current available years as of Feb 8th 2026.

| Geographic Area                              | Group                                                     | Available Years            |
|:---------------------------------------------|:----------------------------------------------------------|:---------------------------|
| Census Divisions                             | Enumeration Units                                         | 2000, 2010, 2012-2025      |
| Census Regions                               | Enumeration Units                                         | 2000, 2010, 2012-2025      |
| States                                       | Enumeration Units                                         | 2000, 2010, 2012-2025      |
| Counties                                     | Enumeration Units                                         | 2000, 2010, 2012-2025      |
| Census Tracts                                | Enumeration Units                                         | 2000, 2010, 2012-2025      |
| Zip Code Tabulation Areas                    | Enumeration Units                                         | 2000, 2010, 2020           |
| Metropolitan New England City and Town Areas | Core-Based Statistical Areas                              | 2010, 2012-2021            |
| Micropolitan New England City and Town Areas | Core-Based Statistical Areas                              | 2010, 2012-2021            |
| Combined Statistical Areas                   | Core-Based Statistical Areas                              | 2010, 2012-2021, 2023-2025 |
| Metropolitan Statistical Areas               | Core-Based Statistical Areas                              | 2010, 2012-2021, 2023-2025 |
| Micropolitan Statistical Areas               | Core-Based Statistical Areas                              | 2010, 2012-2021, 2023-2025 |
| Unified School Districts                     | Schools                                                   | 2000, 2010, 2012-2025      |
| Secondary School Districts                   | Schools                                                   | 2000, 2010, 2012-2025      |
| Elementary School Districts                  | Schools                                                   | 2000, 2010, 2012-2025      |
| Subbarrios                                   | Places                                                    | 2000, 2010, 2012-2025      |
| Consolidated Cities                          | Places                                                    | 2000, 2010, 2012-2025      |
| Incorporated Places                          | Places                                                    | 2000, 2010, 2012-2025      |
| Census Designated Places                     | Places                                                    | 2000, 2010, 2012-2025      |
| Tribal Census Tracts                         | American Indian, Alaska Native, and Native Hawaiian Areas | 2010, 2012-2025            |
| Tribal Block Groups                          | American Indian, Alaska Native, and Native Hawaiian Areas | 2010, 2012-2025            |
| Tribal Subdivisions                          | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Tribal Designated Statistical Areas          | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| State Designated Tribal Statistical Areas    | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Oklahoma Tribal Statistical Areas            | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Federal American Indian Reservations         | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| State American Indian Reservations           | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| American Indian Joint-Use Areas              | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Off-Reservation Trust Lands                  | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Alaska Native Regional Corporations          | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Alaska Native Village Statistical Areas      | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
| Hawaiian Home Lands                          | American Indian, Alaska Native, and Native Hawaiian Areas | 2000, 2010, 2012-2025      |
