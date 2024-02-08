# Import scrapy
import scrapy
import re

# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess

from scrapy import signals
 
# Create the Spider class
class MoviesSpider(scrapy.Spider):
  name = "moviesspider"
  # start_requests method
  def start_requests(self):
    yield scrapy.Request(url = "http://top250.info/charts/?2023/09/25",callback = self.parse_front)


  # First parsing method
  def parse_front(self, response):
    # Extracting all movie links
    movie_links = response.css('a[href^="/movie/"]::attr(href)').getall()
    
    # Cleaning up the links
    cleaned_links = [response.urljoin(link) for link in movie_links]
    cleaned_links = cleaned_links[2:]
    #yield response.follow(url = cleaned_links[0],callback = self.parse_pages)
    
    for link in cleaned_links:
      print(link)
      yield response.follow(url = link,callback = self.parse_pages)
      


  # Second parsing method
  def parse_pages(self, response):

    # Create a SelectorList of the movie title text
    movie_title = response.xpath('/html/body/div[4]/div[1]/h1/a[1]/span/text()')
    # Extract the text and strip it clean
    movie_title_ext = movie_title.extract_first().strip()
    movie_name_without_year = re.match(r'(.+)\s\(\d{4}\)', movie_title_ext).group(1)
    #print("movie name: " + movie_name_without_year)

    # Create a SelectorList of movie release year text
    movie_releaseYear = response.css( 'body > div.layout > div.movie_left > div.movie_info > div:nth-child(1) > p:nth-child(1) > a::text' )
    # Extract the text and strip it clean
    movie_releaseYear_ext = movie_releaseYear.extract_first().strip()
    
    # Create a SelectorList of movie rate text
    movie_rate = response.css(' td:nth-child(4) > a > span.item_now_in::text')
    # Extract the text and strip it clean
    movie_rate_ext = movie_rate.extract_first()
    
    # Create a SelectorList of movie rank text
    movie_rank = response.css(' td:nth-child(1) > a > span.item_now_in::text')
    # Extract the text and strip it clean
    movie_rank_ext = movie_rank.extract_first()

    # Fill in the dictionary
    movie_dict[movie_name_without_year] = [movie_releaseYear_ext, movie_rate_ext, movie_rank_ext]
 
# Initialize the dictionary **outside** of the Spider class
movie_dict = dict()
 
# Function to be called when the spider finishes crawling
def spider_closed(spider, reason):
    # Print the dictionary after the crawling process completes
    print(movie_dict)

# Run the Spider
crawler_process = CrawlerProcess(settings={})
crawler = crawler_process.create_crawler(MoviesSpider)
crawler.signals.connect(spider_closed, signals.spider_closed)

crawler_process.crawl(crawler)
crawler_process.start()