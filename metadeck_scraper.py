import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

DECK_DOC = "https://docs.google.com/spreadsheets/d/1VPeQMqG7r0AR_UUo12rMfxYqREQdXXxDHIM2BGb-abE/htmlview#"
EXPANSION_LIST = "https://ygoprodeck.com/api/set-lists/getCardSetsList.php?_=1666994021496"

CARD_STATUS = {
    "Forbidden": 0,
    "Limited": 1,
    "Semi-Limited": 2,
    "Unlimited": 3
}

MOST_RECENT_EVENT_DATES = {
    "Minneapolis": "2022-10-22",
    "Utrecht": "2022-10-14",
    "Niagra": "2022-09-10",
    "Rio": "2022-08-27",
    "Hartford": "2022-05-28",
    "Guadalajara": "2022-04-30",
    "Bogota": "2022-04-23",
    "Charlotte": "2022-04-09"
}

BANLIST_DATES = ["2022-02-07", "2022-05-17", "2022-10-3"]

def get_expansions():
    expansions = requests.get("https://ygoprodeck.com/api/set-lists/getCardSetsList.php?_=1666994021496")
    expansions_json = json.loads(expansions.content.decode('utf-8'))
    expansions_with_dates = [expansion for expansion in expansions_json["data"] if len(expansion["tcg_date"]) > 1]
    expansions_with_dates.sort(key = lambda x: datetime.strptime(x["tcg_date"], "%Y-%m-%d"), reverse = True)

    return expansions_with_dates

def get_banlist_links():
    wiki_page_request_text = requests.get("https://yugipedia.com/wiki/Historic_Forbidden/Limited_Chart").text
    soup = BeautifulSoup(wiki_page_request_text, "html.parser")
    navbox_list = soup.find("td", {"class":"navbox-list navbox-even"})

    banlist_hash = {}

    for link in navbox_list.find_all("a"):
        title = link.get("title")
        href = link.get("href")
        text = link.string
        year = [int(s) for s in str.split(title) if s.isdigit()][0]

        if year not in banlist_hash:
            banlist_hash[year] = {}
            banlist_hash[year][text] = {"title": title, "href": href, "text": text, "year": year}
        else:
            banlist_hash[year][text] = {"title": title, "href": href, "text": text, "year": year}
    
    return banlist_hash

# For each banlist, add cards field with a previous status and new status
def get_banlist_cards(banlist_hash):

    print("")

def get_ycs_top_decks():
    tournament_deck_type_counts = {}
    xl_file = pd.read_excel(r"YCS 2022 Deck Lists by Lundrity.xlsx", sheet_name=list(MOST_RECENT_EVENT_DATES.keys()), usecols="F")

    for tournament in list(MOST_RECENT_EVENT_DATES.keys()):
        for row in xl_file[tournament].loc[1:33].iterrows():
            deck_type = row[1].values[0]
            if tournament not in tournament_deck_type_counts:
                tournament_deck_type_counts[tournament] = {}
            if deck_type not in tournament_deck_type_counts[tournament]:
                tournament_deck_type_counts[tournament][deck_type] = 1
                continue
            tournament_deck_type_counts[tournament][deck_type] += 1

    return tournament_deck_type_counts

def display_timeline():
    expansions_in_2022 = [] 
    for expansion in get_expansions():
        if  expansion["tcg_date"].split("-")[0] == "2022":
            expansions_in_2022.append([expansion["set_name"], expansion["tcg_date"]])
        else:
            break

    plt.figure(999)
    plt.rcParams["figure.figsize"] = [12, 8]
    plt.rcParams["figure.autolayout"] = True

    x1 = [datetime.strptime(d, "%Y-%m-%d").date() for d in list(MOST_RECENT_EVENT_DATES.values())]
    y1 = [.5] * len(MOST_RECENT_EVENT_DATES.values())

    x2 = [datetime.strptime(d[1], "%Y-%m-%d").date() for d in expansions_in_2022]
    y2 = [-1] * len(expansions_in_2022)

    x3 = [datetime.strptime(d, "%Y-%m-%d").date() for d in BANLIST_DATES]
    y3 = [.5] * len(BANLIST_DATES)

    plt.title("Yugioh Meta Timeline")
    plt.stem(x1, y1, "g", label = "YCS Events")
    plt.stem(x2, y2, "b", label = "Expansions")
    plt.stem(x3, y3, "r", label = "Banlist Changes")
    plt.margins(.1)
    plt.legend()

    event_names = list(MOST_RECENT_EVENT_DATES.keys())
    idx = 0
    for x, event in zip(x1, event_names):
        plt.annotate(event, (x, 0.1 + (idx * .4 / len(x1))))
        idx += 1

    idx = 0
    for x, event in zip(x2, expansions_in_2022):
        plt.annotate(event[0], (x,-1 + (idx * 1.0 / len(x2))), fontsize=10)
        idx += 1

    # plt.show()

def display_decklist_breakdown():
    top_decks = get_ycs_top_decks()
    events = list(top_decks.keys())

    for idx, deck_list in enumerate(events):
        labels = list(top_decks[deck_list].keys())
        sizes = list(get_ycs_top_decks()[deck_list].values())
        plt.figure(idx)
        plt.pie(sizes, labels=labels, autopct='%.1f%%')
        plt.title("YCS {deck_list} Deck Breakdown".format(deck_list=deck_list))
    # plt.show()

display_timeline()
display_decklist_breakdown()
plt.show()
