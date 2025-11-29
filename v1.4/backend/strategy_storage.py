"""
Strategy Storage
Save and load strategies to/from JSON files
"""

import json
import os
from typing import List, Optional
from datetime import datetime
from strategy_models import Strategy, StrategyListItem
from pathlib import Path


class StrategyStorage:
    """Handle strategy persistence"""
    
    STORAGE_DIR = Path(__file__).parent / "saved_strategies"
    
    def __init__(self):
        # Create storage directory if not exists
        self.STORAGE_DIR.mkdir(exist_ok=True)
    
    def save_strategy(self, strategy: Strategy) -> bool:
        """
        Save strategy to JSON file
        
        Returns:
            True if successful
        """
        try:
            # Set timestamps
            now = datetime.now()
            if not strategy.created_at:
                strategy.created_at = now
            strategy.updated_at = now
            
            # Generate filename from strategy name
            filename = self._sanitize_filename(strategy.name) + ".json"
            filepath = self.STORAGE_DIR / filename
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(strategy.dict(), f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving strategy: {e}")
            return False
    
    def load_strategy(self, name: str) -> Optional[Strategy]:
        """
        Load strategy from JSON file
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy object or None if not found
        """
        try:
            filename = self._sanitize_filename(name) + ".json"
            filepath = self.STORAGE_DIR / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Strategy(**data)
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return None
    
    def list_strategies(self) -> List[StrategyListItem]:
        """
        List all saved strategies
        
        Returns:
            List of strategy metadata
        """
        strategies = []
        
        try:
            for filepath in self.STORAGE_DIR.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    strategies.append(StrategyListItem(
                        name=data['name'],
                        description=data.get('description'),
                        indicator_count=len(data.get('indicators', [])),
                        created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
                    ))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
        except Exception as e:
            print(f"Error listing strategies: {e}")
        
        # Sort by updated_at desc
        strategies.sort(key=lambda x: x.updated_at, reverse=True)
        return strategies
    
    def delete_strategy(self, name: str) -> bool:
        """
        Delete a strategy
        
        Args:
            name: Strategy name
            
        Returns:
            True if successful
        """
        try:
            filename = self._sanitize_filename(name) + ".json"
            filepath = self.STORAGE_DIR / filename
            
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting strategy: {e}")
            return False
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Convert strategy name to safe filename
        
        Args:
            name: Strategy name
            
        Returns:
            Safe filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length
        return name[:100]


# Global instance
strategy_storage = StrategyStorage()
