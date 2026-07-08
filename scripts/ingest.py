#!/usr/bin/env python3

# Bulk PDF ingestion script.

# Usage:
#     python scripts/ingest.py /path/to/documents --category support
    
#     python scripts/ingest.py ./data/manuals --category bugfix

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import SessionLocal, Base, engine
from db.models import Document, DocumentType, DocumentStatus, User
from services.rag.parser import parse_document, create_llama_documents
from services.rag.retriever import add_documents
from core.config import get_settings

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)


def get_file_type(filename: str) -> DocumentType:
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    type_map = {
        "pdf": DocumentType.PDF,
        "docx": DocumentType.DOCX,
        "txt": DocumentType.TXT
    }
    return type_map.get(ext)


def ingest_file(file_path: Path, db, user_id: str, category: str = None) -> dict:
    # Ingest a single file.
    import uuid
    from datetime import datetime
    
    print(f"\n Processing: {file_path.name}")
    
    # Validate file type
    file_type = get_file_type(file_path.name)
    if not file_type:
        print(f"     Skipped: Unsupported file type")
        return {"status": "skipped", "reason": "unsupported_type"}
    
    # Create document record
    doc_id = str(uuid.uuid4())
    dest_path = settings.document_upload_path / f"{doc_id}{file_path.suffix}"
    
    # Copy file
    import shutil
    shutil.copy2(file_path, dest_path)
    
    document = Document(
        id=doc_id,
        filename=dest_path.name,
        original_filename=file_path.name,
        file_path=str(dest_path),
        file_size=file_path.stat().st_size,
        file_type=file_type,
        status=DocumentStatus.PROCESSING,
        user_id=user_id
    )
    
    db.add(document)
    db.commit()
    
    try:
        # Parse document
        chunks, metadata = parse_document(str(dest_path))
        
        if not chunks:
            raise ValueError("No text content extracted")
        
        # Create LlamaIndex documents
        llama_docs = create_llama_documents(
            chunks=chunks,
            filename=file_path.name,
            doc_id=doc_id,
            category=category
        )
        
        # Add to ChromaDB
        add_documents(llama_docs, settings.CHROMA_COLLECTION_NAME)
        
        # Update record
        document.status = DocumentStatus.COMPLETED
        document.page_count = metadata.get("page_count")
        document.chunk_count = len(chunks)
        document.chroma_collection = settings.CHROMA_COLLECTION_NAME
        document.processed_at = datetime.utcnow()
        if chunks:
            document.title = chunks[0][:200].replace('\n', ' ')
        
        db.commit()
        
        print(f"   Success: {len(chunks)} chunks created")
        return {"status": "success", "chunks": len(chunks)}
        
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)[:1000]
        db.commit()
        print(f"    Failed: {e}")
        return {"status": "failed", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Bulk document ingestion")
    parser.add_argument("path", help="Path to file or directory")
    parser.add_argument("--category", help="Category to tag documents with")
    parser.add_argument("--user-email", default="system@internal", help="User email for ownership")
    
    args = parser.parse_args()
    
    source_path = Path(args.path)
    if not source_path.exists():
        print(f" Path not found: {source_path}")
        sys.exit(1)
    
    # Get or create system user
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.user_email).first()
        if not user:
            from core.security import hash_password
            user = User(
                email=args.user_email,
                username="system",
                hashed_password=hash_password("system_pass")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    finally:
        pass  # Keep session open
    
    # Collect files
    if source_path.is_file():
        files = [source_path]
    else:
        files = []
        for ext in [".pdf", ".docx", ".txt"]:
            files.extend(source_path.glob(f"**/*{ext}"))
    
    if not files:
        print(" No supported files found")
        sys.exit(1)
    
    print(f" Found {len(files)} file(s) to ingest")
    print(f"  Category: {args.category or 'None'}")
    print("=" * 50)
    
    # Process files
    results = {"success": 0, "failed": 0, "skipped": 0}
    
    for file_path in files:
        result = ingest_file(file_path, db, str(user.id), args.category)
        results[result["status"]] = results.get(result["status"], 0) + 1
    
    print("\n" + "=" * 50)
    print(f" Summary:")
    print(f"   Success: {results.get('success', 0)}")
    print(f"   Failed: {results.get('failed', 0)}")
    print(f"    Skipped: {results.get('skipped', 0)}")
    
    db.close()


if __name__ == "__main__":
    main()