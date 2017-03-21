import ConfigParser
import logging
import os

###############################################################################
# SETTINGS                                                                    #
###############################################################################

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

# Open Data Hub
open_data_hub_url = configuration.get("opendatahub", "url")

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

# reset product shelves?
if configuration.get("debugging", "reset_downloadshelve") == "True":
    cf.reset_downloadshelve()
if configuration.get("debugging", "reset_analyzeshelve") == "True":
    cf.reset_analyzeshelve()

# Logging
standard_logfile = configuration.get("logging", "file")
standard_logpath = os.path.join(log_directory, standard_logfile)
logging.basicConfig(
    filename=standard_logpath,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S")