from selenium import webdriver
import time
import requests
from PIL import Image
import io
import os
import hashlib
import tkinter



def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path:str, url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term: str, driver_path: str, images_count: int, target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, images_count, wd=wd, sleep_between_interactions=1)

    for elem in res:
        persist_image(target_folder, elem)


DRIVER_PATH = 'chromedriver.exe'
#search_term = input('search: ')
#images_count = int(input('images count: '))
#search_and_download(search_term=search_term, driver_path=DRIVER_PATH, images_count=images_count)


def start_scrapping():
    search_term = query.get()
    icount = images_count.get()
    search_and_download(search_term=search_term, driver_path=DRIVER_PATH, images_count=icount)



root = tkinter.Tk()
root.title("ImageScrapper")
root.geometry("300x125")
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
root.wm_geometry("+%d+%d" % (x, y))
root.minsize(300, 125)
root.maxsize(600, 250)

text_q = tkinter.Label(text='Search query: ')
text_q.pack(expand=1)

query = tkinter.StringVar()
query_entry = tkinter.Entry(textvariable=query)
query_entry.pack(expand=1)

text_ic = tkinter.Label(text='Images count: ')
text_ic.pack(expand=1)

images_count = tkinter.IntVar()
icount_entry = tkinter.Entry(textvariable=images_count)
icount_entry.pack(expand=1)

button = tkinter.Button(text="Scrap!", command=start_scrapping)
button.pack(expand=1, padx=10, pady=10)

root.mainloop()
