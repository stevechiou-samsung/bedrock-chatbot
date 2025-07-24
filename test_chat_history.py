#!/usr/bin/env python3
"""
Test script for chat history functionality
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_history import ChatHistoryManager


def test_chat_history_manager():
    """Test the ChatHistoryManager functionality"""
    
    print("🧪 Testing Chat History Manager...")
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ChatHistoryManager(temp_dir)
        
        # Test 1: Save a chat session
        print("\n📝 Test 1: Saving chat session...")
        test_messages = [
            {"role": "assistant", "content": "Hello! How can I help you?"},
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a programming language..."}
        ]
        
        model_config = {
            "model_name": "Claude 4 Sonnet",
            "temperature": 1.0,
            "max_tokens": 4096
        }
        
        session_id = manager.save_chat_session(
            messages=test_messages,
            session_title="Test Python Discussion",
            model_config=model_config
        )
        
        print(f"✅ Session saved with ID: {session_id}")
        
        # Test 2: Load the chat session
        print("\n📂 Test 2: Loading chat session...")
        loaded_session = manager.load_chat_session(session_id)
        
        if loaded_session:
            print(f"✅ Session loaded successfully!")
            print(f"   Title: {loaded_session['title']}")
            print(f"   Messages: {len(loaded_session['messages'])}")
            print(f"   Model: {loaded_session['model_config']['model_name']}")
        else:
            print("❌ Failed to load session")
            return False
        
        # Test 3: List chat sessions
        print("\n📋 Test 3: Listing chat sessions...")
        sessions = manager.list_chat_sessions()
        
        if sessions and len(sessions) == 1:
            print(f"✅ Found {len(sessions)} session(s)")
            print(f"   Session: {sessions[0]['title']}")
        else:
            print(f"❌ Expected 1 session, found {len(sessions)}")
            return False
        
        # Test 4: Update session title
        print("\n✏️ Test 4: Updating session title...")
        success = manager.update_session_title(session_id, "Updated Python Discussion")
        
        if success:
            updated_session = manager.load_chat_session(session_id)
            if updated_session['title'] == "Updated Python Discussion":
                print("✅ Session title updated successfully")
            else:
                print("❌ Session title not updated properly")
                return False
        else:
            print("❌ Failed to update session title")
            return False
        
        # Test 5: Export session as markdown
        print("\n📄 Test 5: Exporting session as markdown...")
        markdown = manager.export_session_markdown(session_id)
        
        if markdown and "Updated Python Discussion" in markdown:
            print("✅ Session exported as markdown successfully")
            print(f"   Length: {len(markdown)} characters")
        else:
            print("❌ Failed to export session as markdown")
            return False
        
        # Test 6: Get session statistics
        print("\n📊 Test 6: Getting session statistics...")
        stats = manager.get_session_stats()
        
        expected_stats = {
            "total_sessions": 1,
            "total_messages": 3,
        }
        
        if (stats["total_sessions"] == expected_stats["total_sessions"] and 
            stats["total_messages"] == expected_stats["total_messages"]):
            print("✅ Session statistics correct")
            print(f"   Total sessions: {stats['total_sessions']}")
            print(f"   Total messages: {stats['total_messages']}")
        else:
            print("❌ Session statistics incorrect")
            print(f"   Expected: {expected_stats}")
            print(f"   Got: {stats}")
            return False
        
        # Test 7: Delete session
        print("\n🗑️ Test 7: Deleting session...")
        delete_success = manager.delete_chat_session(session_id)
        
        if delete_success:
            # Verify deletion
            deleted_session = manager.load_chat_session(session_id)
            if deleted_session is None:
                print("✅ Session deleted successfully")
            else:
                print("❌ Session still exists after deletion")
                return False
        else:
            print("❌ Failed to delete session")
            return False
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting Chat History Tests...")
    print("=" * 50)
    
    try:
        success = test_chat_history_manager()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All tests passed! Chat history functionality is working correctly.")
        else:
            print("❌ Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()