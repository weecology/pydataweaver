from __future__ import absolute_import
from __future__ import print_function

from weaver.lib.scripts import reload_scripts


def compile():
    print("Compiling weaver scripts...")
    reload_scripts()
    print("done.")


if __name__ == "__main__":
    compile()
