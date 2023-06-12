import pandas as pd
import numpy as np
from ast import literal_eval
import re
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import precision_score, recall_score, f1_score

INPUT_MSC_FILE = 'msc_data.csv'
INPUT_NOT_MSC_FILE = 'shaked_connections_data.csv'

relevant_words = ['teacher', 'teaching', 'teach']
similar_words = set()
for word in relevant_words:
    synsets = wordnet.synsets(word)
    for synset in synsets:
        for lemma in synset.lemmas():
            similar_words.add(lemma.name())
similar_words = list(similar_words)

def remove_punctuation(text):
    return re.sub(r"[^a-zA-Z0-9]", " ", text.lower())

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

def add_cleaned_columns(df):
    df['Education_clean'] = df['Education']
    df['Experience_clean'] = df['Experience']
    df['skills_clean'] = df['skills']

    clean_column(df['Education_clean'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")
    clean_column(df['Experience_clean'], r"(\d+ (?:yr|yrs|mos))")
    clean_column(df['skills_clean'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")

    df['Education_clean'] = df['Education_clean'].apply(lambda x: remove_punctuation(x))
    df['Experience_clean'] = df['Experience_clean'].apply(lambda x: remove_punctuation(x))
    df['skills_clean'] = df['skills_clean'].apply(lambda x: remove_punctuation(x))
    
    return df

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

def add_features(df):
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

    return df

def add_nlp_features(df, col_name):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df[col_name])
    df_bow_sklearn = pd.DataFrame(X.toarray(),columns=vectorizer.get_feature_names_out())
    df_features = pd.concat([df.reset_index(drop=True), df_bow_sklearn.reset_index(drop=True)], axis=1)

    return df_features

def remove_unwanted_columns(df):
    columns_to_del = ['Education', 'Education_clean', 'Experience', 'Experience_clean', 
                      'skills', 'skills_clean', 'Name', 'Workplace', 'text_clean']
    for col in columns_to_del:
        if col in df.columns:
            del df[col]

    return df

def clean_train_data(df):
    columns_to_remove = ['ms', 'master', 'msc', 'masters', 'mscs']
    for col in columns_to_remove:
        if col in df.columns:
            df[col] = 0

    return df

def run_model(df):
    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(df.drop('is_msc', axis=1), df['is_msc'], test_size=0.2, random_state=42)
    X_train = clean_train_data(X_train)

    # Create and train your machine learning models
    models = [
        ('Logistic Regression', LogisticRegression(C=100.0, random_state=1, solver='lbfgs', multi_class='ovr', max_iter=5000)),
        ('Decision Tree', DecisionTreeClassifier()),
        ('Random Forest', RandomForestClassifier()),
        ('SVC', SVC())
    ]

    for model_name, model in models:
        # Train the model
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = model.score(X_test, y_test)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        print(f"{model_name} Metrics: Precision={precision:.2f} Recall={recall:.2f} F1-Score={f1:.2f} Accuracy={accuracy:.2f}") 

def main():
    # Read input files
    msc_df = pd.read_csv(INPUT_MSC_FILE, encoding='utf-8')
    not_msc_df = pd.read_csv(INPUT_NOT_MSC_FILE, encoding='utf-8')

    # Add labeling column
    msc_df['is_msc'] = True
    not_msc_df['is_msc'] = False

    # Union dataframes
    combined_df = pd.concat([msc_df, not_msc_df], axis=0)

    # Add cleaned columns
    full_df = add_cleaned_columns(combined_df)

    # Add features
    full_df = add_features(full_df)

    # Add NLP features
    full_df['text_clean'] = full_df['Education_clean']+' '+full_df['Experience_clean']+' '+full_df['skills_clean']
    full_df = add_nlp_features(full_df, 'text_clean')

    # Remove unwanted columns
    full_df = remove_unwanted_columns(full_df)
    
    # Run model
    full_df.to_csv("input_for_model.csv", index=False)
    run_model(full_df)


if __name__ == '__main__':
    main()