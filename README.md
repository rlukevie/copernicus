# Copernicus Satellite Imagery Workflow
## Important Files
### workflow.sh
Wrapper script. Necessary to switch between Python environments.
### product_factory.py
- Search for imagery products on Copernicus Opendata Hub
- Download selected products
- unzip
- Level-2-Processing (using sen2cor)

### analysis.py
No real analysis implemented yet, only:
- Merge RGB bands
- Create thumbnail
- Send notification mail with thumbnail attached

### functions.py
Most of the functions in use can be found here.

### config/conf.cfg