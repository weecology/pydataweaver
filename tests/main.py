'''
Created on Sep 29, 2015

@author: Henry
'''
import os
import platform
import sys


# sys removes the setdefaultencoding method at startup; reload to get it back
reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    # set default encoding to latin-1 to avoid ascii encoding issues
    sys.setdefaultencoding('latin-1')
    
    
def main():
    """This function launches the weaver."""
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == 'gui'):
        # if no command line args are passed, launch GUI
   
#from weaver.app import  

 
        from weaver.app.main import launch_app
#         from weaver.app.main import launch_app
        launch_app()
        
    

if __name__ == "__main__":
    main()
