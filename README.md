# rp_horses

# status

each run returns an array of h_objecst:
For example:

```json

{'trainerName': 'Jim Goldie', 'trainerId': 7795, 'sireU': '/profile/horse/859275/gleneagles', 'sireId': 859275, 'retrievedAt': datetime.datetime(2023, 5, 4, 15, 3, 49, 415587, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>), 'progLinks': ['/profile/horse/859275/gleneagles', '/profile/horse/859520/antique-platinum', '/profile/horse/657462/holy-roman-emperor'], 'prevOwners': [{'name': 'Summerstorm Bloodstock Ltd', 'dateTo': datetime.datetime(2023, 5, 4, 0, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>)}, {'name': 'Summerstorm Bloodstock Ltd', 'dateTo': datetime.datetime(2023, 5, 4, 0, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>)}], 'ownerId': 306424, 'isGray': False, 'isGelded': False, 'isFemale': True, 'horseName': 'cosa-sara', 'horseId': '3125293', 'gender': 'm', 'dob': '09Mar18', 'damU': '/profile/horse/859520/antique-platinum', 'damSireU': '/profile/horse/657462/holy-roman-emperor', 'damSireId': 657462, 'damId': 859520, 'connLinks': ['/profile/trainer/7795/jim-goldie', '/profile/owner/306424/summerstorm-bloodstock-ltd'], 'color': 'b', 'breederName': 'moyglare stud farms ltd'}

```


TODO:
for each prevOwners owner_name ownership_dates 
standardize breederName <there are no slugs>
remove connLinks and progLinks which are controls

If can reduce speed per url consider resultsTable scrape as part of rp_horses_full.py
