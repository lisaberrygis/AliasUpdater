# Hosted Feature Service Alias Updater
Update Hosted Feature Services in ArcGIS Online using this short Python 3 script
This script uses a lookup table to update alias names on a hosted feature service.
The script updates the alias names in two places:
  - The REST endpoint
  - The layer's pop-up JSON
  
The pop-up configuration will not be altered with this implementation.
The script also allows you to update the long description and field type for any field.

The script will use the input excel document and update any fields it finds that matches from the excel document

This script allows for multiple REST layers to be updated. Specify the REST layer count in the inputs

You must have ArcGIS Pro installed on your computer in order to run this script
Python version: 3.6. Make sure your interpreter is calling to the arcgispro-py3 python.exe

# Excel input:
See the included **Test.xlsx** to see how the input excel should be structured

# Comments about python inputs:
**username and password** are your ArcGIS Online organizational credentials

**layerID** is the ID to a hosted feature service 

**restLayerCount** is the count of layers in the service. All layers will use
              the same field/alias lookup, but only matching fields will be updated.

**lookupTable** must be an excel document (.xlsx) with a header row. An example is included in the repo.
The first column should be the field names as they are in the service.
The second column should be the intended alias names for each field.
*optional* The third column should be the intended description for each field.
*optional* The fourth column can include the field type. This must be formatted
          to match the backend JSON. 
           Ex:  nameOrTitle, description, typeOrCategory, countOrAmount, percentageOrRatio
               measurement, currency, uniqueIdentifier, phoneNumber, emailAddress,
               orderedOrRanked, binary, locationOrPlaceName, coordinate, dateAndTime

 **portalName** can be left as-is if you are working in ArcGIS Online.
