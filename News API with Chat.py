import tkinter as tk
from tkinter import scrolledtext
import requests
import openai
import threading

# Function to rotate the loading text
def rotate_loading_text():
    loading_text = ["Fetching", "Fetching.", "Fetching..", "Fetching..."]
    while loading:
        for text in loading_text:
            if not loading:
                break
            loading_label.config(text=text)
            loading_label.update()
            #time.sleep(0.5)
    loading_label.config(text="")

# Function to fetch news from the News API
def fetch_news():
    news_api_key = news_api_key_entry.get()
    news_url = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'NVIDIA',
        'apiKey': news_api_key,
        'pageSize': 10
    }
    news_response = requests.get(news_url, params=params)
    
    if news_response.status_code == 200:
        return news_response.json()
    else:
        result_text.insert(tk.END, f"Request failed with status code {news_response.status_code}. Please check your API key and try again.\n")
        return None

# Function to summarize the article using OpenAI API
def summarize_article(content, openai_api_key):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following article:\n\n{content}"}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        result_text.insert(tk.END, f"Error generating summary: {e}\n")
        return None

# Function to fetch and summarize the news articles
def fetch_and_summarize():
    global loading
    loading = True
    threading.Thread(target=rotate_loading_text).start()
    
    result_text.delete(1.0, tk.END)
    news_data = fetch_news()
    openai_api_key = openai_api_key_entry.get()
    
    if news_data and news_data['status'] == 'ok':
        result_text.insert(tk.END, f"Total Results: {news_data['totalResults']}\n\n")
        
        for article in news_data['articles']:
            source_name = article['source']['name']
            author = article.get('author', 'Unknown')
            title = article['title']
            description = article['description']
            url = article['url']
            content = article.get('content', '')
            published_at = article['publishedAt']
            
            # Filter out articles with "Removed" content
            if content and "Removed" not in content:
                # Print article information
                result_text.insert(tk.END, f"Source: {source_name}\n")
                result_text.insert(tk.END, f"Author: {author}\n")
                result_text.insert(tk.END, f"Title: {title}\n")
                result_text.insert(tk.END, f"Description: {description}\n")
                result_text.insert(tk.END, f"URL: {url}\n")
                result_text.insert(tk.END, f"Published At: {published_at}\n")
                result_text.insert(tk.END, f"Content: {content[:200]}...\n")
                
                # Generate summary using OpenAI API
                summary = summarize_article(content, openai_api_key)
                if summary:
                    result_text.insert(tk.END, f"Summary: {summary}\n\n")
                
                result_text.insert(tk.END, "-"*80 + "\n\n")
    else:
        result_text.insert(tk.END, "Error in News API response or no articles found.\n")
    
    loading = False

# Set up the main application window
app = tk.Tk()
app.title("News Summarizer")

# Create and place the labels and entry widgets for the API keys
tk.Label(app, text="News API Key:").grid(row=0, column=0, padx=10, pady=10)
news_api_key_entry = tk.Entry(app, width=50)
news_api_key_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(app, text="OpenAI API Key:").grid(row=1, column=0, padx=10, pady=10)
openai_api_key_entry = tk.Entry(app, width=50)
openai_api_key_entry.grid(row=1, column=1, padx=10, pady=10)

# Create and place the Fetch and Summarize button
fetch_button = tk.Button(app, text="Fetch and Summarize", command=lambda: threading.Thread(target=fetch_and_summarize).start())
fetch_button.grid(row=2, column=0, columnspan=2, pady=20)

# Create and place the scrolled text widget to display results
result_text = scrolledtext.ScrolledText(app, width=100, height=30)
result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Create a label for the loading animation
loading_label = tk.Label(app, text="")
loading_label.grid(row=4, column=0, columnspan=2)

# Initialize loading flag
loading = False

# Start the Tkinter event loop
app.mainloop()
