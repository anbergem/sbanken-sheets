from typing import List, Dict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


class GSheets(object):

    @staticmethod
    def _create_authenticated_google_service():
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=creds.authorize(Http()))
        return service

    def __init__(self, spreadsheet_id: str):
        self.service = GSheets._create_authenticated_google_service()
        self.spreadsheet_id = spreadsheet_id

    def get(self, range):
        return self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range
        ).execute()

    def append(self,
               range: str,
               values: List[List[str]],
               value_input_option: str = 'USER_ENTERED',
               insert_data_option: str = 'OVERWRITE', ) -> Dict:
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body={
                'range': range,
                'values': values
            }
        ).execute()

    def get_batch(self, ranges: List[str]):
        return self.service.spreadsheets().values().getBatch(
            spreadsheetId=self.spreadsheet_id,
            ranges=ranges
        ).execute()

    def clear(self):
        raise NotImplementedError
