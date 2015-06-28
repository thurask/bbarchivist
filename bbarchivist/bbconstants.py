import os.path  # for producing cap location constant

#: App version.
VERSION = "1.8.1"
#: Version of cap.exe bundled with app.
CAPVERSION = "3.11.0.22"
#: Where cap.exe is. Should be in site-packages.
CAPLOCATION = os.path.join(
                           os.path.dirname(
                                           os.path.abspath(__file__)
                                           ),
                           "cap-" + CAPVERSION + ".dat"
)
#: Device IDs.
DEVICELIST = ["STL100-1",
              "STL100-2",
              "STL100-3",
              "STL100-4",
              "STK100-1",
              "STK100-2",
              "SQN100-1",
              "SQN100-2",
              "SQN100-3",
              "SQN100-4",
              "SQN100-5",
              "SQR100-1",
              "SQR100-2",
              "SQR100-3",
              "SQK100-1",
              "SQK100-2",
              "STA100-1",
              "STA100-2",
              "STA100-3",
              "STA100-4",
              "STA100-5",
              "STA100-6",
              "SQC100-1",
              "SQC100-2",
              "SQC100-3",
              "SQC100-4",
              "SQC100-5",
              "STR100-1",
              "STR100-2",
              "STJ100-1",
              "STJ100-2",
              "SQW100-1",
              "SQW100-2",
              "SQW100-3",
              "SQW100-4"]
#: Device hardware IDs, mapped 1:1 to device list.
HWIDLIST = ["4002607",
            "8700240A",
            "8500240A",
            "8400240A",
            "A500240A",
            "A600240A",
            "8400270A",
            "8500270A",
            "8600270A",
            "8C00270A",
            "8700270A",
            "84002A0A",
            "85002A0A",
            "86002A0A",
            "8F00270A",
            "8E00270A",
            "8C00240A",
            "8D00240A",
            "8E00240A",
            "8F00240A",
            "9500240A",
            "B500240A",
            "9600270A",
            "9400270A",
            "9500270A",
            "9700270A",
            "9C00270A",
            "7002E0A",
            "6002E0A",
            "4002E07",
            "5002E07",
            "87002C0A",
            "85002C0A",
            "84002C0A",
            "8F002C0A"]
#: Device models.
MODELLIST = ["Z10",
             "P9982",
             "Q10",
             "Q5",
             "P9983",
             "Z30",
             "CLASSIC",
             "LEAP",
             "Z3",
             "PASSPORT"]
#: Device families.
FAMILYLIST = ["Z10OMAP",
              "Z10QCOM-P9982",
              "Q10-Q5-P9983",
              "Z30-CLASSIC-LEAP",
              "Z3",
              "PASSPORT"]
#: Somehow, values for lifetimes for escreens.
LIFETIMES = {
    1: "",
    3: "Hello my baby, hello my honey, hello my rag time gal",
    7: "He was a boy, and she was a girl, can I make it any more obvious?",
    15: "So am I, still waiting, for this world to stop hating?",
    30: "I love myself today, not like yesterday. I'm cool, I'm calm, I'm gonna be okay" # @IgnorePep8
}
#: Escreens magic HMAC secret.
SECRET = 'Up the time stream without a TARDIS'
#: Lookup server list.
SERVERS = {
    "p": "https://cs.sl.blackberry.com/cse/srVersionLookup/2.0.0/",
    "b1": "https://beta.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "b2": "https://beta2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a1": "https://alpha.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/",
    "a2": "https://alpha2.sl.eval.blackberry.com/slscse/srVersionLookup/2.0.0/"
}
