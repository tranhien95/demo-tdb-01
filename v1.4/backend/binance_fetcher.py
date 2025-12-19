"""
Binance Live Data Fetcher
Lấy OHLCV data từ Binance với timeframe tùy chọn
"""

import ccxt
from typing import List, Dict, Optional
from datetime import datetime
import time

class BinanceFetcher:
    def __init__(self):
        """Initialize Binance exchange (public API - no API key needed)"""
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Timeframe mapping từ phút sang CCXT format
        self.timeframe_map = {
            '1': '1m',    # 1 phút
            '5': '5m',    # 5 phút
            '15': '15m',  # 15 phút
            '30': '30m',  # 30 phút
            '1h': '1h',   # 1 giờ
            '4h': '4h',   # 4 giờ
            '1d': '1d',   # 1 ngày
            '1w': '1w',   # 1 tuần
        }
        
    def get_available_symbols(self, quote_currency: str = 'USDT') -> List[str]:
        """Lấy danh sách symbol có sẵn (USDT pairs)"""
        try:
            self.exchange.load_markets()
            symbols = [
                s for s in self.exchange.symbols 
                if s.endswith(f'/{quote_currency}')
            ]
            # Return top 50 phổ biến
            popular = [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
                'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT',
                'LTC/USDT', 'BCH/USDT', 'XLM/USDT', 'ATOM/USDT', 'NEAR/USDT',
                'ARB/USDT', 'OP/USDT', 'APE/USDT', 'GALA/USDT', 'SAND/USDT'
            ]
            return popular
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return []
    
    def get_timeframes(self) -> Dict[str, str]:
        """Trả về danh sách timeframe khả dụng"""
        return self.timeframe_map
    
    def _get_timeframe_ms(self, timeframe: str) -> int:
        """Convert timeframe to milliseconds"""
        # Map timeframe to milliseconds
        timeframe_ms_map = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
            '1w': 7 * 24 * 60 * 60 * 1000,
        }
        return timeframe_ms_map.get(timeframe, 15 * 60 * 1000)  # Default to 15m
    
    def _parse_date(self, date_str: str) -> Optional[int]:
        """Parse date string to timestamp (milliseconds)"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # Convert to milliseconds timestamp
                    return int(dt.timestamp() * 1000)
                except ValueError:
                    continue
            
            raise ValueError(f"Unsupported date format: {date_str}")
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            return None
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '15m',
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Lấy OHLCV data từ Binance
        
        Args:
            symbol: 'BTC/USDT', 'ETH/USDT', etc.
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Số lượng candle lấy (max 10000, sẽ fetch nhiều lần nếu > 1000). 
                   Bỏ qua nếu dùng start_date/end_date
            start_date: Ngày bắt đầu (format: 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:MM:SS')
            end_date: Ngày kết thúc (format: 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:MM:SS')
        
        Returns:
            List of OHLCV dicts: {time, open, high, low, close, volume}
        """
        try:
            # Validate timeframe
            tf = self.timeframe_map.get(timeframe, timeframe)
            
            # Parse dates if provided
            start_timestamp = self._parse_date(start_date) if start_date else None
            end_timestamp = self._parse_date(end_date) if end_date else None
            
            # Validate date range
            if start_timestamp and end_timestamp:
                if start_timestamp >= end_timestamp:
                    raise ValueError("start_date must be before end_date")
            
            # Binance API limit is 1000 per request, so fetch multiple times if needed
            max_per_request = 1000
            all_candles = []
            
            # If using date range, calculate estimated candles but don't limit it
            # We'll fetch until we reach end_date
            use_date_range = start_timestamp is not None and end_timestamp is not None
            if use_date_range:
                timeframe_ms = self._get_timeframe_ms(tf)
                date_range_ms = end_timestamp - start_timestamp
                estimated_candles = int(date_range_ms / timeframe_ms) + 1
                # For date range, we don't limit by count, but we set a reasonable max to prevent infinite loops
                # Set limit to estimated candles + buffer, but allow up to 50,000 for large ranges
                limit = min(estimated_candles + 1000, 50000)
            elif not limit:
                limit = 200  # Default limit
            
            print(f"[BinanceFetcher] Request: symbol={symbol}, timeframe={tf}, limit={limit}, start_date={start_date}, end_date={end_date}")
            print(f"[BinanceFetcher] Timestamps: start={start_timestamp} ({datetime.fromtimestamp(start_timestamp/1000) if start_timestamp else None}), end={end_timestamp} ({datetime.fromtimestamp(end_timestamp/1000) if end_timestamp else None})")
            print(f"[BinanceFetcher] use_date_range={use_date_range}, estimated_candles={estimated_candles if use_date_range else 'N/A'}")
            
            if limit <= max_per_request:
                # Single fetch
                if start_timestamp:
                    print(f"[BinanceFetcher] Single fetch: since={start_timestamp} ({datetime.fromtimestamp(start_timestamp/1000)}), limit={limit}")
                    ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, since=start_timestamp, limit=limit)
                    if ohlcv_data:
                        first_time = datetime.fromtimestamp(ohlcv_data[0][0]/1000)
                        last_time = datetime.fromtimestamp(ohlcv_data[-1][0]/1000)
                        print(f"[BinanceFetcher] Got {len(ohlcv_data)} candles. First: {first_time}, Last: {last_time}")
                        
                        # Check if first candle is before start_date (Binance might return data starting from a later point)
                        if first_time > datetime.fromtimestamp(start_timestamp/1000):
                            print(f"[BinanceFetcher] WARNING: First candle ({first_time}) is after start_date ({datetime.fromtimestamp(start_timestamp/1000)}). Binance may not have data from start_date.")
                else:
                    ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)
                
                if not ohlcv_data:
                    return None
                
                # If using date range, filter by both start and end dates
                if use_date_range:
                    # Filter by both start and end dates
                    all_candles = [c for c in ohlcv_data if start_timestamp <= c[0] <= end_timestamp]
                    print(f"[BinanceFetcher] Filtered to {len(all_candles)} candles in date range (from {len(ohlcv_data)} total)")
                elif end_timestamp:
                    all_candles = [c for c in ohlcv_data if c[0] <= end_timestamp]
                    if start_timestamp:
                        all_candles = [c for c in all_candles if c[0] >= start_timestamp]
                else:
                    all_candles = ohlcv_data
            else:
                # Multiple fetches needed
                # Strategy depends on whether we're using date range or limit
                remaining = limit
                since = start_timestamp  # Start from start_date if provided, otherwise None (latest)
                fetched_count = 0
                # Increase max_iterations for date range (may need many batches)
                max_iterations = 100 if use_date_range else 50  # Prevent infinite loops
                iteration = 0
                
                # For date range, we fetch until end_date is reached, not limited by count
                while ((remaining > 0 if not use_date_range else True) and 
                       (fetched_count < limit if not use_date_range else True) and 
                       iteration < max_iterations):
                    iteration += 1
                    fetch_limit = min(remaining, max_per_request) if not use_date_range else max_per_request
                    
                    try:
                        # Fetch from Binance
                        if since is not None:
                            # Fetch from specific timestamp (forward in time)
                            print(f"[BinanceFetcher] Fetching: since={since} ({datetime.fromtimestamp(since/1000)}), limit={fetch_limit}")
                            ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, since=since, limit=fetch_limit)
                            if ohlcv_data:
                                print(f"[BinanceFetcher] Got {len(ohlcv_data)} candles. First: {datetime.fromtimestamp(ohlcv_data[0][0]/1000)}, Last: {datetime.fromtimestamp(ohlcv_data[-1][0]/1000)}")
                        else:
                            # First fetch: get latest data (when not using date range)
                            ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, limit=fetch_limit)
                            ohlcv_data.reverse()  # Reverse to get oldest first
                        
                        if not ohlcv_data or len(ohlcv_data) == 0:
                            print(f"[BinanceFetcher] No more data available. Fetched {fetched_count}/{limit}")
                            break
                        
                        # Filter by date range if specified
                        if start_timestamp or end_timestamp:
                            if start_timestamp:
                                ohlcv_data = [c for c in ohlcv_data if c[0] >= start_timestamp]
                            if end_timestamp:
                                ohlcv_data = [c for c in ohlcv_data if c[0] <= end_timestamp]
                            if not ohlcv_data:
                                print(f"[BinanceFetcher] No candles in date range. Fetched {fetched_count} candles")
                                break
                        
                        # Remove duplicates based on timestamp
                        existing_timestamps = {c[0] for c in all_candles} if all_candles else set()
                        new_candles = [c for c in ohlcv_data if c[0] not in existing_timestamps]
                        if len(new_candles) < len(ohlcv_data):
                            print(f"[BinanceFetcher] Removed {len(ohlcv_data) - len(new_candles)} duplicate candles")
                        
                        # Append new candles (Binance returns oldest first when using 'since')
                        all_candles.extend(new_candles)
                        fetched_count += len(new_candles)
                        
                        # Check if we've reached end_date and should stop
                        if len(new_candles) > 0:
                            newest_timestamp = new_candles[-1][0]
                            timeframe_ms = self._get_timeframe_ms(tf)
                            
                            # Check if newest candle is at or past end_date
                            if end_timestamp and newest_timestamp >= end_timestamp:
                                print(f"[BinanceFetcher] Reached end_date. Fetched {len(all_candles)} candles.")
                                break
                            
                            # Check if next fetch would be beyond end_date
                            next_since = newest_timestamp + timeframe_ms
                            if end_timestamp and next_since > end_timestamp:
                                print(f"[BinanceFetcher] Next candle ({datetime.fromtimestamp(next_since/1000)}) would be beyond end_date ({datetime.fromtimestamp(end_timestamp/1000)}). Stopping.")
                                break
                            
                            # Update since for next iteration
                            since = next_since
                            print(f"[BinanceFetcher] Iteration {iteration}: Fetched {len(new_candles)} candles. Total: {len(all_candles)}. Newest: {datetime.fromtimestamp(newest_timestamp/1000)}, Next since: {datetime.fromtimestamp(since/1000)}")
                        else:
                            break
                        
                        # If using limit (not date range), update remaining
                        if not use_date_range:
                            remaining = limit - fetched_count
                            # If we got less than requested and using limit, check if we should continue
                            if len(new_candles) < fetch_limit:
                                print(f"[BinanceFetcher] Got {len(new_candles)} candles, less than requested {fetch_limit}. Remaining: {remaining}")
                                if remaining > 0 and len(new_candles) > 0:
                                    continue
                                elif len(new_candles) == 0:
                                    print(f"[BinanceFetcher] No more data available from Binance")
                                    break
                                else:
                                    break
                        else:
                            # For date range, continue until we reach end_date
                            if len(new_candles) == 0:
                                print(f"[BinanceFetcher] No more data available from Binance")
                                break
                                
                    except Exception as e:
                        print(f"[BinanceFetcher] Error in multi-fetch iteration {iteration}: {e}")
                        break
                
                # Sort by timestamp to ensure ascending order (oldest first)
                all_candles.sort(key=lambda x: x[0])
                
                # Filter by date range one more time (in case we overshot)
                if start_timestamp:
                    all_candles = [c for c in all_candles if c[0] >= start_timestamp]
                if end_timestamp:
                    all_candles = [c for c in all_candles if c[0] <= end_timestamp]
                
                if use_date_range and len(all_candles) > 0:
                    print(f"[BinanceFetcher] Final result: {len(all_candles)} candles from {datetime.fromtimestamp(all_candles[0][0]/1000)} to {datetime.fromtimestamp(all_candles[-1][0]/1000)}")
                
                # If using limit (not date range), take only requested amount
                if not use_date_range and len(all_candles) > limit:
                    all_candles = all_candles[:limit]
                elif not use_date_range and len(all_candles) < limit:
                    print(f"[BinanceFetcher] Warning: Only fetched {len(all_candles)} candles out of {limit} requested")
            
            if not all_candles:
                return None
            
            # Sort by timestamp to ensure ascending order (oldest first)
            all_candles.sort(key=lambda x: x[0])
            
            # Convert to standard format
            result = []
            for candle in all_candles:
                timestamp = int(candle[0])
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                result.append({
                    'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': int(candle[5])
                })
            
            return result
        
        except ccxt.ExchangeNotAvailable as e:
            print(f"Exchange not available: {e}")
            return None
        except ccxt.ExchangeError as e:
            print(f"Exchange error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching OHLCV: {e}")
            return None
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = '15m',
        limit: int = 200
    ) -> Dict[str, List[Dict]]:
        """Lấy data từ nhiều symbol cùng lúc"""
        result = {}
        for symbol in symbols:
            print(f"Fetching {symbol}...")
            data = self.fetch_ohlcv(symbol, timeframe, limit)
            if data:
                result[symbol] = data
        return result
    
    def validate_symbol(self, symbol: str) -> bool:
        """Kiểm tra symbol có hợp lệ không"""
        try:
            self.exchange.load_markets()
            return symbol in self.exchange.symbols
        except Exception:
            return False
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Lấy thông tin symbol"""
        try:
            self.exchange.load_markets()
            market = self.exchange.market(symbol)
            return {
                'symbol': symbol,
                'id': market.get('id'),
                'base': market.get('base'),
                'quote': market.get('quote'),
                'active': market.get('active'),
                'limits': market.get('limits', {})
            }
        except Exception as e:
            print(f"Error getting symbol info: {e}")
            return {}


# Singleton instance
_fetcher = None

def get_binance_fetcher() -> BinanceFetcher:
    """Get or create singleton BinanceFetcher"""
    global _fetcher
    if _fetcher is None:
        _fetcher = BinanceFetcher()
    return _fetcher
