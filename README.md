# Switch-Classes
I created this to programmatically switch a symbolic link to point towards the correct class folder based on class times from my Google Calendar.

# How to Run
In a .env:
- List class aliases which should match descriptions of classes in Google Calendar and set them to the class directory.
- Include a `CURRENT_COURSE_LINK` and set it to the symbolic link directory.
- Include a `CALENDAR_ID` which will be the Calendar ID for the Google Calendar with all classes

Set up Google Calendar API:
- [https://developers.google.com/calendar/api/quickstart/python](https://developers.google.com/calendar/api/quickstart/python)
- Move `credentials.json` to the project directory

# How to Use
The intent is to schedule cron jobs so we do not have to manually run the script each time. Edit `scripts.sh` to match where the project directory is. `source ~/Projects/switch-classes/venv/bin/activate` can also be modified/deleted depending on if a pyenv is used. My cron job is as follows:

`0,15,30,45 9-15 * 8-12 1-5 sh ~/Projects/switch-classes/scripts.sh`. You can experiment with what works best [here](https://crontab.guru/#0,15,30,45_9-15_*_8-12_1-5).


