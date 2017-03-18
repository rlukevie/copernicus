from osgeo import gdal
import functions as cf
import os
import re
import sys
import time
import ConfigParser
import logging


###############################################################################
# SETTINGS                                                                    #
###############################################################################

# Directories
configuration = ConfigParser.ConfigParser()
configuration.read("./config/conf.cfg")
base_directory = configuration.get("directories", "base")
product_download_directory = os.path.join(base_directory, 'downloads')
product_data_directory = os.path.join(base_directory, 'SAFE')
log_directory = os.path.join(base_directory, 'log')
shelve_directory = os.path.join(base_directory, 'etc')
image_output_directory = os.path.join(base_directory, 'img')

# verbose?
if configuration.get("logging", "verbose") == "True":
    verbose = True
else:
    verbose = False

# log output?
if configuration.get("logging", "log_output") == "True":
    log_name_out = 'analysis_out_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    log_name_err = 'analysis_err_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    sys.stdout = open(os.path.join(log_directory, log_name_out), 'a')
    sys.stderr = open(os.path.join(log_directory, log_name_err), 'a')


###############################################################################
# FUNCTIONS                                                                   #
###############################################################################


def get_image_dir(product_title, pixel_size, band_name):
    pixel_size_path = 'R' + str(pixel_size) + 'm'
    granule_dir = os.listdir(
        os.path.join(product_data_directory, product_title + '.SAFE',
                     'GRANULE'))[0]
    images = os.listdir(
        os.path.join(
            product_data_directory, product_title + '.SAFE', 'GRANULE',
            granule_dir, 'IMG_DATA', pixel_size_path))
    regex = re.compile(".*(_" + band_name + "_).*")
    image_name = [m.group(0) for l in images for m in [regex.search(
        l)] if m][0]
    return os.path.join(product_data_directory,
                        product_title + '.SAFE',
                        'GRANULE',
                        granule_dir,
                        'IMG_DATA',
                        pixel_size_path,
                        image_name)


def get_image_size(image_output_directory):
    raster = gdal.Open(image_output_directory)
    print(raster.RasterXSize)


def merge_bands_to_rgb(r_path, g_path, b_path, out_path):
    os.system('gdal_merge.py -separate ' +
              r_path + ' ' + g_path + ' ' + b_path + ' -o ' + out_path)
    os.system('gdal_translate -co PHOTOMETRIC=RGB ' +
              out_path + ' ' + out_path[:-4] + '_temp.tif')
    os.remove(out_path)
    os.rename(out_path[:-4] + '_temp.tif', out_path)


def create_thumbnail(in_path, out_path):
    os.system('gdal_translate -of jpeg -scale -ot Byte -outsize 1600 1600 ' +
              in_path + ' ' + out_path)


###############################################################################
# MAIN                                                                        #
###############################################################################

logging.info('========== STARTED analysis.py ==========')

products_to_analyze = cf.read_products_to_analyze()

if verbose:
    logging.debug(
        '\ncf.read_products_to_analyze(): {}\n'.format(products_to_analyze))

for product in products_to_analyze:
    r_dir = get_image_dir(products_to_analyze[product][1], 10, 'B04')
    g_dir = get_image_dir(products_to_analyze[product][1], 10, 'B03')
    b_dir = get_image_dir(products_to_analyze[product][1], 10, 'B02')
    rgb_dir = os.path.join(
        image_output_directory, products_to_analyze[product][1] + '_RGB.tif')
    thumb_dir = os.path.join(
        image_output_directory,
        products_to_analyze[product][1] + '_RGB_thumb.jpg')

    merge_bands_to_rgb(r_dir, g_dir, b_dir, rgb_dir)
    logging.info('Completed merge to RGB: ' + rgb_dir)

    create_thumbnail(rgb_dir, thumb_dir)
    logging.info('Completed Create Thumbnail: ' + thumb_dir)

    cf.write_product_analyzed(products_to_analyze[product])
    cf.send_analyzed_mail_with_thumbnail(products_to_analyze[product])
    cf.remove_from_analyzeshelve(products_to_analyze[product])

logging.info('No (more) products to analyze')

logging.info('========== FINISHED analysis.py ==========')
logging.shutdown()
