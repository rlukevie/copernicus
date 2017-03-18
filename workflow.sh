#!/bin/bash
export PATH=/home/roland/anaconda2/bin:$PATH

source activate sen2cor
export SEN2COR_HOME=/home/roland/sen2cor
export SEN2COR_BIN=/home/roland/anaconda2/lib/python2.7/site-packages/sen2cor-2.3.0-py2.7.egg/sen2cor
export GDAL_DATA=/home/roland/anaconda2/lib/python2.7/site-packages/sen2cor-2.3.0-py2.7.egg/sen2cor/cfg/gdal_data
python /home/roland/copernicus/product_factory.py # > "/home/roland/copernicus/log/copernicus-"`date +"%Y-%m-%d-%H-%M-%S"`".log"

source activate gdal
python /home/roland/copernicus/analysis.py # > "/home/roland/copernicus/log/copernicus_analysis-"`date +"%Y-%m-%d-%H-%M-%S"`".log"