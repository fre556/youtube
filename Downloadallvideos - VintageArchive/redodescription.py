import json
import re
import logging
import openai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = 'sk-proj-m1VUttsLHSPjw2m1qdVgT3BlbkFJr02QGO0upljypEtgXyWi'  # Replace with your actual OpenAI API key

# Path to the JSON file
input_file = 'output/video_details.json'
output_file = 'output/updated_video_details.json'

# Function to extract year from text
def extract_year(text):
    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        return match.group(0)
    return None

# Function to remove emails and contact information from text
def remove_contact_info(text):
    text = re.sub(r'\S+@\S+', '', text)  # Remove email addresses
    text = re.sub(r'\b(?:\d{10}|\d{3}-\d{3}-\d{4})\b', '', text)  # Remove phone numbers
    return text

# Function to get new title from OpenAI GPT model
def get_new_title(description, year=None):
    prompt = f"Generate a compelling, click-worthy title for a YouTube video based on the following description: {description}"
    if year:
        prompt += f" Include the year {year} in the title."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,  # Increase token limit for potentially longer titles
            temperature=0.8,  # Increase creativity
        )
        new_title = response['choices'][0]['message']['content'].strip()
        if len(new_title) > 100:
            new_title = new_title[:97] + "..."  # Truncate and add ellipsis if title exceeds 100 characters
        return new_title
    except Exception as e:
        logger.error(f"Error generating new title: {e}")
        return "Error in generating title"

# Function to get new description from OpenAI GPT model
def get_new_description(text):
    cleaned_text = remove_contact_info(text)
    prompt = f"Write a new, engaging, and informative YouTube video description based on the following text, but do not include any email addresses, phone numbers, or other contact information: {cleaned_text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Allow more tokens for longer descriptions
            temperature=0.7,
        )
        new_description = response['choices'][0]['message']['content'].strip()
        if len(new_description) > 5000:
            new_description = new_description[:4997] + "..."  # Truncate and add ellipsis if description exceeds 5000 characters
        return new_description
    except Exception as e:
        logger.error(f"Error generating new description: {e}")
        return "Error in generating description"

# Load video details from JSON file
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    logger.info(f"Loaded details for {len(videos)} videos from {input_file}.")
except Exception as e:
    logger.error(f"Failed to load JSON: {e}")
    raise

# Update titles and descriptions
for video in videos:
    try:
        original_description = video['Description']
        year = extract_year(original_description)
        new_title = get_new_title(original_description, year)
        new_description = get_new_description(original_description)
        
        video['Title'] = new_title
        video['Description'] = new_description
        
        logger.info(f"Updated video {video['Label']}: {new_title}")
    except Exception as e:
        logger.error(f"Error updating video {video['Label']}: {e}")

# Save updated video details to JSON file
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    logger.info(f"Saved updated details for {len(videos)} videos to {output_file}.")
except Exception as e:
    logger.error(f"Failed to save JSON: {e}")
    raise
