from copernicus_tools.analyze import PreviewCreator
from copernicus_tools.mail import MailHandler
from copernicus_tools.product import FactoryProduct, LabProduct
from copernicus_tools.product_shelve import Shelve
from copernicus_tools.request import ProductSelector
from copernicus_tools.settings import *


def main():
    analyze_shelve = Shelve('products_to_analyze')
    products_to_analyze = analyze_shelve.list_product_objects()

    admin_mail_man = MailHandler()

    for product in products_to_analyze:
        PreviewCreator(LabProduct(product)).run()

    for lab_product in LabProduct.instances:
        PreviewCreator(lab_product).run()
        # print(lab_product.lab_history)
        admin_mail_man.send_preview_generated_mail(lab_product)


if __name__ == '__main__':
    main()
