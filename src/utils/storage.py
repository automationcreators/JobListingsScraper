#!/usr/bin/env python3
"""
Persistent Storage System for Job Classification Data
Saves processed data to disk so it survives server restarts
"""

import json
import pickle
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class PersistentStorage:
    """File-based storage system for session data"""
    
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate directories for different data types
        self.sessions_dir = self.storage_dir / "sessions"
        self.dataframes_dir = self.storage_dir / "dataframes"
        self.metadata_dir = self.storage_dir / "metadata"
        
        for dir_path in [self.sessions_dir, self.dataframes_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save complete session data to disk"""
        try:
            # Save metadata (non-DataFrame data)
            metadata = {}
            dataframes = {}
            
            for key, value in session_data.items():
                if isinstance(value, pd.DataFrame):
                    # Save DataFrames separately as pickle for efficiency
                    df_path = self.dataframes_dir / f"{session_id}_{key}.pkl"
                    value.to_pickle(df_path)
                    dataframes[key] = str(df_path)
                else:
                    metadata[key] = value
            
            # Save metadata as JSON
            metadata_path = self.metadata_dir / f"{session_id}.json"
            with open(metadata_path, 'w') as f:
                json.dump({
                    'metadata': metadata,
                    'dataframes': dataframes,
                    'saved_at': datetime.now().isoformat(),
                    'session_id': session_id
                }, f, indent=2)
            
            logging.info(f"Session {session_id} saved successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save session {session_id}: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load complete session data from disk"""
        try:
            metadata_path = self.metadata_dir / f"{session_id}.json"
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                saved_data = json.load(f)
            
            # Reconstruct session data
            session_data = saved_data['metadata'].copy()
            
            # Load DataFrames
            for key, df_path in saved_data['dataframes'].items():
                df_file = Path(df_path)
                if df_file.exists():
                    session_data[key] = pd.read_pickle(df_file)
                else:
                    logging.warning(f"DataFrame file not found: {df_path}")
            
            logging.info(f"Session {session_id} loaded successfully")
            return session_data
            
        except Exception as e:
            logging.error(f"Failed to load session {session_id}: {str(e)}")
            return None
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all available sessions with metadata"""
        sessions = {}
        
        try:
            for metadata_file in self.metadata_dir.glob("*.json"):
                session_id = metadata_file.stem
                
                with open(metadata_file, 'r') as f:
                    saved_data = json.load(f)
                
                sessions[session_id] = {
                    'session_id': session_id,
                    'filename': saved_data['metadata'].get('filename', 'unknown'),
                    'saved_at': saved_data.get('saved_at', 'unknown'),
                    'has_original': 'original_df' in saved_data['dataframes'],
                    'has_processed': 'processed_df' in saved_data['dataframes'],
                }
                
        except Exception as e:
            logging.error(f"Failed to list sessions: {str(e)}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its associated files"""
        try:
            deleted_files = 0
            
            # Delete metadata file
            metadata_path = self.metadata_dir / f"{session_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()
                deleted_files += 1
            
            # Delete associated DataFrame files
            for df_file in self.dataframes_dir.glob(f"{session_id}_*.pkl"):
                df_file.unlink()
                deleted_files += 1
            
            logging.info(f"Session {session_id} deleted ({deleted_files} files)")
            return deleted_files > 0
            
        except Exception as e:
            logging.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a session without loading the data"""
        try:
            metadata_path = self.metadata_dir / f"{session_id}.json"
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                saved_data = json.load(f)
            
            # Get DataFrame info without loading
            df_info = {}
            for key, df_path in saved_data['dataframes'].items():
                df_file = Path(df_path)
                if df_file.exists():
                    # Load just the DataFrame info (shape, columns)
                    try:
                        df = pd.read_pickle(df_file)
                        df_info[key] = {
                            'shape': df.shape,
                            'columns': list(df.columns),
                            'file_size': df_file.stat().st_size
                        }
                    except:
                        df_info[key] = {'error': 'Could not read DataFrame'}
            
            return {
                'session_id': session_id,
                'metadata': saved_data['metadata'],
                'dataframes_info': df_info,
                'saved_at': saved_data.get('saved_at'),
                'total_files': len(saved_data['dataframes'])
            }
            
        except Exception as e:
            logging.error(f"Failed to get session info {session_id}: {str(e)}")
            return None
    
    def cleanup_old_sessions(self, days_old: int = 7) -> int:
        """Clean up sessions older than specified days"""
        try:
            deleted_count = 0
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for metadata_file in self.metadata_dir.glob("*.json"):
                if metadata_file.stat().st_mtime < cutoff_date:
                    session_id = metadata_file.stem
                    if self.delete_session(session_id):
                        deleted_count += 1
            
            logging.info(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logging.error(f"Failed to cleanup old sessions: {str(e)}")
            return 0

# Global storage instance
storage = PersistentStorage()