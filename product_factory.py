#!/home/roland/anaconda2/envs/sen2cor/bin/python

import functions as cf

from factorytools.settings import *
from factorytools.request import ProductSelector


def main():

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
    #                            cloudcoverpercentage:[0 TO 40]',
    #             'rows': '10'},  # Aleppo
    #            {'q': 'beginposition:[NOW-10MONTHS TO NOW] AND\
    #                            footprint:"Intersects(0.000, -50.000)" AND\
    #                            producttype:"S2MSI1C" AND\
    #                            cloudcoverpercentage:[0 TO 45]',
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

    wien = ProductSelector(
        {"q": 'beginposition:[NOW-20MONTHS TO NOW] AND footprint:"Intersects('
              '48.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
              'cloudcoverpercentage:[0 TO 10]',
         "rows": "10"})

    # amazonas_muendung = ProductSelector(
    #     {"q": 'beginposition:[NOW-10MONTHS TO NOW] AND '
    #           'footprint:"Intersects(30.300, 121.000)" AND '
    #           'producttype:"S2MSI1C" AND '
    #           'cloudcoverpercentage:[0 TO 0]',
    #      "rows": "10"})


    for instance in ProductSelector.instances:
        instance.send()
        instance.select()

    # TODO: ab hier gibt es keine Objekte mehr!

    logging.info('---------- STARTED product_factory.py ----------')

    for request in request_queue.queue:
        response = cf.osearch(request.request)

        if verbose:
            logging.debug('\nrequest: {}'.format(request.request))
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


if __name__ == '__main__':
    main()
