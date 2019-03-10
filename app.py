from flask import Flask, render_template, request

from urllib.request import urlopen
from bs4 import BeautifulSoup as soup

#Global variable for cached data
cached_data = {}


# Function to generate the list of apps and add in cached data
def generate_app_list(search_key):

    playstore_url = "https://play.google.com/store/search?q=" + search_key + "&c=apps"
    u_client = urlopen(playstore_url)
    page_html = u_client.read()
    u_client.close()
    page_soup = soup(page_html, 'html.parser')

    containers = page_soup.findAll("div", {"class": "card no-rationale square-cover apps small"})
    app_details = []
    for container in containers:
        single_app = []
        app_name = container.div.div.a['aria-label']

        rating_container = container.findAll("div", {"class": "reason-set"})
        try:
            rating = rating_container[0].span.a.div.div['aria-label']
        except AttributeError:
            cached_data[search_key] = ["Oops! Please try another keyword."]

        description_container = container.findAll("div", {"class": "description"})
        description = description_container[0].text

        single_app.append(app_name)
        single_app.append(rating)
        single_app.append(description)
        app_details.append(single_app)
    cached_data[search_key] = app_details

    
#Function to fetch data from cached_data variable
def app_search(search_key):
    if cached_data.get(search_key)!=None :
        return (cached_data[search_key])
    else:
        generate_app_list(search_key)
        return cached_data[search_key]

# Function to return the list in html format
def html_format(html_code):
    html = """<HTML>
        <body>
            <h1>Google Playstore App List</h1>
            <table>
            <tr>
                <th><h1>App Name</h1></th>
                <th><h1>Rating</h1></th> 
                <th><h1>Description</h1></th>
            </tr>
                {0}
            </table>
        </body>
        </HTML>"""
    tr = "<tr>{0}</tr>"
    td = "<td>{0}</td>"
    subitems = [tr.format(''.join([td.format(a) for a in item])) for item in html_code]
    return html.format("".join(subitems))


app = Flask(__name__)

@app.route('/send', methods=['GET','POST'])
def send():

    if request.method == 'POST':
        play = request.form['play']
        html_code = app_search(str(play))
        html_applist = html_format(html_code)
        return  html_applist
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
