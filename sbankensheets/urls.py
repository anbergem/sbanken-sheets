import re

summary_url = "https://docs.google.com/spreadsheets/d/1-dA8OSYlvLHq-Zfj1wOA7_e4RXM0SmpoOyUcGEwuapI/edit#gid=1861277466"
august_overview_url = "https://docs.google.com/spreadsheets/d/1-dA8OSYlvLHq-Zfj1wOA7_e4RXM0SmpoOyUcGEwuapI/edit#gid=0"
august_transactions_url = "https://docs.google.com/spreadsheets/d/1-dA8OSYlvLHq-Zfj1wOA7_e4RXM0SmpoOyUcGEwuapI/edit#gid=1732160294"

_spreadsheet_id_regex = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
_sheet_id_regex = r"[#&]gid=([0-9]+)"

spreadsheet_id = re.findall(_spreadsheet_id_regex, summary_url)[0]
summary_sheet_id = re.findall(_sheet_id_regex, summary_url)[0]
august_overview_sheet_id = re.findall(_sheet_id_regex, august_overview_url)[0]
august_transactions_sheet_id = re.findall(_sheet_id_regex, august_transactions_url)[0]
