require 'watir'
require 'watir-webdriver'
require 'logger'
require 'csv'

class GuideStar

  LOGIN_URL = 'http://www.guidestar.org/Login.aspx'
  ADVANCED_SEARCH_URL = 'http://www.guidestar.org/AdvancedSearch.aspx'
  INCOME_RANGES = [ ['','1'], ['1','100k'], ['100k','200k'], ['200k','300k'], ['300k','400k'], 
                    ['400k','500k'], ['500k','600k'], ['600k','700k'], ['700k','800k'], ['800k','900k'], 
                    ['900k','1m'], ['1m',''] ]

  def initialize(username,password)
    @log = Logger.new 'guidestar.log'
    @user = username
    @pass = password
    @logged_in = false
    @log.info "Creating browser"
    @browser = Watir::Browser.new :chrome
    @log.info " done"
  end

  def scrape_orgs_matching keyword
    @output_csv = init_csv 'guidestar-'+keyword+'.csv'
    login if not @logged_in
    INCOME_RANGES.each do |income|
      do_advanced_search keyword, income
    end
    @browser.quit
  end

  private

    def login
      @log.info "Trying to log in"
      @browser.goto LOGIN_URL
      @browser.text_field(:name => 'ctl00$phMainBody$LoginMainsite$UserName').when_present.set @user
      @browser.text_field(:name => 'ctl00$phMainBody$LoginMainsite$Password').when_present.set @pass
      @log.info "  submitting login form"
      @browser.input(:name => 'ctl00$phMainBody$LoginMainsite$LoginButton').click
      @log.info "  done - logged in"
      @logged_in = true
    end

    def do_advanced_search keyword, income_range
      @log.info "Searching for '"+keyword+"' orgs ( income between "+income_range.join(" and ")+" )"
      @browser.goto ADVANCED_SEARCH_URL
      # set the keyword
      @browser.text_field(:name=>'ctl00$phMainBody$orgSearchConfiguration_keywords$txtValue').when_present.set keyword
      # set the income range
      @browser.text_field(:name=>'ctl00$phMainBody$orgSearchConfiguration_incometotal$tbMin').when_present.set income_range[0]
      @browser.text_field(:name=>'ctl00$phMainBody$orgSearchConfiguration_incometotal$tbMax').when_present.set income_range[1]
      # click submit
      @browser.input(:name=>'ctl00$phMainBody$ctl08').click
      # scrape results
      page_num = 1
      queue_search_results_page keyword, income_range, page_num
      # go to next page
      more_pages = true
      while more_pages do   # for some reason @browser.link(:text=>'Next >').present? didn't work, so I catch the error instead :-(
        begin
          page_num = page_num + 1
          @log.info "  loading next page..."
          @browser.link(:text=>'Next >').click
          queue_search_results_page keyword, income_range, page_num
        rescue Selenium::WebDriver::Error::WebDriverError
          more_pages = false
        end
      end
    end

    def queue_search_results_page keyword, income_range, page
      @log.info "  Queuing results page "+page.to_s
      @browser.links(:class=>'red_link').each do |link|
        queue_one_org [ keyword, income_range.join("-"), page, link.text, link.href ]
      end
    end

    def queue_one_org properties 
      @output_csv << properties
    end

    def init_csv file
      csv = CSV.open(file,'wb')
      csv << ["keyword", "income", "page", "name", "url"]
    end

end
