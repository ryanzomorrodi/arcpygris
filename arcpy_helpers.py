import arcpy
from datetime import datetime

def get_valueTableValues(valueTable):
    if valueTable.values is not None:
        return [[str(value) for value in field] for field in valueTable.values]
    else:
        return [[None for i, col in enumerate(valueTable.columns)]]

def set_parameterRequired(parameter):
    if parameter.value is None:
        parameter.setIDMessage('ERROR', 530)
        

def write_feature(input_path: str, output_path: str, where_exp: str = None):
    if where_exp:
        arcpy.conversion.ExportFeatures(input_path, output_path, where_exp)
    else:
        arcpy.conversion.ExportFeatures(input_path, output_path)

def merge_features(input_paths: list[str], output_path: str):
    arcpy.management.Merge(input_paths, output_path)
    
def add_metadata(
    output_path: str, geography: str, year: str, req_urls: list[str], 
    geom_type: str = None, resolution: str = None, house: str = None, 
    sd_type: str = None, ua_criteria: str = None, necta_type: str = None, 
    states: list[str] = None
):
    if geom_type:
        title = f"{year} {geom_type} {geography} Boundary"
    else:
        title = f"{year} {geography} Boundary"
    summary = f"This layer contains the {title} file downloaded from the US Census Bureau via the arcpygris toolbox."

    created_date = f"Created on: {datetime.now()}"

    query_params = "\n\nQuery Parameters:"
    query_params += f"\n\tGeography: {geography}"
    query_params += f"\n\tYear: {year}"
    if geom_type:
        query_params += f"\n\tGeometry Type: {geom_type}"
    if resolution:
        query_params += f"\n\tResolution: {resolution}"
    if house:
        query_params += f"\n\tHouse: {house}"
    if sd_type:
        query_params += f"\n\tDistrict Type: {sd_type}"
    if ua_criteria:
        query_params += f"\n\tUrban Area Criteria: {ua_criteria}"
    if necta_type:
        query_params += f"\n\tNew England City and Town Areas Type: {necta_type}"
    if states:
        query_params += f"\n\tStates: {';'.join(states)}"

    sources = "\n\nSource(s):"
    for shape_file_path in req_urls:
        sources += "\n\t" + shape_file_path

    
    
    new_md = arcpy.metadata.Metadata()
    new_md.title = title
    new_md.summary = summary
    new_md.description = created_date + query_params + sources

    tgt_item_md = arcpy.metadata.Metadata(output_path)
    if not tgt_item_md.isReadOnly:
        tgt_item_md.copy(new_md)
        tgt_item_md.save()
