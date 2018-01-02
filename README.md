# About

This code provides an example of how to integrate Guidebook with ICalendar data.

It fetches Session data in the [ICalendar format](https://en.wikipedia.org/wiki/ICalendar) and imports it into Guidebook via the [Guidebook Open API](https://developer.guidebook.com/).

# Sample Usage

Before testing out the code.  Please `pip install -r requirements.txt` to get the package dependencies.  We highly recommend you do this in an [virtualenv](https://virtualenv.pypa.io/en/stable/).

Update `settings.py` with your API information.  Setting the `DEBUG` flag to `True` will output debugging info with each stage of import.  We also provide a `sample_ical.ics` file for demonstration purposes.  You can easily substitute your own file or feed url for importing.  The following command will perform the import.

`python execute_integration`

# Customizing this Integration

This code is provided to Guidebook clients to customize for their own integrations.  Clients are welcome to take this integration code as a starting point and adapt it to their own needs.

Every ICalendar file is different.  If your data feed implements more complex session data such as recurring events, you'll need to adapt the `ical_importer.py` code to accomodate.