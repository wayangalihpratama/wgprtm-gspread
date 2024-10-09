# wgprtm-gspread
Learning Google Sheets API with gpread


## Set Up Google API Credentials
Make sure you have the `credentials.json` file that you obtained from Google’s API Console for accessing the Google Sheets API. Place it in the project directory. If you don't have one:
1. Go to the Google Cloud Console.
2. Enable the Google Sheets API and Google Drive API.
3. Create a new service account, and download the `credentials.json` file.
4. Put `credentials.json` in same location with `app.py` (root project directory).


## Running the application

```bash
docker compose up
```


## Interact with the application

```bash
docker compose exec app /bin/bash
```

```bash
python app.py
```


## Stop the application

```bash
docker compose down
```