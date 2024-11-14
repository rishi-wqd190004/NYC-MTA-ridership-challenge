# helper functions
import base64
import pandas as pd
import logging
import os

def slicing_df(filtered_df, selected_service, start_date, end_date):
    try:
        selected_service_cols = [col for col in list(filtered_df.columns) if selected_service in col]
        df1 = filtered_df[['Date', selected_service_cols[0]]]
        df1 = df1[(df1['Date'] >= pd.to_datetime(start_date)) & (df1['Date'] <= pd.to_datetime(end_date))]
        df2 = filtered_df[['Date', selected_service_cols[1]]]
        # print(df2.head(2))
        df2 = df2[(df2['Date'] >= pd.to_datetime(start_date)) & (df2['Date'] <= pd.to_datetime(end_date))]
    except TypeError:
        logging.info("selected_service is None; defaulting to an empty list for selected_service_cols")
    return df1, df2

def col_change(df):
    prefix_cnt = {}
    new_cols = ['Date']
    for col in list(df.columns):
        if ":" in col:
            prefix, suffix = col.split(":")
            if prefix not in prefix_cnt:
                prefix_cnt[prefix] = 1
            else:
                prefix_cnt[prefix] += 1
            new_col_name = f"{prefix}_{prefix_cnt[prefix]}"
            new_cols.append(new_col_name)

    new_df = pd.DataFrame(df)
    new_df.columns = new_cols
    return new_df

def convert_percent_to_num(df):
    for idx, col in enumerate(list(df.columns)):
        if "%" in col:
            df['tmp_col'] = (df[col] * df.iloc[:, idx-1]) / 100
            df['tmp_col'] = df['tmp_col'].astype(int)
            df = df.drop(col, axis=1)
            df = df.rename(columns={'tmp_col': col})
    return df

def encode_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return None
