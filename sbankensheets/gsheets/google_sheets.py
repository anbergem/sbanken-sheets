from typing import Dict, Sequence

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from ..gsheets.a1 import A1Range


class GSheet(object):
    """
    Class for handling request to Google Sheets.
    """

    @staticmethod
    def _create_authenticated_google_service():
        scope = "https://www.googleapis.com/auth/spreadsheets"
        store = file.Storage("auth/token.json")
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets("auth/credentials.json", scope)
            creds = tools.run_flow(flow, store)
        service = build("sheets", "v4", http=creds.authorize(Http()))
        return service

    def __init__(self, spreadsheet_id: str):
        self.service = GSheet._create_authenticated_google_service()
        self.spreadsheet_id = spreadsheet_id

    def get(
        self, range: A1Range, value_render_option=None, date_time_render_option=None
    ) -> Dict:
        """
        Get the cell values within the specified range.
        :param range: The range to retrieve the cell values from.
        :param value_render_option: Rendering option for output value.
        Valid valued are FORMATTED_VALUE, UNFORMATTED_VALUE and FORMULA
        :param date_time_render_option: Determines how dates should be
        rendered in the output. Valid values are SERIAL_NUMBER and
        FORMATTED_STRING
        :return: A dict with the cell values stored in 'values'.
        """
        return (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=str(range),
                valueRenderOption=value_render_option,
                dateTimeRenderOption=date_time_render_option,
            )
            .execute()
        )

    def append(
        self,
        range: A1Range,
        values: Sequence[Sequence[str]],
        value_input_option: str = "USER_ENTERED",
        insert_data_option: str = "OVERWRITE",
    ) -> Dict:
        """
        Append the values to a range in a google sheet.
        :param range: The range to insert the values.
        :param values: The values to be inserted
        :param value_input_option: 'USER_ENTERED' or 'RAW', whether the input should be as if the user
        entered the values or not.
        :param insert_data_option: 'OVERWRITE' or 'INSERT_ROWS'. The former writes the new data over existing
        data in the areas it is written. This still inserts rows at end of file. The latter inserts completely
        new rows for each entry.
        :return: A confirmation dict.
        """
        return (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=str(range),
                valueInputOption=value_input_option,
                insertDataOption=insert_data_option,
                body={"range": str(range), "values": values},
            )
            .execute()
        )

    def get_batch(self, ranges) -> Dict:
        """
        Get a batch of cell values within the specified ranges.
        :param ranges: The ranges to retrieve the cell values from.
        :return: A list of dicts with the cell values stored in 'values'.
        """
        return (
            self.service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=self.spreadsheet_id, ranges=[str(r) for r in ranges]
            )
            .execute()
        )

    def clear(self):
        raise NotImplementedError
