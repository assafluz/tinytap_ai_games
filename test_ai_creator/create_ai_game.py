from telnetlib import EC
from unittest import TestCase, main
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestCreateAiGame(TestCase):

    def setUp(self):
        self.failed_game_terms = []  # Initialize a list to store terms that failed to generate
        self.used_terms = set()
        self.popular_terms = self.load_popular_terms()
        self.driver = self.setup_webdriver()

    def setup_webdriver(self):
        options = webdriver.ChromeOptions()
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        chrome_driver_path = "/Users/androidtinytap/Downloads/chromedriver-mac-x64/chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        return driver

    def load_popular_terms(self):
        popular_terms_file = os.path.join(os.path.dirname(__file__), "popular_terms.txt")
        with open(popular_terms_file, "r") as file:
            terms = [line.strip() for line in file.readlines()]
        return terms

    def open_url(self, url):
        self.driver.get(url)
        self.driver.maximize_window()
        time.sleep(3)

    def modify_url(self):
        available_terms = list(set(self.popular_terms) - self.used_terms)
        if not available_terms:
            return None

        self.current_term = random.choice(available_terms)
        self.used_terms.add(self.current_term)
        new_url = f"https://www.tinytap.com/ai/game/{self.current_term}"
        return new_url

    def generate_game(self):
        self.driver.find_element_by_tag_name("body").send_keys(Keys.RETURN)
        time.sleep(150)

    def click_play_generated_game(self):
        try:
            # Explicitly wait for the iframe to load and switch to it
            wait = WebDriverWait(self.driver, 20)  # wait for 20 seconds
            iframe = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@title="AI Game"]')))
            self.driver.switch_to.frame(iframe)

            # Wait for the play button to be clickable
            play_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'playButton')))
            play_button.click()
            time.sleep(4)

        except Exception as e:
            print(f"Exception encountered: {e}")
            print(f"Failed to click the play button for term: {self.current_term}")
            self.failed_game_terms.append(self.current_term)
            # Save the failed term to the external file
            self.save_failed_terms()

        finally:
            # Ensure you switch back to the main content after you're done
            self.driver.switch_to.default_content()

    def save_results_html(self, new_url):
        results_html_file = os.path.join(os.path.dirname(__file__), "..", "index.html")
        if not os.path.exists(results_html_file):
            with open(results_html_file, "w") as file:
                file.write("<html><body>\n")

        timestamp = time.strftime("%Y-%m-d %H:%M:%S")
        with open(results_html_file, "r+") as file:
            content = file.read()
            if new_url not in content:
                file.write(f"<p>{timestamp} - <a href='{new_url}'>{new_url}</a></p>\n")

    def save_failed_terms(self):
        failed_terms_file = os.path.join(os.path.dirname(__file__), "failed_terms.txt")
        with open(failed_terms_file, "a") as file:  # Append mode
            file.write(self.current_term + "\n")

    def tearDown(self):
        self.driver.quit()

    def test_create_ai_game(self):
        for _ in range(len(self.popular_terms)):
            new_url = self.modify_url()

            if new_url is None:
                break

            self.open_url(new_url)  # Open the modified URL with the term at the end
            self.generate_game()
            self.click_play_generated_game()
            self.save_results_html(new_url)

        if self.failed_game_terms:
            print("Games failed to generate for the following terms:")
            for term in self.failed_game_terms:
                print(term)

if __name__ == '__main__':
    main()
