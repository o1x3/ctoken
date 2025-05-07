from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os


# Permanent fix for OSError: [WinError 6]
def patch_undetected_chromedriver():
    import undetected_chromedriver as uc

    original_del = uc.Chrome.__del__

    def patched_del(self):
        try:
            if self.service.process:
                self.quit()
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            original_del(self)

    uc.Chrome.__del__ = patched_del


patch_undetected_chromedriver()


def get_openai_pricing():
    CHROME_PATH = r"C:\Users\imkvi\Downloads\chrome-win64\chrome.exe"
    CHROMEDRIVER_PATH = r"C:\Users\imkvi\Downloads\chromedriver-win64\chromedriver.exe"

    # Configure browser with explicit cleanup
    options = ChromeOptions()
    options.binary_location = CHROME_PATH
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    with Chrome(driver_executable_path=CHROMEDRIVER_PATH, options=options) as driver:
        try:
            driver.get("https://platform.openai.com/pricing")

            # Handle Cloudflare
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                )
            except Exception as e:
                print(f"Error: {str(e)}")
                input("Solve CAPTCHA then press Enter...")
                time.sleep(3)

            # Wait for page to fully load
            time.sleep(2)

            # Find and click the "All snapshots" expand button
            try:
                expand_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'All snapshots')]")
                    )
                )
                expand_button.click()
                # Wait for expanded content to load
                time.sleep(2)
            except Exception as e:
                print(f"Could not click expand button: {str(e)}")

            # Get only the first table (Text tokens)
            tables = driver.find_elements(By.CSS_SELECTOR, "table")
            if not tables:
                print("No tables found")
                return

            first_table = tables[0]  # Get only the first table

            # Extract headers and rows from the first table
            headers = [
                th.text.strip() for th in first_table.find_elements(By.TAG_NAME, "th")
            ]

            # Create data structure for the table
            data = []

            # Process rows
            for row in first_table.find_elements(By.TAG_NAME, "tr")[
                1:
            ]:  # Skip header row
                cells = [
                    cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")
                ]
                if len(cells) == len(headers):
                    # Extract model name and version
                    model_info = cells[0].split("\n")
                    model_name = model_info[0] if model_info else ""
                    model_version = model_info[1].strip() if len(model_info) > 1 else ""

                    # Replace the first cell with separate model name and version
                    cells[0] = model_name

                    # Create a row with model name, version, and pricing data
                    row_data = {
                        "Model": model_name,
                        "Version": model_version,
                    }

                    # Add pricing columns
                    for i in range(1, len(headers)):
                        row_data[headers[i]] = cells[i]

                    data.append(row_data)

            # Create DataFrame and save to CSV
            if data:
                # Create data directory if it doesn't exist
                data_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), "data"
                )
                os.makedirs(data_dir, exist_ok=True)

                # Save to CSV
                df = pd.DataFrame(data)
                df.to_csv(
                    os.path.join(data_dir, "openai_text_tokens_pricing.csv"),
                    index=False,
                )
                print("Text tokens pricing data saved successfully")
            else:
                print("No data found in the first table")

            # Explicit cleanup
            driver.close()
            driver.service.stop()

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    get_openai_pricing()
