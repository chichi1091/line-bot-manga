import server


def test_scraping():
    for url in server.url_list:
        print(server.scraping(url))

if __name__ == '__main__':
    test_scraping()
