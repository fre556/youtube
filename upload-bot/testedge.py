import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

# Set up Edge options
options = EdgeOptions()
options.use_chromium = True
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Ensure binary location is correct
edge_binary_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
options.binary_location = edge_binary_path

# Path to Edge WebDriver
edge_driver_path = "msedgedriver.exe"

# Initialize Edge WebDriver
service = EdgeService(executable_path=edge_driver_path)

try:
    print("Launching Microsoft Edge...")
    driver = webdriver.Edge(service=service, options=options)
    print("Microsoft Edge launched successfully!")

    # Navigate to a test website
    driver.get("https://www.example.com")
    print(f"Current URL: {driver.current_url}")

    # Close the browser
    driver.quit()
    print("Microsoft Edge closed.")
except Exception as e:
    print(f"An error occurred: {str(e)}")