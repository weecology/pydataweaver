"""Weaver UI

This module contains the UI elements of the weaver.

"""

from app import App

def launch_app( ):
    """Launches the application GUI."""
    print "Launch weaver..."  
    app = App()
    app.MainLoop()
