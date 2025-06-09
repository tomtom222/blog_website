# Tech Blog

A static blog website that can be hosted on GitHub Pages.

## Local Development

To test the site locally, you have two options:

### Option 1: Python HTTP Server (Recommended)

1. Make sure you have Python installed (Python 3.x)
2. Open a terminal in the project directory
3. Run: `python serve.py`
4. Open your browser to `http://localhost:8000`

### Option 2: VS Code Live Server

If you're using Visual Studio Code:
1. Install the "Live Server" extension
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Adding New Posts

1. Create a new markdown file in the `posts` directory
2. Add the front matter at the top of the file:
   ```markdown
   ---
   title: Your Post Title
   author: Your Name
   date: YYYY-MM-DD
   image: https://path-to-image.jpg
   imageAlt: Image description
   tags: Tag1, Tag2, Tag3
   excerpt: A brief description of your post
   ---
   ```
3. Write your post content in markdown format
4. Add an entry to `posts/index.json`:
   ```json
   {
     "posts": [
       {
         "file": "your-post.md",
         "title": "Your Post Title"
       }
       // ... other posts
     ]
   }
   ```

## Deployment

To deploy to GitHub Pages:

1. Create a new repository on GitHub
2. Push your code to the repository
3. Go to repository Settings > Pages
4. Set the source to the main branch
5. Your blog will be available at `https://<username>.github.io/<repository>`

## Project Structure

```
/
├── index.html (main page)
├── post.html (individual post view)
├── tags.html (tag filtering)
├── 404.html (error page)
├── js/
│   └── blog.js (core functionality)
└── posts/
    ├── index.json (post metadata)
    └── *.md (blog posts)
```

## Features

- Dark theme
- Markdown support
- Tag filtering
- Responsive design
- Client-side search
- No build step required
- Works on GitHub Pages 