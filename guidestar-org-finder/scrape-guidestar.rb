require 'guidestar'

KEYWORDS = ['lesbian', 'gay', 'bisexual', 'transgender', 'transmen', 'transwomen', 
			'queer', '"two spirit"', 'intersex', '"gender non*"', 'gender', 'lgbt', 'lgbtq' ]

guidestar = GuideStar.new('rahulb@yahoo.com','lalahm123')
guidestar.scrape_orgs_matching 'footie'