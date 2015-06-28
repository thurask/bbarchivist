from bbarchivist import lazyloader
from bbarchivist.utilities import is_windows
import easygui as eg
from os import getcwd

osentry = eg.enterbox(msg="OS version")
radentry = eg.enterbox(msg="Radio version, click Cancel to guess")
swentry = eg.enterbox(msg="Software version, click Cancel to guess")
choicelist = ["STL100-1", "STL100-2/3/P9982", "STL100-4", "Q10/Q5/P9983", "Z30/CLASSIC/LEAP", "Z3", "PASSPORT"]
deventry = eg.choicebox(msg="Device", choices=choicelist)
for idx, device in enumerate(choicelist):
    if device == deventry:
        devint = idx
if is_windows():
    autoentry = eg.boolbox(msg="Run autoloader?")
else:
    autoentry = False

lazyloader.do_magic(devint, osentry, radentry, swentry, getcwd(), autoentry, True)
