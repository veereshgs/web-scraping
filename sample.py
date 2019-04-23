from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time
import random
from user_agent_config import user_agent_list
from flask import Flask, request, render_template

__author__ = 'veeresh'

app = Flask(__name__)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

# html_links  = ["https://www.amazon.co.jp/b?ie=UTF8&language=ja_JP&node=465610"]

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'
    }

"""getting the number that is total number of pages in middle page number """
def get_pages_no(soup):
    if(soup.find_all('span',{'class':'pagnDisabled'})):
        total_items = soup.find('span',{'class':'pagnDisabled'})
        total_items = total_items.text
        return total_items
    else:
        return None

"""getting the final page number that is total number of pages from one category"""
def get_total_page(soup):
    if(soup.find_all("ul", {"class": "a-pagination"})):
        data = soup.find_all("ul", {"class": "a-pagination"})
        soup2 = BeautifulSoup(data[0].text, "html.parser")
        page_range = str(soup2).split("\n")[5]
        return page_range
    else:
        return None


"""extracting the final product link and we have to pass the product listing link into this function """
def extract_product_link(link):
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main_url = "https://www.amazon.co.jp/"
    list1 = []
    for i in soup.find_all('span',attrs={"class":"a-size-medium a-color-base a-text-normal"}):
        # print(i)
        if (i.parent.name == 'a'):
            i = i.parent.get('href')
            complete_product_url = main_url+i
            list1.append(complete_product_url)
        else:
            return None
    return list1

"""extract the product links from the product list pages"""
def extract_product_list(soup3):
    main_url = "https://www.amazon.co.jp/"
    second_page_links = []  # it contains the second and third page links
    for link3 in soup3.find_all('span', {'class': "pagnLink"}):
        second_page_links.append(main_url + str(link3.a.get('href')))
    print(second_page_links)
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}

    response4 = requests.get(second_page_links[0], headers={'User-Agent': user_agent})
    time.sleep(10)
    soup4 = BeautifulSoup(response4.text, "html.parser")
    # print(soup4)
    first_part_url = second_page_links[0].split("page=")
    # print(first_part_url[0])
    second_part_url = first_part_url[1].lstrip("2")
    # print(second_part_url)
    #
    # var = get_total_page(soup4)
    # print(var)
    #
    sub_category_links = []
    for i in range(1, int(get_total_page(soup4)) + 1):
        category_link = first_part_url[0] + "page=" + str(i)
        sub_category_links.append(category_link)

    product_list_df = pd.DataFrame(sub_category_links, columns=['sub_category_links'])
    sub_category_links.clear()
    # print(product_list_df)
    df_links_list = product_list_df.loc[1:,
                    'sub_category_links'].tolist()  # making different df and it start from page 2 because page 2 having the end of the page number
    product_list_clear_df = pd.DataFrame(df_links_list, columns=['product_list_links'])
    print(product_list_clear_df)
    list_of_product_list_links_df.append(product_list_clear_df)
    # df.to_csv("/Users/ts-veeresh.gs/Downloads/Amazon-Data-Extraction/scrape-links/main_urls/category/sub_category/" + str(output_counts_category_url) + ".csv", )
    # output_counts_category_url = output_counts_category_url + 1

    product_links = []
    for index3, row in product_list_clear_df.iterrows():
        # print(row["sub_category_links"])
        link1 = extract_product_link(row["product_list_links"])
        # print("links :", link1)
        if (link1 != None):
            product_links.extend(link1)
        # print(index3)
        if index3 == 1:
            break

    final_product_links_df = pd.DataFrame(product_links, columns=['PRODUCT_LINKS'])  # final df for product links
    product_links.clear()
    # print(final_product_links_df)
    list_of_product_links_df.append(final_product_links_df)

    # print("second_page_links ",second_page_links)
    second_page_links.clear()
    return final_product_links_df

output_counts_seed_url = 1

output_counts_category_url = 1

list_of_main_links_df = []
list_of_category_links_df = []
list_of_product_list_links_df = []
list_of_product_links_df = []

@app.route('/')
def my_form():
    return render_template('front-end-design.html')


@app.route("/upload", methods=["POST"])
def upload():
    html = request.form['text']
    print("sedd URL", html)
    response1 = requests.get(html, headers=headers)

    soup1 = BeautifulSoup(response1.text, "html.parser")

    main_url = "https://www.amazon.co.jp/"

    # counter = 0
    link_list = []

    for link1 in soup1.findAll('a', attrs={'href': re.compile("^/b/ref=s9")}):
        href_link = link1.get('href')
        complete_url = main_url + href_link
        link_list.append(complete_url)
        # print(complete_url)
        # counter = counter + 1
    # print(link_list)
    main_df_level1 = pd.DataFrame(link_list, columns=['LINK'])
    link_list.clear()
    list_of_main_links_df.append(main_df_level1)
    # print(main_df_level1)

    # main_df_level1.to_csv("/Users/ts-veeresh.gs/Downloads/Amazon-Data-Extraction/scrape-links/main_urls/"+str(output_counts_seed_url)+".csv",)
    # output_counts_seed_url = output_counts_seed_url+1

    for index1, row in main_df_level1.iterrows():
        response2 = requests.get(row["LINK"], headers=headers)
        print("main Link ", row['LINK'])
        soup2 = BeautifulSoup(response2.text, "html.parser")
        main_url = "https://www.amazon.co.jp/"

        # counter = 0
        link_list1 = []

        for link2 in soup2.findAll('a', attrs={'class': "a-link-normal octopus-pc-category-card-v2-category-link"}):
            hreflink = link2.get('href')
            complete_url = main_url + hreflink
            link_list1.append(complete_url)
            # print(complete_url)
            # counter = counter + 1

        category_df_level2 = pd.DataFrame(link_list1, columns=['CATEGORY_LINK1'])
        link_list1.clear()
        list_of_category_links_df.append(category_df_level2)
        print("category_df ", category_df_level2)

        for index2, row in category_df_level2.iterrows():
            response3 = requests.get(row["CATEGORY_LINK1"], headers=headers)
            soup3 = BeautifulSoup(response3.text, "html.parser")
            user_agent = random.choice(user_agent_list)  # Randomly choosing the user agent from the config file

            if (get_pages_no(soup3) != None):  # some pages having limited pages that will be done here
                result_df = extract_product_list(soup3)
                print(result_df)
                return render_template('view.html',tables=[result_df.to_html(classes='female')],titles = ['PRODUCT_LINKS'])
            elif (get_total_page(soup3) != None):
                result_df = extract_product_list(soup3)
                print(result_df)
                if (index2 == 0):
                    # return render_template('view.html', tables=[result_df.to_html(classes='female')],titles=['PRODUCT_LINKS'])
                    break

            else:
                print("First page don't have the end page number ")
            if (index2 == 0):
                break

        if (index1 == 1):
            break

    # for html in html_links:


if __name__ == "__main__":
    app.run(port=4555, debug=True)

