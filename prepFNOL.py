#!/usr/bin/python

import uuid
import random

FILE_NAME_INP = "claimSaveRq21.xml"
FILE_NAME_OP  = "claimSaveRq.xml"

def prepFNOL():
    claimNum = claimNum = '{0:05}-01'.format(random.randint(1, 100000))
    fout = open(FILE_NAME_OP, 'w+')
    with open(FILE_NAME_INP, 'r') as fin:
        for line in fin:
            print line
            if line.strip().startswith("<RqUID>"):
                newLine = "<RqUID>" + str(uuid.uuid1()) + "</RqUID>\n"
                fout.write(newLine)
                print "replaced rquid" + newLine
            elif line.strip().startswith("<ClaimNum>"):
                newLine = "<ClaimNum>" + claimNum + "</ClaimNum>\n"
                fout.write(newLine)
                print "replaced claimnum" + newLine
            else:
                fout.write(line)
    fout.close()
    return claimNum



if __name__ == "__main__":
    print prepFNOL()