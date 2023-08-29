from unittest import TestCase, main
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import random
import os


class TestCreateAiGame(TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        chrome_driver_path = "/Users/androidtinytap/Downloads/chromedriver-mac-x64/chromedriver"
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        self.original_url = 'https://www.tinytap.com/ai/game/'

        # Construct the path for the index.html file one directory up
        self.results_html_file = os.path.join(os.path.dirname(__file__), "..", "index.html")

        self.used_terms = set()
        self.popular_terms = self.load_popular_terms()

    def load_popular_terms(self):
        # Provide the absolute path to the popular_terms.txt file
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
        new_url = f"{self.original_url}{self.current_term}"
        return new_url

    def generate_game(self):
        term = self.current_term
        self.driver.find_element_by_tag_name("body").send_keys(Keys.RETURN)
        time.sleep(10)

        game_generated = False
        timeout = 60
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.is_game_generated():
                game_generated = True
                break
            time.sleep(2)

        if not game_generated:
            print(f"Game generation failed for term: {term}")

    def is_game_generated(self):
        try:
            self.driver.find_element_by_id("game-generated-element")
            return True
        except NoSuchElementException:
            return False

    def save_results_html(self, new_url):
        if not os.path.exists(self.results_html_file):
            with open(self.results_html_file, "w") as file:
                file.write("<html><body>\n")

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.results_html_file, "r+") as file:
            content = file.read()
            if new_url not in content:
                file.write(f"<p>{timestamp} - <a href='{new_url}'>{new_url}</a></p>\n")

    def tearDown(self):
        self.driver.quit()

    def test_create_ai_game(self):
        for _ in range(len(self.popular_terms)):
            new_url = self.modify_url()

            if new_url is None:
                break

            self.open_url(new_url)  # Open the modified URL with the term at the end
            self.generate_game()
            self.save_results_html(new_url)


def main():
    test = TestCreateAiGame()
    test.test_create_ai_game()


if __name__ == '__main__':
    main()
