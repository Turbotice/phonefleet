import time
import subprocess
from pprint import pprint
import argparse
import phonefleet.rw_data as rw

global routing_table

filename = "routing_table.txt"
table = rw.read_csv(filename,delimiter='\t')
routing_table = rw.csv2dict(table)

pprint(routing_table)

def gen_parser():    
    parser = argparse.ArgumentParser(description="Start a ssh connexion")
    parser.add_argument('-name', dest='name', type=str,default=None,help='Name of the server')
    parser.add_argument('-p', dest='protocol', type=str,default='qrvpn',help='Name of the protocol use for connexion')

#    print(parser)   
    args = parser.parse_args()
    #print(args)
    return args
                
def main(args):
    key = args.name
    if key in routing_table.keys():
        id = routing_table[key]['id']
        ipadress = routing_table[key]['ip_'+args.protocol]
        out = subprocess.run(['ssh',f"{id}@{ipadress}",'-p','8022'],text=True,capture_output=True)

        subprocess(['ssh',f""],)
if __name__=='__main__':
    args = gen_parser()
    main(args)
