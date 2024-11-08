from garmin_class import GarminLoginSession, GarminActionSession
from mywhoosh_class import MyWhooshSession

with GarminLoginSession() as garmin_login, GarminActionSession() as garmin:
    garmin.download_activities_list()
    garmin_activities = garmin.get_activities_list()

    print(garmin_activities)
with MyWhooshSession() as mywhoosh:
    print(garmin_activities)
    mywhoosh.get_list_of_activities(activities_list=garmin_activities)

with GarminLoginSession() as garmin_login, GarminActionSession() as garmin:
    garmin_activities = garmin.upload_activities()
