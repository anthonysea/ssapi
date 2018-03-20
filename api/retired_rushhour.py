@app.route('/api/v1.0/<int:api_key>/scrape/rushhour/new',methods=['GET'])
########scrapes the Rush Hour index page
def get_rush_hour_index(api_key):
    if str(api_key)!=the_api_key:
        return 401
    #base_url = 'http://www.rushhour.nl/store_master.php?idxGroup=2&idxGenre=2&idxSubGenre=&app=250'

    week = datetime.datetime.utcnow().isocalendar()[1]
    year = datetime.datetime.utcnow().isocalendar()[0]

    base_url = 'http://www.rushhour.nl/store_master.php?blNew=1&bIsOutOfStock=1&numYear=%s&numWeek=%s&app=250' % (year,week)


    #for selenium
    display = Display(visible=0, size=(800, 600))
    display.start()
    geckodriver_log_location = os.path.join(app.root_path, 'logs', 'geckodriver.log')
    print(geckodriver_log_location)
    # return geckodriver_log_location

    ####now get the HTML
    try:
        r = requests.get(base_url,timeout=5)
    except Exception as e:
        return "Failed to request the Rush Hour URL " + base_url, 405

    #need to use selenium because of the popup
    browser = webdriver.Firefox(log_path=geckodriver_log_location)
    browser.get(base_url)
    try:
        alert = browser.switch_to_alert()
        alert.accept()
        print "alert accpted"
    except:
        print "no alert"
    html = browser.page_source
    browser.close()


    display.sendstop()



    soup = BeautifulSoup(html, "lxml")

    for product in soup.find_all("div","item_wrap1"):
        details = str()
        label_html = str()
        label = str()
        label_url = str()
        artist_title = str()
        split_a_t = str()
        artist = str()
        title = str()
        release_url = str()



        the_release = product.find("div","item_content")

        all_details = the_release.find("h2","title")
        #print all_details
        release_url = all_details.findAll("a")[0]['href']
        url_split = release_url.split('=')
        store_release_id = url_split[1]
        print store_release_id
        all_details_reg = all_details.text.split(' - ')
        title = all_details_reg[1]
        label = all_details_reg[2]
        print title,label


        if len(store_release_id)<1:
            print('Didnt get the store id - skip')
            continue

        if len(label) < 3 or len(title) < 3:
            print('skipping ' + title + ' or ' + label + ' as less than 3 characters')
            continue


        #sql = ('SELECT id FROM releases_all WHERE label_no_country LIKE %s AND title LIKE %s') % ('%' + label + '%','%' + title + '%')
        try:
            query = db_insert('INSERT INTO store_mappings (release_id,store,store_url,unique_key,store_release_id) SELECT id,%s,%s, md5(concat(id,%s)),%s FROM releases_all WHERE label_no_country LIKE %s AND title LIKE %s ON DUPLICATE KEY UPDATE store_url=values(store_url),store_release_id=values(store_release_id)', ('rushhour','/' + release_url,'rushhour',store_release_id,label + '%','%' + title + '%'))
            data = query.fetchall()
            print(query,data)
        except Exception as e:
            print(str(e))
            continue

    return base_url,201


@app.route('/api/v1.0/<int:api_key>/scrape/rushhour/release/<string:rushhour_id>',methods=['GET'])
def get_rushhour_release(api_key,rushhour_id):
    if str(api_key)!=the_api_key:
        return 401
    base_url = 'http://www.rushhour.nl/store_detailed.php?item=' + rushhour_id

    #for selenium
    display = Display(visible=0, size=(800, 600))
    display.start()
    geckodriver_log_location = os.path.join(app.root_path, 'logs', 'geckodriver.log')
    print(geckodriver_log_location)
    # return geckodriver_log_location

    ####now get the HTML
    try:
        r = requests.get(base_url,timeout=5)
    except Exception as e:
        return "Failed to request the Rush Hour URL " + base_url, 405

    #need to use selenium because of the popup
    browser = webdriver.Firefox(log_path=geckodriver_log_location)
    browser.get(base_url)
    try:
        alert = browser.switch_to_alert()
        alert.accept()
        print "alert accpted"
    except:
        print "no alert"
    html = browser.page_source
    browser.close()

    display.sendstop()

    soup = BeautifulSoup(html, "lxml")
    stock_details = soup.findAll("img",class_="cart_icon")
    print(stock_details)

    cart_url = 'http://www.rushhour.nl/store_detailed.php?action=add&item=' + rushhour_id

    if len(stock_details) > 0:
        return jsonify({'store':'rushhour','in_stock':'true','cart_url':cart_url})
    else:
        return jsonify({'store':'rushhour','in_stock':'false','cart_url':cart_url})