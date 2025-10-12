from chromadb import Client, Settings
from chromadb.config import Settings as ChromaSettings
import chromadb
from pathlib import Path
from app.config import get_settings
from typing import List, Dict, Any
import uuid
from datetime import datetime


class BlogDatabase:
    """
    ChromaDB integration for storing and retrieving blog post content.

    This allows for semantic search and retrieval of blog posts based on content similarity.
    """

    def __init__(self):
        settings = get_settings()

        # Create persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

        # Get or create collection for blog posts
        self.collection = self.client.get_or_create_collection(
            name="blog_posts",
            metadata={"description": "Blog post content and metadata"},
        )

    def add_blog_post(
        self,
        title: str,
        content: str,
        file_name: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Add a blog post to the database.

        Args:
            title: The title of the blog post
            content: The full content of the blog post
            file_name: The file name where the post is saved
            metadata: Additional metadata about the post

        Returns:
            The ID of the added document
        """
        doc_id = str(uuid.uuid4())

        # Prepare metadata
        meta = {
            "title": title,
            "file_name": file_name,
            "created_at": datetime.now().isoformat(),
        }
        if metadata:
            meta.update(metadata)

        # Add to collection
        self.collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id],
        )

        return doc_id

    def search_similar_posts(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for blog posts similar to the query.

        Args:
            query: The search query
            n_results: Number of results to return

        Returns:
            A list of similar blog posts with their metadata
        """
        results = self.collection.query(query_texts=[query], n_results=n_results)

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    }
                )

        return formatted_results

    def get_all_posts(self) -> List[Dict[str, Any]]:
        """
        Get all blog posts from the database.

        Returns:
            A list of all blog posts with their metadata
        """
        results = self.collection.get()

        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                formatted_results.append(
                    {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    }
                )

        return formatted_results

    def delete_post(self, doc_id: str) -> bool:
        """
        Delete a blog post from the database.

        Args:
            doc_id: The ID of the document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def get_collection_count(self) -> int:
        """
        Get the total number of blog posts in the database.

        Returns:
            The count of blog posts
        """
        return self.collection.count()


# Singleton instance
_db_instance = None


def get_blog_database() -> BlogDatabase:
    """Get or create the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = BlogDatabase()
    return _db_instance
