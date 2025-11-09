import pandas as pd

def read_any_table(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try: return pd.read_csv(uploaded_file, low_memory=False)
        except Exception: return pd.read_csv(uploaded_file, engine="python", low_memory=False)
    else:
        return pd.read_excel(uploaded_file)
