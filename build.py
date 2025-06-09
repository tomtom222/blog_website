import os
import frontmatter
import markdown2
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import re

# Configure Jinja2
env = Environment(loader=FileSystemLoader('.'))

def read_template(template_name):
    """Read the content of an HTML template file."""
    with open(template_name, 'r', encoding='utf-8') as f:
        return f.read()

def convert_markdown_to_html(content):
    """Convert markdown content to HTML."""
    return markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])

def generate_preview(content, max_words=50):
    """Generate a preview from the markdown content."""
    # Convert markdown to plain text by removing markdown syntax
    text = re.sub(r'#+ ', '', content)  # Remove headers
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove images
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)  # Convert links to text
    text = re.sub(r'`[^`]+`', '', text)  # Remove inline code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Remove code blocks
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)  # Remove bold/italic
    
    # Split into words and take first max_words
    words = text.split()
    if len(words) <= max_words:
        preview = ' '.join(words)
    else:
        preview = ' '.join(words[:max_words]) + '...'
    
    return preview

def process_post(file_path):
    """Process a single markdown post."""
    post = frontmatter.load(file_path)
    
    # Extract metadata
    metadata = post.metadata
    if 'date' not in metadata:
        metadata['date'] = datetime.fromtimestamp(os.path.getctime(file_path))
    if 'tags' not in metadata:
        metadata['tags'] = []
    
    # Generate preview
    preview = generate_preview(post.content)
    
    # Convert content
    html_content = convert_markdown_to_html(post.content)
    
    # Get template
    template = env.from_string(read_template('post.html'))
    
    # Render HTML
    output = template.render(
        title=metadata.get('title', 'Untitled'),
        content=html_content,
        date=metadata['date'],
        tags=metadata['tags'],
        image=metadata.get('image'),
        image_alt=metadata.get('image_alt', '')
    )
    
    # Create output filename
    output_path = f"posts/{Path(file_path).stem}.html"
    
    # Save the file
    os.makedirs('posts', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    return {
        'title': metadata.get('title', 'Untitled'),
        'date': metadata['date'],
        'tags': metadata['tags'],
        'url': output_path,
        'preview': preview,
        'image': metadata.get('image'),
        'image_alt': metadata.get('image_alt', '')
    }

def build_index(posts):
    """Build the index page with all posts."""
    template = env.from_string(read_template('index.html'))
    
    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    
    output = template.render(posts=sorted_posts)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(output)

def build_tags(posts):
    """Build the tags page."""
    template = env.from_string(read_template('tags.html'))
    
    # Collect all tags
    tag_dict = {}
    for post in posts:
        for tag in post['tags']:
            if tag not in tag_dict:
                tag_dict[tag] = []
            tag_dict[tag].append(post)
    
    # Sort posts within each tag by date
    for tag in tag_dict:
        tag_dict[tag] = sorted(tag_dict[tag], key=lambda x: x['date'], reverse=True)
    
    output = template.render(tags=tag_dict)
    with open('tags.html', 'w', encoding='utf-8') as f:
        f.write(output)

def main():
    """Main build process."""
    # Process all markdown files in content directory
    posts = []
    content_dir = 'content'
    
    for file_name in os.listdir(content_dir):
        if file_name.endswith('.md'):
            file_path = os.path.join(content_dir, file_name)
            post_data = process_post(file_path)
            posts.append(post_data)
    
    # Build index and tags pages
    build_index(posts)
    build_tags(posts)
    
    print(f"Built {len(posts)} posts successfully!")

if __name__ == '__main__':
    main() 