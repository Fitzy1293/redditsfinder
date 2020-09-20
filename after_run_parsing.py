import json
from pprint import pprint
from rich.table import Table,Column
from rich.console import Console

def shortened(jsonPath):
    console = Console()
    with open(jsonPath) as f:
        data = json.load(f)

    console.print('[bold blue]Comment URLs:')
    for comment in  data['comments']:
        if comment["permalink"] is None:
            continue

        urlShort = "/".join (comment["permalink"].replace("https://www.reddit.com/", "").split("/")[0:4])

        console.print(f'[cyan]\t{urlShort}')

    console.print('[bold blue]\nSubmission URLs:')
    for submission in data['submissions']:
        if submission["full_link"] is None:
            continue
        urlShort = "/".join (submission["full_link"].replace("https://www.reddit.com/", "").split("/")[0:4])

        console.print(f'[magenta]\t{urlShort}')
