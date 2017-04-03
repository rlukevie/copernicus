from factorytools.product import FactoryProduct
from factorytools.product_shelve import Shelve
from factorytools.request import ProductSelector
from factorytools.settings import *


def main():
    logging.info('---------- STARTED product_factory.py ----------')

    # wien = ProductSelector(
    #     {"q": 'beginposition:[NOW-20MONTHS TO NOW] AND footprint:"Intersects('
    #           '48.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
    #           'cloudcoverpercentage:[0 TO 10]',
    #      "rows": "10"})

    jiangtse_muendung = ProductSelector(
        {"q": 'beginposition:[NOW-10MONTHS TO NOW] AND '
              'footprint:"Intersects(30.300, 121.000)" AND '
              'producttype:"S2MSI1C" AND '
              'cloudcoverpercentage:[0 TO 0]',
         "rows": "10"})

    for instance in ProductSelector.instances:
        try:
            instance.send()
        except IOError:
            logging.debug("IOError when sending request")
        try:
            instance.select()
        except ValueError:
            logging.debug("Cannot select product: self.response = None")
        FactoryProduct(instance.selected_product)

    download_shelve = Shelve(downloaded_products_shelve)

    for instance in FactoryProduct.instances:
        try:
            if not download_shelve.product_exists(instance.title):
                instance.download_zip()
                download_shelve.write_product(instance)
                instance.unzip()
                download_shelve.write_product(instance)
                instance.process_level_1c_to_2a()
                download_shelve.write_product(instance)
        except IOError as io:
            logging.debug(io.args[0])
    download_shelve.close()

    logging.info('---------- FINISHED product_factory.py ----------')
    logging.shutdown()


if __name__ == '__main__':
    main()
