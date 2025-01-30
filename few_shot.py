import json
import pandas as pd

class FewShotPosts:
    def __init__(self, filepath="data/processed_posts.json"):
        self.df = None
        self.unique_tags = None
        self.load_posts(filepath)

    def load_posts(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            posts = json.load(f)
            self.df = pd.json_normalize(posts)
            self.df['length'] = self.df['line_count'].apply(self.categorize_length)
            all_tags = self.df['tags'].apply(lambda x: x).sum()
            self.unique_tags = set(list(all_tags))

    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif line_count < 10:
            return "Medium"
        else:
            return "Long"
        
    def get_tags(self):
        return self.unique_tags 
    
    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df['length'] == length) &
            (self.df['language'] == language) &
            (self.df['tags'].apply(lambda x: tag in x))
        ]
        return df_filtered.to_dict(orient='records')

if __name__ == '__main__':
    fsp = FewShotPosts()
    posts = fsp.get_filtered_posts("Medium", "English", "Data Science")
    print(posts)