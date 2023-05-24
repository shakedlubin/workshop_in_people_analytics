import re
import pandas as pd
import ast

input_csv = 'msc_data.csv'


def clean_column(series: pd.Series, filter_pattern: str):
    for row_index in range(len(series)):
        new_col_list = []
        # convert string to list
        try:
            col_list_repr = ast.literal_eval(series[row_index])
            for col_element in col_list_repr:
                # filter out elements according to the pattern
                col_element = [elem for elem in col_element if not re.findall(filter_pattern, elem)]
                new_col_list.append(" ".join(col_element))
            # save back as cleaner string
            series[row_index] = ",".join(new_col_list)
        except:
            continue


df = pd.read_csv(input_csv)
# remove strings like 'Feb 2021 - Sep 2022 · 1 yr 8 mos', 'Nov 2021 - Present · 1 yr 7 mos'
clean_column(df['Experience'], r"(\d+ (?:yr|yrs|mos))")
# removes strings like '2019 - 2023', '2016 - 2020', '2020 - Dec 2024', '2020 - 2022'
clean_column(df['skills'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")
clean_column(df['Education'], r"\b\d{4}\b(?:\s*-\s*(?:\d{4}|[A-Za-z]{3} \d{4}))?")

df.to_csv(input_csv[:-4]+'_cleaned.csv', index=False)
