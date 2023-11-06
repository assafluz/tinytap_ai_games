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
        self.failed_game_terms = []
        self.used_terms = set()
        self.popular_terms = self.load_popular_terms()
        self.setup_webdriver()
        self.game_durations = {}

    def setup_webdriver(self):
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    def load_popular_terms(self):
        popular_terms_file = os.path.join(os.path.dirname(__file__), "popular_terms.txt")
        with open(popular_terms_file, "r") as file:
            return [line.strip() for line in file.readlines()]

    def open_url(self, url):
        self.driver.get(url)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def modify_url(self):
        available_terms = list(set(self.popular_terms) - self.used_terms)
        if not available_terms:
            return None

        self.current_term = random.choice(available_terms)
        self.used_terms.add(self.current_term)
        return f"https://www.tinytap.com/ai/game/{self.current_term}"

    def generate_game(self):
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
            self.game_start_time = time.time()
            print(f"Generation started for term: {self.current_term}")

            # Wait up to 180 seconds for the play button to appear
            wait = WebDriverWait(self.driver, 180)
            iframe = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@title="AI Game"]')))
            self.driver.switch_to.frame(iframe)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'playButton')))

            # Once the play button appears, capture the time
            self.game_ready_time = time.time()
            print(f"Play button ready for term: {self.current_term}")

        except Exception as e:
            self.failed_game_terms.append(self.current_term)
            print(f"Exception in generate_game: {e}")
        finally:
            self.driver.switch_to.default_content()

    def click_play_generated_game(self):
        try:
            # Wait for the iframe to load
            wait = WebDriverWait(self.driver, 60)
            iframe = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@title="AI Game"]')))
            self.driver.switch_to.frame(iframe)

            # Wait for the play button to be clickable
            play_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'playButton')))

            # Capture the time just before clicking the play button
            end_time = time.time()
            play_button.click()
            time.sleep(4)

            # Calculate and store the duration
            duration = end_time - self.game_start_time
            self.game_durations[self.current_term] = duration
            print(f"Play button clicked for term: {self.current_term}, duration: {duration}")
        except Exception as e:
            self.failed_game_terms.append(self.current_term)
            print(f"Exception in click_play_generated_game for term {self.current_term}: {e}")
        finally:
            self.driver.switch_to.default_content()

    def save_results_html(self, new_url):
        results_html_file = os.path.join(os.path.dirname(__file__), "..", "index.html")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        duration = self.game_durations.get(self.current_term, "N/A")

        duration_str = f"{duration:.2f} seconds" if isinstance(duration, (float, int)) else duration
        with open(results_html_file, "a") as file:
            file.write(f"<p>{timestamp} - <a href='{new_url}'>{new_url}</a> - ~Duration: {duration_str}</p>\n")

    def save_failed_terms(self):
        failed_terms_file = os.path.join(os.path.dirname(__file__), "failed_terms.txt")
        with open(failed_terms_file, "a") as file:
            file.write(self.current_term + "\n")

    def tearDown(self):
        self.driver.quit()

    def test_create_ai_game(self):
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
