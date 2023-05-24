import pandas as pd
import numpy as np
import collections
from ast import literal_eval
import re
from nltk.corpus import wordnet
from nltk import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

relevant_words = ['teacher', 'teaching', 'teach']
similar_words = set()
for word in relevant_words:
    synsets = wordnet.synsets(word)
    for synset in synsets:
        for lemma in synset.lemmas():
            similar_words.add(lemma.name())
similar_words = list(similar_words)

def remove_special_characters(text):
    pattern = r'[^\x00-\x7F]'  # Keep ASCII characters
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def check_teaching_exprience(arr):
    for item in arr:
        for word in similar_words:
            if item[0].find(word) != -1:
                return True
    return False

def clean_column(series: pd.Series, filter_pattern: str):
    for row_index in range(len(series)):
        new_col_list = []
        # convert string to list
        try:
            col_list_repr = literal_eval(series[row_index])
            for col_element in col_list_repr:
                # filter out elements according to the pattern
                col_element = [elem for elem in col_element if not re.findall(filter_pattern, elem)]
                new_col_list.append(" ".join(col_element))
            # save back as cleaner string
            series[row_index] = ",".join(new_col_list)
        except:
            continue

def remove_punctuation(text):
    return re.sub(r"[^a-zA-Z0-9]", " ", text.lower())

# Data manipulation
df = pd.read_csv('msc_data.csv', encoding='utf-8')

# Add target column
np.random.seed(42)
df['is_msc'] = np.random.choice([True, False], size=len(df))

df['Education_clean'] = df['Education']
df['Experience_clean'] = df['Experience']
df['skills_clean'] = df['skills']

clean_column(df['Education_clean'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")
clean_column(df['Experience_clean'], r"(\d+ (?:yr|yrs|mos))")
clean_column(df['skills_clean'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")

df['Education'] = df['Education'].apply(lambda x: remove_special_characters(x))
df['Experience'] = df['Experience'].apply(lambda x: remove_special_characters(x))
df['skills'] = df['skills'].apply(lambda x: remove_special_characters(x))

df['Education'] = df['Education'].apply(lambda x: literal_eval(x))
df['Experience'] = df['Experience'].apply(lambda x: literal_eval(x))
df['skills'] = df['skills'].apply(lambda x: literal_eval(x))

df['num_of_educations'] = df['Education'].apply(lambda x: len(x))
df['num_of_experience'] = df['Experience'].apply(lambda x: len(x))
df['num_of_skills'] = df['skills'].apply(lambda x: len(x))

df['teaching_exprience'] = df['Experience'].apply(lambda x: check_teaching_exprience(x))



# NLP (Bag of words)
df['Education_clean'] = df['Education_clean'].apply(lambda x: remove_punctuation(x))
df['tokens'] = df['Education_clean'].apply(lambda x: word_tokenize(x))
df = df[df['tokens'].apply(lambda x: len(x) > 0)]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['tokens'].apply(lambda x: ' '.join(x)))
df_bow_sklearn = pd.DataFrame(X.toarray(),columns=vectorizer.get_feature_names_out())

# Concatenate the Bag of Words features with the original feature matrix
selected_columns = ['num_of_educations', 'num_of_experience', 'num_of_skills', 'teaching_exprience']
df_selected = df[selected_columns]
df_features = pd.concat([df_selected.reset_index(drop=True), df_bow_sklearn.reset_index(drop=True)], axis=1)

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(df_features, df['is_msc'], test_size=0.2, random_state=42)

# Create and train your machine learning model
model = LogisticRegression(C=100.0, random_state=1, solver='lbfgs', multi_class='ovr')
model.fit(X_train, y_train)

# Evaluate the model
accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

#print(df)
#df.to_csv('output.csv', index=False)