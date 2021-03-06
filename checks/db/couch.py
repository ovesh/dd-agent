import urllib2
from util import json, headers

from checks import *

class CouchDb(Check):
    """Extracts stats from CouchDB via its REST API
    http://wiki.apache.org/couchdb/Runtime_Statistics
    """
    
    def __init__(self, logger):
        Check.__init__(self, logger)
        

    def _get_stats(self, agentConfig, url):
        "Hit a given URL and return the parsed json"
        try:
            req = urllib2.Request(url, None, headers(agentConfig))

            # Do the request, log any errors
            request = urllib2.urlopen(req)
            response = request.read()
            return json.loads(response)
        except:
            self.logger.exception('Unable to get CouchDB statistics')
            return None

    def check(self, agentConfig):
        if 'couchdb_server' not in agentConfig or agentConfig['couchdb_server'] == '':
            return False

        # The dictionary to be returned.
        couchdb = {'stats': None, 'databases': {}}

        # First, get overall statistics.
        endpoint = '/_stats/'

        url = '%s%s' % (agentConfig['couchdb_server'], endpoint)
        overall_stats = self._get_stats(agentConfig, url)

        # No overall stats? bail out now
        if overall_stats is None:
            return False
        else:
            couchdb['stats'] = overall_stats

        # Next, get all database names.
        endpoint = '/_all_dbs/'

        url = '%s%s' % (agentConfig['couchdb_server'], endpoint)
        databases = self._get_stats(agentConfig, url)

        if databases is not None:
            for dbName in databases:
                endpoint = '/%s/' % dbName

                url = '%s%s' % (agentConfig['couchdb_server'], endpoint)
                db_stats = self._get_stats(agentConfig, url)
                if db_stats is not None:
                    couchdb['databases'][dbName] = db_stats

        return couchdb
