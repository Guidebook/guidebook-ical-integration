from datetime import datetime

import pytz

import settings
from ical_importer import iCalParser

if __name__ == "__main__":
    """ Script that instantiates an iCalParser class and imports the Sessions into Guidebook """
    demo_day = datetime(2017, 11, 17, 0, 0, 0, 0, pytz.UTC)  # iCalParser allows you to simulate the "day" the parser is being run at.  Needed for demo
    ical_parser = iCalParser(gb_api_key=settings.GB_API_KEY, guide_id=settings.GUIDE_ID, today=demo_day)
    print 'Importing Sessions into Guide {}'.format(settings.GUIDE_ID)
    with open("sample_ical.ics") as ical_file:
        ical_parser.parse(ical_file)
