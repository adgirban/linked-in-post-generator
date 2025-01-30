import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm

def process_posts(raw_file_path, processed_file_path="data/processed_posts.json"):
    enriched_posts = []
    with open(raw_file_path, encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            metadata = extract_metadata(post['text'])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)
            post = {'text': 'abc', 'engagement': 345}
            metadata = {'line_count': 10, 'language': 'English', 'tags': ['python', 'data science', 'machine learning']}

    unified_tags = get_unified_tags(enriched_posts)

    for post in enriched_posts:
        new_tags = {unified_tags[tag] for tag in post['tags']}
        post['tags'] = list(new_tags)

    with open(processed_file_path, encoding='utf-8', mode='w') as f:
        json.dump(enriched_posts, f, indent=4)

def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])
    
    unique_tags_list = ', '.join(unique_tags)

    template = '''
    1. I will give you a list of tags. You need to unify them with the following requirements:
    Example 1: "Jobseekers", "Job Hunting" can be all merged into single tag "Job Search".
    Example 2: "Motivation", "Inspiration", "Drive" can be mapped into single tag "Motivation".
    2. Each tag should follow title case capitalization. Eg: "Data Science", "Machine Learning".
    3. Return a valid JSON. No Preamble.
    4. Output should have mapping of original tag and unified tag.
    Example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

    Here is a list of tags:
    {tags}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'tags': str(unique_tags_list)})
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res

def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. Extract the following metadata from the post:
    - Number of lines in the post
    - Language of the post
    - Tags in the post
    1.Return a valid JSON. No Preamble.
    2.The JSON should have the following keys: 'line_count', 'language', 'tags'
    3.tags should be a list of strings. Extract maximum 2 tags from the post.
    4.Language should be English or Roman Nepali(Nepali+English).

    Here is the actual post on which you need to perform the extraction:
    {post}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'post': post})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")
    return res

if __name__ == '__main__':
    process_posts("data/raw_posts.json", "data/processed_posts.json")