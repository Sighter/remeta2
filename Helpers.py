#!/usr/bin/python3

# helpers.py -- file for minor helper functions
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2010-12-04.
# @Revision:    0.1


import re
import urllib
from os import renames

# function -- split_ld
# @ string
# < first part
# < second part
# split a string on last dot
# **************************
def split_ld (str_orig):
    sFktname = "split_ld"

    p = re.compile(r"(.*)\.(.*$)")

    res = p.search(str_orig).groups()

    if len(res) != 2:
        return None
    else:
        return res[1]
# end of split_ld




# function -- ePrint
# @ verLevel
# @ function name
# @ message
# < none
# print messages while controling the verbosity level
# **************************

G_VerbLevel = 1

def ePrint (verLevel, fName, message, end = None):
    sFktname = "ePrint"

    # return if verblevel is not high enough
    if verLevel > G_VerbLevel:
        return

    max_chars = 100
    
    # create a line header
    head_spaces = ""
    for i in range(0, len(fName) + 5):
        head_spaces += " "

    # print header
    print(" --> " + fName + ":" , end = " ")

    # print the message and make new lines
    i = 0
    for char in message:
        if i >= max_chars and char == " ":
            print("\n" + head_spaces, end = " ")
            i = 0

        print(char, end = "")
        i += 1

    print(end = end)
# end of ePrint




# function -- subinstr () {{{
# @ list of regex,sub -pairs
# @ the string 
# < new string
# ****************************** #
def subinstr(list,newstr):
    for i in list:
        p = re.compile(i[0])
        newstr = p.sub(i[1], newstr)

    return newstr
# end of subinstr }}} #

# function -- getWebAsSrc () {{{
# @ url
# < decoded string
# ****************************** #
# fkt -- getWebAsSrc(url) {{{
def GetWebAsString(url):

    #try:
    response = urllib.request.urlopen(url)
    #except:

    # print page info
    #for i,j in response.info().items():
   	#print(i,j)

    # get page-source to str
    string = response.read()

    # convert the string to a raw-string
    return string.decode('Latin1')
# end of }}} #


## function to remove chars from a string
#
def ReplaceChars(chars, dest, target):
    for c in chars:
        target = target.replace(c, dest)

    return target


## method to rename a directory
#
def RenameDirQuery(source, dest):
    ePrint(1, ":", "Rename DIR: " + source + " --> " + dest, end=" ? ")
    choice = "k"
    while choice != "y" and choice != "n":
        choice = input("(y/n): ")

    if choice == "y":
        renames(source, dest)

## download a file from url
def DownloadFile(url, file_name):
    import urllib.request
    import shutil

    ePrint(2, ":", "Downloading file from: " + url)
    ePrint(2, ":", "To: " + file_name)

    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


# function to colorize a strint
def ColorString(string, color):
    
    if color == "green":
        string = "\33[32m" + string + "\033[0m"

    return string

