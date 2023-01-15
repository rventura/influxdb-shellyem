#!/usr/bin/env python3

import sys
import os.path
import json
import urllib.request
import influxdb

CONFIG = 'hosts'
DATABASE = 'shellyem'

def main():
    hosts = []
    #
    cfn = os.path.join(os.path.dirname(sys.argv[0]), CONFIG)
    with open(cfn) as fh:
        for ln in fh:
            fs = ln.strip().split()
            if len(fs)>0:
                if fs[0][0]!='#' and len(fs)>=2:
                    hosts.append(fs[:2])
    #
    db = influxdb.InfluxDBClient()
    for (ip,hostname) in hosts:
        url = f"http://{ip}/status"
        with urllib.request.urlopen(url) as fh:
            data = json.load(fh)
        try:
            for (idx,em) in enumerate(data['emeters']):
                if em['is_valid']:
                    ln = f"shellyem,host={hostname},index={idx} "
                    ln += ','.join([f"{k}={em[k]}" for k in ('voltage', 'power', 'reactive', 'pf' )])
                #print(ln)
                db.write(ln, params={'db':DATABASE}, protocol='line')
        except IndexError as ex:
            print(f"*** Error extracting data")
    db.close()


if __name__=='__main__':
    main()

# EOF
