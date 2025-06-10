import os
import frontmatter
import markdown2
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import re

# Configure Jinja2 to look for templates in the templates directory
env = Environment(loader=FileSystemLoader('templates'))

def read_template(template_name):
    """Read the content of an HTML template file."""
    return env.get_template(template_name).render()

def convert_markdown_to_html(content):
    """Convert markdown content to HTML."""
    # Replace relative image paths to work from the posts directory
    content = re.sub(r'!\[(.*?)\]\((?!http)(.*?)\)', r'![\1](../\2)', content)
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
    elif isinstance(metadata['date'], str):
        # Convert string date to datetime if needed
        try:
            metadata['date'] = datetime.strptime(metadata['date'], '%Y-%m-%d')
        except ValueError:
            # If date parsing fails, use file creation time as fallback
            metadata['date'] = datetime.fromtimestamp(os.path.getctime(file_path))
    if 'tags' not in metadata:
        metadata['tags'] = []
        
    # Fix image paths in metadata to be relative to posts directory
    if 'image' in metadata and not metadata['image'].startswith(('http://', 'https://')):
        metadata['image'] = metadata['image'].lstrip('/')  # Remove leading slashes
        if not metadata['image'].startswith('static/'):
            metadata['image'] = f"static/images/{metadata['image']}"
    
    # Generate preview
    preview = generate_preview(post.content)
    
    # Convert content
    html_content = convert_markdown_to_html(post.content)
    
    # Get template
    template = env.get_template('post.html')
    
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

def build_index(posts, posts_per_page=5):
    """Build the index pages with pagination."""
    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    
    # Calculate number of pages needed
    total_pages = (len(sorted_posts) + posts_per_page - 1) // posts_per_page
    
    # Get all unique tags
    all_tags = set()
    for post in posts:
        if 'tags' in post:  # Check if tags exist for the post
            all_tags.update(post['tags'])
    all_tags = sorted(all_tags)
    
    # Get template
    template = env.get_template('index.html')
    
    for page_num in range(total_pages):
        start_idx = page_num * posts_per_page
        end_idx = start_idx + posts_per_page
        current_posts = sorted_posts[start_idx:end_idx]
        
        # Render HTML
        output = template.render(
            posts=current_posts,
            all_posts=sorted_posts,
            all_tags=all_tags,
            current_page=page_num,
            total_pages=total_pages
        )
        
        # Write the file
        output_file = 'index.html' if page_num == 0 else f'page{page_num + 1}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)

def build_tags(posts):
    """Build the tags page."""
    template = env.get_template('tags.html')
    
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