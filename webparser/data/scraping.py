from bs4 import BeautifulSoup
from .parsing import Parser
from selenium.webdriver import FirefoxOptions

class Scraper(Parser):

    def __init__(self, url: str, executable_path: str, firefox_options: FirefoxOptions, 
                qualification: str, education_base: str, unis: list) -> None:
        super().__init__(url, executable_path, firefox_options, 
                        qualification, education_base)
        self.unis = unis

    def get_uni_data(self, raw_data: str) -> list:

        def get_offer_data(soup: BeautifulSoup, class_name: str) -> str:
            offer = soup.find('dl', {'class': class_name})
            if not offer: return
            return offer.find('dd').text
        
        def get_stat_data(soup: BeautifulSoup, class_name: str) -> int:
            if not soup: return 0
            stat = soup.find('div', {'class': class_name})
            if not stat: return 0
            value = stat.find('div', {'class': 'value'}).text
            return int(value)

        soup = BeautifulSoup(raw_data, 'html.parser')

        unis_soup = soup.find('div', id='universities')

        data = []

        for uni in unis_soup.find_all('div', {'class': 'university'}):

            uni_id = f"{uni['data-university']}"
            if not uni_id in self.unis:
                continue

            _uni = {}
            _uni['id'] = uni_id
            _uni['name'] = \
                uni.find('h5', {'class': 'text-primary text-uppercase'}).text
            _uni['offers'] = []
            
            for offer in uni.find_all('div', {'class': 'offer'}):
                
                _offer = {}

                offer_name = offer.find_all(
                    'dl', 
                    {'class': 'offer-university-specialities-name'}
                )
                
                _offer['id'] = offer_name[0].find('span', 
                                        {'class': 'badge badge-primary'}
                                    ).text

                _offer['name'] = offer_name[1].find('dd').text
                
                form = get_offer_data(offer, 'row offer-education-form-name')
                if form: 
                    _offer['form'] = form
                
                price = get_offer_data(offer, 'row offer-education-price')
                if price: 
                    _offer['price'] = int(price)
                else: _offer['price'] = 'Немає даних'
                
                statistics = offer.find('div', {'class': 'offer-requests-stats'})

                apps = get_stat_data(statistics, 'stats-field-t')
                _offer['apps'] = apps
                
                ob = get_stat_data(statistics, 'stats-field-ob')
                _offer['ob'] = ob
                
                oc = get_stat_data(statistics, 'stats-field-oc')
                _offer['oc'] = oc

                _uni['offers'].append(_offer)

            data.append(_uni)
                
        return data
    
    @staticmethod
    def get_region_options(raw_regions) -> list:

        region_id = 'Код регіону'
        region_name = 'Назва регіону'
        data = []

        for index, region in enumerate(raw_regions[region_id]):

            data.append({
                'name': raw_regions[region_name][index],
                'registry_id': raw_regions[region_id][index]
            })
        
        return data
    
    @staticmethod
    def get_speciality_options(raw_data: str) -> list:

        speciality_id = 'offers-search-speciality'
        soup = BeautifulSoup(raw_data, 'html.parser')

        select = soup.find(
            "select", 
            { "id": speciality_id }
        )

        data = []
        for option in select.find_all('option'):

            option: BeautifulSoup
            speciality_id = option.get('value')
            if not speciality_id: continue

            data.append({
                'name': option.text,
                'registry_id': speciality_id
            })
            
        return data