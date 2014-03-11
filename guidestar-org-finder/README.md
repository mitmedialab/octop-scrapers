GuideStar Scraper
=================

A quick and dirty scraper to generate lists of nonprofits by keyword and income level from the GuideStar online database.

Installation
------------

You need ruby and bundler installed already.  Then just run `bundle install` in this folder and bundle will install the dependencies for you.

Execution
---------

Just run this:
```ruby
ruby -I./ scrape-guidestar.rb
```
Then wait for a long time, and open the `guidestar.csv` file.
