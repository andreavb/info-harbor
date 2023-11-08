import concurrent.futures
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


main_chess_results_url = "https://chess-results.com/SpielerSuche.aspx?lan=1"
download_dir = "/tmp/games"

def setup_chrome_driver():

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Set up the Chrome driver
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def extract_tournament_details_from_table(table_rows):

    links_to_save = []

    # Iterate through the rows and extract data
    for row in table_rows:
        columns = row.find_all("td")
        tournament = columns[5].text.strip()
        end_date = columns[6].text.strip()
        number = columns[9].text.strip()

        # Extract the href value
        link = (columns[0].find("a")["href"]).split("?")[0]

        print("Tournament:", tournament)
        print("End Date:", end_date)
        print("Link:", link)
        print("-------------------------")
        links_to_save.append(link)

    return links_to_save


def extract_players_from_table(table_rows):

    players = []

    # Iterate through the rows and extract data
    for row in table_rows:
        columns = row.find_all("td")
        player = {}
        player["id"] = columns[4].text.strip()
        player["name"] = columns[2].text.strip()
        player["rtg"] = columns[5].text.strip()

        if player["rtg"] is None or player["rtg"] == "0":
            print("SKIPPING PLAYER: %s does not have FIDE ID and/or rating" % player["name"])
        else:
            print("ADDING PLAYER: %s %s %s" %(player["id"], player["name"], player["rtg"]))
            players.append(player)

    return players


def save_links_to_file(filepath, links_to_save):

    # Save the links to a file
    with open(filepath, "w") as file:
        for link in links_to_save:
            file.write(link + "\n")


def search_player_in_form(driver, keyword):

    # Find the search input field by ID and enter the FIDE ID
    search_box = driver.find_element("id", "P1_txt_fideID")
    search_box.send_keys(keyword)

    # Submit the search query
    search_box.send_keys(Keys.RETURN)

    # Wait for the search results to load
    driver.implicitly_wait(10)

    # Print the page content (you can adjust this part to extract specific information)
    page_source = driver.page_source

    return page_source


def scrap_page(driver, url, player_id):

    # Navigate to the chess-results website, search for player, and collect results
    driver.get(url)
    page_source = search_player_in_form(driver, player_id)
    return page_source


def get_tournament_details(link, tournament_driver):
    cr_link = "https://chess-results.com/" + link
    print("Getting details for: %s" % link)
    expected_file_name =  link.split('.')[0][3:] + ".pgn"
    if expected_file_name in os.listdir(download_dir):
        return

    # set up the Chrome driver
    tournament_driver.get(cr_link)
    tournament_source = tournament_driver.page_source

    # tournaments that finished more than 5 days ago will require extra processing
    if "cb_alleDetails" in tournament_source:
        alle_details_button = tournament_driver.find_element("id", "cb_alleDetails")
        alle_details_button.click()

        # update source after clicking the load data button
        tournament_source = tournament_driver.page_source

    # find downloadable games
    if "games available" in tournament_source:

        games_link = tournament_driver.find_element("xpath", "//a[contains(@href, 'PartieSuche.aspx?lan=1&id=')]").get_attribute("href")
        print("Games Link: ", games_link)
        download_pgn(games_link, expected_file_name)

    else:
        open(download_dir + "/" + expected_file_name, 'a').close()
        print("No games found here")

    print("--------")


def download_pgn(games_link, expected_file_name):

   # get link to downloadable games
    games_driver = setup_chrome_driver()
    games_driver.get(games_link)
    download_pgn_button = games_driver.find_element("id", "P1_cb_DownLoadPGN")
    download_pgn_button.click()

    # wait for the updated page to load
    wait = WebDriverWait(games_driver, 60)
    wait.until(lambda games_driver: expected_file_name in os.listdir(download_dir))

    games_driver.quit()


def download_tournament_details(link):
    # Create a new driver for each thread or process
    driver = setup_chrome_driver()
    get_tournament_details(link, driver)
    driver.quit()

def download_all_pgns(tournaments_filepath):
    with open(tournaments_filepath, "r") as file:
        links = file.readlines()

    cleaned_links = [link.strip() for link in links]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_tournament_details, link) for link in cleaned_links]

    # Wait for all tasks to complete
    concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)


def parse_main_page(player_id, tournaments_filepath):

    # Setup driver, scrap the page, let the driver go
    chess_results_driver = setup_chrome_driver()
    tournaments_played_source = scrap_page(chess_results_driver, main_chess_results_url, player_id)
    chess_results_driver.quit()

    # Parse the results
    soup = BeautifulSoup(tournaments_played_source, 'html.parser')

    # Find all the table rows with the class "CRg1" or "CRg2"
    tournaments_table_rows = soup.find_all("tr", class_=["CRg1", "CRg2"])

    # Extract and print data
    list_of_links = extract_tournament_details_from_table(tournaments_table_rows)

    # Save links to file
    save_links_to_file(tournaments_filepath, list_of_links)


def parse_tournament_page(tournament_id):

    cr_link = "https://chess-results.com/tnr%s.aspx?lan=1" %tournament_id
    tournament_driver = setup_chrome_driver()
    tournament_driver.get(cr_link)
    tournament_source = tournament_driver.page_source
    tournament_driver.quit()

    # Parse the results
    soup = BeautifulSoup(tournament_source, 'html.parser')

    # Find all players
    tournament_players_rows = soup.find_all("tr", class_=["CRng1 BRA", "CRng2 BRA"])

    # Extract and print data
    list_of_players = extract_players_from_table(tournament_players_rows)

    return list_of_players
