#!/usr/bin/env python

import os
import sys
from settings import get_settings
import smtplib
import string
from sys import argv
from sys import exit
from json import loads as jloads
import errno
from socket import error as socket_error

import mimetypes
from optparse import OptionParser
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_args():
    
    settings = get_settings()
    
    if '-c' in argv:
        for index, argument in enumerate(argv):
            if '-c' == argument:
                position = index+1
                new_settings = open(argv[position], 'r')
                overwride_settings = jloads(new_settings.read())['settings']
                tmp_dict = dict(settings, **overwride_settings )
                settings = tmp_dict         
    else:
        if argv.__len__() < 3:
            print('You need to give me at least two arguments\n')
            help()
            exit(100)
    
            if argv.__len__() == 4:
                if isinstance(argv[4], str):
                    settings['mail-body-message'] = argv[4]
            
        settings['files-to-attach'] = argv[2]
        settings['mail-destination'] = argv[1]
    
    return settings
          
def help():
    print ("Usage:\n\txmsender [DESTINATION] [FILE] \"Body Message\"")
    print ("\nExemples:")
    print ("\txmsender adm@host.com.br /tmp/relatorio \"Hello buddy\"")
    print ("\txmsender -c /home/adm/xmsender_dbreport.json")

def send_mail(settings):
    
    COMMASPACE = ', '
    
    if 'files-to-attach' in settings:
        mail = load_attachment(settings['files-to-attach'])
        msg = MIMEText(settings['mail-body-message'])
        mail.attach(msg)
    else:
        mail = MIMEText(settings['mail-body-message'])
        
    mail['Subject'] = settings['mail-subject']
    mail['From'] = settings['mail-source']
    
    mail_destination = settings['mail-destination']
    mail['To'] = COMMASPACE.join(mail_destination)
  
    try: 
        smtp = smtplib.SMTP(settings['smtp-server'])
        smtp.sendmail(settings['mail-source'], settings['mail-destination'], mail.as_string())
    except ConnectionRefusedError as serr:
        if serr.errno != errno.ECONNREFUSED:
            print(serr.strerror)
            raise serr
        
        
def load_attachment(filesToAttach):
    outer = MIMEMultipart()
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    if os.path.isdir(filesToAttach):
        for filename in os.listdir(filesToAttach):
            file_path = os.path.join(filesToAttach, filename)
            if not os.path.isfile(file_path):
                continue
            ctype, encoding = mimetypes.guess_type(file_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(file_path)
                mail = MIMEText(fp.read(), _subtype=subtype)
                fp.close(   )
            elif maintype == 'image':
                fp = open(file_path, 'rb')
                mail = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(file_path, 'rb')
                mail = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(file_path, 'rb')
                mail = MIMEBase(maintype, subtype)
                mail.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(mail)
            mail.add_header('Content-Disposition', 'attachment', filename=filename)
            outer.attach(mail)
    else:
        file_path = filesToAttach
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(file_path)
            mail = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(file_path, 'rb')
            mail = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(file_path, 'rb')
            mail = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(file_path, 'rb')
            mail = MIMEBase(maintype, subtype)
            mail.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(mail)
        mail.add_header('Content-Disposition', 'attachment', filename=file_path)
        outer.attach(mail)
            
    return outer
        
def main():
    settings = load_args()
    send_mail(settings)

main()

