import copernicus_functions as cf
import pprint
import sys
import os
import time

# SETTINGS
basedir = '/home/roland/copernicus'
# download_dir = os.path.join(basedir, 'downloads')
# SAFE_dir = os.path.join(basedir, 'SAFE')
log_dir = os.path.join(basedir, 'log')
# etc_dir = os.path.join(basedir, 'etc')
# img_dir = os.path.join(basedir, 'img')

verbose = True

queries = [{'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                footprint:"Intersects(48.2000, 16.1000)" AND\
                producttype:"S2MSI1C" AND\
                cloudcoverpercentage:[0 TO 10]',
            'rows': '10'},  # WIEN
           {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                           footprint:"Intersects(36.197, 37.144)" AND\
                           producttype:"S2MSI1C" AND\
                           cloudcoverpercentage:[0 TO 10]',
            'rows': '10'},  # Aleppo
           {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                           footprint:"Intersects(0.000, -50.000)" AND\
                           producttype:"S2MSI1C" AND\
                           cloudcoverpercentage:[0 TO 15]',
            'rows': '10'},  # Amazonas Muendung
           {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                           footprint:"Intersects(30.300, 121.000)" AND\
                           producttype:"S2MSI1C" AND\
                           cloudcoverpercentage:[0 TO 15]',
            'rows': '10'},  # Jiangtse Muendung
           {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                           footprint:"Intersects(-33.457, -70.648)" AND\
                           producttype:"S2MSI1C" AND\
                           cloudcoverpercentage:[0 TO 15]',
            'rows': '10'},  # Santiago de Chile
           {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                           footprint:"Intersects(39.031, 125.343)" AND\
                           producttype:"S2MSI1C" AND\
                           cloudcoverpercentage:[0 TO 10]',
            'rows': '10'}]  # Pyongyang

# =============================================================================

if verbose:
    log_name_out = 'copernicus_out_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    log_name_err = 'copernicus_err_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    sys.stdout = open(os.path.join(log_dir, log_name_out), 'a')
    sys.stderr = open(os.path.join(log_dir, log_name_err), 'a')

# cf.reset_downloadshelve()
# cf.reset_analyzeshelve()

cf.write_download_log('Started copernicus.py')

for query in queries:
    response = cf.osearch(query)
    if verbose:
        print('\nquery: {}'.format(query))
        print('\nresponse: {}'.format(response))
        print('\n\nresponse.text:')
        print(response.text)

    products_in_response = (cf.parse_osearch_response(response))

    if not products_in_response:
        cf.write_download_log('No Entries in Response - skipping')
        continue

    if verbose:
        print('\ncf.list_products(products_in_response):')
        cf.list_products(products_in_response)

    product_to_download = cf.select_product_to_download(products_in_response)
    if verbose:
        print('\nproduct_to_download:')
        pprint.pprint(product_to_download)

    # print(cf.translate_l1c_to_l2a_title(product_to_download))

    if cf.product_already_downloaded(product_to_download):
        cf.write_download_log(
            'Selected product already downloaded: {} | {}'.format(
                product_to_download[0], product_to_download[1]))
    else:
        if cf.proceed_with_download(product_to_download):
            cf.download_product(product_to_download)
            cf.write_product_to_downloaded(product_to_download)
            cf.unzip_downloaded_product(product_to_download)
            cf.process_l1c_to_l2a(product_to_download)
            cf.write_product_to_analyze(
                cf.translate_l1c_to_l2a_title(product_to_download))

cf.write_download_log('Finished copernicus.py')
