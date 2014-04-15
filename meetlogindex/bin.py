#!/usr/bin/python

import MeetLogIndex
import ConfigParser

import sys
import os
import re
import datetime

# name of the binary
PROG_NAME = 'meetbot-logs'

# config files that are read
CONFIG_FILES = ['/etc/meetlogindex.cfg',
                os.path.expanduser('~/.meetlogindex.cfg'),
                os.path.join(os.path.abspath(__file__), 'meetlogindex.cfg')]


def version():
    global PROG_NAME
    print("%s 0.1" % PROG_NAME)
    print
    print("Written by Honza Horak <hhorak@redhat.com>")
    exit(0)


def usage():
    global PROG_NAME
    print("%s analysis quality of individual RPM packages and reports various kinds of results" % PROG_NAME)
    print
    print("Usage: %s package [ package, package, dir, ... ]" % PROG_NAME)
    print
    print("Options:")
    print("  -h, --help             Prints help")
    print("  -V, --version          Prints version info")
    print("  -d, --debug            Print debug output")
    print("  -v, --verbose          Prints more verbose degug output during processing")
    print("  -s, --ince             Date when to start with searching through the meeting logs")
    print("  -i, --onlymeetlogid    If specified, only specified meetlogindex will be proceeded")
    print("  -p, --print-config     Only prints configuration of meeting log parsed from wiki")
    print("  -c, --only-check       Only checks what new meetings are in the log index, do not add the links")
    print("  -f, --config           Only use this config file; can be used more times")
    print
    print("Examples:")
    print("  %s -h" % PROG_NAME)
    print("  %s -s 2014-01-01" % PROG_NAME)
    print("  %s -v -i env-and-stacks" % PROG_NAME)
    print("  %s --print-config" % PROG_NAME)
    print("  %s --only-check" % PROG_NAME)
    exit(1)


def main():
    global CONFIG_FILES

    verbose = False
    debug = False
    since = datetime.date.today() - datetime.timedelta(2)
    onlyid = None
    printconfig = None
    onlycheck = None
    login = None
    password = None
    configfiles = []

    # parsing arguments
    args = list(sys.argv)
    args.reverse()
    args.pop()
    while args:
        arg = args.pop()
        if arg == "-h" or arg == "--help":
            usage()
        if arg == "-V" or arg == "--version":
            version()
        elif arg == "-v" or arg == "--verbose":
            verbose = True
        elif arg == "-d" or arg == "--debug":
            debug = True
        elif args and (arg == "-s" or arg == "--since"):
            date_given = args.pop()
            if not re.match(r'\d{4}-\d{2}-\d{2}', date_given):
                print("Date %s does not have format YYYY-MM-DD." % date_given)
                exit(1)
            (y, m, d) = date_given.split('-')
            since = datetime.date(int(y), int(m), int(d))
        elif arg == "-i" or arg == "--onlymeetlogid":
            onlyid = args.pop()
        elif arg == "-f" or arg == "--config":
            configfiles.append(args.pop())
        elif arg == "-p" or arg == "--print-config":
            printconfig = True
        elif arg == "-c" or arg == "--only-check":
            onlycheck = True
        else:
            usage()

    if verbose:
        print("Since: %s" % since)
        print("Only ID: %s" % onlyid)

    # read some basic configuration (wiki url, username, password)
    config = ConfigParser.ConfigParser()
    configfilesused = CONFIG_FILES
    if configfiles:
        configfilesused = configfiles
    config.read(configfilesused)
   
    if not config.sections():
        print("There are no valid sections in config files: %s" % str(configfilesused))
        exit(1)

    for section in config.sections():
        login = config.get(section, 'login')
        password = config.get(section, 'password')

        if verbose:
            print("Fedora wiki base url: %s" % config.get(section, 'base-url'))
            print("Fedora wiki API url: %s" % config.get(section, 'api-url'))
            print("Fedora meetbot index url: %s" % config.get(section, 'meetbot-index'))
            print("Fedora project login: %s" % login)
            print("Meetlog index config wiki page: %s" % config.get(section, 'config-page'))

        if login == "YOUR_WIKI_LOGIN":
            print("Please, change the login in one of the config files: %s" % str(configfilesused))
            exit(1)

        # initialize the data from config (available as wiki page as well)
        mli = MeetLogIndex.MeetLogIndex(verbose=verbose, debug=debug)
        mli.parse_meet_config(wikiurl=config.get(section, 'base-url'),
                              configurl=config.get(section, 'config-page'),
                              apiurl=config.get(section, 'api-url'),
                              onlyid=onlyid)

        if printconfig:
            mli.print_wiki_config()
            exit(0)

        # get the links
        if mli.get_log_links(index_url=config.get(section, 'meetbot-index'), since=since):
            if verbose:
                print("Getting logs links succeeded")
        else:
            if verbose:
                print("Getting logs links failed")
            exit(1)

        if onlycheck:
            mli.print_links()
            exit(0)

        # change the wiki page
        if mli.update_indexes(login, password):
            if verbose:
                print("Uploading the new links succeeded")
            exit(0)
        else:
            if verbose:
                print("Uploading the new links failed.")
            exit(1)

if __name__ == "__main__":
    main()



