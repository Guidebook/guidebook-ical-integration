from datetime import datetime, timedelta

import pytz
from icalendar import Calendar

import settings
from guidebook_api import GuidebookAPI


class InvalidiCalendarFile(Exception):
    " Raised if we cannot parse the original iCal file."


class iCalParser:
    """
    This class takes an ical file and uses the Guidebook Open API (https://developer.guidebook.com/)
    to import the session data into Guideboook
    """
    def __init__(self, gb_api_key=None, guide_id=None, timezone='US/Pacific', days_before=7, days_after=60, today=None):
        """Initializes basic settings and creates a client to the Guidebook API"""
        self.gb_api_key = gb_api_key
        self.guide_id = guide_id
        self.gb_api_client = GuidebookAPI(api_key=gb_api_key, guide_id=guide_id)

        # Parameters that determine how the datetimes should be interpreted and what date range of events we care about.
        self.timezone = pytz.timezone(timezone)
        self.days_before = days_before
        self.days_after = days_after
        if today is None:
            # This value is used to calculate the range of events we import for `days_before` and `days_after`
            # By default, the parser assumes the time of import is the current time.
            self.today = pytz.UTC.localize(datetime.today())
        else:
            self.today = today
        if settings.DEBUG:
            print u'Using {} for today'.format(self.today)

    def parse(self, ical_file):
        """
        Parse the given ical_file, and create objects in Guidebook via the API
        """
        cal = self.get_ical_object(ical_file)
        # Determine what timezone these events should be interpreted as.
        self.x_wr_timezone = self.get_ical_timezone_info(cal)

        # Determine the date range of events we care about
        limit_start = self.today - timedelta(days=self.days_before)
        limit_end = self.today + timedelta(days=self.days_after)

        if settings.DEBUG:
            print u'Limit start value: {}'.format(limit_start)
            print u'Limit end value: {}'.format(limit_end)
        # dictionaries to keep track of name and id mapping to minimize redundant API calls
        schedule_track_name_to_id_mapping = {}
        location_name_to_id_mapping = {}

        cal_components = self.cal_components(cal)
        session_ids = []  # maintain a list of all Session IDs.  Return this upon completion.
        for component in cal_components:
            # get the raw ical representations of UID
            UID = component['UID']
            if settings.DEBUG:
                print u'Parsing iCal event: {}'.format(UID)
            session_start_time = component['DTSTART'].dt
            session_end_time = component['DTEND'].dt

            # confirm that this given event is within our import range
            session_within_limits = self.is_within_time_and_date_limits(session_start_time, session_end_time, limit_start, limit_end)
            if not session_within_limits:
                continue

            # For this integration, we are mapping the CATEGORIES field to the Schedule Track object in Guidebook
            schedule_track_name = u'{}'.format(component['CATEGORIES'])
            if schedule_track_name not in schedule_track_name_to_id_mapping:
                track_id = self.gb_api_client.get_or_create_schedule_track(name=schedule_track_name)
                schedule_track_name_to_id_mapping[schedule_track_name] = track_id
            else:
                track_id = schedule_track_name_to_id_mapping.get(schedule_track_name)

            location_name = u'{}'.format(component['LOCATION'])
            if location_name not in location_name_to_id_mapping:
                location_id = self.gb_api_client.get_or_create_location(name=location_name)
                location_name_to_id_mapping[location_name] = location_id
            else:
                location_id = location_name_to_id_mapping.get(location_name)

            # The SUMMARY field will map to the Session name in Guidebook
            session_name = u'{}'.format(component['SUMMARY'])
            description = u'{}'.format(component['DESCRIPTION'])
            session = self.gb_api_client.update_or_create_session(import_id=UID, name=session_name, start_time=session_start_time,
                                                                  end_time=session_end_time, description_html=description,
                                                                  schedule_tracks=[track_id], locations=[location_id])
            if settings.DEBUG:
                print session
            session_ids.append(session.get('id'))
        if settings.DEBUG:
            print schedule_track_name_to_id_mapping
            print location_name_to_id_mapping
            print session_ids
        return session_ids

    def get_ical_timezone_info(self, cal):
        """
        Get the timezone info of an calendar object parsed by Calendar.from_ical().
        Return the 'X-WR-TIMEZONE' if present, None o.w.
        """
        ical_xwr_timezone = cal.get('X-WR-TIMEZONE', None)
        if ical_xwr_timezone:
            ical_xwr_timezone = pytz.timezone(ical_xwr_timezone.rstrip('/'))  # remove trailing slashes
        return ical_xwr_timezone

    def is_within_time_and_date_limits(self, session_start_time, session_end_time, limit_start, limit_end):
        """
        Return True if session_start_time and session_end_time are within limit_start and limit_end.
        False otherwise.
        """
        return session_start_time > limit_start and session_end_time < limit_end

    def get_ical_object(self, ical_file):
        """
        Get a Calendar object from an ical_file.  Return that parsed object.
        Raise InvalidiCalendarFile on bad iCal input.
        """
        # get a string representation of the ical_file if we don't already have one
        if not isinstance(ical_file, basestring):
            ical_file.seek(0)
            ical_file_string = ical_file.read()
        else:
            ical_file_string = ical_file
        try:
            cal = Calendar.from_ical(ical_file_string)
        except Exception as error_on_string:
            raise InvalidiCalendarFile("Invalid Calendar file: {error}".format(error=error_on_string))
        return cal

    def cal_components(self, cal):
        """
        Walk through a Calendar object checking the components for only the ones we're interested in.
        """
        cal_components = []
        for component in cal.walk():
            #  We only want to import VEVENTs.  It is fine if the VEVENT is marked as VFREEBUSY
            if component.name == 'VEVENT' or component.name == 'VFREEBUSY':
                cal_components.append(component)
        return cal_components
