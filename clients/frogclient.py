###############################################################
#  PyNLPl - Frog Client - Version 1.4.1
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Derived from code by Rogier Kraf
#       
#       Licensed under GPLv3
# 
# This is a Python library for on-the-fly communication with
# a Frog/Tadpole Server. Allowing on-the-fly lemmatisation and
# PoS-tagging. It is recommended to pass your data on a 
# sentence-by-sentence basis to FrogClient.process()
#
###############################################################

from socket import *
import re

class FrogClient:
    def __init__(self,host="localhost",port=12345, tadpole_encoding="utf-8", parser=False, timeout=120.0):
        """Create a client connecting to a Frog or Tadpole server."""
        self.BUFSIZE = 4096
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect( (host,int(port)) )
        self.tadpole_encoding = tadpole_encoding
        self.parser = parser
        

    def process(self,input_data, source_encoding="utf-8", return_unicode = True):
        """Receives input_data in the form of a str or unicode object, passes this to the server, with proper consideration for the encodings, and returns the Tadpole output as a list of tuples: (word,pos,lemma,morphology), each of these is a proper unicode object unless return_unicode is set to False, in which case raw strings in the tadpole encoding will be returned."""
        if isinstance(input_data, list):
            input_data = " ".join(input_data)

        input_data = input_data.strip(' \t\n')

        targetbuffer = re.sub("[ -]","",input_data)
        #buffer = ""

        #print "SEND: ",input_data #DEBUG
        if not isinstance(input_data, unicode):
            input_data = unicode(input_data, source_encoding) #decode (or preferably do this in an earlier stage)
        self.socket.sendall(input_data.encode(self.tadpole_encoding) +'\r\n') #send to socket in desired encoding

        tp_output = []

        done = False
        while not done:    
            data = ""
            while not data or data[-1] != '\n':
                data += self.socket.recv(self.BUFSIZE)
            if return_unicode:
                data = unicode(data,self.tadpole_encoding)


            for line in data.strip(' \t\r\n').split('\n'):
                if line == "READY":
                    done = True
                    break
                elif line:
                    line = line.split('\t') #split on tab
                    if len(line) > 4 and line[0].isdigit(): #first column is token number
                        if line[0] == '1' and tp_output:
                            if self.parser:
                                tp_output.append( (None,None,None,None, None, None) )
                            else:
                                tp_output.append( (None,None,None,None) )  
                        fields = line[1:]
                        parse1=parse2=""
                        if len(fields) == 7:
                             word,lemma,morph,pos,posprob, parse1,parse2 = line[1:]
                        elif len(fields) == 6:
                            word,lemma,morph,pos, parse1,parse2 = line[1:]
                        elif len(fields) == 5:
                            word,lemma,morph,pos, posprob = line[1:]
                        elif len(fields) == 4:
                            word,lemma,morph,pos = line[1:]
                        else:
                            raise Exception("Can't process line: ", repr(line))

                        if self.parser:
                            tp_output.append( (word,lemma,morph,pos,parse1,parse2) )
                        else:
                            tp_output.append( (word,lemma,morph,pos) )
                        
        return tp_output

    def __del__(self):
        self.socket.close()

