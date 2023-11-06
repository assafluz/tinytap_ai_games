from unittest import TestCase, main
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class TestCreateAiGame(TestCase):
    def setUp(self):
        self.failed_game_terms = []  # List to store terms that failed to generate
        self.used_terms = set()  # Set to keep track of used terms
        self.popular_terms = self.load_popular_terms()  # Load popular terms
        self.setup_webdriver()  # Set up the webdriver
        self.game_durations = {}  # Dictionary to store the duration for each game

    def setup_webdriver(self):
        # Set up Chrome WebDriver
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    def load_popular_terms(self):
        # Load terms from an external file
        popular_terms_file = os.path.join(os.path.dirname(__file__), "popular_terms.txt")
        with open(popular_terms_file, "r") as file:
            return [line.strip() for line in file.readlines()]

    def open_url(self, url):
        # Open the URL in the browser
        self.driver.get(url)
        self.driver.maximize_window()
        time.sleep(3)  # Consider dynamic wait instead of fixed sleep

    def modify_url(self):
        # Modify the URL with a unique term
        available_terms = list(set(self.popular_terms) - self.used_terms)
        if not available_terms:
            return None

        self.current_term = random.choice(available_terms)
        self.used_terms.add(self.current_term)
        return f"https://www.tinytap.com/ai/game/{self.current_term}"

    def generate_game(self):
        # Start generating the game and record the start time
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
        self.game_start_time = time.time()  # Record start time

    def click_play_generated_game(self):
        try:
            wait = WebDriverWait(self.driver, 30)
            iframe = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@title="AI Game"]')))
            self.driver.switch_to.frame(iframe)
            play_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'playButton')))
            play_button.click()

            # Calculate and store the duration for the current term
            duration = time.time() - self.game_start_time
            self.game_durations[self.current_term] = duration
        except Exception as e:
            self.failed_game_terms.append(self.current_term)
        finally:
            self.driver.switch_to.default_content()

    def save_results_html(self, new_url):
        # Save the results to an HTML file
        results_html_file = os.path.join(os.path.dirname(__file__), "..", "index.html")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        duration = self.game_durations.get(self.current_term, "N/A")

        # Check if duration is a number and format accordingly
        if isinstance(duration, (float, int)):
            duration_str = f"{duration:.2f} seconds"
        else:
            duration_str = duration

        with open(results_html_file, "a") as file:
            file.write(f"<p>{timestamp} - <a href='{new_url}'>{new_url}</a> - Duration: {duration_str}</p>\n")

    def save_failed_terms(self):
        # Save failed terms to a file
        failed_terms_file = os.path.join(os.path.dirname(__file__), "failed_terms.txt")
        with open(failed_terms_file, "a") as file:
            file.write(self.current_term + "\n")

    def tearDown(self):
        # Clean up and close the browser
        self.driver.quit()

    def test_create_ai_game(self):
        # Main test method to create AI games
        for _ in range(len(self.popular_terms)):
            new_url = self.modify_url()
            if new_url is None:
                break

            self.open_url(new_url)
            self.generate_game()
            self.click_play_generated_game()
            self.save_results_html(new_url)

        if self.failed_game_terms:
            print("Games failed to generate for the following terms:")
            for term in self.failed_game_terms:
                print(term)

if __name__ == '__main__':
    main()
