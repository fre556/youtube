import logging
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Configure detailed logging for the log file (only errors)
log_file = "upload_bot.log"
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,  # Log only errors
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='a'  # Append to existing log file
)

# Adding console logging for all levels
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Constants
class Constant:
    YOUTUBE_URL = 'https://www.youtube.com'
    YOUTUBE_STUDIO_URL = 'https://studio.youtube.com'
    YOUTUBE_UPLOAD_URL = 'https://www.youtube.com/upload'
    USER_WAITING_TIME = 1
    VIDEO_TITLE = 'title'
    VIDEO_DESCRIPTION = 'description'
    VIDEO_EDIT = 'edit'
    VIDEO_TAGS = 'tags'
    TEXTBOX_ID = 'textbox'
    TEXT_INPUT = 'text-input'
    RADIO_LABEL = 'radioLabel'
    UPLOADING_STATUS_CONTAINER = '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[1]/ytcp-video-upload-progress[@uploading=""]'
    NOT_MADE_FOR_KIDS_LABEL = 'VIDEO_MADE_FOR_KIDS_NOT_MFK'
    UPLOAD_DIALOG = '//ytcp-uploads-dialog'
    ADVANCED_BUTTON_ID = 'toggle-button'
    TAGS_CONTAINER_ID = 'tags-container'
    TAGS_INPUT = 'text-input'
    NEXT_BUTTON = 'next-button'
    PUBLIC_BUTTON = 'PUBLIC'
    VIDEO_URL_CONTAINER = "//span[@class='video-url-fadeable style-scope ytcp-video-info']"
    VIDEO_URL_ELEMENT = "//a[@class='style-scope ytcp-video-info']"
    HREF = 'href'
    ERROR_CONTAINER = '//*[@id="error-message"]'
    VIDEO_NOT_FOUND_ERROR = 'Could not find video_id'
    DONE_BUTTON = 'done-button'
    INPUT_FILE_VIDEO = "//input[@type='file']"
    INPUT_FILE_THUMBNAIL = "//input[@id='file-loader']"
    VIDEO_PLAYLIST = 'playlist_title'
    CATEGORY = 'category'
    PL_DROPDOWN_CLASS = 'ytcp-video-metadata-playlists'
    PL_SEARCH_INPUT_ID = 'search-input'
    PL_ITEMS_CONTAINER_ID = 'items'
    PL_ITEM_CONTAINER = '//span[text()="{}"]'
    PL_NEW_BUTTON_CLASS = 'new-playlist-button'
    PL_CREATE_PLAYLIST_CONTAINER_ID = 'create-playlist-form'
    PL_CREATE_BUTTON_CLASS = 'create-playlist-button'
    PL_DONE_BUTTON_CLASS = 'done-button'
    SCHEDULE_DATE_INPUT_ID = 'datepicker'
    SCHEDULE_TIME_INPUT_ID = 'time-of-day'
    SCHEDULE_CONTAINER_ID = 'second-container-expand-button'
    CLOSE_BUTTON = 'close-button'
    SCHEDULE_DATE_TEXTBOX = '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'
    SCHEDULE_TIME = '//*[@aria-label="Time"]'
    VIDEO_SCHEDULE = 'schedule'
    SCHEDULE_TRIGGER_XPATH = '//*[@id="datepicker-trigger"]/ytcp-dropdown-trigger/div/div[2]/span'

# Set up Edge options
options = EdgeOptions()
options.use_chromium = True
options.add_argument("--log-level=3")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Ensure binary location is correct
options.binary_location = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

# Path to Edge WebDriver
edge_driver_path = "msedgedriver.exe"

# Initialize Edge WebDriver
service = EdgeService(executable_path=edge_driver_path)

class YouTubeUploader:
    def __init__(self, video_path, thumbnail_path, metadata_path, start_label, end_label):
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path
        self.metadata_path = metadata_path
        self.start_label = start_label
        self.end_label = end_label
        self.bot = None
        self.metadata = self.load_metadata()
        print(f"Uploader initialized with labels from {start_label} to {end_label}.")

    def load_metadata(self):
        print(f"Loading metadata from {self.metadata_path}.")
        with open(self.metadata_path, 'r', encoding='utf-8') as file:
            metadata = json.load(file)
        print(f"Metadata loaded.")
        return metadata

    def ensure_element_interactable(self, element):
        print(f"Checking if element is interactable.")
        if not element.is_displayed() or not element.is_enabled():
            logging.error("Element is not interactable")
            raise Exception("Element not interactable")
        print("Element is interactable")

    def upload_videos(self):
        try:
            print("Creating Edge WebDriver instance...")
            self.bot = webdriver.Edge(service=service, options=options)
            print("Edge WebDriver initialized successfully.")
            
            print("Navigating to YouTube Studio...")
            self.bot.get(Constant.YOUTUBE_STUDIO_URL)
            
            # Pause to allow manual login
            print("Please log into your Google account manually.")
            input("Press Enter after logging in to continue...")  # Wait for user input to continue
            
            # Debug: Check the current URL
            current_url = self.bot.current_url
            print(f"Current URL after login: {current_url}")
            
            if "studio.youtube.com" not in current_url:
                logging.error("Navigation to YouTube Studio failed.")
                print("Navigation to YouTube Studio failed.")
                return
            
            for item in self.metadata:
                label = item['Label']
                
                if label < self.start_label or label > self.end_label:
                    continue
                
                title = item['Title']
                description = item['Description']
                tags = item['Tags']
                schedule = item['schedule']
                
                video_file = f"{label}.mp4"
                video_path = os.path.join(self.video_path, video_file)
                
                # Ensure the file exists
                if not os.path.isfile(video_path):
                    print(f"Video file {video_file} not found, skipping.")
                    continue

                print(f"Processing video {label}: {title}")

                # Wait for the upload button to be visible and clickable
                print(f"Waiting for the upload button to be clickable for {video_file}...")
                upload_button = WebDriverWait(self.bot, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="upload-icon"]'))
                )
                upload_button.click()
                print(f"Clicked on upload button for {video_file}.")

                # Wait for the file input to appear
                print(f"Waiting for the file input to appear for {video_file}...")
                file_input = WebDriverWait(self.bot, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/input'))
                )
                
                abs_path = os.path.abspath(video_path)
                print(f"Uploading video from path: {abs_path}")
                file_input.send_keys(abs_path)
                print(f"Video file {video_file} uploaded.")

                # Wait for upload to process
                print(f"Waiting for the upload to process for {video_file}...")
                time.sleep(10)  # Adjust this time based on your internet speed and video size

                # Set title
                print(f"Setting title for {video_file}...")
                title_input = WebDriverWait(self.bot, 20).until(
                    EC.presence_of_element_located((By.ID, Constant.TEXTBOX_ID))
                )
                title_input.clear()
                title_input.send_keys(title)
                time.sleep(1)
                print(f"Title set for {video_file}")

                # Set description
                print(f"Setting description for {video_file}...")
                description_input = self.bot.find_elements(By.ID, Constant.TEXTBOX_ID)[1]
                description_input.clear()
                description_input.send_keys(description)
                time.sleep(1)
                print(f"Description set for {video_file}")

                # Set tags
                print(f"Setting tags for {video_file}...")
                self.bot.find_element(By.ID, Constant.ADVANCED_BUTTON_ID).click()
                tags_input = WebDriverWait(self.bot, 20).until(
                    EC.presence_of_element_located((By.ID, Constant.TAGS_INPUT))
                )
                tags_input.clear()
                tags_input.send_keys(", ".join(tags))
                time.sleep(1)
                print(f"Tags set for {video_file}")

                # Select playlist
                print(f"Selecting 'Classic War Movies' playlist for {video_file}...")
                playlist_dropdown = WebDriverWait(self.bot, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, Constant.PL_DROPDOWN_CLASS))
                )
                playlist_dropdown.click()
                time.sleep(1)
                
                vintage_videos_playlist = WebDriverWait(self.bot, 20).until(
                    EC.element_to_be_clickable((By.XPATH, Constant.PL_ITEM_CONTAINER.format("Classic mystery Movie")))
                )
                vintage_videos_playlist.click()
                time.sleep(1)

                done_playlist_button = WebDriverWait(self.bot, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, Constant.PL_DONE_BUTTON_CLASS))
                )
                done_playlist_button.click()
                time.sleep(1)
                print(f"Playlist 'Classic War Movies' selected for {video_file}.")

                # Upload thumbnail
                thumbnail_file = f"{label}.jpg"
                thumbnail_path = os.path.join(self.thumbnail_path, thumbnail_file)
                
                if os.path.isfile(thumbnail_path):
                    print(f"Uploading thumbnail for {video_file} from path: {thumbnail_path}")
                    thumbnail_input = WebDriverWait(self.bot, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="file-loader"]'))
                    )
                    thumbnail_input.send_keys(os.path.abspath(thumbnail_path))
                    time.sleep(1)
                    print(f"Thumbnail uploaded for {video_file}: {thumbnail_file}")
                else:
                    print(f"Thumbnail file {thumbnail_file} not found, skipping thumbnail upload.")
                    
                    
                    
                    

                # Click 'Next' buttons to navigate through the upload steps
                print(f"Clicking through the 'Next' buttons for {video_file}...")
                for _ in range(3):  # Click the 'Next' button three times to get to the "Checks" section
                    next_button = WebDriverWait(self.bot, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="next-button"]'))
                    )
                    next_button.click()
                    time.sleep(2)
                print(f"'Next' buttons clicked for {video_file}.")

                # Select Schedule option
                print(f"Selecting 'Schedule' for {video_file}...")
                try:
                    schedule_radio = WebDriverWait(self.bot, 20).until(
                        EC.element_to_be_clickable((By.ID, Constant.SCHEDULE_CONTAINER_ID))
                    )
                    schedule_radio.click()
                    time.sleep(1)

                    # Click to open the date picker
                    date_picker_trigger = WebDriverWait(self.bot, 20).until(
                        EC.element_to_be_clickable((By.XPATH, Constant.SCHEDULE_TRIGGER_XPATH))
                    )
                    date_picker_trigger.click()
                    time.sleep(1)

                    # Set schedule date and time
                    print(f"Setting schedule date and time from metadata: {schedule}")
                    schedule_datetime = datetime.strptime(schedule, '%Y-%m-%d %H:%M:%S')
                    date_str = schedule_datetime.strftime('%b %d, %Y')
                    time_str = schedule_datetime.strftime('%I:%M %p')

                    date_input = WebDriverWait(self.bot, 20).until(
                        EC.presence_of_element_located((By.XPATH, Constant.SCHEDULE_DATE_TEXTBOX))
                    )
                    date_input.click()
                    date_input.clear()
                    date_input.send_keys(date_str)
                    date_input.send_keys(Keys.ENTER)
                    time.sleep(1)

                    # Click 'Schedule' button to finish the scheduling
                    print(f"Clicking the 'Schedule' button for {video_file}...")
                    schedule_button = WebDriverWait(self.bot, 20).until(
                        EC.element_to_be_clickable((By.ID, Constant.DONE_BUTTON))
                    )
                    schedule_button.click()
                    
                    print(f"Scheduling of {video_file} completed successfully.")
                    time.sleep(10)
                    self.bot.refresh()
                except Exception as e:
                    logging.error(f"Error selecting 'Schedule' option: {e}")
                    print(f"Error selecting 'Schedule' option: {e}")

                time.sleep(20)  # Wait a bit before proceeding to the next video
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
        finally:
            if self.bot is not None:
                time.sleep(2400)
                print("Quitting the browser session.")
                self.bot.quit()

if __name__ == "__main__":
    video_path = "M:/Youtube/MovieChannel/SpagettiWestern/"
    thumbnail_path = "D:/Users/mini-beast/OneDrive/Business/Youtube/Classic Cinema Collection/toupload/Mystery/"
    metadata_path = "D:/Users/mini-beast/OneDrive/Business/Youtube/Classic Cinema Collection/WorkingFolder/metadata.json"
    start_label = 1  # Adjust as necessary
    end_label = 100 # Adjust as necessary
    uploader = YouTubeUploader(video_path, thumbnail_path, metadata_path, start_label, end_label)
    uploader.upload_videos()
