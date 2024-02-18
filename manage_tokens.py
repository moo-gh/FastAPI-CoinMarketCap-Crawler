#!/usr/bin/env python3
"""
Script to manage API tokens for the FastAPI Crawler application.
"""
import sys
import secrets
from sqlalchemy.orm import Session
from database import SessionLocal, ApiToken


def create_token(name: str, token: str = None):
    """Create a new API token."""
    db = SessionLocal()
    try:
        if token is None:
            # Generate a secure random token
            token = secrets.token_urlsafe(32)

        # Check if name already exists
        existing = db.query(ApiToken).filter(ApiToken.name == name).first()
        if existing:
            print(f"Error: Token with name '{name}' already exists")
            return False

        # Check if token already exists
        existing_token = db.query(ApiToken).filter(ApiToken.token == token).first()
        if existing_token:
            print(f"Error: Token '{token}' already exists")
            return False

        # Create new token
        api_token = ApiToken(name=name, token=token)
        db.add(api_token)
        db.commit()
        db.refresh(api_token)

        print(f"Created API token:")
        print(f"  Name: {api_token.name}")
        print(f"  Token: {api_token.token}")
        print(f"  Created: {api_token.created_at}")
        return True

    except Exception as e:
        print(f"Error creating token: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_tokens():
    """List all API tokens."""
    db = SessionLocal()
    try:
        tokens = db.query(ApiToken).all()
        if not tokens:
            print("No API tokens found")
            return

        print("API Tokens:")
        print("-" * 50)
        for token in tokens:
            print(f"ID: {token.id}")
            print(f"Name: {token.name}")
            print(f"Token: {token.token}")
            print(f"Created: {token.created_at}")
            print(f"Updated: {token.updated_at}")
            print("-" * 50)

    except Exception as e:
        print(f"Error listing tokens: {e}")
    finally:
        db.close()


def delete_token(name: str):
    """Delete an API token by name."""
    db = SessionLocal()
    try:
        token = db.query(ApiToken).filter(ApiToken.name == name).first()
        if not token:
            print(f"Error: Token with name '{name}' not found")
            return False

        db.delete(token)
        db.commit()
        print(f"Deleted API token: {name}")
        return True

    except Exception as e:
        print(f"Error deleting token: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function for command line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_tokens.py list")
        print("  python manage_tokens.py create <name> [token]")
        print("  python manage_tokens.py delete <name>")
        return

    command = sys.argv[1]

    if command == "list":
        list_tokens()
    elif command == "create":
        if len(sys.argv) < 3:
            print("Error: Name is required for create command")
            return
        name = sys.argv[2]
        token = sys.argv[3] if len(sys.argv) > 3 else None
        create_token(name, token)
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Name is required for delete command")
            return
        name = sys.argv[2]
        delete_token(name)
    else:
        print(f"Error: Unknown command '{command}'")


if __name__ == "__main__":
    main()
