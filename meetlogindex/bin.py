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
CONFIG_FILES = ['/etc/meetlogindex.cfg', os.path.expanduser('~/.meetlogindex.cfg')]


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
    config.read(CONFIG_FILES)
    
    login = config.get('fedora-project', 'login')
    password = config.get('fedora-project', 'password')

    if verbose:
        print("Fedora wiki base url: %s" % config.get('fedora-project', 'base-url'))
        print("Fedora wiki API url: %s" % config.get('fedora-project', 'api-url'))
        print("Fedora meetbot index url: %s" % config.get('fedora-project', 'meetbot-index'))
        print("Fedora project login: %s" % login)
        print("Meetlog index config wiki page: %s" % config.get('fedora-project', 'config-page'))

    if login == "FEDORA-LOGIN":
        print("Please, change the fedora login in one of the config files: %s" % str(CONFIG_FILES))
        exit(1)

    # initialize the data from config (available as wiki page as well)
    mli = MeetLogIndex.MeetLogIndex(verbose=verbose, debug=debug)
    mli.parse_meet_config(wikiurl=config.get('fedora-project', 'base-url'),
                          configurl=config.get('fedora-project', 'config-page'),
                          apiurl=config.get('fedora-project', 'api-url'),
                          onlyid=onlyid)

    if printconfig:
        mli.print_wiki_config()
        exit(0)

    # get the links
    if mli.get_log_links(index_url=config.get('fedora-project', 'meetbot-index'), since=since):
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



