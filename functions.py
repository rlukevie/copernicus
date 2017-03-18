import datetime
import os
import shelve
import smtplib
import requests
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import xml.etree.cElementTree as ET
import zipfile
import pprint
import time
import ConfigParser

# SETTINGS
# Credentials
credentials = ConfigParser.ConfigParser()
credentials.read("./config/credentials.cfg")
opendatahub_user = credentials.get("opendatahub", "user")
opendatahub_password = credentials.get("opendatahub", "pw")
email_user = credentials.get("email", "user")
email_password = credentials.get("email", "pw")

# Directories
configuration = ConfigParser.ConfigParser()
configuration.read("./config/conf.cfg")
base_directory = configuration.get("directories", "base")
product_download_directory = os.path.join(base_directory, 'downloads')
product_data_directory = os.path.join(base_directory, 'SAFE')
log_directory = os.path.join(base_directory, 'log')
shelve_directory = os.path.join(base_directory, 'etc')
image_output_directory = os.path.join(base_directory, 'img')


# ===================================================================
# SEARCHING

def osearch(query):
    write_download_log('Opensearch Query: {}'.format(query))
    response = requests.get(
        "https://scihub.copernicus.eu/apihub/search",
        params=query, auth=(opendatahub_user, opendatahub_password))
    return response


def parse_osearch_response(response):
    parsed_response = []
    tree = ET.fromstring(response.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    id_list = tree.findall("./atom:entry/atom:id", ns)
    title_list = tree.findall("./atom:entry/atom:title", ns)
    beginposition_list = tree.findall(
        "./atom:entry/atom:date[@name='beginposition']", ns)
    querytime = tree.find("./atom:updated", ns).text
    size_list = tree.findall("./atom:entry/atom:str[@name='size']", ns)
    producttype_list = tree.findall(
        "./atom:entry/atom:str[@name='producttype']", ns)
    for i in range(len(id_list)):
        parsed_response.append([id_list[i].text,
                                title_list[i].text,
                                beginposition_list[i].text,
                                size_list[i].text,
                                producttype_list[i].text,
                                querytime])
    return sorted(parsed_response, key=lambda x: x[2], reverse=True)


# ===================================================================
# LOGGING

def write_log(logentry, logfile):
    entrytime = datetime.datetime.now().isoformat()[:-7]
    with open(os.path.join(log_directory, logfile), 'a') as f:
        f.write('{:s} {:s}\n'.format(entrytime, logentry))


def write_download_log(logentry):
    write_log(logentry, os.path.join(log_directory, 'download.log'))


def write_analysis_log(logentry):
    write_log(logentry, os.path.join(log_directory, 'analysis.log'))


# ===================================================================
# VARIOUS HELPERS

def translate_l1c_to_l2a_title(product):
    l2a_title = product[1][:7] + 'L2A' + product[1][10:]
    product[1] = l2a_title
    return product


def list_products(parsed_response):
    i = 0
    print('\nLIST PRODUCTS\nTotal: ' +
          str(len(parsed_response)) + '\n' + 13 * '=')
    for p in parsed_response:
        i += 1
        print("{:03d}: {:s} --> {:10s} {:10s} {:s}".format(i,
                                                           p[0][:4] + '..' +
                                                           p[0][-4:],
                                                           p[3],
                                                           p[2][:10],
                                                           p[1]))


# ===================================================================
# DOWNLOADING ETC

def select_product_to_download(parsed_response):
    # einfacher Fall: nur das erste Produkt selektieren:
    return parsed_response[0]


def proceed_with_download(product):
    return True  # Batch-Modus
    print('\nProduct to Download:')
    pprint.pprint(product)
    inputstr = ''
    while inputstr not in ['y', 'n']:
        inputstr = raw_input('Proceed? (y/n)')
        if inputstr == 'y':
            return True
        if inputstr == 'n':
            return False
        print('Enter "y" or "n"')


def download_product(product):
    filename = product[1] + '.zip'
    path = os.path.join(product_download_directory, filename)
    write_download_log(
        'Requesting download for: {} | {}'.format(product[0], product[1]))

    r = requests.get(
        "https://scihub.copernicus.eu/dhus/odata/v1/Products('" +
        product[0] + "')/$value",
        auth=(opendatahub_user, opendatahub_password),
        stream=True)

    if r.status_code == 200:
        write_download_log(
            'Starting download for: {} | {}'.format(product[0], product[1]))
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    write_download_log(
        'Product download complete for: {} | {}'.format(
            product[0], product[1]))


def unzip_downloaded_product(product):
    write_download_log(
        'Starting Unzip for: {} | {}'.format(product[0], product[1]))
    file_to_extract = product[1] + '.zip'
    extract_from_path = os.path.join(product_download_directory, file_to_extract)
    extract_to_path = product_data_directory
    safezip = zipfile.ZipFile(extract_from_path)
    safezip.extractall(extract_to_path)
    safezip.close()
    write_download_log(
        'Completed Unzip for: {} | {}'.format(product[0], product[1]))


def process_l1c_to_l2a(product):
    log_name = 'copernicus_process_l1c_to_l2a_' + \
        time.strftime('%Y-%m-%d__%H_%M_%S') + '.log'
    saveout = sys.stdout
    sys.stdout = open(os.path.join(log_directory, log_name), 'w')

    filename = product[1] + '.SAFE'
    l1c_path = os.path.join(product_data_directory, filename)
    write_download_log(
        'Starting L2A_Process for: {} | {}'.format(product[0], l1c_path))
    os.system('L2A_Process ' + l1c_path)
    write_download_log(
        'Completed L2A_Process for: {} | {}'.format(product[0], l1c_path))

    sys.stdout = saveout


# ===================================================================
# Product Downloaded Shelve


def product_already_downloaded(product):
    sf = shelve.open(os.path.join(shelve_directory, 'downloaded_products'))
    if product[0] in sf.keys():
        sf.close()
        return True
    else:
        sf.close()
        return False


def reset_downloadshelve():
    sf = shelve.open(os.path.join(shelve_directory, 'downloaded_products'))
    sf.clear()
    sf.close()
    write_download_log('Reset downloadshelve')


def write_product_to_downloaded(product):
    sf = shelve.open(os.path.join(shelve_directory, 'downloaded_products'))
    sf[product[0]] = product  # oder product[1:]???
    sf.close()
    write_download_log(
        'Product written to shelve "downloaded_products": {}'.format(
            product[0]))
    return


def ids_in_downloaded_shelve():
    sf = shelve.open(os.path.join(shelve_directory, 'downloaded_products'))
    ids = sf.keys()
    return ids


def products_in_shelve():
    sf = shelve.open(os.path.join(shelve_directory, 'downloaded_products'))
    products = sf.values()
    return products


def print_products_in_shelve():
    print(products_in_shelve())


# ===================================================================
# Product to Analyze Shelve


def write_product_to_analyze(product):
    sf = shelve.open(os.path.join(shelve_directory, 'products_to_analyze'))
    sf[product[0]] = product
    sf.close()
    write_download_log(
        'Product written to shelve "products_to_analyze": {}'.format(
            product[0]))


def read_products_to_analyze():
    sf = shelve.open(os.path.join(shelve_directory, 'products_to_analyze'))
    productsreturn = {}
    for productkey in sf.keys():
        productsreturn[productkey] = sf[productkey]
    sf.close()
    return productsreturn


def print_products_to_analyze():
    print(read_products_to_analyze())


def remove_from_analyzeshelve(product):
    sf = shelve.open(os.path.join(shelve_directory, 'products_to_analyze'))
    print(sf.pop(product[0], False))
    sf.close()
    sf = shelve.open(os.path.join(shelve_directory, 'products_to_analyze'))
    print('sf: {}'.format(sf))
    sf.close()
    write_analysis_log('Removed from analyzeshelve: {}'.format(product[0]))


def reset_analyzeshelve():
    sf = shelve.open(os.path.join(shelve_directory, 'products_to_analyze'))
    sf.clear()
    sf.close()
    write_analysis_log('Reset analyzeshelve')


# ===================================================================
# Product Analyzed Shelve

def write_product_analyzed(product):
    sf = shelve.open(os.path.join(shelve_directory, 'products_analyzed'))
    sf[product[0]] = product
    sf.close()
    write_analysis_log(
        'Product written to shelve "products_analyzed": {}'.format(product[0]))


def read_products_analyzed():
    sf = shelve.open(os.path.join(shelve_directory, 'products_analyzed'))
    return sf


def reset_analyzedshelve():
    sf = shelve.open(os.path.join(shelve_directory, 'products_analyzed'))
    sf.clear()
    sf.close()
    write_analysis_log('Reset analyzedshelve')

# ===================================================================
# Send Mails


def send_analyzed_mail_with_thumbnail(product):
    thumb_path = os.path.join(image_output_directory, product[1] + '_RGB_thumb.jpg')
    msg = MIMEMultipart()
    msg['Subject'] = 'Thumbnail created: ' + product[1]
    msg['From'] = 'Copernicus Analysator <r.lukesch@gmx.net>'
    msg['To'] = 'Roland Lukesch <r.lukesch@gmx.net>'
    text = MIMEText('Thumbnail created: ' + product[1])
    msg.attach(text)
    f = open(thumb_path, 'rb')
    bild = MIMEImage(f.read())
    f.close()
    msg.attach(bild)

    smtp = smtplib.SMTP_SSL("mail.gmx.com:465")
    smtp.login(email_user, email_password)
    smtp.sendmail('Copernicus <r.lukesch@gmx.net>',
                  'Roland Lukesch <r.lukesch@gmx.net>', msg.as_string())
    smtp.quit()

    write_analysis_log(
        'Sent Thumbnail Mail to r.lukesch@gmx.net: {}'.format(thumb_path))
