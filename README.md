# AI Blog Assistant API

An intelligent blog writing assistant powered by FastAPI, LangChain, Claude AI, and ChromaDB. This application demonstrates the power of AI agents with custom tools that can autonomously research, write, and save high-quality blog posts.

## Features

- **Autonomous Blog Generation**: AI agent that can research, write, and save complete blog posts
- **Custom Tools**: Three specialized tools for the agent:
  - `WebSearchTool`: Search the web for latest information
  - `ImageSearchTool`: Find royalty-free cover images
  - `FileWriterTool`: Save blog posts to MDX files
- **Semantic Search**: ChromaDB integration for content storage and similarity search
- **ReAct Pattern**: Agent uses Reasoning + Acting pattern for autonomous decision-making
- **FastAPI Backend**: Modern, high-performance API with automatic documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Blog Assistant Agent                        │  │
│  │  (LangChain + Claude AI)                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│      ┌───────────────────┼───────────────────┐             │
│      │                   │                   │             │
│  ┌───▼────┐        ┌────▼─────┐       ┌────▼────┐        │
│  │  Web   │        │  Image   │       │  File   │        │
│  │ Search │        │  Search  │       │ Writer  │        │
│  │  Tool  │        │   Tool   │       │  Tool   │        │
│  └────────┘        └──────────┘       └─────────┘        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               ChromaDB                                │  │
│  │  (Semantic Search & Storage)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Anthropic API key (for Claude AI)
- (Optional) Tavily API key for web search
- (Optional) Pexels API key for image search

### Setup Steps

1. **Clone the repository**:
```bash
git clone <repository-url>
cd langchain-python-test
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
PEXELS_API_KEY=your_pexels_api_key_here  # Optional
```

5. **Run the server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```http
GET /health
```

### Generate Blog Post
```http
POST /generate-blog
Content-Type: application/json

{
  "topic": "The Rise of AI-Native Development",
  "additional_instructions": "Focus on practical examples"
}
```

Response:
```json
{
  "success": true,
  "message": "Blog post about 'The Rise of AI-Native Development' generated successfully",
  "file_name": "ai-native-development.mdx",
  "content_preview": "---\ntitle: \"The Rise of AI-Native Development\"..."
}
```

### Search Blog Posts
```http
GET /search?query=AI%20development&limit=5
```

### Get All Posts
```http
GET /posts
```

### Delete Post
```http
DELETE /posts/{post_id}
```

### Chat with Agent
```http
POST /chat?message=Tell me about AI agents
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## How It Works

### The ReAct Loop

The agent uses the ReAct (Reasoning + Acting) pattern:

1. **Thought**: Agent analyzes what needs to be done
2. **Action**: Agent selects and uses appropriate tools
3. **Observation**: Agent processes the results
4. **Repeat**: Continue until task is complete

Example agent execution:

```
User: "Write a blog post about AI-Native Development"

Thought: I need latest information about AI-Native Development.
Action: web_search("AI-Native Development trends 2025")
Observation: [Search results about AI-Native Development...]

Thought: Now I need a cover image for the blog.
Action: image_search("futuristic AI robot programming")
Observation: [Image URL found]

Thought: I have all the information. Time to write and save the blog.
Action: write_blog_file("ai-native-development.mdx", "---\ntitle: ...\n---\n\n# Content...")
Observation: File saved successfully

Final Answer: Successfully created blog post about AI-Native Development
```

### Custom Tools

Each tool is defined with a clear description that helps the AI understand when to use it:

```python
@tool
def web_search(query: str) -> str:
    """Search the web for latest information about a given topic.

    This tool is useful for getting current trends, facts, and recent information
    that will help create well-researched blog content.
    """
    # Implementation...
```

### ChromaDB Integration

Blog posts are stored in ChromaDB for semantic search:

- **Automatic Storage**: Posts are automatically indexed after generation
- **Semantic Search**: Find similar posts based on content, not just keywords
- **Efficient Retrieval**: Fast similarity search across all stored content

## Project Structure

```
langchain-python-test/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # ChromaDB integration
│   ├── agents/
│   │   ├── __init__.py
│   │   └── blog_assistant_agent.py  # Main AI agent
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search_tool.py       # Web search capability
│   │   ├── image_search_tool.py     # Image search capability
│   │   └── file_writer_tool.py      # File operations
│   └── models/
│       ├── __init__.py
│       └── schemas.py               # Pydantic models
├── content/
│   └── blog/                   # Generated blog posts
├── chroma_db/                  # ChromaDB storage
├── requirements.txt
├── .env.example
└── README.md
```

## Usage Examples

### Example 1: Generate a Technical Blog Post

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-blog",
    json={
        "topic": "Introduction to LangChain Agents",
        "additional_instructions": "Include code examples and practical use cases"
    }
)

print(response.json())
```

### Example 2: Search Similar Posts

```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={"query": "machine learning", "limit": 3}
)

for post in response.json():
    print(f"Title: {post['metadata']['title']}")
    print(f"Similarity: {post['distance']}")
```

### Example 3: Chat with Agent

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    params={"message": "What are the best practices for writing technical blogs?"}
)

print(response.json()["response"])
```

## API Keys

### Anthropic API Key (Required)
- Sign up at https://console.anthropic.com/
- Used for Claude AI model access

### Tavily API Key (Optional)
- Sign up at https://tavily.com/
- Improves web search quality
- Falls back to simulated search if not provided

### Pexels API Key (Optional)
- Sign up at https://www.pexels.com/api/
- Access to high-quality royalty-free images
- Falls back to placeholder images if not provided

## Customization

### Modify Agent Behavior

Edit `app/agents/blog_assistant_agent.py` to customize the system prompt:

```python
system_prompt = """You are an expert blog writing assistant...

Customize the instructions here to change agent behavior.
"""
```

### Add New Tools

Create a new tool in `app/tools/`:

```python
from langchain.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Description of what your tool does."""
    # Implementation
    return result
```

Register it in the agent:
```python
self.tools = [web_search, image_search, write_blog_file, my_custom_tool]
```

## Troubleshooting

### Agent Not Using Tools
- Check tool descriptions are clear and specific
- Verify API keys are set correctly
- Review agent logs (verbose=True)

### ChromaDB Errors
- Ensure write permissions for `chroma_db` directory
- Delete `chroma_db` folder to reset database

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version` (should be 3.10+)

## Development

### Run Tests
```bash
pytest tests/
```

### Format Code
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## References

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## Support

For issues and questions, please open an issue on the GitHub repository.
