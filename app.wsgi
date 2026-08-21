import sys
import os

# Add the directory containing your Flask application to the Python path
# here I must give the whole path to the file because the excecution of this file takes place in another directory
sys.path.insert(0, '/var/www/carbonate-system-modelling/multipage_website')

# try to load the newly created  venv
sys.path.insert(0, '/var/www/carbonate-system-modelling/multipage_website/venv/lib/python3.12/site-packages')


from app import server as application