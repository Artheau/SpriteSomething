#unit testing framework
#I have no idea what I'm doing:  http://www.quickmeme.com/meme/3p0di5

import unittest

class TestStuff(unittest.TestCase):
	#all tests must start with "test_"
    def test_make_sure_it_is_not_nothing(self):
    	self.assertFalse("it" == None)

    def test_make_sure_it_is_something(self):
    	self.assertTrue("it" != None)

    def test_make_sure_it_is_what_it_is(self):
    	my_metaphor = "it"
    	self.assertEqual(my_metaphor, "it")

if __name__ == '__main__':
    unittest.main()
