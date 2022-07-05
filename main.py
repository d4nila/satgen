# pylint: disable=E1101,C0114
# I disabled E1101 because crayons dynamically
# generates functions such as red, green...
# You can delete this line and
# run the Pylint test and you will see it

from itertools import cycle
import webbrowser
import sys
import sqlite3
import random
import string
from tqdm import tqdm
import requests
import crayons


def extract(line, start, stop):
    """Function to extract text from string"""
    return line[start:stop].strip()


print(' _____       _       _ _ _ _       _____')
print('/  ___|     | |     | | (_) |     |  __ \\')
print('\\ `--.  __ _| |_ ___| | |_| |_ ___| |  \\/ ___ _ __  ')
print(' `--. \\/ _` | __/ _ \\ | | | __/ _ \\ | __ / _ \\ \'_ ')
print('/\\__/ / (_| | ||  __/ | | | ||  __/ |_\\ \\  __/ | | |')
print('\\____/ \\__,_|\\__\\___|_|_|_|\\__\\___|\\____/\\___|_| |_| ')
print(f'                                \
v0.1 {crayons.yellow("Caramel")} ')
print(f'Made by @biteofspace with {crayons.red("love")} ❤️\n')

phases = cycle(['-', '\\', '|', '/'])
print('Choose TLE collector mode:')
print(f'1. {crayons.cyan("Space-Track")} - more space objects, the \
account is required, little bit slower, recommended')
print(f'2. {crayons.cyan("Celestrak", bold = True)} - few objects, no \
account needed, fast, no recommended')
runmode = input('Choose mode: ')
if runmode not in ['1', '2']:
    print(crayons.red('Invalid choice'))
    sys.exit(1)
print()

if runmode == '1':
    login = input(f'Enter your {crayons.cyan("Space-Track")} login \
(Press Enter if you don\'t have an account): ')
    if not login:
        print(f'{crayons.cyan("Space-Track")} account is required.\
        Please register it and restart script')
        webbrowser.open('https://www.space-track.org/auth/createAccount')
        sys.exit(1)
    password = input(f'Enter your {crayons.cyan("Space-Track")} password: ')
    print('Trying to login...')
    lrequest = requests.post('https://www.space-track.org/ajaxauth/login',
        data = {
            'identity': login,
            'password': password
        }
    )
    if lrequest.text == '""' and \
        'chocolatechip' in lrequest.cookies.get_dict():
        print(crayons.green('Successful!'))
    else:
        print(crayons.red('Invalid login, password or bad IP!'))
        sys.exit()
    print('Trying to download TLEs list...')
    response = requests.get(
        'https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le',
        stream = True,
        cookies = lrequest.cookies
    )
    TLES = b''
    size = int(response.headers.get('content-length', 0))
    pb = tqdm(total = size, unit = 'iB', unit_scale = True)
    for data in response.iter_content(1024):
        pb.update(len(data))
        TLES += data
    pb.close()
    TLES = TLES.decode()
    TLES = {sat[0].strip()[2:]: [sat[1].strip(), sat[2].strip()] \
    for sat in list(zip(*[iter(TLES.split('\n'))] * 3))}
    print(crayons.green('Successful!') + f' Total TLEs received: {len(TLES)}')

elif runmode == '2':
    print('Trying to download TLEs list...')
    response = requests.get(
        'http://www.celestrak.com/NORAD/elements/active.txt',
        stream = True
    )
    TLES = b''
    size = int(response.headers.get('content-length', 0))
    pb = tqdm(total = size, unit = 'iB', unit_scale = True)
    for data in response.iter_content(1024):
        pb.update(len(data))
        TLES += data
    pb.close()
    TLES = TLES.decode()
    TLES = {sat[0].strip(): [sat[1].strip(), sat[2].strip()] \
    for sat in list(zip(*[iter(TLES.split('\n'))] * 3))}
    print(crayons.green('Successful!') + f' Total TLEs received: {len(TLES)}')

print()
print('Trying to download SATCAT...')
response = requests.get(
    'https://www.celestrak.com/pub/satcat.txt',
    stream = True
)
SATCAT = b''
size = int(response.headers.get('content-length', 0))
pb = tqdm(total = size, unit = 'iB', unit_scale = True)
for data in response.iter_content(1024):
    pb.update(len(data))
    SATCAT += data
pb.close()
satcat1 = SATCAT.decode().split('\n')
SATCAT = [{
    'intlcode': extract(line, 0, 11),
    'name': extract(line, 23, 47),
    'norad': extract(line, 13, 18),
    'multipleNames': extract(line, 19, 20) == 'M',
    'isPayload': extract(line, 20, 21) == '*',
    'status': extract(line, 21, 22),
    'source': extract(line, 49, 54),
    'launchDate': extract(line, 56, 66),
    'launchSite': extract(line, 68, 73),
    'decayDate': extract(line, 75, 85) ,
    'orbitalPeriod': extract(line, 87, 94),
    'inclination': extract(line, 96, 101),
    'apogeeAltitude': extract(line, 103, 109),
    'perigeeAltitude': extract(line, 111, 117),
    'radarCrossSection': extract(line, 119, 127),
    'orbitalStatus': extract(line, 129, 132)
} for line in satcat1]
print(crayons.green('Successful!') + f' Total satellites received: {len(satcat1)}')
print()
print('Generating database...')
NDB = 'satdb' + ''.join([random.choice(string.ascii_uppercase) for _ in range(3)]) + '.db'
con = sqlite3.connect(NDB)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS satellites (
    intlcode TEXT,
    name TEXT,
    norad TEXT,
    hasMultipleNames TEXT,
    isPayload TEXT,
    status TEXT,
    source TEXT,
    launchDate TEXT,
    launchSite TEXT,
    decayDate TEXT,
    orbitalPeriod TEXT,
    inclination TEXT,
    apogeeAltitude TEXT,
    perigeeAltitude TEXT,
    rcs TEXT,
    orbitalStatus TEXT,
    tle TEXT
);
''')
used = []
COUNT = 0
con.commit()
print(crayons.green('Successful!') + f' DB Name: {NDB}')
print('\nStarting compiler...')
for satellite in SATCAT:
    if not satellite['intlcode'] or satellite['name'] in used:
        continue

    used.append(satellite['name'])
    print('\x1b[?25l' + next(phases) + f' | \
Working with satellite {satellite["name"]}                 ', end = '\r')
    if satellite['name'] in TLES:
        satellite['tle'] = str(TLES[satellite['name']])
        COUNT += 1
    else:
        satellite['tle'] = None

    data = (
        satellite['intlcode'],
        satellite['name'],
        satellite['norad'],
        satellite['multipleNames'],
        satellite['isPayload'],
        satellite['status'],
        satellite['source'],
        satellite['launchDate'],
        satellite['launchSite'],
        satellite['decayDate'],
        satellite['orbitalPeriod'],
        satellite['inclination'],
        satellite['apogeeAltitude'],
        satellite['perigeeAltitude'],
        satellite['radarCrossSection'],
        satellite['orbitalPeriod'],
        satellite['tle']
    )
    cur.execute('INSERT INTO satellites VALUES(?, ?, ?, ?, ?\
    , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', data)
print('\x1b[?25h')

print(crayons.green('Successful!') + f' Total satellites with TLE: {COUNT}')
con.commit()
print('Thanks for using!')
