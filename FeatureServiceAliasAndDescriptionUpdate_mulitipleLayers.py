# Name: Alias Updater
# Created by: Lisa Berry, Esri
# Created: December 2018
#
# This script uses a lookup table to update alias names on a hosted feature service.
# The script updates the alias names in two places:
#   - The REST endpoint
#   - The layer's pop-up JSON via fieldInfos
#   - *If the layer was saved in the new Map Viewer in ArcGIS Online, updates the additional popupElement fieldInfos
# The pop-up configuration will not be altered with this implementation
# The script also allows you to update the long description, field type, and pop-up decimals/thousand separator for any field
#
# The script will use the input excel document and update any fields it finds that matches from the excel document.
# This script allows for multiple REST layers to be updated. Specify the REST layer count in the inputs.
# You must have ArcGIS Pro installed on your computer in order to run this script.
#
# Python version: 3.7 - Make sure your interpreter is calling to the arcgispro-py3 python.exe
# Updated: April 2020 - all http calls removed and replaced with python API calls
# Updated: July 2022 - Converted XLRD to OPENPYXL to read in excel file. XLRD no longer supports .xlsx files.
# Updated: August 2022 - can also update decimals for popup JSON.
#          Also updates popupElement in JSON if saved in new Map Viewer

# Comments about inputs:_________________________________________________________________________________________
# username and password are your ArcGIS Online or ArcGIS Enterprise credentials
#
# layerID is the ID to a hosted feature service. You must own the service to run this script.
#
# restLayerCount is the count of layers in the service. All layers will use
#               the same field/alias lookup, but only matching fields will be updated.
#
# lookupTable must be an excel document (.xlsx) with a header row. 
#   The first column should be the field names
#   The second column should be the intended alias names for each field.
#   *optional* The third column should be the intended description for each field.
#   *optional* The fourth column can include the field type. This must be formatted
#           to match the backend JSON. 
#           Ex:  nameOrTitle, description, typeOrCategory, countOrAmount, percentageOrRatio
#               measurement, currency, uniqueIdentifier, phoneNumber, emailAddress,
#               orderedOrRanked, binary, locationOrPlaceName, coordinate, dateAndTime
#   *optional* The fifth column can include a specification for how many decimals you want for each field
#               to have in the pop-up.
#   *optional* The sixth column can include a specification for if a numeric attribute should have a thousands comma
#                separator. Only specify this if it is a numeric field.
#               Ex: can use "true" or "yes" to specify. You can leave this column blank for any fields that are string
#                   or don't need a comma. You can also specify those as "no" or "false".
#
# If your script is having issues, make sure you at least have these 5 headers in the excel document,
# even if no values appear in the rows. This can cause the script to fail sometimes. Also make sure your excel file is empty

# portalName can be left as-is if you are working in ArcGIS Online. Change to your portal URL otherwise.

# Inputs:_______________________________________________________________________________________________________
username = "username"
password = "password"
layerID = "itemID"
restLayerCount = 1
lookupTable = r"C:\pathName\ExcelDocName.xlsx"
portalName = "https://www.arcgis.com"

# MAIN SCRIPT___________________________________________________________________________________________________

from arcgis import gis
from arcgis.features import FeatureLayer
import openpyxl
from copy import deepcopy
import os
import copy

# Login to your arcgis account
login = gis.GIS(portalName, username, password)

# format the path to the excel document so it is recognized as a path
lookupTable = os.path.normpath(lookupTable)

# Read the lookup table and store the fields and alias names
if lookupTable[-4:] != "xlsx":
    print("Please check your input. It needs to be a .xlsx excel file")
else:
    print("Grabbing field and alias names from excel document...")
    # Open Master Metadata excel document
    workbook = openpyxl.load_workbook(lookupTable)
    sheet = workbook.active

    # Create an empty list to store all fields and alias names
    lookupList = []

    # Store values from master metadata excel doc and put into a list
    iter = sheet.iter_rows()
    iter.__next__()
    for row in iter:
        innerList = []
        for val in row:
            innerList.append(val.value)
        lookupList.append(innerList)

    looper = 0
    while restLayerCount > 0:
        # Access the feature layer intended for updating
        search = login.content.search("id:" + layerID, item_type="Feature Layer")
        featureLayer = FeatureLayer.fromitem(search[0], layer_id=looper)
        layerName = search[0].name
        print("Updating layer " + str(looper) + " on " + str(layerName) + "...")

        print("\tGetting field definitions from service...")
        # Loop through fields in service and store JSON for any that are going to be updated
        layerFields = featureLayer.manager.properties.fields

        print("\tFinding fields to update...")
        # Loop through the fields in the service
        updateJSON = []
        for field in layerFields:
            fieldName = field['name']
            for lookupField in lookupList:
                # As you loop through the service fields, see if they match a field in the excel document
                if lookupField[0] == fieldName:
                    # store the field JSON from the online layer
                    fieldJSON = dict(deepcopy(field))
                    # assign the new alias name in JSON format
                    fieldJSON['alias'] = lookupField[1]
                    # assign the new field description in JSON format
                    longDesc = lookupField[2]
                    fldType = lookupField[3]
                    # Remove escape characters like double quotes, newlines, or encoding issues
                    longDesc = longDesc.replace('"', '\\\"').replace("\n", " ").replace("\t", " ").replace(u'\xa0', u' ')
                    # Build the JSON structure with the proper backslashes and quotes
                    fieldJSON['description'] = "{\"value\":" + "\"" + longDesc + "\"" + ",\"fieldValueType\":\"" + fldType + "\"}"
                    fieldJSON.pop('sqlType')
                    print("\t\tField '" + fieldName + "' will be updated to get the alias name '" + lookupField[1] + "'")
                    # Create a python list containing any fields to update
                    updateJSON.append(fieldJSON)

        if updateJSON:
            print("\tUpdating alias names of the REST service...")
            #jsonFormat =  json.dumps(updateJSON)
            aliasUpdateDict = {'fields': updateJSON}
            #aliasUpdateJSON = json.dumps(aliasUpdateDict)
            # Use the update definition call to push the new alias names into the service
            featureLayer.manager.update_definition(aliasUpdateDict)
            print("\tAlias names updated on service!")

        # Now check if the item has a pop-up configuration saving the alias names as well
        # First, grab the item JSON for the layer and create an item to hold the new edited JSON
        print("\tUpdating the alias names within the pop-up configuration on the item...")
        item = gis.Item(login, itemid=layerID)

        # Grab the existing JSON for the popup, store a copy, and edit the aliases
        itemJSON = item.get_data(try_json=True)
        # Loop through the existing layer and check if any alias names don't match
        counter = 0
        if itemJSON:
            print("\tFinding all replacements of alias names within pop-up...")
            newItemJSON = copy.deepcopy(itemJSON)
            print("\t\tUpdating alias names in popup fieldInfos...")
            for i in itemJSON['layers'][looper]['popupInfo']['fieldInfos']: #change [0] to whatever layer you're working on (1,2,3)
                fieldName2 = i['fieldName']
                for lookup in lookupList:
                    if lookup[0] == fieldName2:
                        newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter]['label'] = lookup[1] #change [0] to whatever layer you're working on (1,2,3)
                        # Check if there is a decimal spec
                        if "format" in i and "places" in i["format"]:
                            # If a value is specified in the lookup doc, assign that
                            if lookup[4]:
                                newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter]['format']['places'] = lookup[4]
                            # If a value is not specified and the decimals have defaulted to 6, change to 2
                            else:
                                if newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter]['format']['places'] == 6:
                                    newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter]['format']['places'] = 2
                        # Update thousands separator if lookup document specifies and if it exists in JSON
                        if lookup[5] != None and str(lookup[5]).lower() != "no" and str(lookup[5]).lower() != "false" and "format" in i and "digitSeparator" in i["format"]:
                            newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter]['format']['digitSeparator'] = True


                counter += 1

            # Check if layer was updated in new Map Viewer and contains a popupElement JSON section with fieldInfos
            if "popupElements" in itemJSON['layers'][looper]['popupInfo'] and itemJSON['layers'][looper]['popupInfo']["popupElements"] and "fieldInfos" in itemJSON['layers'][looper]['popupInfo']["popupElements"][0]:
                print("\t\tUpdating popupElement fieldInfo...")
                counter2 = 0
                for j in itemJSON['layers'][looper]['popupInfo']["popupElements"][0]["fieldInfos"]:
                    fldName = j["fieldName"]
                    for lkup in lookupList:
                        if lkup[0] == fldName:
                            newItemJSON['layers'][looper]['popupInfo']['popupElements'][0]["fieldInfos"][counter2]['label'] = lkup[1]
                            # Check if there is a decimal spec
                            if "format" in j and "places" in j["format"]:
                                # If a value is specified in the lookup doc, assign that
                                if lkup[4] != None:
                                    newItemJSON['layers'][looper]['popupInfo']['popupElements'][0]["fieldInfos"][counter2]['format']['places'] = lkup[4]
                                # If a value is not specified and the decimals have defaulted to 6, change to 2
                                else:
                                    if newItemJSON['layers'][looper]['popupInfo']['popupElements'][0]["fieldInfos"][counter2]['format']['places'] == 6:
                                        newItemJSON['layers'][looper]['popupInfo']['popupElements'][0]["fieldInfos"][counter2]['format']['places'] = 2
                            # Update thousands separator if lookup document specifies and if it exists in JSON
                            if lkup[5] != None and str(lkup[5]).lower() != "no" and str(lkup[5]).lower() != "false" and "format" in j and "digitSeparator" in j["format"]:
                                newItemJSON['layers'][looper]['popupInfo']['fieldInfos'][counter2]['format']['digitSeparator'] = True
                    counter2 += 1


            # Update json
            print("\tUpdating the alias names within the existing item pop-up...")
            portal = portalName
            update = item.update(item_properties={'text': newItemJSON})
            if update:
                print("\tSuccess! Your alias names have been updated. Please check your service to confirm.")
            else:
                print("\tUpdating pop-up failed.")
        else:
            print("\tNo pop-up JSON. Skipping.")

        looper += 1
        restLayerCount -= 1
