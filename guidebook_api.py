from guidebook import api_requestor

import settings


class GuidebookAPI(object):

    # This class uses the guidebook api_requestor found at https://github.com/Guidebook/guidebook-api-python
    # to interact with the Guidebook API.  Documentation found at: https://developer.guidebook.com/v1/
    BASE_API_URL = 'https://builder.guidebook.com/open-api/v1/'

    def __init__(self, api_key=None, guide_id=None):
        """Initialize the instance with the given parameters."""
        if settings.DEBUG:
            print 'BASE API URL: {}'.format(self.BASE_API_URL)
        self.api_client = api_requestor.APIRequestor(api_key)
        self.guide_id = guide_id
        if settings.DEBUG:
            print 'Starting Guidebook API connection...'
        self.sessions = self.fetch_existing_sessions()
        if settings.DEBUG:
            print '{} existing sessions fetched from guide {}'.format(len(self.sessions), guide_id)
        self.schedule_tracks = self.fetch_existing_schedule_tracks()
        if settings.DEBUG:
            print '{} existing schedule tracks fetched from guide {}'.format(len(self.schedule_tracks), guide_id)
        self.locations = self.fetch_existing_locations()
        if settings.DEBUG:
            print '{} existing locations fetched from guide {}'.format(len(self.locations), guide_id)

    def concatenate_all_page_data(self, api_url, result_keys):
        """Guidebook API responses are paged.  This helper function will iterate through the pages and return all objects in one list."""
        objects = []
        next_page = api_url
        while next_page:
            response = self.api_client.request('get', next_page)
            results = response['results']
            next_page = response['next']
            for result in results:
                objects.append({key: result[key] for key in result_keys})
        return objects

    def find_session_by_import_id(self, import_id):
        """Check to see if a Session already exists in Guidebook that matches on import_id.  Return Session id if matched."""
        for session in self.sessions:
            if session['import_id'] == import_id:
                return session['id']
        return None

    def find_session_by_name(self, name):
        """Check to see if a Session already exists in Guidebook that matches on name.  Return Session id if matched."""
        for session in self.sessions:
            if session['name'] == name:
                return session['id']
        return None

    def find_schedule_track_by_name(self, name):
        """Check to see if a Schedule Track already exists in Guidebook that matches on name.  Return Schedule Track id if matched."""
        for track in self.schedule_tracks:
            if track['name'] == name:
                return track['id']
        return None

    def find_location_by_name(self, name):
        """Check to see if a Location already exists in Guidebook that matches on name.  Return Location id if matched."""
        for location in self.locations:
            if location['name'] == name:
                return location['id']
        return None

    def fetch_existing_sessions(self):
        """Fetch all existing Sessions for a given Guide in Guidebook."""
        api_url = '{}sessions/?guide={}'.format(self.BASE_API_URL, self.guide_id)
        sessions = self.concatenate_all_page_data(api_url, ['id', 'import_id', 'name', 'start_time', 'end_time'])
        return sessions

    def fetch_existing_schedule_tracks(self):
        """Fetch all existing Schedule Tracks for a given Guide in Guidebook."""
        api_url = '{}schedule-tracks/?guide={}'.format(self.BASE_API_URL, self.guide_id)
        schedule_tracks = self.concatenate_all_page_data(api_url, ['id', 'name', 'color'])
        return schedule_tracks

    def fetch_existing_locations(self):
        """Fetch all existing Locations for a given Guide in Guidebook."""
        api_url = '{}locations/?guide={}'.format(self.BASE_API_URL, self.guide_id)
        locations = self.concatenate_all_page_data(api_url, ['id', 'import_id', 'name'])
        return locations

    def create_session(self, name=None, description_html=None, start_time=None, end_time=None, all_day=False,
                       allow_rating=True, add_to_schedule=True, import_id=None, schedule_tracks=None, locations=None):
        """Create a Session in the Guidebook Guide."""
        api_url = '{}sessions/'.format(self.BASE_API_URL)
        if schedule_tracks is None:
            schedule_tracks = []
        if locations is None:
            locations = []
        post_data = {
            'guide': self.guide_id,
            'name': name,
            'description_html': description_html,
            'start_time': start_time,
            'end_time': end_time,
            'schedule_tracks': schedule_tracks,
            'locations': locations,
            'all_day': all_day,
            'allow_rating': allow_rating,
            'add_to_schedule': add_to_schedule,
            'import_id': import_id,
        }
        response = self.api_client.request('post', api_url, data=post_data)
        return response

    def create_schedule_track(self, name=None, color=None):
        """Create a Schedule Track in the Guidebook Guide."""
        api_url = '{}schedule-tracks/'.format(self.BASE_API_URL)
        post_data = {
            'guide': self.guide_id,
            'name': name,
            'color': color,
        }
        response = self.api_client.request('post', api_url, data=post_data)
        return response

    def create_location(self, name=None, location_type=2, latitude=None, longitude=None, import_id=None):
        """Create a Location in the Guidebook Guide."""
        api_url = '{}locations/'.format(self.BASE_API_URL)
        post_data = {
            'guide': self.guide_id,
            'name': name,
            'location_type': location_type,
            'latitude': latitude,
            'longitude': longitude,
            'import_id': import_id,
        }
        response = self.api_client.request('post', api_url, data=post_data)
        return response

    def update_session(self, session_id=None, update_data=None):
        """Update a Session in the Guidebook Guide."""
        api_url = '{}sessions/{}/'.format(self.BASE_API_URL, session_id)
        response = self.api_client.request('patch', api_url, data=update_data)
        return response

    def update_schedule_track(self, schedule_track_id=None, update_data=None):
        """Update a Schedule Track in the Guidebook Guide."""
        api_url = '{}schedule-tracks/{}/'.format(self.BASE_API_URL, schedule_track_id)
        response = self.api_client.request('patch', api_url, data=update_data)
        return response

    def update_location(self, location_id=None, update_data=None):
        """Update a Location in the Guidebook Guide."""
        api_url = '{}locations/{}/'.format(self.BASE_API_URL, location_id)
        response = self.api_client.request('patch', api_url, data=update_data)
        return response

    def update_or_create_session(self, **kwargs):
        """Checks for an existing Session for updating before creating a new Session in the Guidebook Guide."""
        if settings.USE_IMPORT_ID:
            existing_session_id = self.find_session_by_import_id(kwargs['import_id'])
        else:
            existing_session_id = self.find_session_by_name(kwargs['name'])
        if existing_session_id is not None:
            return self.update_session(session_id=existing_session_id, update_data=kwargs)
        else:
            return self.create_session(**kwargs)

    def update_or_create_schedule_track(self, **kwargs):
        """Checks for an existing Schedule Track for updating before creating a new Schedule Track in the Guidebook Guide."""
        existing_track_id = self.find_schedule_track_by_name(kwargs['name'])
        if existing_track_id is not None:
            return self.update_schedule_track(session_id=existing_track_id, update_data=kwargs)
        else:
            return self.create_schedule_track(**kwargs)

    def update_or_create_location(self, **kwargs):
        """Checks for an existing Location for updating before creating a new Location in the Guidebook Guide."""
        existing_location_id = self.find_location_by_name(kwargs['name'])
        if existing_location_id is not None:
            return self.update_location(location_id=existing_location_id, update_data=kwargs)
        else:
            return self.create_location(**kwargs)

    def get_or_create_session(self, **kwargs):
        """Checks for an existing Session before creating a new Session in the Guidebook Guide. Returns the object id."""
        if settings.USE_IMPORT_ID:
            existing_session_id = self.find_session_by_import_id(kwargs['import_id'])
        else:
            existing_session_id = self.find_session_by_name(kwargs['name'])
        if existing_session_id is None:
            return self.create_session(**kwargs)['id']
        else:
            return existing_session_id

    def get_or_create_schedule_track(self, **kwargs):
        """Checks for an existing Schedule Track before creating a new Schedule Track in the Guidebook Guide. Returns the object id."""
        existing_track_id = self.find_schedule_track_by_name(kwargs['name'])
        if existing_track_id is None:
            return self.create_schedule_track(**kwargs)['id']
        else:
            return existing_track_id

    def get_or_create_location(self, **kwargs):
        """Checks for an existing Location before creating a new Location in the Guidebook Guide. Returns the object id."""
        existing_location_id = self.find_location_by_name(kwargs['name'])
        if existing_location_id is None:
            return self.create_location(**kwargs)['id']
        else:
            return existing_location_id
