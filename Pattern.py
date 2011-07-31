#!/usr/bin/python3

# Pattern.py
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-20.
# @Revision:    0.1

## class for managing a Pattern
#
class Pattern:
    # constructor
    #
    def __init__(self, entry = "%n %a - %t"):
        # check for given string
        if entry:
            if entry.find("%a") != -1:
                self.NeedArtist = True
            else:
                self.NeedArtist = False

            if entry.find("%t") != -1:
                self.NeedTitle = True
            else:
                self.NeedTitle = False

            if entry.find("%n") != -1:
                self.NeedNumber = True
            else:
                self.NeedNumber = False

            if entry.find("%k") != -1:
                self.NeedKey = True
            else:
                self.NeedKey = False

        self.Entry = entry

    ## this resolves a pattern with given fields
    #
    # @return new string
    #
    def GetResolvedString(self, artist=None, title=None, number=None, key=None):
        
        entry = self.Entry

        if self.NeedArtist:
            if artist:
                entry = entry.replace("%a", artist)
            else:
                entry = entry.replace("%a", "")

        if self.NeedTitle:
            if title:
                entry = entry.replace("%t", title)
            else:
                entry = entry.replace("%t", "")

        if self.NeedNumber:
            if number:
                entry = entry.replace("%n", "{:02d}".format(number))
            else:
                entry = entry.replace("%n", "")

        if self.NeedKey:
            if key:
                entry = entry.replace("%k", key)
            else:
                entry = entry.replace("%k", "")

        return entry

## Module Test:
#
def ModuleTest():
    #p = Pattern("%a - %k - %k")
    p = Pattern()

    if p.NeedKey:
        print("key is needed " + str(p.NeedKey) )

    print(p.NeedKey)


if __name__ == "__main__":
    ModuleTest()
