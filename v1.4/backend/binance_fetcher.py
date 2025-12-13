"""
Binance Live Data Fetcher
Lấy OHLCV data từ Binance với timeframe tùy chọn
"""

import ccxt
from typing import List, Dict, Optional
from datetime import datetime

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
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '15m',
        limit: int = 200
    ) -> Optional[List[Dict]]:
        """
        Lấy OHLCV data từ Binance
        
        Args:
            symbol: 'BTC/USDT', 'ETH/USDT', etc.
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Số lượng candle lấy (max 10000, sẽ fetch nhiều lần nếu > 1000)
        
        Returns:
            List of OHLCV dicts: {time, open, high, low, close, volume}
        """
        try:
            # Validate timeframe
            tf = self.timeframe_map.get(timeframe, timeframe)
            
            # Binance API limit is 1000 per request, so fetch multiple times if needed
            max_per_request = 1000
            all_candles = []
            
            if limit <= max_per_request:
                # Single fetch
                ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)
                if not ohlcv_data:
                    return None
                all_candles = ohlcv_data
            else:
                # Multiple fetches needed
                # Strategy: Fetch in chunks, going back in time
                # Binance returns data in chronological order (oldest first) when using 'since'
                remaining = limit
                since = None  # Start from latest (None = most recent)
                fetched_count = 0
                max_iterations = 10  # Prevent infinite loops
                iteration = 0
                
                while remaining > 0 and fetched_count < limit and iteration < max_iterations:
                    iteration += 1
                    fetch_limit = min(remaining, max_per_request)
                    
                    try:
                        # Fetch from Binance
                        if since:
                            # Fetch older data (before 'since' timestamp)
                            ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, since=since, limit=fetch_limit)
                        else:
                            # First fetch: get latest data
                            ohlcv_data = self.exchange.fetch_ohlcv(symbol, tf, limit=fetch_limit)
                        
                        if not ohlcv_data or len(ohlcv_data) == 0:
                            print(f"[BinanceFetcher] No more data available. Fetched {fetched_count}/{limit}")
                            break
                        
                        # Binance returns oldest first when using 'since', newest first when not
                        # We want oldest first, so prepend when using 'since', append when not
                        if since:
                            # Prepend older data (already oldest first)
                            # Remove duplicates based on timestamp to avoid overlap
                            existing_timestamps = {c[0] for c in all_candles} if all_candles else set()
                            new_candles = [c for c in ohlcv_data if c[0] not in existing_timestamps]
                            if len(new_candles) < len(ohlcv_data):
                                print(f"[BinanceFetcher] Removed {len(ohlcv_data) - len(new_candles)} duplicate candles")
                            all_candles = new_candles + all_candles
                            ohlcv_data = new_candles  # Update for count calculation
                        else:
                            # First fetch: reverse to get oldest first, then prepend
                            ohlcv_data.reverse()
                            all_candles = ohlcv_data + all_candles
                        
                        fetched_count += len(ohlcv_data)
                        remaining = limit - fetched_count
                        
                        # Get oldest timestamp for next fetch (go back in time)
                        if len(all_candles) > 0:
                            oldest_timestamp = all_candles[0][0]  # First item is oldest
                            # Use oldest_timestamp - 1ms to fetch next batch
                            # This ensures we don't miss any candles (duplicates will be removed)
                            since = oldest_timestamp - 1
                            
                            print(f"[BinanceFetcher] Iteration {iteration}: Fetched {len(ohlcv_data)} candles. Total: {len(all_candles)}. Oldest timestamp: {oldest_timestamp}, Next since: {since}")
                        else:
                            break
                        
                        # If we got less than requested, check if we need to continue
                        if len(ohlcv_data) < fetch_limit:
                            print(f"[BinanceFetcher] Got {len(ohlcv_data)} candles, less than requested {fetch_limit}. Remaining: {remaining}")
                            # If we still need more and got some data, continue
                            if remaining > 0 and len(ohlcv_data) > 0:
                                # Continue fetching if we got some data but not enough
                                continue
                            elif len(ohlcv_data) == 0:
                                # No more data available
                                print(f"[BinanceFetcher] No more data available from Binance")
                                break
                            else:
                                # We got all available data
                                break
                                
                    except Exception as e:
                        print(f"[BinanceFetcher] Error in multi-fetch iteration {iteration}: {e}")
                        break
                
                # Take only requested amount (oldest N candles)
                if len(all_candles) > limit:
                    all_candles = all_candles[:limit]
                elif len(all_candles) < limit:
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
