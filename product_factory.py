from copernicus_tools.mail import MailHandler
from copernicus_tools.product import FactoryProduct
from copernicus_tools.product_shelve import Shelve
from copernicus_tools.request import ProductSelector
from copernicus_tools.settings import *


def main():
    logging.info('---------- STARTED product_factory.py ----------')

    wien = ProductSelector(
        {"q": 'beginposition:[NOW-20MONTHS TO NOW] AND footprint:"Intersects('
              '48.2000, 16.1000)" AND producttype:"S2MSI1C" AND '
              'cloudcoverpercentage:[0 TO 10]',
         "rows": "10"})

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
            instance.select_first()
        except ValueError:
            logging.debug("Cannot select product: self.response = None")
        FactoryProduct(instance.selected_product)

    download_shelve = Shelve(downloaded_products_shelve)
    to_analyze_shelve = Shelve(products_to_analyze_shelve)

    admin_mail_man = MailHandler()

    for product in FactoryProduct.instances:
        admin_mail_man.send_product_selected_mail(product)
        try:
            if not download_shelve.product_exists(product.title):
                product.download_zip()
                download_shelve.write_product(product)
                admin_mail_man.send_product_downloaded_mail(product)

                product.unzip()
                download_shelve.write_product(product)

                product.process_level_1c_to_2a()
                download_shelve.write_product(product)
                admin_mail_man.send_product_processed_mail(product)

                to_analyze_shelve.write_product(product)
        except IOError as io:
            logging.debug(io.args[0])
    download_shelve.close()

    logging.info('---------- FINISHED product_factory.py ----------')
    logging.shutdown()


if __name__ == '__main__':
    main()
