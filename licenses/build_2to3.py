import pyNastran
from .applyLicense import getFoldersFiles 

#assert sys.version_info[:2]==(2,7),'this must be done in python 2.7'

def fix_object(files):
    for fname in files:
        if '.py' in fname:
            print "adding fname=%s" %(fname)
            f = open(fname,'r')
            lines = f.readlines()
            f.close()
            
            for codeLine in lines:
                if '#' in line:
                    isPound = True
                    line = line.strip().split('#')[0]
                    indx = line.index('#')
                else:
                    isPound = False
                    line = codeLine
                    
                if 
                if 'from future' in line: # print & float
                    line = ''
                if '(object):' in line:
                    line = line.replace('(object):','():')
                elif '.iteritems()' in line:
                    line = line.replace('.iteritems()','.items()')

                #elif ",'wb')" in line:
                    #assert 'open' in line,codeLine
                    #line = line.replace(",'wb')",",'wb',encoding='ascii')")
                #elif ",'r')" in line:
                    #assert 'open' in line,codeLine
                    #line = line.replace(",'r')",",'r',encoding='ascii')")
                #elif 'import' in line and ('bdf' in line or 'op2' in line or 'f06' in line or 'gui' in line or 'op4' in line):
                    #assert 'pyNastran.' in line,line # validates that the import is correct
                #elif 'print '
                #elif 
                if isPound:
                    line += codeLine[indx:]
                lines2.append(line)
                
            f = open(fname,'wb')
            for line in lines2:
                f.write(line)
            ###
        ###
    ###

if __name__ == "__main__":
    pkg_path = pyNastran.__file__[0]
    (folders,files) = getFoldersFiles(pkg_path)
    fix_object(files)