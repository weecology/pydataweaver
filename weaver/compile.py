from __future__ import absolute_import
from __future__ import print_function

from weaver.lib.scripts import MODULE_LIST
# from retriever.lib.scripts import reload_scripts
# above switched for the commented

def compile():
    print("Compiling weaver scripts...")
    MODULE_LIST(force_compile=True)
    # reload_scripts()
    # above switched to the commented
    print("done.")


if __name__ == "__main__":
    compile()
