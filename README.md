# Hosted Feature Service Alias Updater
Update Hosted Feature Services in ArcGIS Online using this short Python 3 script
This script uses a lookup table to update alias names on a hosted feature service.
The script updates the alias names in two places:
  - The REST endpoint
  - The layer's pop-up JSON in the fieldInfos section 
  - *If saved in the new Map Viewer, also edits the popupElement fieldInfos*
As of August 2022, the script also can update the pop-up decimals based on an additional field in the excel lookup.
  
The pop-up configuration will not be altered with this implementation, just the fields list for the pop-up.
The script also allows you to update the long description, field decimals, field type, or thousands separator for any field.

The script will use the input excel document and update any fields it finds that matches from the excel document

This script allows for multiple REST layers to be updated. Specify the REST layer count in the inputs

You must have ArcGIS Pro installed on your computer in order to run this script
Python version: 3.6. Make sure your interpreter is calling to the arcgispro-py3 python.exe

# Excel input:
See the included **Test.xlsx** to see how the input excel should be structured

# Comments about python inputs:
**username and password** are your ArcGIS Online organizational credentials

**layerID** is the ID to a hosted feature service. [Visit this blog](https://community.esri.com/t5/arcgis-online-blog/where-can-i-find-the-item-id-for-an-arcgis-online/ba-p/890284) if you need help looking for this. 

**restLayerCount** is the count of layers in the service. All layers will use
              the same field/alias lookup, but only matching fields will be updated.

**lookupTable** must be an excel document (.xlsx) with a header row. An example is included in the repo.

The first column should be the field names as they are in the service.

The second column should be the intended alias names for each field.

*optional* The third column should be the intended long description for each field. This can be multiple sentences long and helps describe the field in detail.

*optional* The fourth column can include the field type. This must be formatted
          to match the backend JSON. 
           Ex:  nameOrTitle, description, typeOrCategory, countOrAmount, percentageOrRatio
               measurement, currency, uniqueIdentifier, phoneNumber, emailAddress,
               orderedOrRanked, binary, locationOrPlaceName, coordinate, dateAndTime.
               
*optional* The fifth column can include a specification for how many decimals you want for each field
         to have in the pop-up. If your script is having issues, make sure you at least have these 5 headers in the excel document,
         even if no values appear in the      rows. This can cause the script to fail sometimes.
         
*optional* The sixth column can include a specification for if a numeric attribute should have a thousands comma
                separator. Only specify this if it is a numeric field.
               Ex: can use "true" or "yes" to specify. You can leave this column blank for any fields that are string
                   or don't need a comma. You can also specify those as "no" or "false".

 **portalName** can be left as-is if you are working in ArcGIS Online.
