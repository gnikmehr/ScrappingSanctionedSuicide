import pandas as pd
from nltk.corpus import stopwords
import re
import string
import json

import nltk
nltk.download('stopwords')

def lowercase_without_numbers(text):
    if isinstance(text, str):
        result = ''
        for char in text:
            if not char.isnumeric():
                result += char.lower()
            else:
                result += char  # Retain numeric digits as they are
        return result
    else:
        return "Input is not a string"
    

def clean_text(text):
    # Convert text to lowercase

    text = lowercase_without_numbers(text)
    if text == "Input is not a string":
        return "F"
    # Remove numbers and special characters
    text = re.sub(r'\d+', '', text)  # Remove digits
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation

    # Remove extra whitespaces
    text = ' '.join(text.split())


    # Remove stopwords (optional, you may need to download a list of stopwords)
    # Example using NLTK:
    # from nltk.corpus import stopwords
    stopwords_list = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stopwords_list])

    return text


if __name__ == "__main__":

    data = pd.read_json("All_Threads.json")

    dataset_data = []
    length_data = []
    for row_dict in data.to_dict(orient="records"):
        cleaned = clean_text(row_dict["title"])
        if cleaned != "" and cleaned!= "F":
            dataset_data.append(
            {
                "text": cleaned,
                "replies": row_dict["replies"],
                "views" : row_dict["views"]
            })
            length_data.append(len(cleaned))
        else:
            pass
            
    print(len(dataset_data))
    with open("cleaned_thread_titles_without_stopwords.json", "w") as f:
        json.dump(dataset_data, f)

