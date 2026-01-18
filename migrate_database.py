"""
기존 데이터베이스의 잘못된 데이터를 삭제하고,
실제 MDX 파일 내용을 읽어서 다시 저장하는 마이그레이션 스크립트
"""
from pathlib import Path
from app.database import get_blog_database
import re


def extract_title_from_mdx(content: str) -> str:
    """MDX 파일의 frontmatter에서 title을 추출"""
    title_match = re.search(r"title:\s*[\"']([^\"']+)[\"']", content)
    if title_match:
        return title_match.group(1)
    return "Untitled"


def migrate_database():
    """데이터베이스를 마이그레이션"""
    db = get_blog_database()
    
    # 1. 기존 모든 데이터 삭제
    print("기존 데이터 삭제 중...")
    all_posts = db.get_all_posts()
    for post in all_posts:
        db.delete_post(post["id"])
    print(f"삭제 완료: {len(all_posts)}개 항목")
    
    # 2. content/blog 디렉토리의 모든 MDX 파일 읽기
    blog_dir = Path("content/blog")
    if not blog_dir.exists():
        print(f"디렉토리가 존재하지 않습니다: {blog_dir}")
        return
    
    mdx_files = list(blog_dir.glob("*.mdx"))
    print(f"\n발견된 MDX 파일: {len(mdx_files)}개")
    
    # 3. 각 파일을 읽어서 데이터베이스에 저장
    for mdx_file in mdx_files:
        try:
            with open(mdx_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # frontmatter에서 title 추출
            title = extract_title_from_mdx(content)
            
            # 데이터베이스에 저장
            db.add_blog_post(
                title=title,
                content=content,
                file_name=mdx_file.name,
                metadata={"topic": title},
            )
            
            print(f"✅ 저장 완료: {mdx_file.name} (제목: {title})")
            
        except Exception as e:
            print(f"❌ 오류 발생 ({mdx_file.name}): {e}")
    
    print(f"\n마이그레이션 완료! 총 {len(mdx_files)}개 파일이 데이터베이스에 저장되었습니다.")


if __name__ == "__main__":
    migrate_database()
