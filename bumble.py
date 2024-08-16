import sys
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from colorama import init, Fore, Style

# Start Colorama
init(autoreset=True)

# For Turkish characters stdout set to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Protect current browser session.
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\path\\to\\your\\chrome\\profile")  # Do not change default
driver = webdriver.Chrome(options=options)

driver.maximize_window()
driver.get("https://bumble.com/app")  # Please go bumble site chrome driver !!

paused = False  # Pause/Continue option for space key.

def pause_or_continue():
    global paused
    paused = not paused
    if paused:
        print("Script paused. Continue with Space.", flush=True)
    else:
        print("Script contiue...", flush=True)

def save_and_exit():
    driver.quit()
    print("Browser closed Script will be terminated...", flush=True)
    sys.exit()

# Terminate with ESC
keyboard.add_hotkey('esc', save_and_exit)
# Press Space ket to pause/continue
keyboard.add_hotkey('space', pause_or_continue)

try:
    # After browser opened wait until user login operation
    print("Tarayıcı açıldı. Lütfen Bumble'a giriş yapın.", flush=True)
    user_input = input("Bumble'a giriş yaptınız mı? (Y/N): ")

    if user_input.lower() == 'y':
        try:
            profile_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sidebar-profile"]'))
            )
            print("Session opened. Bot continue to work...", flush=True)

            # Get Target Location from user
            target_location = input("Go to the intended location (Bursa etc...): ")

            while True:
                if paused:
                    time.sleep(1)  # Script duraklatıldığında bekleme yap
                    continue

                try:
                    # Profil bilgilerini bul ve işlem yap
                    profiles = driver.find_elements(By.CLASS_NAME, 'encounters-user__frame')

                    if not profiles:
                        print("There is no processing profile. Bot will be stopped.", flush=True)
                        break

                    for profile in profiles:
                        try:
                            # Konum bilgisini al
                            location_element = WebDriverWait(profile, 30).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="location-widget__town"]//span[@class="header-2 text-color-black"]'))
                            )
                            location_text = location_element.get_attribute('textContent').strip()

                            # İsim ve yaş bilgisini al
                            name_element = profile.find_element(By.XPATH, '//span[@class="encounters-story-profile__name"]')
                            name_text = name_element.text.strip()

                            age_element = profile.find_element(By.XPATH, '//span[@class="encounters-story-profile__age"]')
                            age_text = age_element.text.strip()

                            if location_text:
                                status = ""
                                if target_location.lower() in location_text.lower():
                                    right_swipe_button = profile.find_element(By.XPATH, '//span[@data-qa-icon-name="floating-action-yes"]')
                                    right_swipe_button.click()
                                    status = "Sağ kaydırıldı"
                                    print(f"Status: {Fore.GREEN}{status}{Style.RESET_ALL}, Name: {name_text}, Age: {age_text}, Location: {location_text}", flush=True)
                                else:
                                    left_swipe_button = profile.find_element(By.XPATH, '//span[@data-qa-icon-name="floating-action-no"]')
                                    left_swipe_button.click()
                                    status = "Sola kaydırıldı"
                                    print(f"Status: {Fore.RED}{status}{Style.RESET_ALL}, Name: {name_text}, Age: {age_text}, Location: {location_text}", flush=True)

                                time.sleep(3)  # Her işlemden sonra 3 saniye bekle

                            else:
                                print("Konum bilgisi boş, profil atlandı.", flush=True)
                                time.sleep(3)

                        except NoSuchElementException as e:
                            print(f"Profilde element bulunamadı: {str(e)}", flush=True)
                            time.sleep(3)

                except NoSuchElementException as e:
                    print(f"Profil bulunamadı: {str(e)}", flush=True)
                    break

        except NoSuchElementException as e:
            print(f"Element bulunamadı: {str(e)}", flush=True)
            driver.quit()

        except Exception as e:
            print(f"Bir hata oluştu: {str(e)}", flush=True)
            driver.quit()

except KeyboardInterrupt:
    save_and_exit()
