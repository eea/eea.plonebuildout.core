#!/usr/bin/env python
""" Github utils
"""
import base64
import os
import sys
import json
import urllib2
import logging
import contextlib
from datetime import datetime
from ConfigParser import SafeConfigParser


class Github(object):
    """ Usage: github.py <loglevel> <logpath> <exclude>

    loglevel:
      - fatal    Log only critical errors
      - critical Log only critical errors
      - error    Log only errors
      - warn     Log only warnings
      - warning  Log only warnings
      - info     Log only status messages (default)
      - debug    Log all messages

    logpath:
      - . current directory (default)

      - "var/log"  relative path to current directory (e.g.
         <current directory>/var/log/github.log)

      - "/var/log" - absoulute path (e.g. /var/log/github.log)

    exclude:

      - exclude packages, space separated.

    Within your home directory you need to provide a .github file that stores
    github username and password like::

    [github]
    username: foobar
    password: secret

    """
    def __init__(self,
        github="https://api.github.com/orgs/eea/repos?per_page=100&page=%s",
        sources="http://svn.eionet.europa.eu/repositories/Zope/trunk/www.eea.europa.eu/trunk/",
        timeout=15,
        loglevel=logging.INFO,
        logpath='.',
        exclude=None):

        self.github = github
        self.sources = sources
        self.timeout = timeout
        self.status = 0
        self.repos = []
        self.username = ''
        self.password = ''

        self.loglevel = loglevel
        self._logger = None
        self.logpath = logpath
        if exclude:
            self.logger.warn("Exclude %s", ', '.join(exclude))
            self.exclude = exclude
        else:
            self.exclude = []

    @property
    def credentials(self):
        """ Get github credentials
        """
        if not (self.username or self.password):
            cfg_file = os.path.expanduser("~/.github")
            if not os.path.exists(cfg_file):
                with contextlib.closing(open(cfg_file, 'w')) as cfg:
                    cfg.write("[github]\nusername:\npassword:\n")
            config = SafeConfigParser()
            config.read([cfg_file])
            self.username = config.get('github', 'username')
            self.password = config.get('github', 'password')

        return {
            'username': self.username,
            'password': self.password,
        }

    def request(self, url):
        """ Complex request
        """
        req = urllib2.Request(url)
        req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode(
            "%(username)s:%(password)s" % self.credentials))
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        return req

    @property
    def logger(self):
        """ Logger
        """
        if self._logger:
            return self._logger

        # Setup logger
        self._logger = logging.getLogger('github')
        self._logger.setLevel(self.loglevel)
        fh = logging.FileHandler(os.path.join(self.logpath, 'github.log'))
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(lineno)3d - %(levelname)7s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self._logger.addHandler(fh)
        self._logger.addHandler(ch)
        return self._logger

    def check_pulls(self, repo):
        """ Check if any open pull for repo
        """
        name = repo.get('full_name', '')
        if name in self.exclude:
            return

        self.logger.info('Checking repo pulls: %s', name)
        url = repo.get('url', '') + '/pulls'
        try:
            with contextlib.closing(urllib2.urlopen(
                self.request(url), timeout=self.timeout)) as conn:
                pulls = json.loads(conn.read())
                for pull in pulls:
                    self.status = 1
                    self.logger.warn("%s - %s", name, pull.get('title', '-'))
        except Exception, err:
            self.logger.exception(err)

        url = repo.get('url', '') + '/forks'
        try:
            with contextlib.closing(urllib2.urlopen(
                self.request(url), timeout=self.timeout)) as conn:
                forks = json.loads(conn.read())
                for fork in forks:
                    if '/collective/' in fork.get('url', ''):
                        self.check_pulls(fork)
                        break
        except Exception, err:
            self.logger.exception(err)

    def check_repo(self, repo):
        """ Sync repo
        """
        # Open pulls
        self.check_pulls(repo)

    def check_repos(self):
        """ Check all repos
        """
        count = len(self.repos)
        self.logger.info('Checking %s repositories found at %s',
                         count, self.github)

        start = datetime.now()
        for repo in self.repos:
            self.check_repo(repo)
        end = datetime.now()
        self.logger.info('DONE Checking %s repositories in %s seconds',
                         count, (end - start).seconds)

    def start(self):
       """ Start syncing
       """
       self.repos = []
       with contextlib.closing(urllib2.urlopen(self.sources, timeout=self.timeout)) as conn:
           for line in conn:
               if '=' not in line:
                   continue
               repo_name, _url = line.split('=', 1)
               repo_name = repo_name.strip()
               self.repos.append({
                   'full_name': "eea/{name}".format(name=repo_name),
                   'url': 'https://api.github.com/repos/eea/{name}'.format(name=repo_name),
                })
       self.check_repos()

    __call__ = start

if __name__ == "__main__":
    LOG = len(sys.argv) > 1 and sys.argv[1] or 'info'
    if LOG.lower() not in ('fatal', 'critical', 'error',
                           'warn', 'warning', 'info', 'debug'):
        print Github.__doc__
        sys.exit(1)

    if LOG.lower() in ['fatal', 'critical']:
        LOGLEVEL = logging.FATAL
    elif LOG.lower() == 'error':
        LOGLEVEL = logging.ERROR
    elif LOG.lower() in ['warn', 'warning']:
        LOGLEVEL = logging.WARNING
    elif LOG.lower() == 'info':
        LOGLEVEL = logging.INFO
    else:
        LOGLEVEL = logging.DEBUG

    PATH = len(sys.argv) > 2 and sys.argv[2] or '.'

    EXCLUDE = len(sys.argv) > 3 and sys.argv[3:] or []

    daemon = Github(loglevel=LOGLEVEL, logpath=PATH, exclude=EXCLUDE)
    daemon.start()

    sys.exit(daemon.status)
