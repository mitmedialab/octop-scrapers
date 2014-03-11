require 'yaml'
require 'guidestar'

KEYWORDS = ['lesbian', 'gay', 'bisexual', 'transgender', 'transmen', 'transwomen', 
			'queer', '"two spirit"', 'intersex', '"gender non*"', 'gender', 'lgbt', 'lgbtq' ]

config = YAML.load_file('config.yaml')

guidestar = GuideStar.new(config['user'],config['pass'])
guidestar.scrape_orgs_matching KEYWORDS[7]
