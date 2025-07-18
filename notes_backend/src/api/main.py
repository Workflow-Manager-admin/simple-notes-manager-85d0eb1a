import os
import uuid
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class Note(BaseModel):
    """A representation of a note."""
    id: str = Field(..., description="The unique identifier of the note")
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content (body) of the note")

# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Data required to create a note."""
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content (body) of the note")

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Data allowed when updating a note."""
    title: Optional[str] = Field(None, description="The title of the note")
    content: Optional[str] = Field(None, description="The content (body) of the note")

# In-memory "database" for storing notes
notes_db: Dict[str, Note] = {}

# Use environment variable for app title (default fallback)
APP_TITLE = os.getenv("NOTES_API_TITLE", "Notes API")
APP_DESCRIPTION = "A simple FastAPI backend providing CRUD operations for notes. Data is stored in memory and cleared on restart."
APP_VERSION = "1.0.0"

openapi_tags = [
    {
        "name": "notes",
        "description": "CRUD operations for Notes"
    }
]

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    openapi_tags=openapi_tags
)

# Enable CORS broadly for local/frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """
    Health check endpoint.

    Returns a simple message indicating the service is running.
    """
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED, tags=["notes"], summary="Create a note")
def create_note(note: NoteCreate):
    """
    Create a new note.

    Args:
        note (NoteCreate): The note data to create.

    Returns:
        Note: The created note, including its unique id.
    """
    note_id = str(uuid.uuid4())
    new_note = Note(id=note_id, title=note.title, content=note.content)
    notes_db[note_id] = new_note
    return new_note

# PUBLIC_INTERFACE
@app.get("/notes", response_model=List[Note], tags=["notes"], summary="List all notes")
def list_notes():
    """
    Retrieve a list of all notes.

    Returns:
        List[Note]: All notes currently stored.
    """
    return list(notes_db.values())

# PUBLIC_INTERFACE
@app.get("/notes/{note_id}", response_model=Note, tags=["notes"], summary="Get a single note")
def get_note(
    note_id: str = Path(..., description="The ID of the note to retrieve")
):
    """
    Retrieve a specific note by its ID.

    Args:
        note_id (str): The unique identifier of the note.

    Returns:
        Note: The note with the matching ID.

    Raises:
        HTTPException(404): If no note with the ID exists.
    """
    if note_id not in notes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return notes_db[note_id]

# PUBLIC_INTERFACE
@app.put("/notes/{note_id}", response_model=Note, tags=["notes"], summary="Update a note")
def update_note(
    note_id: str = Path(..., description="The ID of the note to update"),
    note_update: NoteUpdate = ...
):
    """
    Update an existing note.

    Args:
        note_id (str): The unique identifier of the note.
        note_update (NoteUpdate): The fields to update.

    Returns:
        Note: The updated note.

    Raises:
        HTTPException(404): If the note doesn't exist.
    """
    existing_note = notes_db.get(note_id)
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    updated_data = existing_note.dict()
    if note_update.title is not None:
        updated_data["title"] = note_update.title
    if note_update.content is not None:
        updated_data["content"] = note_update.content
    updated_note = Note(**updated_data)
    notes_db[note_id] = updated_note
    return updated_note

# PUBLIC_INTERFACE
@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"], summary="Delete a note")
def delete_note(
    note_id: str = Path(..., description="The ID of the note to delete")
):
    """
    Delete a note by its ID.

    Args:
        note_id (str): The unique identifier of the note.

    Returns:
        None

    Raises:
        HTTPException(404): If the note doesn't exist.
    """
    if note_id not in notes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    del notes_db[note_id]
