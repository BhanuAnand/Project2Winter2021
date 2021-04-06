##############################
##### Name: Aditi Anand  #####
##### Uniqname: anandadi #####
##############################

from bs4 import BeautifulSoup
import requests, json, sys
from json import JSONEncoder
from fcache.cache import FileCache
from urllib.parse import urlparse, urljoin
import secrets # file that contains your API key

api_key = secrets.API_KEY

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, catg, add, zipc, ph):
        self.name = name
        self.category = catg
        self.address = add
        self.zipcode = zipc
        self.phone = ph
    
    def info(self):
        '''
        a string representation of itself. 
        The format is <name> (<category>): <address> <zip> .
        Example: Isle Royale (National Park): Houghton, MI 49931
        '''
        str = self.name+" ("+self.category+"): "+self.address+" "+self.zipcode
        return str

class NationalSiteEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def nationalSiteDecoder(siteDict):
    return namedtuple('X', siteDict.keys())(*siteDict.values())

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url = "https://www.nps.gov"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    state_path = "/state/"
    state_dict = {}
      
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if state_path in href:
            href =  urljoin(url, href)
            state_dict[a_tag.text.lower()] = href
    return state_dict      

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    page = requests.get(site_url)
    soup = BeautifulSoup(page.content, "html.parser")
    category = ""

    name_result = soup.find("a", {"class": "Hero-title"})
    name = name_result.text.strip()
    
    catg_result = soup.find("span", {"class": "Hero-designation"})
    if catg_result != "":
        category = catg_result.text.strip()
    
    add_result1 = soup.find("span", {"itemprop": "addressLocality"})
    address1 = add_result1.text
   
    add_result2 = soup.find("span", {"itemprop": "addressRegion"})
    address2 = add_result2.text.strip()
    
    address = address1+", "+address2
    
    postal_result = soup.find("span", {"itemprop": "postalCode"})
    zipcode = postal_result.text.strip()
    
    ph_result = soup.find("span", {"itemprop": "telephone"})
    phone = ph_result.text.strip()
    
    classInst = NationalSite(name, category, address, zipcode, phone)
    return classInst

def get_state_url(state):
    '''Get the state url for a state entered by user.
    Parameters
    ----------
    state: string
        The name of the state entered by the user
    
    Returns
    -------
    list
        a list of national site instances
    '''
    url = "https://www.nps.gov"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    state_path = "/state/"
    state_url_list = set()
    isValidState = False
      
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if (state_path in href and a_tag.text.lower() == state.lower()):
            href =  urljoin(url, href)
            isValidState = True
            return get_sites_for_state(href)
    if isValidState == False:
        print("[Error] Enter proper state name")

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    inst_list = []
    state_url_list = []
    parsed_url = urlparse(state_url)
    domain = parsed_url.scheme +"://"+ parsed_url.netloc
    soup = BeautifulSoup(requests.get(state_url).content, "html.parser")
    site_list_html = soup.findAll("div", {"class": "col-md-9 col-sm-9 col-xs-12 table-cell list_left"})
    mycache = FileCache('fcacheFileStore', flag='cs')

    for item in site_list_html:
        a_tag = item.find("a")
        href = a_tag.attrs.get("href")
        href =  urljoin(domain, href)
        state_url_list.append(href)
        
    for url in state_url_list:
        if url in mycache:
            print("Using Cache")
            classInst = mycache[url]
        else:
            print("Fetching")
            classInst = get_site_instance(url)
            mycache[url] = classInst
        inst_list.append(classInst) 
        
    return inst_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    zipcode = site_object.zipcode
    resource_url = "http://www.mapquestapi.com/search/v2/radius"
    params = {'origin': zipcode, 'radius': '10', 'maxMatches': '10', 'ambiguities': 'ignore', 'outFormat': 'json', 'key': api_key}
    apiDataCache = FileCache('fcacheFileStore', flag='cs')

    if zipcode in apiDataCache:
        print("Using Cache")
        result = apiDataCache[zipcode]
    else:
        print("Fetching")
        r = requests.get(resource_url, params=params)
        result = r.json()
        apiDataCache[zipcode] = result

    return result
  
def list_national_sites_by_state():
    '''To print the obtained national sites in the desired format.
    Parameters
    ----------
    None
           
    Returns
    -------
    list
        a list of national site instances
    '''
    state = input("Enter a state name (e.g. Michigan, michigan) or \"exit\": ")
    if(state == "exit"):
        sys.exit("Aborting the execution of the program")
    listOfNS = get_state_url(state)
    if listOfNS:
        print("-------------------------------------")
        print("List of national sites in "+state.capitalize())
        print("-------------------------------------")
        for idx,inst in enumerate(listOfNS):
            print("["+str(idx+1)+"] "+inst.info())
    
    return listOfNS

def get_nearby_places_by_state(listOfNationalSites):
    '''To print the nearby places of the selected national site by the user in the desired format.
    Parameters
    ----------
    listOfNationalSites: list
        a list of national site instances
          
    Returns
    -------
    None
    '''
    inputFromUser = input("Choose the number for detail search or \"exit\" or \"back\": ")
    numOfSites = len(listOfNationalSites)
    try:
        if (inputFromUser != "exit" and inputFromUser != "back"):
            inputFromUser = int(inputFromUser)
    except:
        print("[Error] Invalid input")
        get_nearby_places_by_state(listOfNationalSites)
        
    if inputFromUser == "exit":
        sys.exit("Aborting the execution of the program")
    elif inputFromUser == "back":
        mainFunc()
    elif (inputFromUser < 1 or inputFromUser > numOfSites):
        print("[Error] Invalid input")
        get_nearby_places_by_state(listOfNationalSites)
    else:
        siteObjIdx = inputFromUser - 1
        site_object = listOfNationalSites[siteObjIdx]
        resultJson = get_nearby_places(site_object)
        
        if resultJson:
            print("-------------------------------------")
            print("Places near "+site_object.name)
            print("-------------------------------------")
            searchResults = resultJson.get('searchResults')
            for item in searchResults:
                category = "no category"
                address = "no address"
                city = "no city"
                resultDict = item.get("fields")
                name = resultDict["name"]
                if ("group_sic_code_name_ext" in resultDict and resultDict["group_sic_code_name_ext"]):
                    category = resultDict["group_sic_code_name_ext"]
                if ("address" in resultDict and resultDict["address"]):
                    address = resultDict["address"]
                if ("city" in resultDict and resultDict["city"]):
                    city = resultDict["city"]
                print("- " + name + " (" + category + "): " + address + ", " + city)
        else:
            print("No nearby places found for "+site_object.name)
            
    get_nearby_places_by_state(listOfNationalSites)

def mainFunc():
    '''Driver function for executing interactive search interface
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    listOfNationalSites = list_national_sites_by_state()
    if listOfNationalSites:
        get_nearby_places_by_state(listOfNationalSites)
    else:
        mainFunc()

if __name__ == "__main__":
    mainFunc()