import unittest
import proj2_nps as nps

# SI 507 Fall 2020
# Project 2

class Test_Part1(unittest.TestCase):
    def setUp(self):
        self.state_url = nps.build_state_url_dict()

    def test_1_1_return_type(self):
        self.assertEqual(type(self.state_url), dict)

    def test_1_2_return_length(self):
        self.assertEqual(len(self.state_url), 56)
    
    def test_1_3_contents(self):
        self.assertEqual(self.state_url['michigan'], 'https://www.nps.gov/state/mi/index.htm')
        self.assertEqual(self.state_url['virgin islands'], 'https://www.nps.gov/state/vi/index.htm')


class Test_Part2(unittest.TestCase):
    def setUp(self):
        self.site_mi1 = nps.get_site_instance('https://www.nps.gov/noco/index.htm')
        self.site_wy1 = nps.get_site_instance('https://www.nps.gov/yell/index.htm')
    
    def test_2_1_basic(self):
        self.assertEqual(self.site_mi1.name, "North Country")
        self.assertEqual(self.site_mi1.category, "National Scenic Trail")
        self.assertEqual(self.site_wy1.name, "Yellowstone")
        self.assertEqual(self.site_wy1.category, "National Park")
        
    def test_2_2_address(self):
        self.assertEqual(self.site_mi1.address, "Lowell, MI")
        self.assertEqual(self.site_mi1.zipcode, "49331")
        self.assertEqual(self.site_wy1.address, "Yellowstone National Park, WY")
        self.assertEqual(self.site_wy1.zipcode, "82190-0168")
        
    def test_2_3_phone(self):
        self.assertEqual(self.site_mi1.phone, "(616) 319-7906")
        self.assertEqual(self.site_wy1.phone, "307-344-7381")

    def test_2_4_str(self):
        self.assertEqual(self.site_mi1.info(), "North Country (National Scenic Trail): Lowell, MI 49331")
        self.assertEqual(self.site_wy1.info(), "Yellowstone (National Park): Yellowstone National Park, WY 82190-0168")


class Test_Part3(unittest.TestCase):
    def setUp(self):
        self.wy_list = nps.get_sites_for_state('https://www.nps.gov/state/wy/index.htm')
    
    def test_3_1_return_type(self):
        self.assertEqual(type(self.wy_list), list)

    def test_3_2_length(self):
        self.assertEqual(len(self.wy_list), 10)

    def test_3_3_contents(self):
        self.assertEqual(self.wy_list[0].name, "Bighorn Canyon")
        self.assertEqual(self.wy_list[0].category, "National Recreation Area")
        self.assertEqual(self.wy_list[0].address, "Lovell, WY")
        self.assertEqual(self.wy_list[0].zipcode, "82435")
        self.assertEqual(self.wy_list[0].phone, "(307) 548-5406")
        self.assertEqual(self.wy_list[0].info(),"Bighorn Canyon (National Recreation Area): Lovell, WY 82435")


class Test_Part4(unittest.TestCase):
    def setUp(self):
        self.site_mi2 = nps.get_site_instance('https://www.nps.gov/slbe/index.htm')
        self.site_wy2 = nps.get_site_instance('https://www.nps.gov/fobu/index.htm')
        self.near_mi = nps.get_nearby_places(self.site_mi2)
        self.near_wy = nps.get_nearby_places(self.site_wy2)

    def test_4_1_basic(self):
        self.assertEqual(type(self.near_mi), dict)        
        self.assertEqual(type(self.near_wy), dict)        
    
    def test_4_2_contents(self):
        self.assertEqual(len(self.near_mi.keys()), 7)
        self.assertEqual(self.near_mi['resultsCount'], 10)
        self.assertEqual(len(self.near_wy.keys()), 7)
        self.assertEqual(self.near_wy['resultsCount'], 10)
        self.assertEqual(self.near_wy['options']['maxMatches'], 10)
        self.assertEqual(self.near_wy['options']['radius'], 10)


if __name__ == '__main__':
    unittest.main()
