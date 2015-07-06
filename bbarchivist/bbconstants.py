import os.path  # for producing cap location constant

#: App version.
VERSION = "1.9.0"
#: Version of cap.exe bundled with app.
CAPVERSION = "3.11.0.22"
#: Where cap.exe is. Should be in site-packages.
CAPLOCATION = os.path.join(
                           os.path.dirname(
                                           os.path.abspath(__file__)
                                           ),
                           "cap-" + CAPVERSION + ".dat"
)
#: JSON storage file.
JSONFILE = os.path.join(
                           os.path.dirname(
                                           os.path.abspath(__file__)
                                           ),
                           "bbconstants.json"
)
#: Lookup server list.
SERVERS = {
    "p": "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/",
    "b1": "https://beta.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "b2": "https://beta2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a1": "https://alpha.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a2": "https://alpha2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/"
}
