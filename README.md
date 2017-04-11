# Copernicus Satellite Imagery Workflow
## Important Files
### workflow.sh
Wrapper script. Necessary to switch between Python environments. Calls product_factory.py and product_lab.py.
### product_factory.py
- Search for imagery products on Copernicus Opendata Hub
- Download selected products
- unzip
- Level-2-Processing (using sen2cor)

### product_lab.py
No real analysis implemented yet, only:
- Merge RGB bands
- Create thumbnail
- Send notification mail with thumbnail attached

### config/conf.cfg