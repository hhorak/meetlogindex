import ConfigParser
import wikitools
import re
import urllib2
import collections

class MeetLogIndex(object):

    def __init__(self, verbose=False, debug=False):
        self.verbose = verbose
        self.debug = debug
        self.meetlog_data = []
        self.logged = False


    def _verbose_print(self, message):
        """
        Helper for printing some verbose messages.
        """
        if self.verbose:
             print(message)

    def _debug_print(self, message):
        """
        Helper for printing some debuggin messages.
        """
        if self.debug:
             print("DEBUG: %s" % message)


    def _debug_print_html(self, url, html):
        """
        Helper for printing some debuggin messages with longer content.
        """
        self._debug_print("Content of the page %s is:\n---\n%s\n---\n" % (url, html))


    def _find_all(self, needle, haystack):
        """
        Finds needle defined by user in haystack, and print some debugging info.
        """
        result = re.findall(needle, haystack)
        if result:
            count = len(result)
        else:
            count = 0
        self._verbose_print("Looking for %s had %s matches." % (needle, str(count)))
        self._debug_print("Matches: %s" % str(result))
        return result


    def _normalize_matches(self, matches):
        """
        We don't know if users defined brackets, so we either take string
        or first item from result tuple.
        """
        return [m for m in matches if not isinstance(m, collections.Iterable) ] + \
               [m[0] for m in matches if isinstance(m, collections.Iterable) ]


    def parse_meet_config(self, wikiurl=None, apiurl=None, configurl=None, onlyid=False):
        """
        Parses the configuration available on the wiki page.
        Stores the configuration into self.meetlog_data.
        """
        if not wikiurl:
            print("Error: No wiki url given.")
            exit(1)

        if not configurl:
            print("Error: No config url given.")
            exit(1)

        self.onlyid = onlyid
        self.wikiurl = wikiurl
        self.apiurl = apiurl
        self.configurl = configurl

        self.site = wikitools.wiki.Wiki(self.apiurl)

        self._verbose_print("Parsing Meeting Log config file at %s with api %s." % (wikiurl+'/'+configurl, self.apiurl))
        self._verbose_print("Result of init for %s: %s" % (self.apiurl, str(self.site)))

        self.config_page = wikitools.page.Page(self.site, title=self.configurl)
        self.config_text = self.config_page.getWikiText()
        
        self._debug_print_html(self.configurl, self.config_text)

        # config page has the following format:
        # | meetlog ID || regexp for meeting rooms || regexp for meetbot logs || wikipage with index
        matches = self._find_all(r'\|([^|]*)\|\|(.*)\|\|(.*)\|\|([^|]*)', self.config_text)
        if matches:
           for (meetlog_id, regexp_rooms, regexp_logs, wiki_index_page) in matches:
               meetlog_id_stripped = meetlog_id.strip()
               if not self.onlyid or self.onlyid == meetlog_id_stripped:
                   self.meetlog_data.append({'meetlog_id': meetlog_id_stripped,
                                             'regexp_rooms': regexp_rooms.strip(),
                                             'regexp_logs': regexp_logs.strip(),
                                             'wiki_index_page': wiki_index_page.strip()})


    def print_wiki_config(self):
        """
        Prints configuration parsed from wiki.
        """
        self._verbose_print("Printing parsed wiki config:")
        for entry in self.meetlog_data:
            print("%s:\n  regexp room: %s\n  regexp logs: %s\n  wiki index page: %s\n\n"
                  % (entry['meetlog_id'], entry['regexp_rooms'],
                     entry['regexp_logs'], entry['wiki_index_page']))


    def _wget(self, url):
        """
        Gets a page from the internet and prints some debugging info.
        """
        self._verbose_print("wgetting %s" % url)
        response = urllib2.urlopen(url)
        result = response.read()
        self._debug_print_html(url, result)
        return result


    def _get_room_matches(self, regexp_rooms, rooms_list_html):
        """
        Scans for the room_regexp in room_page_html and returns matches in rooms
        """
        self._verbose_print("Scanning for regexp_rooms in the room html (%s)" % regexp_rooms)
        matches = self._find_all("<a href=\"(%s)/" % regexp_rooms, rooms_list_html)
        if matches:
            return self._normalize_matches(matches)
        else:
            self._verbose_print("Not found.")
            return []


    def _get_link_date(self, date_url, meetbot_regexp):
        """
        Scans for link that match "meetbot_regexp" in the url "date_url".
        Returns links found as an array.
        """
        result = []
        date_html = self._wget(date_url)
        matches = self._find_all("<a href=\"(%s.\d{4}-\d{2}-\d{2}-\d{2}.\d{2}.log.html)" % meetbot_regexp, date_html)
        if matches:
            result += [ ("%s/%s" % (date_url.strip('/'), l)) for l in self._normalize_matches(matches) ]
        return result
        

    def _get_links_room(self, since, room_url, meetbot_regexp):
        """
        Loops through all dates since "since" in the room "room_name" and
        retrieves all links for "meetbot_log_regexp".
        Results if any are returned as array of links (strings).
        """
        result = []
        dates_list_html = self._wget(room_url)
        matches = self._find_all("<a href=\"(\d{4}-\d{2}-\d{2})/", dates_list_html)
        if matches:
            for d in matches:
                if d >= str(since):
                    result += self._get_link_date("%s/%s/" % (room_url.strip('/'), d), meetbot_regexp)
        return result


    def get_log_links(self, index_url=None, since=None):
        """
        Gets links from meetbot logs and stores them into the particular
        entry in self.meetlog_data.
        """
        if not index_url:
            print("Not meetbot index url given.")
            exit(1)


        if not since:
            print("Not since date given.")
            exit(1)

        self._verbose_print("Getting log links since %s." % since)

        rooms_list_html = self._wget(index_url)
        for entry in self.meetlog_data:
            entry['rooms'] = self._get_room_matches(entry['regexp_rooms'], rooms_list_html)
            self._verbose_print("Rooms for %s are: %s" % (entry['meetlog_id'], str(entry['rooms'])))
            entry['links'] = []
            for room in entry['rooms']:
                entry['links'] += self._get_links_room(since, "%s/%s/" % (index_url.strip('/'), room), entry['regexp_logs'])
            self._verbose_print("Links for ID %s: %s" % (entry['meetlog_id'], str(entry['links'])))

        return True


    def print_links(self):
        """
        Prints the parsed data for all entries.
        """
        self._verbose_print("Printing gathered links.")
        for entry in self.meetlog_data:
            print("Links for ID %s: %s" % (entry['meetlog_id'], str(entry['links'])))


    def update_indexes(self, login, password):
        """
        Returns True if indexes have been inserted, False otherwise.
        """
        self._verbose_print("Updating indexes.")

        self._verbose_print("Try to log in as %s to %s." % (login, str(self.site)))
        self.logged = self.site.login(username=login, password=password)
        if not self.logged:
            print("Could not log in as user %s." % login)
            exit(1)
        
        self._verbose_print("We are now logged in: %s." % (str(self.site)))

        for entry in self.meetlog_data:
            if not entry['links']:
                self._verbose_print("No links for %s, skipping index page adjustment." % entry['meetlog_id'])
                continue

            # load the page where the meeting log index is stored
            p = wikitools.page.Page(self.site, title=entry['wiki_index_page'])
            if not p:
                print("Could not load page %s." % entry['wiki_index_page'])
                exit(1)
            self._verbose_print("Page %s successfully loaded." % entry['wiki_index_page'])

            # filter the links already present in the text
            old_text = p.getWikiText()
            new_links = [ link for link in entry['links'] if old_text.find(link) == -1 ]

            # use two lines between links
            added_text = "\n" + "\n\n".join(new_links)
            self._debug_print("About to add the following text to %s:\n---\n%s\n---\n" % (entry['wiki_index_page'], added_text))

            # append the new links to the end of the existing page
            if p.edit(appendtext=added_text):
                self._verbose_print("Addition of the links for %s succeeded." % entry['meetlog_id'])
                return True
            else:
                self._verbose_print("Addition of the links for %s failed." % entry['meetlog_id'])

        return False

