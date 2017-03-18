import time
import sys
import functions as cf
import os
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
    log_name_out = 'product_factory_out_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    log_name_err = 'product_factory_err_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    sys.stdout = open(os.path.join(log_directory, log_name_out), 'a')
    sys.stderr = open(os.path.join(log_directory, log_name_err), 'a')

# reset shelves?
if configuration.get("debugging", "reset_downloadshelve") == "True":
    cf.reset_downloadshelve()
if configuration.get("debugging", "reset_analyzeshelve") == "True":
    cf.reset_analyzeshelve()


###############################################################################
# PRODUCT QUERIES                                                             #
###############################################################################

# queries = [{'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                 footprint:"Intersects(48.2000, 16.1000)" AND\
#                 producttype:"S2MSI1C" AND\
#                 cloudcoverpercentage:[0 TO 10]',
#             'rows': '10'},  # WIEN
#            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                            footprint:"Intersects(36.197, 37.144)" AND\
#                            producttype:"S2MSI1C" AND\
#                            cloudcoverpercentage:[0 TO 10]',
#             'rows': '10'},  # Aleppo
#            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                            footprint:"Intersects(0.000, -50.000)" AND\
#                            producttype:"S2MSI1C" AND\
#                            cloudcoverpercentage:[0 TO 15]',
#             'rows': '10'},  # Amazonas Muendung
#            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                            footprint:"Intersects(30.300, 121.000)" AND\
#                            producttype:"S2MSI1C" AND\
#                            cloudcoverpercentage:[0 TO 15]',
#             'rows': '10'},  # Jiangtse Muendung
#            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                            footprint:"Intersects(-33.457, -70.648)" AND\
#                            producttype:"S2MSI1C" AND\
#                            cloudcoverpercentage:[0 TO 15]',
#             'rows': '10'},  # Santiago de Chile
#            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
#                            footprint:"Intersects(39.031, 125.343)" AND\
#                            producttype:"S2MSI1C" AND\
#                            cloudcoverpercentage:[0 TO 10]',
#             'rows': '10'}]  # Pyongyang

queries = [{'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
                footprint:"Intersects(48.2000, 16.1000)" AND\
                producttype:"S2MSI1C" AND\
                cloudcoverpercentage:[0 TO 10]',
            'rows': '10'}]  # WIEN


###############################################################################
# MAIN                                                                        #
###############################################################################


logging.info('---------- STARTED product_factory.py ----------')

for query in queries:
    response = cf.osearch(query)

    if verbose:
        logging.debug('\nquery: {}'.format(query))
        logging.debug('\nresponse: {}'.format(response))
        logging.debug('\n\nresponse.text:')
        logging.debug(response.text)

    products_in_response = (cf.parse_osearch_response(response))

    if not products_in_response:
        logging.info('No Entries in Response - skipping')
        continue

    if verbose:
        logging.debug('\ncf.list_products(products_in_response):')
        cf.list_products(products_in_response)

    product_to_download = cf.select_product_to_download(products_in_response)

    if verbose:
        logging.debug('\nproduct_to_download:')
        logging.debug(product_to_download)

    if cf.product_already_downloaded(product_to_download):
        logging.info(
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

logging.info('---------- FINISHED product_factory.py ----------')
logging.shutdown()
