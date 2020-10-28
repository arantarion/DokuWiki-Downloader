# -*- coding: utf-8 -*-
"""
A simple crawler/downloader for websites based on DokuWiki
Written in Python 3
By Henry Weckermann
2020
"""

import re
import os
import sys
import gzip
import getopt
import urllib.parse
import urllib.request
from tqdm import tqdm


def openSiteMap(location):

    with open(location, "r") as file:
        return file.read()


def downloadSitemap(website):

    from io import BytesIO

    url = f"{website}/doku.php?do=sitemap"
    url = url[:7] + url[7:].replace("//", "/")

    #packedSitemap = requests.get(url).content
    packedSitemap = urllib.request.urlopen(url).read()
    file = gzip.open(BytesIO(packedSitemap), 'rb')
    sitemap = file.read()
    file.close()

    return str(sitemap)


def processSitemap(sitemap, CMD):

    urls = list(set(re.findall(r'(https?://\S+)', sitemap)))
    urls = [url[:-8] + CMD for url in urls]

    return urls


def prepareDownload():
    try:
        os.mkdir(f"{os.getcwd()}/Dokuwiki_Output")
    except BaseException:
        pass
    return "Dokuwiki_Output"


def getFileName(url):
    filename = urllib.parse.urlparse(url)[2]
    return filename.replace("/", "_")


def downloadWebsite(url, extension, folder):

    filename = getFileName(url)
    urllib.request.urlretrieve(url, f"{folder}/{filename}.{extension}")

    #response = requests.get(url)
    # try:
    #    with open(f"{folder}/{filename}.{extension}", "xb") as file:
    #        file.write(response.read().decode('UTF-8', "ignore"))
    # except:
    #    pass


def downloadAllWebsites(urls, extension, folder):
    for url in tqdm(urls):
        downloadWebsite(url, extension, folder)


def printHelp():
    print("""A downloading tool for DokuWiki powered websites \n\n
          -a= \t --address= \t\t Specify the Website. If you want to use the -f/--full option please specify the root website \n
          -s= \t --sitemap= \t\t Specify the location of a sitemap.xml file. If empty the tool atempts to download it automatically\n
          -f \t --full \t\t Download all sites\n
          -x \t --xhtml \t\t Downloads the site(s) as a rendered html file. Requires more space and time\n
          -t \t --text \t\t Downloads the site(s) as a plain text file. Requires less space and time\n
          -h \t --help \t\t Dispalys this help text""")


def main():

    argv = sys.argv

    WEBSITE = ""
    CMD = ""
    EXTENSION = ""
    SITEMAP = ""
    SELECTION = "single"
    HELP_MODE = False

    (opts, _) = getopt.getopt(argv[1:], "a:xtfsh", [
        "address=", "xhtml", "text", "full", "sitemap=", "help"])

    for (opt, value) in opts:
        if (opt == "-a") or (opt == "--address"):
            WEBSITE = str(value)
        elif (opt == "-x") or (opt == "--xhtml"):
            CMD = "?do=export_xhtml"
            EXTENSION = "html"
        elif (opt == "-t") or (opt == "--text"):
            CMD = "?do=export_raw"
            EXTENSION = "txt"
        elif (opt == "-s") or (opt == "--sitemap"):
            SITEMAP = str(value)
        elif (opt == "-f") or (opt == "--full"):
            SELECTION = "full"
        elif (opt == "-h") or (opt == "--help"):
            HELP_MODE = True

    if HELP_MODE:
        printHelp()
        sys.exit(0)

    if CMD == "" or WEBSITE == "":
        printHelp()
        sys.exit(0)

    if SELECTION == "single":
        try:
            folder = prepareDownload()
            downloadWebsite(WEBSITE + CMD, EXTENSION, folder)
        except BaseException:
            print("An error has occured")
            sys.exit(0)

        print("Successfully downloaded the specified page into the directory 'Dokuwiki_Output'")

    elif SELECTION == "full":
        if SITEMAP == "":
            try:
                SITEMAP = downloadSitemap(WEBSITE)
            except BaseException:
                print("Error downloading the sitemap. Please specify one urself.")
                sys.exit(0)
        else:
            SITEMAP = openSiteMap(SITEMAP)

        SITEMAP = processSitemap(SITEMAP, CMD)

        downloadAllWebsites(SITEMAP, EXTENSION, prepareDownload())


if __name__ == "__main__":
    main()
