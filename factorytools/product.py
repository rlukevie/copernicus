import xml.etree.ElementTree as ET
import zipfile

import requests

from factorytools.settings import *


class Product(object):
    def __init__(self, selected_product):
        if not isinstance(selected_product, ET.Element):
            raise TypeError("Selected products have to be of type 'Element'")
        else:
            self.xml_tree = selected_product

            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            self.id = self.xml_tree.find("./atom:id", ns).text
            self.title = self.xml_tree.find("./atom:title", ns).text
            self.summary = self.xml_tree.find("./atom:summary", ns).text
            self.beginposition = self.xml_tree.find(
                "./atom:date[@name='beginposition']", ns).text
            size_text = self.xml_tree.find("./atom:str[@name='size']", ns).text
            self.size = self.convert_size_text_to_float(size_text)
            self.producttype = self.xml_tree.find(
                "./atom:str[@name='producttype']", ns).text
            self.gmlfootprint = self.xml_tree.find(
                "./atom:str[@name='gmlfootprint']", ns).text
            self.cloudcoverpercentage = float(self.xml_tree.find(
                "./atom:double[@name='cloudcoverpercentage']", ns).text)

    def convert_size_text_to_float(self, size_text):
        if "MB" in size_text:
            return float(size_text[:-3])
        if "GB" in size_text:
            return float(size_text[:-3]) * 1000


class FactoryProduct(Product):
    instances = []

    def __init__(self, xml_tree):
        super(FactoryProduct, self).__init__(xml_tree)

        self.__class__.instances.append(self)

        self.zip_name = self.title + '.zip'
        self.level_1c_name = None
        self.level_2a_name = None

    def download_zip(self):
        download_path = os.path.join(product_download_directory, self.zip_name)
        logging.info(
            'Requesting download for: {} | {}'.format(self.id, self.title))

        r = requests.get(
            "https://scihub.copernicus.eu/dhus/odata/v1/Products('" +
            self.id + "')/$value",
            auth=(opendatahub_user, opendatahub_password),
            stream=True)

        if r.status_code == 200:
            logging.info(
                'Starting download for: {} | {}. Filesize: {}'.format(
                    self.id, self.title, self.size))
            with open(download_path, 'wb') as f:
                chunks = 0
                for chunk in r.iter_content(1024):
                    chunks += 1
                    if chunks % 1000 == 0:
                        print(str(chunks / 1000) + 'MB')
                    f.write(chunk)
            logging.info(
                'Product download complete for: {} | {}'.format(
                    self.id, self.title))
        else:
            raise IOError("Cannot download zip: r.status_code != 200")

    def unzip(self):
        unzip_from_path = os.path.join(product_download_directory,
                                       self.zip_name)
        unzip_to_path = product_data_directory
        try:
            logging.debug('Zipfile to unzip: {}'.format(unzip_from_path))
            product_zip = zipfile.ZipFile(unzip_from_path)
            self.level_1c_name = product_zip.namelist()[0]
            logging.info(
                'Starting Unzip for: {} to {}'.format(
                    self.title, unzip_to_path))
            product_zip.extractall(unzip_to_path)
            product_zip.close()
            logging.info(
                'Completed Unzip for: {}'.format(self.title))
        except IOError:
            return

    def process_level_1c_to_2a(self):
        if not self.level_1c_name:
            logging.debug('Product object {} has no attribute "level_1c_name".'
                          ' Cannot start L2A processing.')
            return
        try:
            l1c_path = os.path.join(product_data_directory, self.level_1c_name)
            logging.info(
                'Starting L2A_Process for: {} | {}'.format(
                    self.title, l1c_path))
            os.system('L2A_Process ' + l1c_path)
            self.level_2a_name = self.level_1c_name.replace('1C_', '2A_')
            logging.info(
                'Completed L2A_Process for: {} | {}'.format(
                    self.title, l1c_path))
        except IOError:
            return
