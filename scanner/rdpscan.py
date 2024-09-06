#!/usr/bin/env python3
# ~WAiv3d @ github.com/waived/rdp-vnc-finder
from scapy.all import *
from colorama import Fore
import os, sys, socket, time, threading, random

_online = []

_svcs = [
    '3389',  # WinRDP, RemotePC, Zoho, MobaXterm
    '5800',  # UltraVNC (JavaViewer), TightVNC
    '5900',  # VNC Viewer, UltraVNC, TigerVNC, TightVNC
    '5938',  # TeamViewer
    '4000',  # NXServer
    '4489',  # Radmin
    '6129',  # Dameware
    '6568',  # AnyDesk 
    '7070',  # AnyDesk
    '8040',  # ConnectWise
    '21115', # RustDesk
    '21116', # RustDesk
    '21117', # RustDesk
    '21118', # RustDesk (web)
    '21119'  # RustDesk (web)
]

def _done():
    time.sleep(1)
    
    if len(_online) != 0:
        while True:
            try:
                y = input('Save results to .txt file? (Y/n): ')
                if y.lower() == 'y':
                    # save scan results to .txt file
                    
                    _path = input('Path (ex- /tmp/my_results.txt): ')
                    
                    with open(_path, 'w') as file:
                        for _line in my_list:
                            file.write(_line + '\n')
                            
                    break
                else:
                    break
            except KeyboardInterrupt:
                sys.exit('\r\nAborted.\r\n')
            except:
                print('Error! Try again...')
    
    sys.exit(Fore.WHITE + '\r\nScan complete!')

def _scan(_ip, _prt, _tout):
    global _active 
    
    _active +=1
    try:
        response = sr1(IP(dst=_ip)/TCP(dport=int(_prt), flags="S"), timeout=int(_tout), verbose=0)
        if response and response.haslayer(TCP):
            if response[TCP].flags == 0x12:
                # open
                print(Fore.GREEN + 'Possible RDP/VNC @ ' + _ipaddr + ":" + str(_prt))
                success = _ip + ":" + _prt
                global _online
                _online.append(success)
            else:
                # closed/filtered
                print(Fore.RED + 'Port ' + str(_prt) + ' closed/filered')
        else:
            #syn not received
            print(Fore.RED + 'Port ' + str(_prt) + ' closed/filered')
    except KeyboardInterrupt:
        sys.exit()
    except:
        pass
    finally:
        _active -= 1
        
def main():
    os.system("clear")
    
    if not os.geteuid() == 0:
        sys.exit("\r\nScript requires root elevation!\r\n")
    
    global _active
    
    print(Fore.WHITE + '''
░█▀█░█▀▄░█▀█░░░▄▀░█░█░█▀█░█▀▀░░░█▀▀░▀█▀░█▀█░█▀▄░█▀▀░█▀█░
░█▀▄░█░█░█▀▀░░▄▀░░▀▄▀░█░█░█░░░░░█▀▀░░█░░█░█░█░█░█▀▀░█▀▄░
░▀░▀░▀▀░░▀░░░▄▀░░░░▀░░▀░▀░▀▀▀░░░▀░░░▀▀▀░▀░▀░▀▀░░▀▀▀░▀░▀░
''')

    # gather user input
    try:
        _stop = int(input('IPs to generate/probe: '))        
        _tout = int(input('Connection timeout (seconds): '))
        _thdz = int(input('# of threads (default 5): '))
        
        input('\r\nReady? Strike <ENTER> to scan and <CTRL+C> to abort...\r\n')
    except KeyboardInterrupt:
        sys.exit('\r\nAborted.\r\n')
    except:
        main()
    
    _max = 0      # indicates the cap for how many endpoints scanned
    _index = 0    # used to iterate through port list in _svcs
    _active = 0   # calculate currently running threads
    _ipaddr = ""

    # generate first endpoint
    _ipaddr = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    print(Fore.GREEN + "---> PROBING NEW HOST " + _ipaddr + " <---")
    #_stop -=1
        
    try:
        # generate / probe endpoints until _max equals _stop
        while True:
            # get next port from index of _svcs
            _port = _svcs[_index]
            
            # pause if thread-cap reached
            while True:
                if _active != _thdz:
                    break
                
            # execute new thread
            t = threading.Thread(target=_scan, args=(_ipaddr, _port, _tout))
            t.start()
            
            # once last port is scanned, generate new endpoint
            if _index == len(_svcs) - 1:
                # increase # of endpoints scanned
                _max +=1
                
                # stop scanning upon max # of endpoints scanned
                if _max == _stop:
                    # wait for any probe threads to end
                    while _active != 0:
                        pass
                        
                    # verbose result output
                    _done()
                else:
                    # wait for any probe threads to end before generating new endpoint
                    while _active != 0:
                        pass
                        
                    # generate new endpoint / reset _index
                    _ipaddr = '.'.join(str(random.randint(0, 255)) for _ in range(4))
                    print(Fore.GREEN + "---> PROBING NEW HOST " + _ipaddr + " <---")
                    _index = 0    
            else:
                # increase to pull next port from _svcs
                _index +=1
            
    except KeyboardInterrupt:
        sys.exit('\r\nAborted.\r\n')

if __name__ == "__main__":
    main()
