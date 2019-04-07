# -*- Coding:UTF-8 -*-
from adb.client import Client as AdbClient
import adb
import subprocess
import os
import PySimpleGUI as sg
from datetime import datetime, timedelta
import csv
import shutil
import logging
import operator
import textwrap
from lxml import etree
import time
import json
import base64
import webbrowser
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Get the starting application time
start_time = time.time()

# Define and create the results folder
nb = 1
script_dir = os.path.dirname(os.path.realpath(__file__))
result_folder_name = 'Resultats ' + str(nb)
results_dir = os.path.join(script_dir, result_folder_name)
while os.path.isdir(results_dir):
    nb += 1
    result_folder_name = 'Resultats ' + str(nb)
    results_dir = os.path.join(script_dir, result_folder_name)
os.mkdir(results_dir)

# Define the log file path and set up logger
log_name = 'tel_xtract.log'
log_path = os.path.join(results_dir, log_name)
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

logging.info('Starting Program')

logging.info('Defining necessary variables')

# Html related variables
html_list = list()
table_css_style = """
    body {
      background-color: #CECECE;
    }

    li:not(:last-child) {
      margin: 0 0 10px 0;
    }

    table {
      border: 3px solid #000000;
      max-width: 150%;
      text-align: left;
      border-collapse: collapse;
    }

    table td, table th {
      border: 1px solid #000000;
      padding: 5px 4px;
    }

    table tbody td {
      font-size: 13px;
    }

    table thead {
      background: #818181;
      background: -moz-linear-gradient(top, #a0a0a0 0%, #8d8d8d 66%, #818181 100%);
      background: -webkit-linear-gradient(top, #a0a0a0 0%, #8d8d8d 66%, #818181 100%);
      background: linear-gradient(to bottom, #a0a0a0 0%, #8d8d8d 66%, #818181 100%);
      border-bottom: 3px solid #000000;
    }

    table thead th {
      border: 1px solid #000000;
      padding: 5px 4px;
      font-size: 15px;
      font-weight: bold;
      color: #000000;
      text-align: left;
      white-space:nowrap;
    }

    table tfoot td {
      font-size: 14px;
    }

    .column {
      float: left;
      padding: 10px;
    }

    .left {
      width: 15%;
    }

    .middle {
      width: 75%;
    }

    .row:after {
      content: "";
      display: table;
      clear: both;
    }"""

# Get all the necessary images from the data.json file into data_dict
script_resource_dir = os.path.join(script_dir, 'Resources')
data_json_file = os.path.join(script_resource_dir, 'data.json')
with open(data_json_file, encoding='utf8') as f:
    data_dict = json.load(f)

app_icon = data_dict['app_icon']['app_icon'].encode('ascii')

# Define PySImpleGUI parameters
sg.ChangeLookAndFeel('Topanga')
sg.SetOptions(icon=app_icon)

# Define list to store all pictures stored on the phone
pic_list = list()

# Define csv directory realted paths
raw_dir = os.path.join(script_dir, 'forensics')
csv_dir = os.path.join(results_dir, 'Fichiers CSV')
csv_dir_resources = os.path.join(csv_dir, 'Resources')

# Define report directory
report_dir = os.path.join(results_dir, 'Rapport HTML')

# Define HTML report paths
html_resource_dir = os.path.join(report_dir, 'Resources')
html_internal_dir = os.path.join(report_dir, 'Internal')

# Define forensics files lists and paths
# Define raw files paths
raw_call_log = os.path.join(raw_dir, 'CallLog Calls.csv')
raw_mms = os.path.join(raw_dir, 'MMS.csv')
raw_sms = os.path.join(raw_dir, 'SMS.csv')
raw_contacts = os.path.join(raw_dir, 'Contacts Phones.csv')
raw_info = os.path.join(raw_dir, 'info.xml')
raw_mmsparts = os.path.join(raw_dir, 'MMSParts.csv')

# Define reworked files paths
call_log_final = os.path.join(csv_dir, 'CallLog Calls.csv')
mms_final = os.path.join(csv_dir, 'MMS.csv')
sms_final = os.path.join(csv_dir, 'SMS.csv')
contacts_final = os.path.join(csv_dir, 'Contacts Phones.csv')
info_final = os.path.join(csv_dir, 'info.xml')
mmsparts_final = os.path.join(csv_dir, 'MMSParts.csv')

csv_forensic_file_list = [call_log_final, contacts_final, info_final, mms_final, mmsparts_final, sms_final]
raw_forensic_file_list = [raw_call_log, raw_contacts, raw_info, raw_mms, raw_mmsparts, raw_sms]

# html images report paths
index_image_path = 'Internal/index_image.png'
file_not_found_rel_path = 'Internal/image-not-found.png'
video_not_found_rel_path = 'Internal/video-not-found.png'
video_icon_rel_path = 'Internal/video.png'
audio_not_found_rel_path = 'Internal/audio-not-found.png'
audio_icon_rel_path = 'Internal/audio.png'

# Define each file path for the html index links
contacts = 'Contacts.html'
call_logs = 'Journaux d\'Appels.html'
sms = 'SMS.html'
mms = 'MMS.html'
index = 'Index.html'
apps = 'Applications.html'
tel_info = 'Infos Tel.html'
images = 'Images.html'

# Define all numbers communicated file path
num_list_file = os.path.join(csv_dir, 'Numéros_comm.csv')

# Define the extraction summary list
summary_list = list()

logging.info('Finished defining variables')


def tel_xtract_gui():
    """Create the starting GUI"""

    # Create the layout
    layout = [[sg.T('Tel_Xtract', size=(23, 1), justification='center', font='Any 24 bold underline')],
              [sg.T('', font='Any 5')],
              [sg.T('N° U.N.A:', size=(16, 1)), sg.In(key='una')],
              [sg.T('Affaire:', size=(16, 1)), sg.In(key='affaire')],
              [sg.T('N° du scellé:', size=(16, 1)), sg.In(key='num_scelle')],
              [sg.T('Description du scellé:', size=(16, 1)), sg.In(key='desc_scelle')],
              [sg.T('Personne qualifiée:', size=(16, 1)), sg.In(key='examiner')],
              [sg.T('{}'.format('-' * 115))],
              [sg.T('Etapes à suivre:', font='Any 10 underline')],
              [sg.T('1. Activer les options développeur et le débogage USB sur le téléphone.')],
              [sg.T('2. Si le téléphone n\'est pas reconnu par l\'ADB, le programme vous le dira.')],
              [sg.T('3. Se laisser guider par le programme.')],
              [sg.T('4. Exploiter les résultats et vérifier le fichier log pour d\'éventuelles erreurs.')],
              [sg.Checkbox('Extraction des images', key='images')],
              [sg.T('ATTENTION: Bien vouloir s\'assurer qu\'un seul téléphone est branché', font='Any 10 bold')],
              [sg.T('{}'.format(' ' * 85)), sg.T('Licence', key='license', enable_events=True, justification='right', font='Any 7', text_color='blue'), sg.T('Manuel', key='manual', enable_events=True, justification='right', font='Any 7', text_color='blue')],
              [sg.Button('Valider', key='ok'), sg.Button('Quitter', key='quit')]]

    # Create the window
    logging.info('Starting GUI')
    window = sg.Window('Tel Xtract', icon=app_icon).Layout(layout)

    # Open the window and read the results
    while True:
        event, values = window.Read()
        logging.info('GUI closed, user input')
        if event in (None, 'quit'):
            logging.info('User chose to exit via the GUI. Exiting.')
            window.Close()
            exit()
        elif event == 'manual':
            readme_html_path = os.path.join(script_resource_dir, 'Manuel.html')
            webbrowser.open('file://' + readme_html_path)
            continue
        elif event == 'license':
            license_path = script_dir + '/LICENSE.txt'
            webbrowser.open('file://' + license_path)
            continue
        else:
            window.Close()
            logging.info('GUI closed, user input returned')
            return values


def popup_working(text):
    """Black persistent popup to show progress"""

    layout = [[sg.T(text, text_color='white', font='Any 24 bold', background_color='black')]]
    window = sg.Window('Please Wait', no_titlebar=True, grab_anywhere=True, location=(0, 0), background_color='black', ).Layout(layout)
    window.Read(timeout=0)
    return window


def close_popup(window):
    """Close the black persistent popup"""

    window.Close()


def get_info(values):
    """Install user agent, retrieve info and uninstall agent"""

    os.chdir(script_resource_dir)
    apk_path = 'AFLogical-OSE_1.5.2.apk'

    # Define destination folder and make it if necessary
    dest_dir = raw_dir
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    # Start the ADB server and try to install the AFLogical apk
    window = popup_working('démarrage de l\'ADB et détection du téléphone en cours...')
    device = False
    wait_period = 1
    while not device:
        if wait_period == 1:
            subprocess.call("adb.exe start-server", shell=True)
            time.sleep(4)
            wait_period = 0
        else:
            subprocess.call("adb.exe start-server", shell=True)
        client = AdbClient(host="127.0.0.1", port=5037)
        try:

            # Check to make sure only one device is detected by ADB and that the device is correctly detected
            if len(client.devices()) > 1:
                logging.info('Multiple devices detected by ADB.')
                sg.PopupOK('Plusieurs appareils sont détectés par l\'ADB.\nBien vouloir déconnecter tous les appareils'
                           'sauf celui à exploiter.')
                logging.info('Checking if single device id detected by ADB again.')
                continue
            device = client.devices()[0]
            logging.info('Phone detected by ADB')
        except IndexError:
            event = sg.PopupYesNo('Le téléphone n\'est pas détecté par l\'ADB, voulez-vous rééssayer?')
            logging.warning('Phone is not detected by ADB')
            if event == 'Yes':
                logging.info('Trying to detect phone again')
                continue
            else:
                subprocess.call("adb.exe kill-server", shell=True)
                logging.info('Phone was not detected, user chose to exit')
                exit()
        except:
            logging.exception('An error occured while detecting the phone')
    close_popup(window)
    window = popup_working('Installation du User Agent et récupération des données.')

    # Get phone information from adb
    phone_make = device.shell('getprop ro.product.brand').strip()
    phone_model = device.shell('getprop ro.product.model').strip()

    # Install the user agent and get info from it
    installed = False
    while not installed:
        try:
            device.install(apk_path)
            installed = True
            logging.info('User agent installed successfully')
        except adb.InstallError:
            if device.shell('pm list packages | grep com.viaforensics.android.aflogical_ose') == '':
                logging.error('The user agent was not installed')
                event = sg.PopupYesNo('Le User Agent ne s\'est pas installé.\nVérifiez les paramétrages du téléphone.\n'
                                      'Souhaitez-vous réessayer?')
                if event == 'Yes':
                    logging.info('Trying to install user agent again')
                    continue
                else:
                    logging.info('User chose to not try installing User Agent again. Exiting.')
                    exit()
            else:
                logging.info('User agent already installed on device, continuing')
                pass

    # Remove a previously installed forensics folder if it exists
    device.shell('rm -r /mnt/sdcard/forensics')

    # Launch the apk on the phone and tell user to click "Capture"
    device.shell('monkey -p com.viaforensics.android.aflogical_ose -c android.intent.category.LAUNCHER 1')
    sg.Popup('Application installée avec succès.\n\nSur le téléphone, bien vouloir appuyer sur "Capture".\n\n'
             'Une fois la procédure d\'extraction des données terminée, cliquez "OK" dans cette fenêtre.')

    # List all the files in the forensics folder on the phone and create the paths for the ADB pull
    files = device.shell('cd /mnt/sdcard/forensics/* && ls $PWD/*')
    files = files.split('\n')
    files = [item.strip() for item in files]
    if not files:
        logging.error('There are no files in forensics directory on phone')
    for num, item in enumerate(files):
        sg.OneLineProgressMeter('Extraction', num + 1, len(files), 'key', 'Extraction des éléments MMS')
        try:
            filename = os.path.basename(item)
            final_path = os.path.join(raw_dir, filename)
            device.pull(item, final_path)
            if item not in raw_forensic_file_list:
                path_in_csv_dir = os.path.join(csv_dir_resources, filename)
                pic_list.append({'phone_fpath': item, 'csv_fpath': path_in_csv_dir})
        except FileNotFoundError:
            pass

    # Clean up the phone
    device.uninstall('com.viaforensics.android.aflogical_ose')
    if device.shell('pm list packages | grep com.viaforensics.android.aflogical_ose') != '':
        logging.warning('The user agent was not uninstalled')
    else:
        logging.info('User agent correctly uninstalled')
    device.shell('rm -r /mnt/sdcard/forensics')
    logging.info('Finished retrieving files from forenscis folder')

    # List all the files in the DCIM folder on the phone and create the paths for the ADB pull
    if values['images']:
        logging.info('Starting to retrieve all elements from DCIM')
        files = device.shell('cd $EXTERNAL_STORAGE/DCIM && find "$PWD" -type f')
        files = files.split('\n')
        files = [item.strip() for item in files]
        if not files:
            logging.error('There are no items in DCIM directory on phone')
            pass
        else:
            for num, item in enumerate(files):
                sg.OneLineProgressMeter('Extraction', num + 1, len(files), 'key', 'Extraction des éléments DCIM')
                try:
                    filename = os.path.basename(item)
                    final_path = os.path.join(raw_dir, filename)
                    device.pull(item, final_path)
                    path_in_csv_dir = os.path.join(csv_dir_resources, filename)
                    pic_list.append({'phone_fpath': item, 'csv_fpath': path_in_csv_dir})
                except FileNotFoundError:
                    pass
        logging.info('Finished retrieving elements from DCIM folder')

        # List all the files in the Pictures folder on the phone and create the paths for the ADB pull
        logging.info('Starting to retrieve all elements from Pictures')
        files = device.shell('cd $EXTERNAL_STORAGE/Pictures && find "$PWD" -type f')
        files = files.split('\n')
        files = [item.strip() for item in files]
        if not files:
            logging.error('There are no items in Pictures directory on phone')
            pass
        else:
            for num, item in enumerate(files):
                sg.OneLineProgressMeter('Extraction', num + 1, len(files), 'key', 'Extraction des éléments dans Pictures')
                try:
                    filename = os.path.basename(item)
                    final_path = os.path.join(raw_dir, filename)
                    device.pull(item, final_path)
                    path_in_csv_dir = os.path.join(csv_dir_resources, filename)
                    pic_list.append({'phone_fpath': item, 'csv_fpath': path_in_csv_dir})
                except FileNotFoundError:
                    pass
        logging.info('Finished retrieving elements from Pictures')

    # Kill ADB server
    subprocess.call("adb.exe kill-server", shell=True)
    logging.info('Killing ADB server')
    close_popup(window)
    logging.info('Finished creating and fetching data through ADB')
    os.chdir(script_dir)

    return phone_make, phone_model


def prepare_case_data(values, phone_make, phone_model):
    """Prepare the data that will go in the cas information file and html index"""

    logging.info('Preparing case information')
    extra_data_dict = dict()
    index_values_list = ['una', 'affaire', 'num_scelle', 'desc_scelle', 'examiner']
    for key, value in values.items():
        if key in index_values_list:
            if value == '':
                extra_data_dict[key] = 'Non renseigné'
            else:
                extra_data_dict[key] = value
    extra_data_dict['brand_tel'] = phone_make
    extra_data_dict['model_tel'] = phone_model
    extra_data_dict['date'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    logging.info('Finished preparing case information')
    return extra_data_dict


def prepare_data(values, case_data):
    """Prepare all the files for examination"""

    def change_date(old_file, new_file):
        """Change the dates in the raw csv files"""

        new_content = list()
        with open(old_file, encoding='utf-8') as f:
            content = csv.DictReader(f)
            for row in content:
                row = dict(row)
                if 'date' in row.keys():
                    if os.path.basename(old_file) == 'MMS.csv':
                        row['date'] = datetime.fromtimestamp(int(row['date'])).strftime('%d-%m-%Y %H:%M:%S')
                    else:
                        row['date'] = datetime.fromtimestamp(int(row['date']) / 1000).strftime('%d-%m-%Y %H:%M:%S')
                if 'date_sent' in row.keys():
                    if os.path.basename(old_file) == 'MMS.csv':
                        row['date_sent'] = datetime.fromtimestamp(int(row['date_sent'])).strftime('%d-%m-%Y %H:%M:%S')
                    else:
                        row['date_sent'] = datetime.fromtimestamp(int(row['date_sent']) / 1000).strftime(
                            '%d-%m-%Y %H:%M:%S')
                if 'last_time_contacted' in row.keys():
                    try:
                        if os.path.basename(old_file) == 'MMS.csv':
                            row['last_time_contacted'] = datetime.fromtimestamp(
                                int(row['last_time_contacted'])).strftime('%d-%m-%Y %H:%M:%S')
                        else:
                            row['last_time_contacted'] = datetime.fromtimestamp(
                                int(row['last_time_contacted']) / 1000).strftime('%d-%m-%Y %H:%M:%S')
                    except ValueError:
                        pass
                new_content.append(row)
        with open(new_file, 'w', encoding='utf-8', newline='') as f:
            csv_dict_writer = csv.DictWriter(f, fieldnames=new_content[0].keys())
            csv_dict_writer.writeheader()
            for row in new_content:
                csv_dict_writer.writerow(row)

    # Create the CSV files directory and html report directory if chosen
    logging.info('Preparing and formatting files')
    window = popup_working('Préparation des fichiers')
    os.mkdir(csv_dir)
    os.mkdir(csv_dir_resources)
    # Create report directories and support files if the option was chosen
    os.mkdir(report_dir)
    os.mkdir(html_resource_dir)
    os.mkdir(html_internal_dir)
    for key, value in data_dict['report_images'].items():
        file_path = os.path.join(html_internal_dir, key)
        byte_value = value.encode('ascii')
        binary_value = base64.b64decode(byte_value)
        with open(file_path, 'wb') as f:
            f.write(binary_value)
    # Change dates for each file then save the new csv file
    try:
        change_date(raw_call_log, call_log_final)
        logging.info('Successfully changed dates in {}'.format(raw_call_log))
    except:
        logging.exception('Error changing dates in {}'.format(raw_call_log))
        pass

    try:
        change_date(raw_mms, mms_final)
        logging.info('Successfully changed dates in {}'.format(raw_mms))
    except:
        logging.exception('Error changing dates in {}'.format(raw_mms))
        pass

    try:
        change_date(raw_sms, sms_final)
        logging.info('Successfully changed dates in {}'.format(raw_sms))
    except:
        logging.exception('Error changing dates in {}'.format(raw_sms))
        pass

    try:
        change_date(raw_contacts, contacts_final)
        logging.info('Successfully changed dates in {}'.format(raw_contacts))
    except:
        logging.exception('Error changing dates in {}'.format(raw_contacts))
        pass

    # Copy forensic files that don't contain dates
    try:
        with open(raw_info, encoding='utf8') as fr, open(info_final, 'w', encoding='utf8') as fw:
            content = fr.read()
            content = content.replace('&', '&amp;').replace('<3', '#COEUR#')
            fw.write(content)
        logging.info('Successfully copied {}'.format(raw_info))
    except:
        logging.exception('Error copying {}'.format(raw_info))
        pass

    try:
        shutil.copy2(raw_mmsparts, mmsparts_final)
        logging.info('Successfully copied {}'.format(raw_mmsparts))
    except:
        logging.exception('Error copying {}'.format(raw_mmsparts))
        pass

    # Copy all non forensics files
    for root, _, files in os.walk(raw_dir):
        for num, filename in enumerate(files):
            sg.OneLineProgressMeter('Copy', num + 1, len(files), 'key', 'Copie des fichiers')
            full_path = os.path.join(root, filename)
            if full_path not in raw_forensic_file_list:
                new_path = os.path.join(html_resource_dir, filename)
                shutil.copy2(full_path, new_path)
                new_path = os.path.join(csv_dir_resources, filename)
                shutil.copy2(full_path, new_path)

    # Write case data to file
    formatted_case_data = """Date et heure de l'extraction: {}
U.N.A: {}
Affaire: {}
N° du scellé: {}
Description du scellé: {}
Marque du téléphone: {}
Modèle du téléphone: {}
Personne quallifiée: {}""".format(case_data['date'], case_data['una'], case_data['affaire'], case_data['num_scelle'],
                                  case_data['desc_scelle'], case_data['brand_tel'],case_data['model_tel'],
                                  case_data['examiner'])
    case_data_file = os.path.join(csv_dir, 'Informations.txt')
    with open(case_data_file, 'w', encoding='utf8') as f:
        f.write(formatted_case_data)

    close_popup(window)
    logging.info('Finished preparing and formatting files')


def extract_data(case_data):
    # Get a list of files in forensics dir
    forensics_file_list = csv_forensic_file_list

    # Define number:name dictionnary
    id_dict = dict()
    
    # Get phone info and apps
    logging.info('Starting phone information and application information extraction')
    window = popup_working('Lecture des informations du téléphone et des applications')
    info_tel = list()
    programs_list = list()
    # Récupération des informations du téléphone et des programmes
    try:
        fichier_info = etree.parse(forensics_file_list[2])
        info_tel.append(['Marque', case_data['brand_tel']])
        info_tel.append(['Modèle', case_data['model_tel']])
        # Get phone info from info.xml
        for donnee in fichier_info.xpath("/android-forensics/IMSI"):
            imsi = str(donnee.text)
            info_tel.append(['ISMI', imsi])
        for donnee in fichier_info.xpath("/android-forensics/IMEI-MEID"):
            imei = str(donnee.text)
            info_tel.append(['IMEI', imei])
        for donnee in fichier_info.xpath("/android-forensics/MSISDN-MDN"):
            msisdn = str(donnee.text)
            info_tel.append(['MSISDN', msisdn])
        for donnee in fichier_info.xpath("/android-forensics/ICCID"):
            iccid = str(donnee.text)
            info_tel.append(['ICCID', iccid])
        for donnee in fichier_info.xpath("/android-forensics/build/version.release"):
            android_version = str(donnee.text)
            info_tel.append(['Version d\'ANDROID', android_version])
        info_tel.insert(0, ['Catégorie', 'Valeur'])

        # Get apps list
        for application in fichier_info.xpath("/android-forensics/applications/app"):
            for repertoire in application.xpath("sourceDir"):
                if repertoire.text.split('/')[1] == "data":
                    info_list = list()
                    for nom in application.xpath("label"):
                        app = str(nom.text).replace('&amp;', '&').replace('#COEUR#', '<3')
                        info_list.append(app)
                    for package_name in application.xpath('packageName'):
                        app_package_name = str(package_name.text)
                        package_link = '<a href="https://play.google.com/store/apps/details?id={0}" target="_blank">{0}</a>'.format(app_package_name)
                        info_list.append(package_link)
                    programs_list.append(info_list)
        programs_list.sort(key=lambda x: x[0])
        programs_list_headers = ['Nom de l\'application', 'Lien PlayStore']
        programs_list.insert(0, programs_list_headers)
    except:
        logging.exception('There was an error parsing {}'.format(forensics_file_list[2]))
        info_tel = ['']
        programs_list = ['']
        pass

    summary_list.append(['<a href="{}">Applications</a>'.format(apps), str(len(programs_list))])
    close_popup(window)
    logging.info('Finished parsing phone information and application information')

    # Start Contact extraction
    logging.info('Starting Contact extraction')
    window = popup_working('Lecture des contacts')
    contact_list = list()
    contact_headers = ['name', 'number', 'starred']
    # Get contact information for report
    try:
        with open(forensics_file_list[1], encoding='utf-8', newline='') as f:
            content = csv.DictReader(f)
            for row in content:
                try:
                    info_list = list()
                    for key, value in row.items():
                        if key in contact_headers:
                            if key == 'starred':
                                if value == '0':
                                    info_list.append('Non')
                                else:
                                    info_list.append('Oui')
                            else:
                                info_list.append(value)
                    info_list.insert(0, info_list.pop(len(info_list) - 1))
                    contact_list.append(info_list)
                    id_dict[row['number'].replace(' ', '')] = row['name']
                except:
                    logging.exception('There was an error parsing contact information in {}'.format(row))
                    continue
        contact_list.sort(key=operator.itemgetter(0))
        contact_headers = ['Nom', 'Numéro', 'Favori']
        contact_list.insert(0, contact_headers)
    except:
        logging.exception('There was an error opening {}'.format(forensics_file_list[1]))
        contact_list = ['']
        pass

    summary_list.append(['<a href="{}">Contacts</a>'.format(contacts), str(len(contact_list) - 1)])
    close_popup(window)
    logging.info('Finished parsing contact data')

    # Get Call Logs information
    logging.info('Starting Call Logs extraction')
    window = popup_working('Lecture des Journaux d\'appels')
    try:
        with open(forensics_file_list[0], encoding='utf-8', newline='') as f:
            call_logs_list = list()
            call_logs_headers = ['_id', 'number', 'date', 'duration', 'type']
            content = csv.DictReader(f)
            for row in content:
                try:
                    info_list = list()
                    for key, value in row.items():
                        if key in call_logs_headers:
                            if key == 'type':
                                if value == '1':
                                    bg_color = '#9de89d'
                                    info_list.append(['Reçu', bg_color])
                                elif value == '2':
                                    bg_color = '#ffe591'
                                    info_list.append(['Emis', bg_color])
                                elif value == '3':
                                    bg_color = '#a8d5ff'
                                    info_list.append(['Manqué', bg_color])
                                elif value == '4':
                                    info_list.append('Messagerie Vocale')
                                elif value == '5':
                                    info_list.append('Rejeté')
                                elif value == '6':
                                    info_list.append('Liste des refusés')
                                else:
                                    info_list.append('Inconnu')
                            elif key == 'number':
                                info_list.append(value)
                                if row['name'] == '':
                                    if value in id_dict.keys():
                                        name = id_dict[value]
                                    else:
                                        name = ''
                                else:
                                    name = row['name']
                            elif key == 'duration':
                                raw_time = value
                                formatted_time = str(timedelta(seconds=int(raw_time)))
                                info_list.append(formatted_time)
                            else:
                                info_list.append(value)
                    info_list.insert(1, name)
                    call_logs_list.append(info_list)
                except:
                    logging.exception('There was an error parsing call log {}'.format(row))
                    continue
        call_logs_headers = ['Identifiant', 'Nom', 'Numéro', 'Date et heure', 'Durée', 'Type']
        call_logs_list.insert(0, call_logs_headers)
    except:
        logging.exception('There was an error opening {}'.format(forensics_file_list[0]))
        call_logs_list = ['']
        pass
    summary_list.append(['<a href="{}">Journaux d\'Appels</a>'.format(call_logs), str(len(call_logs_list) - 1)])
    close_popup(window)
    logging.info('Finished parsing call log data')

    # Get SMS information
    logging.info('Starting SMS extraction')
    window = popup_working('Lecture des SMS')
    try:
        with open(forensics_file_list[5], encoding='utf-8', newline='') as f:
            sms_list = list()
            sms_headers = ['_id', 'address', 'date', 'read', 'type', 'body']
            content = csv.DictReader(f)
            for row in content:
                try:
                    info_list = list()
                    for key, value in row.items():
                        if key in sms_headers:
                            if key == 'read':
                                if value == '1':
                                    info_list.append('Oui')
                                else:
                                    info_list.append('Non')
                            elif key == 'type':
                                if value == '1':
                                    info_list.append('Reçu')
                                elif value == '2':
                                    info_list.append('Emis')
                                else:
                                    info_list.append('Autre')
                            elif key == 'body':
                                value1 = textwrap.fill(value, 50)
                                if row['type'] == '1':
                                    bg_color = '#9de89d'
                                    info_list.append([value1, bg_color])
                                elif row['type'] == '2':
                                    bg_color = '#ffe591'
                                    info_list.append([value1, bg_color])
                                else:
                                    info_list.append(value1)
                            elif key == 'address':
                                if value in id_dict.keys():
                                    info_list.append(id_dict[value])
                                    info_list.append(value)
                                else:
                                    info_list.append('Inconnu')
                                    info_list.append(value)
                            else:
                                info_list.append(value)
                    sms_list.append(info_list)
                except:
                    logging.exception('There was an error parsing SMS {}'.format(row))
                    continue

        # get thread_id:name dict for mms display
        asso_mms_contact = dict()
        with open(forensics_file_list[5], encoding='utf-8', newline='') as f:
            content = csv.DictReader(f)
            for row in content:
                # row = dict(row)
                for key, value in row.items():
                    if key == 'address':
                        if value in id_dict.keys():
                            contact = id_dict[value]
                        else:
                            contact = value
                    elif key == 'thread_id':
                        tid = value
                asso_mms_contact[tid] = contact

        sms_headers = ['Identifiant', 'Nom Contact', 'Numéro', 'Date et heure', 'Lu', 'Type', 'Message']
        sms_list.insert(0, sms_headers)
    except:
        logging.error('There was an error opening {}'.format(forensics_file_list[5]))
        sms_list = ['']

    summary_list.append(['<a href="{}">SMS</a>'.format(sms), str(len(sms_list) - 1)])
    close_popup(window)
    logging.info('Finished parsing SMS data')

    # Get MMS data
    logging.info('Starting MMS extraction')
    window = popup_working('Lecture des MMS')
    try:
        with open(forensics_file_list[3], encoding='utf8', newline='') as f:
            info_mms_dict = dict()
            mms_headers = ['_id', 'thread_id', 'date', 'msg_box', 'read']
            content = csv.DictReader(f)
            for row in content:
                try:
                    info_list = list()
                    for key, value in row.items():
                        if key in mms_headers:
                            if key == 'read':
                                if value == '1':
                                    info_list.append('Oui')
                                else:
                                    info_list.append('Non')
                            elif key == 'msg_box':
                                if value == '1':
                                    info_list.append('Reçu')
                                else:
                                    info_list.append('Emis')
                            elif key == 'thread_id':
                                if value in asso_mms_contact:
                                    info_list.append(asso_mms_contact[value])
                                else:
                                    info_list.append('Inconnu')
                            elif key == '_id':
                                info_list.append(value)
                                numero = value
                            else:
                                info_list.append(value)
                    info_mms_dict[numero] = info_list
                except:
                    logging.exception('There was an error parsing MMS {}'.format(row))
                    continue
        logging.info('Finished parsing MMS data')

        # Get MMSParts data
        logging.info('Starting MMSParts extraction')
        parts_dict = dict()
        with open(forensics_file_list[4], encoding='utf8', newline='') as f:
            content = csv.DictReader(f)
            for row in content:
                if row['seq'] != '-1':
                    numero = row['mid']
                    # Show plain text in browser
                    if row['ct'] == 'text/plain':
                            if numero in parts_dict:
                                parts_dict[numero].append(row['text'])
                            else:
                                parts_dict[numero] = [row['text']]
                    # Show image in browser if possible
                    elif row['ct'] == 'image/jpeg' or row['ct'] == 'image/gif' or row['ct'] == 'image/png':
                        try:
                            image_path = 'Resources/{}'.format(row['cl'])
                            if row['cl'] != '':
                                html_image_element = '<a href="{0}" target="_blank"><img src="{0}" width="100" height="100" title="{0}" onerror="this.src=\'{1}\'"></a><br /><a href="{0}" target="_blank">{0}</a>'.format(image_path, file_not_found_rel_path)
                                if numero in parts_dict:
                                    parts_dict[numero].append(html_image_element)
                                else:
                                    parts_dict[numero] = [html_image_element]
                            else:
                                html_image_element = '<img src="{0}" width="100" height="100" title="{0}">'.format(file_not_found_rel_path)
                                if numero in parts_dict:
                                    parts_dict[numero].append(html_image_element)
                                else:
                                    parts_dict[numero] = [html_image_element]
                        except (TypeError, FileNotFoundError) as e:
                            if numero not in parts_dict.keys():
                                parts_dict[numero] = ['(Image introuvable)']
                    # Show video icon with link in browser if possible
                    elif 'video' in row['ct']:
                        video_path = 'Resources/{}'.format(row['cl'])
                        if row['cl'] != '':
                            html_video_element = '<a href="{1}" target="_blank"><img src="{0}" width="100" height="100"></a><br /><a href="{1}" target="_blank">{1}</a>'.format(video_icon_rel_path, video_path)
                            if numero in parts_dict:
                                parts_dict[numero].append(html_video_element)
                            else:
                                parts_dict[numero] = [html_video_element]
                        else:
                            html_video_not_found = '<img src="{0}" width="100" height="100">'.format(video_not_found_rel_path)
                            if numero in parts_dict:
                                parts_dict[numero].append(html_video_not_found)
                            else:
                                parts_dict[numero] = [html_video_not_found]
                    # Show audio icon with link in browser if possible
                    elif 'audio' in row['ct']:
                        audio_path = 'Resources/{}'.format(row['cl'])
                        if row['cl'] != '':
                            html_audio_element = '<a href="{1}" target="_blank"><img src="{0}" width="100" height="100"></a><br /><a href="{1}" target="_blank">{1}</a>'.format(audio_icon_rel_path, audio_path)
                            if numero in parts_dict:
                                parts_dict[numero].append(html_audio_element)
                            else:
                                parts_dict[numero] = [html_audio_element]
                        else:
                            html_audio_not_found = '<img src="{0}" width="100" height="100">'.format(audio_not_found_rel_path)
                            if numero in parts_dict:
                                parts_dict[numero].append(html_audio_not_found)
                            else:
                                parts_dict[numero] = [html_audio_not_found]

                    else:
                        if row['cl'] != '':
                            other_element_path = os.path.join('Resources', row['cl'])
                            html_other_element = '<a href="{0}" target="_blank">{0}</a>'.format(other_element_path)
                            if numero in parts_dict.keys():
                                parts_dict[numero].append(html_other_element)
                            else:
                                parts_dict[numero] = [html_other_element]
                        else:
                            html_other_element = '<p>*****Le contenu du MMS est de type "{}". Il n\'a pas été extrait du téléphone*****</p>'.format(row['ct'])
                            if numero in parts_dict.keys():
                                parts_dict[numero].append(html_other_element)
                            else:
                                parts_dict[numero] = [html_other_element]

        logging.info('Finished parsing MMSParts data')

        logging.info('Merging MMS and MMSParts data')
        # Fix mmsparts dict
        for key, value in parts_dict.items():
            if len(value) > 1 and value[0] == '':
                del value[0]
            formatted_string = '<br />'.join(value)
            parts_dict[key] = formatted_string

        # Merge MMS and MMSParts data
        logging.info('Merging MMS and MMSParts')
        mms_list = list()
        for key, value in info_mms_dict.items():
            if key in parts_dict.keys():
                if info_mms_dict[key][3] == 'Emis':
                    bg_color = '#ffe591'
                    value = value + [[parts_dict[key], bg_color]]
                else:
                    bg_color = '#9de89d'
                    value = value + [[parts_dict[key], bg_color]]
                mms_list.append(value)
        mms_list.sort(key=lambda x: datetime.strptime(x[2], '%d-%m-%Y %H:%M:%S'), reverse=True)
        mms_header = ['N°', 'Contact', 'Date - Heure', 'Type', 'Lu', 'Message']
        mms_list.insert(0, mms_header)
    except:
        logging.exception('There was an error opening {} or {}'.format(forensics_file_list[3], forensics_file_list[4]))
        mms_list = ['']

    summary_list.append(['<a href="{}">MMS</a>'.format(mms), str(len(mms_list) - 1)])
    close_popup(window)
    logging.info('Finished merging MMS and MMSParts data')

    # Sort the summary list and append it to the case data dict
    summary_list.insert(len(summary_list) - 1, summary_list.pop(0))
    summary_headers = ['Catégorie', 'Nombre']
    summary_list.insert(0, summary_headers)
    case_data['summary'] = summary_list

    return contact_list, call_logs_list, sms_list, programs_list, info_tel, mms_list, case_data


def get_all_numbers_communicated(call_logs_data, sms_data, mms_data):
    logging.info('Starting to gather all numbers who communicated with the phone')
    # Gather all the phone numbers in all the data sets
    try:
        numbers_set = set()
        for entry in call_logs_data[1:]:
            formatted_number = entry[2].replace('+33', '0')
            try:
                tmp = int(formatted_number)
                if len(formatted_number) == 10 or len(formatted_number) == 12:
                    numbers_set.add(formatted_number)
            except ValueError:
                continue
        for entry in sms_data[1:]:
            formatted_number = entry[2].replace('+33', '0')
            try:
                tmp = int(formatted_number)
                if len(formatted_number) == 10 or len(formatted_number) == 12:
                    numbers_set.add(formatted_number)
            except ValueError:
                continue
        for entry in mms_data:
            formatted_number = entry[1].replace('+33', '0')
            try:
                tmp = int(formatted_number)
                if len(formatted_number) == 10 or len(formatted_number) == 12:
                    numbers_set.add(formatted_number)
            except ValueError:
                continue
        numbers_list = list(numbers_set)
        # Write them to file
        with open(num_list_file, 'w', encoding='utf8', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['Numéro'])
            for num in numbers_list:
                csv_writer.writerow([num])
    except:
        logging.exception('There was an error collecting all the phone numbers')
        pass

    logging.info('Finished gathering all the phone numbers and writing them to file')


def get_pic_exifdata(case_data):
    """Get the exif data for each image and append it to each image in pic_list"""

    def process_gps_coords(coord):
        """Process GPS coordinates"""
        coord_deg = 0
        for count, values in enumerate(coord):
            coord_deg += (float(values[0]) / values[1]) / 60 ** count
        return coord_deg

    def format_gps_data(gps_data_dict):
        """Format GPS data into human readable decimal GPS coordinates"""

        # Format GPS data
        raw_gps_dict = {}
        for key, value in gps_data_dict.items():
            decode = GPSTAGS.get(key, key)
            raw_gps_dict[decode] = value

        # Get the latitude GPS data in decimal form
        latitude = process_gps_coords(raw_gps_dict['GPSLatitude'])
        latitude_ref = raw_gps_dict['GPSLatitudeRef'] == u'N'
        if not latitude_ref:
            latitude = latitude * -1

        # Get the longitude GPS data in decimal form
        longitude = process_gps_coords(raw_gps_dict['GPSLongitude'])
        longitude_ref = raw_gps_dict['GPSLongitudeRef'] == u'E'
        if not longitude_ref:
            longitude = longitude * -1
        if latitude == 0 and longitude == 0:
            return ''
        gps_data = '{} {}'.format(longitude, latitude)
        return gps_data

    logging.info('Starting to extract exif data from images')

    # Extract all exif data from the images (will also detect which files are not images)
    exifdata_category_list = [
        'Filename',
        'DateTime',
        'DateTimeDigitized',
        'DateTimeOriginal',
        'Make',
        'Model',
        'GPSInfo',
        'LensMake',
        'LensModel',
        'Software'
    ]

    for i, image in enumerate(pic_list, 0):
        sg.OneLineProgressMeter('Exif', i + 1, len(pic_list), 'key', 'Extraction des données exif des images')
        # Try to extract exif data from the file
        try:
            im = Image.open(image['csv_fpath'])
            exif = im.getexif()
            exif_data = dict()
            for name, value in exif.items():
                tag = TAGS.get(name, name)
                if tag in exifdata_category_list:
                    if tag == 'GPSInfo':
                        try:
                            value = format_gps_data(value)
                        except KeyError:
                            continue
                    if 'Date' in tag:
                        value = datetime.strptime(value, '%Y:%m:%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
                    value = value.replace('\n', '').replace('\0', '') if isinstance(value, str) else value
                    exif_data[tag] = value

            # Associate string formatted exif data with it's corresponding image
            formatted_exif = str()
            for key, value in exif_data.items():
                formatted_exif += '{}: {}<br />'.format(key, value)
            image['exif'] = formatted_exif

        # If Image.open cannot open the file then it is not an image, remove it from list
        except:
            del pic_list[i]
            continue
    logging.info('Finished retrieving all the exif data')

    # Now that image data is complete, format it into a list for HTML report
    final_pic_list = list()
    for image in pic_list:
        basename = os.path.basename(image['csv_fpath'])
        html_path = os.path.join('Resources', basename)
        html_image_path = '<a href="{0}" target="_blank"><img src="{0}" width="100" height="100" title="{0}" onerror="this.src=\'{1}\'"></a>'.format(html_path, file_not_found_rel_path,)
        try:
            formatted_list = [html_image_path, image['phone_fpath'], image['exif']]
        except KeyError:
            formatted_list = [image['phone_fpath'], html_image_path, 'Aucune information exif n\'a été trouvée']
        final_pic_list.append(formatted_list)
    final_pic_list.sort(key=lambda x: x[1])
    final_pic_list.insert(0, ['Cheminement Sur le Téléphone', 'Image', ''])

    case_data['summary'].insert(len(case_data['summary']) - 1, ['<a href="{}">Images</a>'.format(images), len(final_pic_list)])
    return final_pic_list


def generate_html(file_content, title, values, type='table', page='default', extra_data=dict()):
    """Create the HTML report files"""

    def make_html_element(type, content='', link_name='', image_width='100', image_height='100', link_target='_blank'):
        """Creates the different HTML entities"""
        # Function to divide table list into chunks of 18
        def list_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        if type == 'h1':
            html_list.append('<h1>{}</h1>'.format(content))
        elif type == 'linebreak':
            html_list.append('<p>&nbsp;</p>')
        elif type == 'h2':
            html_list.append('<h2>{}</h2>'.format(content))
        elif type == 'table':
            table_list = list()
            table_list.append('<table>')
            count = 0
            for row in content:
                # Check of body contains background color and extract it
                if isinstance(row[-1], list):
                    formatted_body = row[-1]
                    bg_color = formatted_body[-1]
                    body = formatted_body[0]
                    del row[-1]
                    row.insert(len(row), body)
                else:
                    bg_color = '#CECECE'

                # Get the table headers
                if count == 0:
                    table_list.append('<thead>')
                    table_list.append('<tr>')
                    column_index = 0
                    for item in row:
                        table_list.append('<th>{}</th>'.format(item))
                    table_list.append('</tr>')
                    table_list.append('</thead>')
                    count += 1
                # Get the rest of the content
                else:
                    table_list.append('<tr style="background-color: {};">'.format(bg_color))
                    for item in row:
                        table_list.append('<td>{}</td>'.format(item))
                    table_list.append('</tr>')
            table_list.append('</table>')
            table = '\n'.join(table_list)
            html_list.append(table)
        elif type == 'image':
            html_list.append(
                '<p><img src="{}" alt="Impossible d\'afficher l\'image" width="{}" height="{}" /></p>'.format(content,
                                                                                                              image_width,
                                                                                                              image_height))
        elif type == 'link':
            html_list.append('<p><a href="{0}" target="{2}">{1}</a></p>'.format(content, link_name, link_target))
        elif type == 'list':
            formatted_list = list(list_chunks(content, 20))
            for section in formatted_list:
                html_list.append('<div style="width:175px; height:550px; float:left; margin-right:30px">')
                html_list.append('<ul>')
                for item in section:
                    html_list.append('<li style="font-size:12px">{}</li>'.format(item))
                html_list.append('</ul>')
                html_list.append('</div>')

    def finalize_html(filename):
        """Insert the final formalities in the html list and write the HTML file"""
        html_list.insert(0, '<html>')
        html_list.insert(1, '<head>')
        html_list.insert(2, '<style>{}</style>'.format(table_css_style))
        html_list.insert(3, '</head>')
        html_list.insert(len(html_list), '</html>')
        # Write HTML file to report directory
        with open(filename, 'w', encoding='utf8') as f:
            f.write('\n'.join(html_list))

    # Start generating HTML file
    logging.info('Starting to generate HTML report for {}'.format(title))
    # Define paths to create the html file
    html_filename = title + '.html'
    current_html_path = os.path.join(report_dir, html_filename)
    try:
        global html_list
        del html_list
        html_list = list()
        html_list.append('<div class="column left">')
        make_html_element('image', index_image_path, image_width='150', image_height='150')
        make_html_element('h2', 'Index')
        make_html_element('link', index, link_name='Page d\'Accueil', link_target='')
        make_html_element('link', tel_info, link_name='Infos Tel', link_target='')
        make_html_element('link', contacts, link_name='Contacts', link_target='')
        make_html_element('link', call_logs, link_name='Journaux d\'Appels', link_target='')
        make_html_element('link', sms, link_name='SMS', link_target='')
        make_html_element('link', mms, link_name='MMS', link_target='')
        if values['images']:
            make_html_element('link', images, link_name='Images', link_target='')
        make_html_element('link', apps, link_name='Applications', link_target='')
        html_list.append('</div>')
        html_list.append('<div class="column middle">')

        if page == 'index':
            html_list.append('<h1><font size="24"><center>{}</center></font></h1>'.format(title))
            html_list.append('<h1><center>Extraction du téléphone {} modèle {} en date du {}</center></h1>'.format(
                extra_data['brand_tel'], extra_data['model_tel'], extra_data['date']))
            html_list.append('<div>')
            html_list.append('<div style="width:400px; float:left; margin-left:50px">')
            html_list.append('<h2><u>Informations Générales:</u></h2>')
            html_list.append('<p>Date de l\'extraction: {}</p>'.format(extra_data['date']))
            html_list.append('<p>U.N.A: {}</p>'.format(extra_data['una']))
            html_list.append('<p>Affaire: {}</p>'.format(extra_data['affaire']))
            html_list.append('<p>N° du scellé: {}</p>'.format(extra_data['num_scelle']))
            html_list.append('<p>Description du scellé: {}</p>'.format(extra_data['desc_scelle']))
            html_list.append('<p>Marque du téléphone: {}</p>'.format(extra_data['brand_tel']))
            html_list.append('<p>Modèle du téléphone: {}</p>'.format(extra_data['model_tel']))
            html_list.append('<p>Personne qualifiée: {}</p>'.format(extra_data['examiner']))
            html_list.append('</div>')
            html_list.append('<div style="float:left">')
            html_list.append('<h2><u>Résumé de l\'Extraction:</u></h2>')
            make_html_element(type, extra_data['summary'])
            html_list.append('</div>')
            html_list.append('</div>')

        elif page == 'default':
            make_html_element('h1', title)
            make_html_element(type, file_content)
        html_list.append('</div>')
        finalize_html(current_html_path)
        logging.info('Finished generating {}'.format(current_html_path))
    except:
        logging.exception('Error creating {}'.format(current_html_path))
        return


def cleanup():
    file_list = list()
    for root, _, files in os.walk(raw_dir):
        for item in files:
            file_path = os.path.join(root, item)
            file_list.append(file_path)
    for files in file_list:
        os.remove(files)
    os.rmdir(raw_dir)


def main():
    """Main script function"""

    values = tel_xtract_gui()
    phone_make, phone_model = get_info(values)
    # phone_make = 'a'
    # phone_model = 'a'
    case_data = prepare_case_data(values, phone_make, phone_model)
    prepare_data(values, case_data)
    contact_data, call_logs_data, sms_data, program_data, tel_data, mms_data, case_data = extract_data(case_data)
    get_all_numbers_communicated(call_logs_data, sms_data, mms_data)
    window = popup_working('Création du rapport')
    if values['images']:
        pic_data = get_pic_exifdata(case_data)
        generate_html(pic_data, 'Images', values)
    generate_html('', 'Index', values, page='index', extra_data=case_data)
    generate_html(tel_data, 'Infos Tel', values)
    generate_html(contact_data, 'Contacts', values)
    generate_html(call_logs_data, 'Journaux d\'Appels', values)
    generate_html(sms_data, 'SMS', values)
    generate_html(program_data, 'Applications', values)
    generate_html(mms_data, 'MMS', values)
    close_popup(window)
    # cleanup()
    logging.info('Program finished executing. Exiting.')
    # Define the application finish time and log the total runtime
    end_time = time.time()
    logging.info('Total application runtime: {} seconds'.format(end_time - start_time))
    sg.Popup('Terminé!')


if __name__ == '__main__':
    main()
