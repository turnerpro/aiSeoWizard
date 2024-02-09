from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import openai
import constants

app = Flask(__name__)

#ToDo move this to build step
openai_api_key = constants.openai_api_key

def get_meta_tags_and_ga(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract meta tags
        meta_tags = [meta.attrs for meta in soup.find_all('meta')]
        
        # Extract body text
        body_text = soup.body.get_text(separator=' ', strip=True)
        
        # Check for Google Analytics script
        ga_script_found = False
        for script in soup.find_all("script"):
            if "google-analytics.com" in str(script) or "ga('create'" in str(script) or "gtag('config'" in str(script):
                ga_script_found = True
                break
        
        return meta_tags, ga_script_found, body_text
    except requests.exceptions.RequestException as e:
        print(e)
        return None, False, None
    
def generate_meta_tags(html_body_text, openai_api_key):
    openai.api_key = openai_api_key

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Generate meta tags for the following HTML body text: {html_body_text}", 
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].text.strip()


# openai_api_key = "your_openai_api_key_here"  # Replace with your actual API key
# html_body_text = "<p>This is an example of HTML body text. Imagine this being content from a webpage.</p>"
# meta_tags_suggestions = generate_meta_tags(html_body_text, openai_api_key)
# print(meta_tags_suggestions)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        meta_tags, body_text, ga_script_found = get_meta_tags_and_ga(url)
        return render_template('index.html', meta_tags=meta_tags, body_text=body_text, ga_script_found=ga_script_found)
    return render_template('index.html', meta_tags=None, ga_script_found=None)

if __name__ == '__main__':
    app.run(debug=True)
