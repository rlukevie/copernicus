from osgeo import gdal
import copernicus_functions as cf
import os
import re
import sys
import time


# SETTINGS
basedir = '/home/roland/copernicus'
download_dir = os.path.join(basedir, 'downloads')
SAFE_dir = os.path.join(basedir, 'SAFE')
log_dir = os.path.join(basedir, 'log')
etc_dir = os.path.join(basedir, 'etc')
img_dir = os.path.join(basedir, 'img')

verbose = True

def get_image_dir(product_title, pixel_size, band_name):
    pixel_size_path = 'R' + str(pixel_size) + 'm'
    granule_dir = os.listdir(os.path.join(SAFE_dir, product_title + '.SAFE', 'GRANULE'))[0]
    images = os.listdir(os.path.join(SAFE_dir,
                        product_title + '.SAFE',
                        'GRANULE',
                        granule_dir,
                        'IMG_DATA',
                        pixel_size_path))
    regex = re.compile(".*(_" + band_name + "_).*")
    image_name = [m.group(0) for l in images for m in [regex.search(l)] if m][0]
    return os.path.join(SAFE_dir,
                        product_title + '.SAFE',
                        'GRANULE',
                        granule_dir,
                        'IMG_DATA',
                        pixel_size_path,
                        image_name)


def get_image_size(img_dir):
    raster = gdal.Open(img_dir)
    print(raster.RasterXSize)


def merge_bands_to_rgb(r_path, g_path, b_path, out_path):
    os.system('gdal_merge.py -separate ' + r_path + ' ' + g_path + ' ' + b_path + ' -o ' + out_path)
    os.system('gdal_translate -co PHOTOMETRIC=RGB ' + out_path + ' ' + out_path[:-4] + '_temp.tif')
    os.remove(out_path)
    os.rename(out_path[:-4] + '_temp.tif', out_path)


def create_thumbnail(in_path, out_path):
    os.system('gdal_translate -of jpeg -scale -ot Byte -outsize 1600 1600 ' + in_path + ' ' + out_path)


# =======================================================================================

if verbose:
    log_name_out = 'copernicus_analysis_out_' + time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    log_name_err = 'copernicus_analysis_err_' + time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    sys.stdout = open(os.path.join(log_dir, log_name_out), 'a')
    sys.stderr = open(os.path.join(log_dir, log_name_err), 'a')

products_to_analyze = cf.read_products_to_analyze()

# print('\ncf.read_products_to_analyze(): {}\n'.format(products_to_analyze))

cf.write_analysis_log('Started copernicus_analysis.py')

for product in products_to_analyze:
    r_dir = get_image_dir(products_to_analyze[product][1], 10, 'B04')
    g_dir = get_image_dir(products_to_analyze[product][1], 10, 'B03')
    b_dir = get_image_dir(products_to_analyze[product][1], 10, 'B02')
    rgb_dir = os.path.join(img_dir, products_to_analyze[product][1] + '_RGB.tif')
    thumb_dir = os.path.join(img_dir, products_to_analyze[product][1] + '_RGB_thumb.jpg')

    merge_bands_to_rgb(r_dir, g_dir, b_dir, rgb_dir)
    cf.write_analysis_log('Completed merge to RGB: ' + rgb_dir)

    create_thumbnail(rgb_dir, thumb_dir)
    cf.write_analysis_log('Completed Create Thumbnail: ' + thumb_dir)

    cf.write_product_analyzed(products_to_analyze[product])
    cf.send_analyzed_mail_with_thumbnail(products_to_analyze[product])
    cf.remove_from_analyzeshelve(products_to_analyze[product])

cf.write_analysis_log('No (more) products to analyze')

cf.write_analysis_log('Finished copernicus_analysis.py')
