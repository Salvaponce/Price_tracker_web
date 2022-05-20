import os
import re
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

class AmazonAPI:
    def __init__(self, search_term, filters, base_url, currency, number):
        self.search_term = search_term
        self.base_url = base_url
        self.currency = currency
        self.number = number
        self.filters = filters
        options = self.get_web_driver_options()
        self.set_ignore_certificate_error(options)
        self.set_browser_as_incognito(options)
        self.set_browser_options(options)
        self.driver = self.get_chrome_web_driver(options)
        try:
            self.price_filters = f'&rh=p_36%3A{filters[0]}00-{filters[1]}00'
        except:
            self.price_filters = f'&rh=p_36%3A{filters[0]}00-'

    def get_chrome_web_driver(self, options):
        GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
        CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
        options.binary_location = os.environ.get("GOOGLE_CHROME_PATH")
        #options.binary_location = GOOGLE_CHROME_PATH
        return webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), chrome_options=options)
        #return webdriver.Chrome(executable_path='Price_tracker_app/chromedriver.exe', chrome_options=options)

    def get_web_driver_options(self):
        return webdriver.ChromeOptions()

    def set_ignore_certificate_error(self, options):
        options.add_argument('--ignore-certificate-errors')

    def set_browser_as_incognito(self, options):
        options.add_argument('--incognito')

    def set_browser_options(self, options):        
        options.add_argument("--headless")        
        options.headless = True
        options.add_argument("window-size=1400,800")
        #options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

    def run(self):
        print(f'Buscando {self.search_term}...')
        links = self.get_products_links()
        #time.sleep(8)
        if not links:
            print('Parar Script')
            return
        print(f'Tengo {len(links)} links...')
        print('Obteniendo informacion...')
        products = self.get_products_info(links)
        print(f'Tengo informacion sobre {len(products)} productos...')
        self.driver.quit()
        return products

    # Buscamos los links del producto que buscamos entre los precios que hemos elegido en amazon_config    
    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        #time.sleep(2)
        print(self.filters)
        try:
            if self.filters[1] != '0':
                self.driver.get(f'{self.driver.current_url}{self.price_filters}')
                #time.sleep(2)
        except:
            self.driver.get(f'{self.driver.current_url}{self.price_filters}')
            #time.sleep(2)
        result_link_list = self.driver.find_elements_by_class_name('s-underline-link-text')
        links = []       
        try:
            links = set([link.get_attribute('href') for link in result_link_list])
            return links
        except Exception as e:
            print('SIN PRODUCTOS')
            print(e)
            return links

    def get_products_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins:
            product = self.get_one_product_info(asin)
            print(len(products))
            if len(products) == self.number:
                break
            if product:
                products.append(product)
        return products

    def get_one_product_info(self, asin):
        print(f'ID: {asin}. Obteniendo datos...')
        prod_short_url = self.base_url + '/dp/' + asin
        self.driver.get(f'{prod_short_url}?language=es_ES')
        time.sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        image = self.get_image()
        print(title, seller, price)
        if title and seller and price:
            product_info = {
                'asin' : asin,
                'url': prod_short_url,
                'title': title,
                'seller': seller,
                'price': price,
                'image':image
            }
            return product_info
        return None
    
    #Conseguimos el id(asin) de los poductos
    def get_asins(self, links):
        return [self.get_one_asin(p_link) for p_link in links if '/dp/' in p_link]

    def get_one_asin(self, p_link):
        return p_link[p_link.find('/dp/') + 4 : p_link.find('ref')]

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f'Titulo no encontrado')
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('bylineInfo').text
        except:
            try:
                return self.driver.find_element_by_id('brand').text
            except Exception as e:
                print(e)
                print(f'Vendedor no encontrado')
                return None

    def get_price(self):
        try:
            price = self.driver.find_element_by_id('sns-base-price').text
            price = self.conver_price(price)
            return price
        except:
            try:
                price_w = self.driver.find_element_by_class_name('a-price-whole').text
                price_f = self.driver.find_element_by_class_name('a-price-fraction').text
                price = self.conver_price(price_w + ',' + price_f)
                return price
            except Exception as e:
                print(e)
                print(f'Precio no encontrado')
                return None
    def get_image(self):
        try:
            img = self.driver.find_element_by_class_name('a-dynamic-image')
            return img.get_attribute('src')
        except Exception as e:
            print(e)
            print(f'Imagen no encontrado')
            return None
    
    # Convertimos el texto donde esta el precio en un numero flotante
    def conver_price(self, price):
        p_price = re.findall(r'[0-9]+', price)
        return float(p_price[0] + "." + p_price[1])    
