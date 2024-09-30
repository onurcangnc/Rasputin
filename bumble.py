import sys
import time
import keyboard
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from colorama import init, Fore, Style
from telegram import Bot
import logging

# Start Colorama
init(autoreset=True)

# For Turkish characters stdout set to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(filename='bumble_bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot token ve chat ID bilgileri
TELEGRAM_TOKEN = '' # Botfather tokeni
CHAT_ID = ''  # Sizin chat ID'niz

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Telegram mesajı gönderilemedi: {str(e)}", exc_info=True)
        print(f"Telegram mesajı gönderilemedi: {str(e)}", flush=True)

# Protect current browser session.
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\path\\to\\your\\chrome\\profile")  # Mevcut kullanıcı profili
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Uyarıyı gizle
options.add_experimental_option('useAutomationExtension', False)  # Otomasyon uzantısını devre dışı bırak
driver = webdriver.Chrome(options=options)

driver.maximize_window()
driver.get("https://bumble.com/app")  # Please go to Bumble site with chrome driver!!

paused = False  # Pause/Continue option for space key.

def pause_or_continue():
    global paused
    paused = not paused
    if paused:
        logging.info("Script paused. Continue with F10.")
        print("Script paused. Continue with F10.", flush=True)
    else:
        logging.info("Script continue...")
        print("Script continue...", flush=True)

def save_and_exit():
    logging.info("ESC'ye basıldı, Script durduruluyor...")
    print("ESC'ye basıldı, Script durduruluyor", flush=True)
    try:
        driver.quit()
        logging.info("Browser closed. Script will be terminated.")
        print("Browser closed. Script will be terminated...", flush=True)
    except Exception as e:
        logging.error(f"Tarayıcı kapatılırken bir hata oluştu: {str(e)}", exc_info=True)
        print(f"Tarayıcı kapatılırken bir hata oluştu: {str(e)}", flush=True)
    finally:
        sys.exit()

# Terminate with ESC
keyboard.add_hotkey('esc', save_and_exit)
# Press Space key to pause/continue
keyboard.add_hotkey('F10', pause_or_continue)

async def retry_login(driver, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # Try to re-establish session
            logging.info(f"Attempting to re-login (Attempt {retries + 1}/{max_retries})")
            print(f"Attempting to re-login (Attempt {retries + 1}/{max_retries})...", flush=True)
            driver.get("https://bumble.com/app")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sidebar-profile"]'))
            )
            logging.info("Session re-established.")
            print("Session re-established.", flush=True)
            return True
        except Exception as e:
            logging.error(f"Re-login attempt failed: {str(e)}", exc_info=True)
            print(f"Re-login attempt failed: {str(e)}", flush=True)
            retries += 1
            time.sleep(5)
    return False

async def process_profile(profile, target_location):
    try:
        location_element = WebDriverWait(profile, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="location-widget__town"]//span[@class="header-2 text-color-black"]'))
        )
        location_text = location_element.get_attribute('textContent').strip()

        name_element = profile.find_element(By.XPATH, '//span[@class="encounters-story-profile__name"]')
        name_text = name_element.text.strip()

        age_element = profile.find_element(By.XPATH, '//span[@class="encounters-story-profile__age"]')
        age_text = age_element.text.strip()

        if location_text:
            if target_location.lower() in location_text.lower():
                right_swipe_button = profile.find_element(By.XPATH, '//span[@data-qa-icon-name="floating-action-yes"]')
                right_swipe_button.click()
                status = "Sağ kaydırıldı"
                message = f"Status: {status}, Name: {name_text}, Age: {age_text}, Location: {location_text}"
                logging.info(message)
                print(f"{Fore.GREEN}{message}{Style.RESET_ALL}", flush=True)
                await send_telegram_message(message)
            else:
                left_swipe_button = profile.find_element(By.XPATH, '//span[@data-qa-icon-name="floating-action-no"]')
                left_swipe_button.click()
                status = "Sola kaydırıldı"
                logging.info(f"Status: {status}, Name: {name_text}, Age: {age_text}, Location: {location_text}")
                print(f"Status: {Fore.RED}{status}{Style.RESET_ALL}, Name: {name_text}, Age: {age_text}, Location: {location_text}", flush=True)

            # Dynamic sleep between 2 to 4 seconds
            time.sleep(2 + (time.time() % 2))

        else:
            logging.info("Konum bilgisi boş, profil atlandı.")
            print("Konum bilgisi boş, profil atlandı.", flush=True)
            time.sleep(3)

    except NoSuchElementException as e:
        logging.error(f"Profilde element bulunamadı: {str(e)}", exc_info=True)
        print(f"Profilde element bulunamadı: {str(e)}", flush=True)
        time.sleep(3)

async def main():
    try:
        logging.info("Tarayıcı açıldı. Lütfen Bumble'a giriş yapın.")
        print("Tarayıcı açıldı. Lütfen Bumble'a giriş yapın.", flush=True)
        user_input = input("Bumble'a giriş yaptınız mı? (Y/N): ")

        if user_input.lower() == 'y':
            try:
                profile_div = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="sidebar-profile"]'))
                )
                logging.info("Session opened. Bot continue to work...")
                print("Session opened. Bot continue to work...", flush=True)

                target_location = input("Go to the intended location (Bursa etc...): ")

                while True:
                    if paused:
                        time.sleep(1)
                        continue

                    try:
                        profiles = driver.find_elements(By.CLASS_NAME, 'encounters-user__frame')

                        if not profiles:
                            logging.info("There is no processing profile. Bot will be stopped.")
                            print("There is no processing profile. Bot will be stopped.", flush=True)
                            break

                        for profile in profiles:
                            await process_profile(profile, target_location)

                    except NoSuchElementException as e:
                        logging.error(f"Profil bulunamadı: {str(e)}", exc_info=True)
                        print(f"Profil bulunamadı: {str(e)}", flush=True)
                        break
                    except WebDriverException as e:
                        logging.error(f"Browser session invalid: {str(e)}", exc_info=True)
                        # Try to re-login
                        if not await retry_login(driver):
                            logging.error("Re-login failed. Exiting script.")
                            break

            except NoSuchElementException as e:
                logging.error(f"Element bulunamadı: {str(e)}", exc_info=True)
                driver.quit()

            except Exception as e:
                logging.error(f"Bir hata oluştu: {str(e)}", exc_info=True)
                driver.quit()

    except KeyboardInterrupt:
        save_and_exit()

if __name__ == "__main__":
    asyncio.run(main())
