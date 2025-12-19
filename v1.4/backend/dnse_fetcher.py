"""
DNSE Fetcher (Alternative data source for Vietnam Stock Market)
DNSE có thể là:
1. DNSE - một sàn giao dịch hoặc platform
2. Hoặc data source khác

Có thể sử dụng web scraping hoặc API công khai
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
import pandas as pd

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance chưa được cài đặt. Chạy: pip install yfinance")


class DNSEFetcher:
    """Fetcher cho chứng khoán Việt Nam sử dụng các nguồn công khai"""
    
    def __init__(self):
        """Initialize DNSE Fetcher"""
        # Timeframe mapping
        self.timeframe_map = {
            '1': '1m',      # 1 phút
            '5': '5m',      # 5 phút
            '15': '15m',    # 15 phút
            '30': '30m',    # 30 phút
            '1h': '1h',     # 1 giờ
            '1d': '1d',     # 1 ngày
            '1w': '1wk',    # 1 tuần
            '1M': '1mo',    # 1 tháng
        }
        
        # Danh sách cổ phiếu phổ biến
        self._popular_stocks = None
    
    def get_available_symbols(self) -> List[str]:
        """Lấy danh sách mã cổ phiếu phổ biến"""
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
        ]
        
        try:
            if self._popular_stocks is None:
                # Try to fetch from public sources
                # For now, use fallback
                self._popular_stocks = fallback_symbols
            
            return self._popular_stocks if self._popular_stocks else fallback_symbols
        except Exception as e:
            print(f"⚠️ Error getting symbols: {e}")
            return fallback_symbols
    
    def get_timeframes(self) -> Dict[str, str]:
        """Trả về danh sách timeframe khả dụng"""
        return {
            '1': '1 phút',
            '5': '5 phút',
            '15': '15 phút',
            '30': '30 phút',
            '1h': '1 giờ',
            '1d': '1 ngày',
            '1w': '1 tuần',
            '1M': '1 tháng'
        }
    
    def fetch_ohlcv_yfinance(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Lấy OHLCV data từ yfinance (hỗ trợ một số mã VN)
        Note: yfinance có thể không hỗ trợ đầy đủ mã VN
        """
        if not YFINANCE_AVAILABLE:
            print("⚠️ yfinance chưa được cài đặt. Chạy: pip install yfinance")
            return None
        
        try:
            # Convert timeframe
            tf = self.timeframe_map.get(timeframe, '1d')
            
            # Determine date range
            if start_date and end_date:
                try:
                    start_dt = datetime.strptime(start_date.split()[0], '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date.split()[0], '%Y-%m-%d')
                except:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            elif limit:
                end_dt = datetime.now()
                if tf in ['1m', '5m', '15m', '30m', '1h']:
                    start_dt = end_dt - timedelta(days=min(limit, 60))  # Limit to 60 days for intraday
                elif tf == '1d':
                    start_dt = end_dt - timedelta(days=limit)
                elif tf == '1wk':
                    start_dt = end_dt - timedelta(weeks=limit)
                elif tf == '1mo':
                    start_dt = end_dt - timedelta(days=limit * 30)
                else:
                    start_dt = end_dt - timedelta(days=limit)
            else:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=200)
            
            # Try multiple symbol formats
            symbol_variants = [
                f"{symbol}.VN",  # Try with .VN suffix first
                symbol,           # Try without suffix
                f"{symbol}.VX",   # Alternative suffix
            ]
            
            df = None
            used_symbol = None
            
            for sym_variant in symbol_variants:
                try:
                    print(f"🔍 Trying yfinance symbol: {sym_variant}")
                    ticker = yf.Ticker(sym_variant)
                    
                    # For daily and above, use period instead of start/end for better compatibility
                    if tf in ['1d', '1wk', '1mo']:
                        # Calculate period
                        days_diff = (end_dt - start_dt).days
                        if days_diff <= 5:
                            period = '5d'
                        elif days_diff <= 30:
                            period = '1mo'
                        elif days_diff <= 90:
                            period = '3mo'
                        elif days_diff <= 180:
                            period = '6mo'
                        elif days_diff <= 365:
                            period = '1y'
                        else:
                            period = '2y'
                        
                        df = ticker.history(period=period, interval=tf)
                    else:
                        # For intraday, use start/end
                        df = ticker.history(start=start_dt, end=end_dt, interval=tf)
                    
                    if df is not None and not df.empty:
                        used_symbol = sym_variant
                        print(f"✅ Found data for {sym_variant}")
                        break
                except Exception as e:
                    print(f"⚠️ Error with {sym_variant}: {e}")
                    continue
            
            if df is None or df.empty:
                print(f"❌ No data found for {symbol} with any symbol variant")
                return None
            
            # Filter by date range if needed
            if start_date and end_date:
                df = df[(df.index >= pd.Timestamp(start_dt)) & (df.index <= pd.Timestamp(end_dt))]
            
            # Limit number of rows if needed
            if limit and len(df) > limit:
                df = df.tail(limit)
            
            if df.empty:
                return None
            
            # Convert to list of dicts
            ohlcv_data = []
            for idx, row in df.iterrows():
                timestamp = idx
                if isinstance(idx, pd.Timestamp):
                    timestamp_str = idx.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(idx)
                
                ohlcv_data.append({
                    'time': timestamp_str,
                    'open': float(row['Open']) if 'Open' in row else float(row['open']) if 'open' in row else 0.0,
                    'high': float(row['High']) if 'High' in row else float(row['high']) if 'high' in row else 0.0,
                    'low': float(row['Low']) if 'Low' in row else float(row['low']) if 'low' in row else 0.0,
                    'close': float(row['Close']) if 'Close' in row else float(row['close']) if 'close' in row else 0.0,
                    'volume': float(row['Volume']) if 'Volume' in row else float(row['volume']) if 'volume' in row else 0.0
                })
            
            print(f"✅ Successfully fetched {len(ohlcv_data)} candles for {used_symbol}")
            return ohlcv_data
            
        except Exception as e:
            print(f"⚠️ Error fetching from yfinance for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_ohlcv_web_scraping(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Lấy OHLCV data từ web scraping (cafef, vndirect, etc.)
        Note: Cần implement theo từng website cụ thể
        """
        try:
            # Placeholder - cần implement web scraping logic
            # Có thể scrape từ:
            # - cafef.vn
            # - vndirect.com.vn
            # - dnse.com.vn (nếu có)
            # - vcbs.com.vn
            # etc.
            
            print(f"⚠️ Web scraping chưa được implement cho {symbol}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error web scraping for {symbol}: {e}")
            return None
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Lấy OHLCV data - thử nhiều nguồn
        """
        print(f"📊 Fetching OHLCV for {symbol}, timeframe={timeframe}, limit={limit}, start={start_date}, end={end_date}")
        
        # Try yfinance first
        if YFINANCE_AVAILABLE:
            print("🔍 Trying yfinance...")
            data = self.fetch_ohlcv_yfinance(symbol, timeframe, limit, start_date, end_date)
            if data and len(data) > 0:
                print(f"✅ Successfully fetched {len(data)} candles from yfinance")
                return data
            else:
                print("⚠️ yfinance returned no data")
        else:
            print("⚠️ yfinance not available. Install with: pip install yfinance")
        
        # Try web scraping (not implemented yet)
        print("🔍 Trying web scraping...")
        data = self.fetch_ohlcv_web_scraping(symbol, timeframe, limit, start_date, end_date)
        if data and len(data) > 0:
            print(f"✅ Successfully fetched {len(data)} candles from web scraping")
            return data
        
        print(f"❌ No data found for {symbol} from any source")
        return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Kiểm tra mã cổ phiếu có hợp lệ không"""
        try:
            symbols = self.get_available_symbols()
            return symbol.upper() in [s.upper() for s in symbols]
        except Exception:
            return False
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Lấy thông tin mã cổ phiếu"""
        try:
            return {
                'symbol': symbol.upper(),
                'name': '',
                'exchange': 'HOSE/HNX',
                'sector': ''
            }
        except Exception as e:
            print(f"Error getting symbol info: {e}")
            return {
                'symbol': symbol.upper(),
                'name': '',
                'exchange': '',
                'sector': ''
            }


# Singleton instance
_fetcher = None

def get_dnse_fetcher() -> DNSEFetcher:
    """Get singleton instance of DNSEFetcher"""
    global _fetcher
    if _fetcher is None:
        _fetcher = DNSEFetcher()
    return _fetcher

