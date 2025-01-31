from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    elif length == "Medium":
        return "6 to 10 lines"
    else:
        return "11 to 15 lines"

def generate_post(topic, length, language):
    length_str = get_length_str(length)
    prompt = f'''
    Generate a LinkedIn post using the information. No preamble.

    1) Topic: {topic}
    2) Length: {length_str}
    3) Language: {language}

    If language is Roman Nepali then it means it is a mix of Nepali and English where Nepali is written with English letters. Be sure to not mix Hindi with Nepali.
    '''

    examples = few_shot.get_filtered_posts(length, language, topic)
    if len(examples)>0:
        prompt += "4) Use the writing style as per the following examples."
        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f"\nExample {i+1}: {post_text}"

            if i==1:
                break

    response = llm.invoke(prompt)
    return response.content

if __name__ == '__main__':
    generate_post()