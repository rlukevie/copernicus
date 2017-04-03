import shelve

from factorytools.settings import *


class Shelve:
    def __init__(self, shelve_filename):
        self.shelve_filename = shelve_filename
        self.shelve_file = None
        try:
            self.shelve_file = shelve.open(
                os.path.join(shelve_directory, 'downloaded_products'))
        except IOError:
            return

    def close(self):
        self.shelve_file.close()

    def write_product(self, product_title, product_object):
        self.shelve_file[product_title] = product_object
        logging.info(
            'Product written to shelve "downloaded_products": {}'.format(
                product_title))