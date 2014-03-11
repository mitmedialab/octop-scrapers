GuideStar Scraper
=================

A quick and dirty scraper to generate lists of nonprofits by keyword and income level from the GuideStar online database.

Installation
------------

You need ruby and bundler installed already.  Then just run this command (in this folder) and bundle will install the dependencies for you:
```ruby
bundle install
```

Also, to use chrome you need to install the chromedriver from here:
```
http://chromedriver.storage.googleapis.com/index.html?path=2.9/
```

Then copy `config.yaml.template` to `config.yaml` and edit it.  Put in your GuideStar username and password.

Execution
---------

Open the `scrape-guidestar.rb` file and put in the keyword you want to scrape for.  Then just run this:
```ruby
ruby -I./ scrape-guidestar.rb
```
Then wait for a long time, and open the `guidestar-[keyword].csv` file to see the results once the script finishes.  You can watch the `guidestar.log` file while this is happening to keep an eye on what is going on.
