import shelve

from factorytools.settings import *


class Shelve:
    def __init__(self, shelve_filename):
        self.shelve_filename = shelve_filename
        self.shelve_file = None
        try:
            self.shelve_file = shelve.open(
                os.path.join(shelve_directory, shelve_filename))
        except IOError:
            return

    def close(self):
        self.shelve_file.close()

    def list_titles(self):
        return self.shelve_file.keys()

    def list_product_objects(self):
        return self.shelve_file.values()

    def write_product(self, product_object):
        self.shelve_file[product_object.title] = product_object
        logging.info(
            'Product written to shelve "downloaded_products": {}'.format(
                product_object.title))

    def product_exists(self, product_title):
        if product_title in self.shelve_file.keys():
            logging.info(
                'Product "{}" already downloaded'.format(product_title))
            return True
        else:
            return False

    def reset(self):
        self.shelve_file.clear()
        logging.info(
            'Resetting shelve of downloaded products')