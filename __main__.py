'''
@author: Henry
'''

""" Weaver Wizard

Running this module directly will launch weaver.

The main() function can be used for bootstrapping.

"""

import os
import platform
import sys



# sys removes the setdefaultencoding method at startup; reload to get it back
reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    # set default encoding to latin-1 to avoid ascii encoding issues
    sys.setdefaultencoding('latin-1')
    
    
dbengines = [
           "mysql",
           "postgres",
           "sqlite",
           "msaccess",
           "csv",
           "download_only"
           ]

def main():
    """This function launches the weaver."""
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == 'gui'):
        # if no command line args are passed, launch GUI  
        from app.main import launch_app
        launch_app() 
        

    else:
        if sys.argv[1] in dbengines:
            from weaver.app.appcontrol import run_app
            run_app(sys.argv[1])
            print "arg 1", sys.argv[1]
            
        
        


if __name__ == "__main__":
    main()
