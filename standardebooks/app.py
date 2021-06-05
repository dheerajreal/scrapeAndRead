import time
from pathlib import Path
from typing import List

import bs4
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads" / "standardebooks"

if not DOWNLOAD_DIR.exists():
    DOWNLOAD_DIR.mkdir(parents=True)


def generate_filepath(author_name: str = "UNKNOWN", book_name: str = "UNKNOWN"):
    filename = author_name + "-" + book_name + ".epub"
    filepath = DOWNLOAD_DIR / filename
    return filepath


def download_file(url=None, filepath=None):
    if url is None or filepath is None:
        raise ValueError("filepath and url required")
    if filepath.exists():
        print("Found on disk, skipping download")
        return False
    response = requests.get(url=url)
    if response.status_code == 200:
        with open(filepath, "wb") as fp:
            fp.write(response.content)
        return True
    else:
        raise IOError("unable to download or save file")


def get_standardebooks_markup() -> str:
    try:
        response = requests.get('https://standardebooks.org/opds/all')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)
    return ""


def parse_standardebooks_markup(markup: str = None) -> List:
    domain = "https://standardebooks.org"
    content = bs4.BeautifulSoup(markup=markup, features="xml")
    entries = content.findAll('entry')

    book_list = []
    for entry in entries:
        url = entry.find("id").text
        language = entry.find("dc:language").text
        author = entry.find("author").find("name").text
        epub_link = entry.find("link", type="application/epub+zip").get("href")
        cover_image_link = entry.find(
            "link",
            rel="http://opds-spec.org/image"
        ).get("href")
        cover_image_thumbnail_link = entry.find(
            "link",
            rel="http://opds-spec.org/image/thumbnail"
        ).get("href")

        updated = entry.find("updated").text
        summary = entry.find("summary").text
        title = entry.find("title").text

        book_list.append({
            "url": url,
            "title": title,
            "author": author,
            "language": language,
            "epub_link": domain + epub_link,
            "updated": updated,
            "summary": summary,
            "cover_image_link": domain + cover_image_link,
            "cover_image_thumbnail_link": domain + cover_image_thumbnail_link,
        })

    return book_list


def get_books_list() -> List:
    markup = get_standardebooks_markup()
    books_list = parse_standardebooks_markup(markup)
    return books_list


def download_all_ebooks():
    books = get_books_list()
    number_of_books = len(books)
    for index, book in enumerate(books):
        url = book.get("epub_link", None)
        filepath = generate_filepath(
            author_name=book.get("author", "UNKNOWN"),
            book_name=book.get("title", "UNKNOWN"),
        )
        print(f"Downloading {index + 1 } of {number_of_books}")
        print(f"FROM:\n{url}\nTo:\n{filepath}\n")
        downloaded = download_file(url=url, filepath=filepath)
        print(f"STATUS:\t{downloaded}\n")
        print("Waiting two seconds\n")
        if downloaded:
            time.sleep(2)


if __name__ == "__main__":
    print("Getting information from web")
    j = get_books_list()
    print(f"Number of books {len(j)}")
    import json
    j = json.dumps(j)
    print("saving to file")
    with open(DOWNLOAD_DIR / "books.json", "w") as file_handler:
        file_handler.write(j)
