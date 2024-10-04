import json
import re
import logging
import openai
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = 'sk-proj-m1VUttsLHSPjw2m1qdVgT3BlbkFJr02QGO0upljypEtgXyWi'  # Replace with the path to your API key file

# Paths to JSON files
input_file = 'output/video_details.json'
output_file = 'output/updated_video_details.json'

# Hardcoded schedule date
schedule_date = "2024-08-15 00:00:00"  # Replace with your desired date

# Manually input the meta tags
meta_tags_input = input("Enter the meta tags separated by commas: ").strip().split(',')
meta_tags = ["vintage archive", "archive"] + meta_tags_input  # Add "vintage archive" and "archive" to the meta tags

# Function to extract year from text
def extract_year(text):
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return match.group(0) if match else None

# Function to get new title from OpenAI GPT model
def get_new_title(original_title, description, year=None):
    prompt = f"Generate a compelling, click-worthy title for a YouTube video based on the following title and description: Title: {original_title} Description: {description}"
    if year:
        prompt += f" Include the year {year} in the title."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.8  # Increase creativity
        )
        new_title = response['choices'][0]['message']['content'].strip()
        return new_title if len(new_title) <= 100 else new_title[:97] + "..."  # Truncate and add ellipsis if title exceeds 100 characters
    except Exception as e:
        logger.error(f"Error generating new title: {e}")
        return "Error in generating title"

# Function to get new description from OpenAI GPT model
def get_new_description(original_title, original_description):
    prompt = f"Write a new, engaging, and informative YouTube video description based on the following title and description: Title: {original_title} Description: {original_description}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Allow more tokens for longer descriptions
            temperature=0.7
        )
        new_description = response['choices'][0]['message']['content'].strip()
        if len(new_description) > 5000:
            new_description = new_description[:4997] + "..."  # Truncate and add ellipsis if description exceeds 5000 characters
        return new_description
    except Exception as e:
        logger.error(f"Error generating new description: {e}")
        return "Error in generating description"

# Contact information to be added at the end of each description
contact_information = """
For any concerns or issues regarding the video, please contact us at vintagearchivecontact@gmail.com. If you have any copyright issues, we kindly ask that you reach out to us directly before filing a copyright strike with YouTube. Please send us a message with your concerns, and we will resolve the matter promptly. All our contact details are available on our channel's 'About' page and above.

Note: When emailing us, please include a subject line relevant to your concern, such as 'Video Concern' or 'Copyright Issue,' to ensure your email is addressed promptly.
"""

# Load video details from JSON file
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    logger.info(f"Loaded details for {len(videos)} videos from {input_file}.")
except Exception as e:
    logger.error(f"Failed to load JSON: {e}")
    raise

# Update titles, descriptions, and add schedule and meta tags
for video in videos:
    try:
        original_title = video['Title']
        original_description = video['Description']
        year = extract_year(original_description)
        new_title = get_new_title(original_title, original_description, year)
        new_description = get_new_description(original_title, original_description)
        
        video['Title'] = new_title
        video['Description'] = f"{new_description}\n\n{contact_information}"
        video['Tags'] = meta_tags
        video['Schedule'] = schedule_date
        
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
