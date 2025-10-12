from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import BlogRequest, BlogResponse, HealthResponse
from app.agents.blog_assistant_agent import get_blog_assistant_agent
from app.database import get_blog_database
from typing import List, Dict, Any
import re

# Create FastAPI app
app = FastAPI(
    title="AI Blog Assistant API",
    description="An intelligent blog writing assistant powered by LangChain and Claude",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(status="ok", message="AI Blog Assistant API is running")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        db = get_blog_database()
        post_count = db.get_collection_count()
        return HealthResponse(
            status="healthy",
            message=f"API is running. Database contains {post_count} blog posts.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/generate-blog", response_model=BlogResponse)
async def generate_blog(request: BlogRequest, background_tasks: BackgroundTasks):
    """
    Generate a new blog post about the given topic.

    The AI agent will:
    1. Research the topic using web search
    2. Find an appropriate cover image
    3. Write a well-structured blog post
    4. Save it to an MDX file
    5. Store it in ChromaDB for future retrieval

    Args:
        request: BlogRequest containing the topic and optional instructions

    Returns:
        BlogResponse with success status and details
    """
    try:
        # Get the AI agent
        agent = get_blog_assistant_agent()

        # Generate the blog post
        result = agent.generate_blog_post(
            topic=request.topic, additional_instructions=request.additional_instructions or ""
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=f"Blog generation failed: {result.get('error', 'Unknown error')}"
            )

        output = result["result"]

        # Extract file name from the output (if mentioned)
        file_name = None
        file_name_match = re.search(r"'([^']*\.mdx)'|\"([^\"]*\.mdx)\"", output)
        if file_name_match:
            file_name = file_name_match.group(1) or file_name_match.group(2)

        # Get preview of the content
        content_preview = output[:500] + "..." if len(output) > 500 else output

        # Store in database (background task to avoid blocking)
        if file_name:

            def store_in_db():
                db = get_blog_database()
                db.add_blog_post(
                    title=request.topic,
                    content=output,
                    file_name=file_name,
                    metadata={"topic": request.topic},
                )

            background_tasks.add_task(store_in_db)

        return BlogResponse(
            success=True,
            message=f"Blog post about '{request.topic}' generated successfully",
            file_name=file_name,
            content_preview=content_preview,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")


@app.get("/search", response_model=List[Dict[str, Any]])
async def search_blog_posts(query: str, limit: int = 5):
    """
    Search for blog posts similar to the query using semantic search.

    Args:
        query: The search query
        limit: Maximum number of results to return (default: 5)

    Returns:
        A list of similar blog posts with their metadata
    """
    try:
        db = get_blog_database()
        results = db.search_similar_posts(query=query, n_results=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/posts", response_model=List[Dict[str, Any]])
async def get_all_posts():
    """
    Get all blog posts from the database.

    Returns:
        A list of all blog posts with their metadata
    """
    try:
        db = get_blog_database()
        posts = db.get_all_posts()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve posts: {str(e)}")


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    """
    Delete a blog post from the database.

    Args:
        post_id: The ID of the post to delete

    Returns:
        Success message
    """
    try:
        db = get_blog_database()
        success = db.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": f"Post {post_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


@app.post("/chat")
async def chat_with_agent(message: str):
    """
    Chat directly with the AI agent.

    Args:
        message: The message to send to the agent

    Returns:
        The agent's response
    """
    try:
        agent = get_blog_assistant_agent()
        response = agent.chat(message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
