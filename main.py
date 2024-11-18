from garmin_class import GarminLoginSession, GarminActionSession
from mywhoosh_class import MyWhooshSession


def sync():
    with GarminLoginSession() as garmin_login, GarminActionSession() as garmin:
        garmin.download_activities_list()
        garmin_activities = garmin.get_activities_list()
    with MyWhooshSession() as mywhoosh:
        print(garmin_activities)

        if mywhoosh.download_activities(activities_list=garmin_activities):
            print("Activities Downloaded")
        else:
            print("No Activities to be synced")
            garmin.delete_cookies()
            return

    with GarminActionSession() as garmin:
        garmin.upload_activities()
        garmin.delete_cookies()


if __name__ == "__main__":
    sync()
