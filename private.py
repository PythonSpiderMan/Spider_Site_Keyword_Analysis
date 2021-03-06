import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from bs4.element import Comment
import copy
import logging


class KeywordAnalysis():
    # (chrome | firefox)
    BROWSER_SETTING = "chrome"


    driver = None
    targets_response = None
    keywords_counts_url1, keywords_counts_url2 = None, None
    log = None

    def __init__(self):
        super(KeywordAnalysis, self).__init__()

        # TODO: Debug use Example Input
        # self.keywords_list = ["one", "what"]
        # self.target_urls = ['https://timesofindia.indiatimes.com/india/would-you-mind-saying-sorry-for-note-ban-prakash-raj-to-pm-modi/articleshow/61565057.cms',
        #                     'https://timesofindia.indiatimes.com/videos/news/with-one-sarcastic-tweet-owaisi-nails-bjp-congress-on-their-hypocrisy/videoshow/61859286.cms']
        # self.url1_news_agency_name = ["Times Of India", "Economic Times"]
        # self.url2_news_agency_name = ["Times Of India", "Economic Times"]

        # TODO: Input without news_agency_name
        self.input_keyword_string = input\
            ("Please Enter Keywords to Search, split multiple keyword with space (for Ex. Narendra Modi ): ")
        self.keywords_list = copy.deepcopy(str(self.input_keyword_string).split())
        self.target_urls = []
        for i in range(1, 3):
            self.target_urls.append(input("Please type in the URL%s (with http/https): " % str(i)))

        # TODO: Input with news_agency_name
        # self.input_keyword_string = input\
        #     ("Please Enter Keywords to Search, split multiple keyword with space (for Ex. Narendra Modi ): ")
        # self.keywords_list = copy.deepcopy(str(self.input_keyword_string).split())
        # self.target_urls = []
        # for i in range(1, 3):
        #     self.target_urls.append(input("Please type in the URL%s (with http/https): " % str(i)))
        #     self.news_agency_names = input("Please Type News Agency Name (for ex. Times Of India, Economic Times ) : ")\
        #         .lower().strip().split(',')
        #     if i == 1:
        #         self.url1_news_agency_name = copy.deepcopy(self.news_agency_names)
        #     elif i == 2:
        #         self.url2_news_agency_name = copy.deepcopy(self.news_agency_names)

        # Check Input
        if not len(self.target_urls) == 2:
            logging.error("Please make sure that you have exactly 2 urls in your url string")
            quit()
        else:
            print("=" * 30)
            print("This is URL1:")
            print(self.target_urls[0])
            print("=" * 30)
            print("This is URL2:")
            print(self.target_urls[1])
            print("=" * 30)

        if len(self.keywords_list) <= 1:
            logging.error("Please make sure that you have entered at least 2 keywords")
        else:
            print("Here are your keywords:")
            print("=" * 30)
            [print("keyword: '%s'" % keyword) for keyword in self.keywords_list]

        print("=" * 30)
        print("Input Verified, Begin Scraping")

    def run(self):
        # Start Scrapping
        self.driver = self.start_selenium()
        self.targets_response = self.scrape_sites()

        self.keywords_counts_url1, self.keywords_counts_url2 = self.result_analysis()
        self.log = self.result_to_pandas()

        self.plot_graphs()

    def start_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--mute-audio")

        if self.BROWSER_SETTING == "firefox":
            return webdriver.Firefox(executable_path=r'geckodriver.exe')
        elif self.BROWSER_SETTING == "chrome":
            return webdriver.Chrome(executable_path=r'chromedriver.exe', chrome_options=chrome_options)
        else:
            logging.error("Please check your BROWSER_SETTING variable")

    @staticmethod
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def scrape_sites(self):
        targets_response = []
        for target in self.target_urls:
            self.driver.get(target)
            WebDriverWait(self.driver, 5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*4);")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*4);")

            bs_obj = BeautifulSoup(self.driver.page_source, 'html.parser')
            texts = bs_obj.find_all(text=True)
            visible_texts = filter(KeywordAnalysis.tag_visible, texts)
            visible_texts_string = u" ".join(t.strip() for t in visible_texts)

            targets_response.append(copy.deepcopy(visible_texts_string))

        self.driver.close()
        return targets_response

    def result_analysis(self):
        keywords_counts_url1 = []
        for keyword in self.keywords_list:
            keywords_counts_url1.append(self.targets_response[0].count(keyword))
        keywords_counts_url2 = []
        for keyword in self.keywords_list:
            keywords_counts_url2.append(self.targets_response[1].count(keyword))

        return keywords_counts_url1, keywords_counts_url2

    def result_to_pandas(self):
        log_cols = ["Keywords", "Keyword Counts in URL1", "Keyword Counts in URL2"]
        log = pd.DataFrame(columns=log_cols)

        for index in range(0, len(self.keywords_list)):
            keyword = copy.deepcopy(self.keywords_list[index])
            keyword_count_url1 = copy.deepcopy(self.keywords_counts_url1[index])
            keyword_count_url2 = copy.deepcopy(self.keywords_counts_url2[index])
            log_entry = pd.DataFrame([[keyword, keyword_count_url1, keyword_count_url2]], columns=log_cols)
            log = log.append(log_entry, ignore_index=True)

        return log

    def plot_graphs(self):
        # Plot Graph 1 & 2
        log_cols = ["Keywords", "Keyword Counts in URL1", "Keyword Counts in URL2"]
        log = pd.DataFrame(columns=log_cols)

        for index in range(0, len(self.keywords_list)):
            keyword = copy.deepcopy(self.keywords_list[index])
            keyword_count_url1 = copy.deepcopy(self.keywords_counts_url1[index])
            keyword_count_url2 = copy.deepcopy(self.keywords_counts_url2[index])
            log_entry = pd.DataFrame([[keyword, keyword_count_url1, keyword_count_url2]], columns=log_cols)
            log = log.append(log_entry, ignore_index=True)

        # Plot Graph 1
        fig = plt.figure(figsize=(10, 10))
        fig.add_subplot(221)
        sns.set_color_codes("muted")
        ax = sns.barplot(y="Keyword Counts in URL1", x="Keywords", data=log, color="b")
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2.,
                    height / 2,
                    s='{:1.2f}'.format(height),
                    ha="center")
        plt.title("Keywords Counts in URL1")
        plt.ylabel("Keywords Counts in URL1")

        # Plot Graph 2
        fig.add_subplot(223)
        sns.set_color_codes("muted")
        ax = sns.barplot(y="Keyword Counts in URL2", x="Keywords", data=log, color="r")
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2.,
                    height / 2,
                    s='{:1.2f}'.format(height),
                    ha="center")
        plt.title("Keywords Counts in URL2")
        plt.ylabel("Keywords Counts in URL2")

        # Plot Pearson Correlation Graph for 2 URL
        df = pd.DataFrame({'keyword_counts_in_url1': log.iloc[:, 1].astype(float),
                           'keyword_counts_in_url2': log.iloc[:, 2].astype(float)})
        pearson_correlation = (df.corr() * df['keyword_counts_in_url1'].std() * df['keyword_counts_in_url2'].std() / df[
            'keyword_counts_in_url1'].var()).ix[0, 1]
        ax = fig.add_subplot(222)
        ax.scatter(self.keywords_counts_url1, self.keywords_counts_url2)
        for i, txt in enumerate(self.keywords_list):
            ax.annotate(('Key: "%s",\n URL1: "%s",\n URL2: "%s"' %
                         (txt, self.keywords_counts_url1[i], self.keywords_counts_url2[i])),
                        (self.keywords_counts_url1[i], self.keywords_counts_url2[i]))
        plt.xlabel("Keyword Counts in URL1")
        plt.ylabel("Keyword Counts in URL2")
        plt.title("Pearson value is : %s" % str(pearson_correlation))

        # Plot Graph 4 for 2 URL
        df = pd.DataFrame({'keyword_counts_in_url1': log.iloc[:, 1].astype(float),
                           'keyword_counts_in_url2': log.iloc[:, 2].astype(float)})
        pearson_correlation = (df.corr() * df['keyword_counts_in_url1'].std() * df['keyword_counts_in_url2'].std() / df[
            'keyword_counts_in_url1'].var()).ix[0, 1]
        ax = fig.add_subplot(224)
        ax.plot(self.keywords_counts_url1, self.keywords_counts_url2, marker='o', markersize=10, color="red")
        for i, txt in enumerate(self.keywords_list):
            ax.annotate(('Key: "%s",\n URL1: "%s",\n URL2: "%s"' %
                         (txt, self.keywords_counts_url1[i], self.keywords_counts_url2[i])),
                        (self.keywords_counts_url1[i], self.keywords_counts_url2[i]))
        plt.xlabel("Keyword Counts in URL1")
        plt.ylabel("Keyword Counts in URL2")
        plt.title("Pearson value is : %s" % str(
            pearson_correlation))
        plt.show()


if __name__ == '__main__':
    ka = KeywordAnalysis()
    ka.run()

    # Keep matplotlib running until you click on X
    while True:
        plt.pause(100)
