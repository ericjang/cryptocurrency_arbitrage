# Copyright (c) 2013 Alan McIntyre

from HTMLParser import HTMLParser
import datetime
import warnings
from btceapi.common import BTCEConnection, all_pairs


class BTCEScraper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.messageId = None
        self.messageTime = None
        self.messageUser = None
        self.messageText = None
        self.messages = []
        self.reserves24change = None
        self.reservesALFAcashier = None
        self.usersOnline = None
        self.botsOnline = None

        self.inMessageA = False
        self.inMessageSpan = False
        self.in24changeSpan = False
        self.inALFAcashierSpan = False
        self.inUsersOnlineDiv = False

        self.devOnline = False
        self.supportOnline = False
        self.adminOnline = False

    def handle_data(self, data):
        # Capture contents of <a> and <span> tags, which contain
        # the user ID and the message text, respectively.
        if self.inMessageA:
            self.messageUser = data.strip()
        elif self.inMessageSpan:
            self.messageText = data.strip()
        elif self.in24changeSpan:
            self.reserves24change = int(data)
        elif self.inALFAcashierSpan:
            self.reservesALFAcashier = int(data)
        elif self.inUsersOnlineDiv:
            utext, ucount, bottext, botcount = data.split()
            self.usersOnline = int(ucount)
            self.botsOnline = int(botcount)
            self.inUsersOnlineDiv = False

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            # Check whether this <p> tag has id="msgXXXXXX" and
            # class="chatmessage"; if not, it doesn't contain a message.
            messageId = None
            for k, v in attrs:
                if k == 'id':
                    if v[:3] != 'msg':
                        return
                    messageId = v
                if k == 'class' and v != 'chatmessage':
                    return

            # This appears to be a message <p> tag, so set the message ID.
            # Other code in this class assumes that if self.messageId is None,
            # the tags being processed are not relevant.
            if messageId is not None:
                self.messageId = messageId
        elif tag == 'a':
            if self.messageId is not None:
                # Check whether this <a> tag has class="chatmessage" and a
                # time string in the title attribute; if not, it's not part
                # of a message.
                messageTime = None
                for k, v in attrs:
                    if k == 'title':
                        messageTime = v
                    if k == 'class' and v != 'chatmessage':
                        return

                if messageTime is None:
                    return

                # This appears to be a message <a> tag, so remember the message
                # time and set the inMessageA flag so the tag's data can be
                # captured in the handle_data method.
                self.inMessageA = True
                self.messageTime = messageTime
            else:
                for k, v in attrs:
                    if k != 'href':
                        continue

                    # If the <a> tag for dev/support/admin is present, then
                    # they are online (otherwise nothing appears on the
                    # page for them).
                    if v == 'https://btc-e.com/profile/1':
                        self.devOnline = True
                    elif v == 'https://btc-e.com/profile/2':
                        self.supportOnline = True
                    elif v == 'https://btc-e.com/profile/3':
                        self.adminOnline = True
        elif tag == 'span':
            if self.messageId is not None:
                self.inMessageSpan = True
            else:
                for k, v in attrs:
                    if k == 'id':
                        if v == '_24CH_reserve':
                            self.in24changeSpan = True
                            return
                        elif v == 'ALFA_reserve':
                            self.inALFAcashierSpan = True
                            return
        elif tag == 'div':
            for k, v in attrs:
                if k == 'id' and v == "users-online":
                    self.inUsersOnlineDiv = True

    def handle_endtag(self, tag):
        if tag == 'p' and self.messageId is not None:
            # exiting from the message <p> tag

            # check for invalid message contents
            if self.messageId is None:
                warnings.warn("Missing message ID")
            if self.messageUser is None:
                warnings.warn("Missing message user")
            if self.messageTime is None:
                warnings.warn("Missing message time")

            if self.messageText is None:
                # messageText will be None if the message consists entirely
                # of emoticons.
                self.messageText = ''

            # parse message time
            t = datetime.datetime.now()
            messageTime = t.strptime(self.messageTime, '%d.%m.%y %H:%M:%S')

            self.messages.append((self.messageId, self.messageUser,
                                  messageTime, self.messageText))
            self.messageId = None
            self.messageUser = None
            self.messageTime = None
            self.messageText = None
        elif tag == 'a' and self.messageId is not None:
            self.inMessageA = False
        elif tag == 'span':
            self.inMessageSpan = False
            self.in24changeSpan = False
            self.inALFAcashierSpan = False


class ScraperResults(object):
    __slots__ = ('messages', 'reserves24change', 'reservesALFAcashier',
                 'usersOnline', 'botsOnline', 'devOnline', 'supportOnline',
                 'adminOnline')

    def __init__(self):
        self.messages = None
        self.reserves24change = None
        self.reservesALFAcashier = None
        self.usersOnline = None
        self.botsOnline = None
        self.devOnline = False
        self.supportOnline = False
        self.adminOnline = False

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in ScraperResults.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


_current_pair_index = 0


def scrapeMainPage(connection=None):
    if connection is None:
        connection = BTCEConnection()

    parser = BTCEScraper()

    # Rotate through the currency pairs between chat requests so that the
    # chat pane contents will update more often than every few minutes.
    global _current_pair_index
    _current_pair_index = (_current_pair_index + 1) % len(all_pairs)
    current_pair = all_pairs[_current_pair_index]

    response = connection.makeRequest('/exchange/%s' % current_pair,
                                      with_cookie=True)

    parser.feed(parser.unescape(response.decode('utf-8')))
    parser.close()

    r = ScraperResults()
    r.messages = parser.messages
    r.reserves24change = parser.reserves24change
    r.reservesALFAcashier = parser.reservesALFAcashier
    r.usersOnline = parser.usersOnline
    r.botsOnline = parser.botsOnline
    r.devOnline = parser.devOnline
    r.supportOnline = parser.supportOnline
    r.adminOnline = parser.adminOnline

    return r
