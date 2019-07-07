from __future__ import absolute_import
from __future__ import print_function

from dataweaver.lib.scripts import reload_scripts


def compile():
    print("Compiling dataweaver scripts...")
    reload_scripts()
    print("done.")


if __name__ == "__main__":
    compile()
