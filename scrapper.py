import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, \
    TimeoutException

import time
import json
from iteration_utilities import unique_everseen
import logging

logging.basicConfig(filename='scrapper_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BASE_URL = "https://sanctioned-suicide.net"
START_URL = "https://sanctioned-suicide.net/forums/suicide-discussion.2"
DATA_PATH = './data/'



def is_element_present(drv, type_of_element, locator):
    try:
        WebDriverWait(drv, 20)
        drv.find_element(type_of_element, locator)
    except NoSuchElementException:
        return False
    return True


def get_users(driver):
    persons = []
    for person in driver.find_elements(By.CLASS_NAME, 'uix_messagePostBitWrapper'):
        name = person.find_element(By.XPATH, './/h4[@class="message-name"]').text
        title = person.find_element(By.XPATH, './/h5[@class="userTitle message-userTitle"]').text
        date = person.find_element(By.CLASS_NAME, 'message-userExtras').text
        register_date = date.split('\n')[0]
        number_of_posts = date.split('\n')[-1]

        persons.append(
            {'name': name, 'title': title, 'register_date': register_date, 'number_of_posts': number_of_posts})

    return persons


def get_reactions(driver):
    reactions = []

    continue_exist = True
    while continue_exist:
        try:
            WebDriverWait(driver, 20)
            reaction_driver = driver.find_elements(By.XPATH, "//div[@class='contentRow']")
            time.sleep(3)
            for reaction in reaction_driver:
                username = reaction.find_element(By.XPATH, './/h3[@class="contentRow-header"]').text
                type_of_reaction = reaction.find_element(By.XPATH,
                                                         './/img[@class="reaction-sprite js-reaction"]').get_attribute(
                    "title")
                time_element = reaction.find_element(By.XPATH, './/time[@class="u-dt"]')
                reaction_time = time_element.get_attribute("title")
                M_R = reaction.find_element(By.XPATH, './/ul[@class="listInline listInline--bullet"]').text
                M_R_split = M_R.split(" ")
                messages = M_R_split[1]
                reaction_score = M_R_split[4]

                reactions.append({'username': username, 'type_of_reaction': type_of_reaction, 'time': reaction_time,
                                  'messages': messages, 'reaction_score': reaction_score})

            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            continue_exist = is_element_present(driver, By.LINK_TEXT, 'Continue…')
            if continue_exist:
                driver.find_element(By.LINK_TEXT, 'Continue…').click()
            else:
                break
        except StaleElementReferenceException:
            pass
    logging.info(f"  -- Number of Reactions:  {len(reactions)}")
    print("  -- Number of Reactions: ", len(reactions))
    return reactions


def get_posts_each_page(driver):
    posts = []
    post_driver = driver.find_elements(By.CLASS_NAME, 'message-inner')
    time.sleep(1)
    logging.info("Getting posts in a page ...")
    print("Getting posts in a page ...")

    for post in post_driver:
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'message-name')))

            author = post.find_element(By.XPATH, './/h4[@class="message-name"]').text
            post_text = post.find_element(By.CLASS_NAME, 'bbWrapper').text
            time_item = post.find_element(By.CLASS_NAME, 'u-dt')
            post_date = time_item.get_attribute("title")

            reaction_exist = is_element_present(post, By.CLASS_NAME, "reactionsBar-link")
            main_window_handle = driver.current_window_handle

            if reaction_exist:
                element = post.find_element(By.CLASS_NAME, "reactionsBar-link")
                reaction_link = element.get_attribute("href")

                driver.execute_script("window.open('" + reaction_link + "');")
                driver.switch_to.window(driver.window_handles[-1])

                reactions = get_reactions(driver)

                # Go back
                time.sleep(1)
                driver.close()
                driver.switch_to.window(main_window_handle)

                time.sleep(2)
            else:
                reactions = []
                pass
        except Exception as e:
            logging.error(f"In getting reactions of each post {e} happen!")
            print(f"In getting reactions of each post {e} happen!")

        time.sleep(2)

        posts.append({'author': author, 'post': post_text, 'post_date': post_date, 'reactions': reactions})

    return posts


def get_all_the_posts_in_thread(driver):
    post_page = 0
    next_exist = True
    thread_posts = []
    thread_users = []

    while next_exist:
        try:
            post_page += 1
            logging.info(f" - Page of Posts: {post_page}")
            print(" - Page of Posts:", post_page)

            WebDriverWait(driver, 20)
            time.sleep(2)
            thread_users.extend(get_users(driver))

            thread_posts.extend(get_posts_each_page(driver))
            time.sleep(3)

            next_exist = is_element_present(driver, By.LINK_TEXT, 'Next')
            if next_exist:
                driver.find_element(By.LINK_TEXT, 'Next').click()
            else:
                break

        except (TimeoutException, WebDriverException) as e:
            logging.error(f"In navigating to next page of posts {e} happen!")
            print(f"In navigating to next page of posts {e} happen!")
            break
    return thread_users, thread_posts


def get_thread_details(threads_list):
    thread_detail = []
    thread_count = 0
    for item in threads_list:
        start_time = time.time()
        thread_count += 1
        logging.info(f"* Thread Number is: {thread_count}")
        print(f"* Thread Number is: {thread_count}")
        driver.get(BASE_URL + item['url'])

        thread_users, thread_posts = get_all_the_posts_in_thread(driver)

        # Remove duplicates users
        unique_users = list(unique_everseen(thread_users))

        thread_detail.append(
            {'title': item["title"], 'url': item["url"], 'views': item["views"], 'replies': item["replies"],
             'label': item["label"], 'users': unique_users, 'posts': thread_posts})

        # Save thread data
        try:
            thread_name = item["title"].replace(" ", "_")
            save_time = time.strftime("%Y%m%d-%H%M%S")
            with open(DATA_PATH + f"{thread_name}_{save_time}.json", 'w') as fp:
                json.dump(thread_detail, fp)
            logging.info(f"** {thread_name} is saved!")
            print(f"** {thread_name} is saved!")
            thread_detail = []
        except:
            logging.error(f"Problem with the name {thread_name}")
            print(f"Problem with the name {thread_name}")
            with open(DATA_PATH + f"noName_{save_time}.json", 'w') as fp:
                json.dump(thread_detail, fp)
            th_name = item["title"]
            logging.info(f"** {th_name} is saved!")
            print(f"** {th_name} is saved!")
            thread_detail = []

        end_time = time.time()
        if thread_count % 3 == 0:
            print(f"Time taken for three thread {end_time - start_time} seconds")
            logging.error(f"Time taken for three thread {end_time - start_time} seconds")
        else:
            pass

        time.sleep(5)
    driver.quit()


def get_all_threads(driver):
    threads = []
    thread_page = 0
    time.sleep(2)
    last_page = driver.find_element(By.XPATH, './/li[@class="pageNav-page "]').text
    print("Getting all threads start ...")
    logging.info("Getting all threads start ...")

    while thread_page < int(last_page):
        try:
            thread_page += 1

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            threads_driver = driver.find_elements(By.CSS_SELECTOR, "[class^='structItem structItem--thread ']")

            for thread in threads_driver:
                time.sleep(2)
                temp = thread.find_element(By.CLASS_NAME, 'structItem-title')
                title = temp.text
                url = temp.get_attribute('uix-href')
                views = thread.find_element(By.XPATH, './/dl[@class="pairs pairs--justified"]').text.split('\n')[1]
                replies = \
                    thread.find_element(By.XPATH, './/dl[@class="pairs pairs--justified structItem-minor"]').text.split(
                        '\n')[1]

                label_exist = is_element_present(thread, By.CSS_SELECTOR, "a > span[class^='label label--']")

                if label_exist:
                    label = thread.find_element(By.CSS_SELECTOR, "a > span[class^='label label--']").text
                else:
                    label = ""

                threads.append({'title': title, 'url': url, 'views': views, 'replies': replies, 'label': label})

                time.sleep(2)

            time.sleep(2)
            print(f"Lenght of threads list till page {thread_page} is {len(threads)}")
            logging.info(f"Lenght of threads list till page {thread_page} is {len(threads)}")

            driver.find_element(By.XPATH, "//a[@class='pageNav-jump pageNav-jump--next']").click()

        except (TimeoutException, WebDriverException) as e:
            logging.error(f"In getting each thread data {e} occured!")
            print(f"In getting each thread data {e} occured!")
            break

    with open(DATA_PATH + f"All_Threads.json", 'w') as fp:
        json.dump(threads, fp)

    return threads


if __name__ == "__main__":
    option = webdriver.ChromeOptions()

    # option.add_argument('--headless')
    option.headless = True
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=option, service_log_path='log.txt')

    driver.get(START_URL)
    WebDriverWait(driver, 5)
    coockie_link = driver.find_element(By.XPATH,
                                       "//a[@class='js-noticeDismiss button--notice button button--icon button--icon--confirm rippleButton']")
    coockie_link.click()

    threads = get_all_threads(driver)

    get_thread_details(threads)
