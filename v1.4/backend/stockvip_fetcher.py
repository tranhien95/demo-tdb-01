"""
StockVIP Fetcher (Alternative to vnstock)
Lấy OHLCV data từ thị trường chứng khoán Việt Nam
Sử dụng thư viện stockvip
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

try:
    from stockvip import StockVIP
    STOCKVIP_AVAILABLE = True
except ImportError:
    STOCKVIP_AVAILABLE = False
    print("⚠️ stockvip chưa được cài đặt. Chạy: pip install stockvip")


class StockVIPFetcher:
    """Fetcher cho chứng khoán Việt Nam sử dụng stockvip"""
    
    def __init__(self):
        """Initialize StockVIP Fetcher"""
        if not STOCKVIP_AVAILABLE:
            raise ImportError("stockvip library is not installed. Run: pip install stockvip")
        
        self.client = StockVIP()
        
        # Timeframe mapping cho chứng khoán VN
        # stockvip hỗ trợ: '1', '5', '15', '30', '60', 'D', 'W', 'M'
        self.timeframe_map = {
            '1': '1',      # 1 phút
            '5': '5',      # 5 phút
            '15': '15',    # 15 phút
            '30': '30',    # 30 phút
            '1h': '60',    # 1 giờ
            '1d': 'D',     # 1 ngày
            '1w': 'W',     # 1 tuần
            '1M': 'M',     # 1 tháng
        }
        
        # Danh sách cổ phiếu phổ biến (fallback)
        self._popular_stocks = None
    
    def get_available_symbols(self) -> List[str]:
        """Lấy danh sách mã cổ phiếu phổ biến"""
        # Fallback list (always available)
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
        ]
        
        try:
            if self._popular_stocks is None:
                # Try to get from stockvip
                try:
                    # stockvip có thể có method để lấy danh sách
                    # Tùy vào API của stockvip, có thể cần điều chỉnh
                    # For now, use fallback
                    self._popular_stocks = fallback_symbols
                except Exception as e:
                    print(f"⚠️ Error fetching symbols from stockvip: {e}")
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
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        try:
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
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
        Lấy OHLCV data từ chứng khoán Việt Nam sử dụng stockvip
        
        Args:
            symbol: Mã cổ phiếu (VD: 'VCB', 'VIC', 'HPG')
            timeframe: '1', '5', '15', '30', '60', 'D', 'W', 'M'
            limit: Số lượng candle (chỉ dùng khi không có start_date/end_date)
            start_date: Ngày bắt đầu (format: 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:MM:SS')
            end_date: Ngày kết thúc (format: 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:MM:SS')
        
        Returns:
            List of OHLCV dicts: {time, open, high, low, close, volume}
        """
        try:
            if not STOCKVIP_AVAILABLE:
                raise ImportError("stockvip library is not installed")
            
            # Convert timeframe
            tf = self.timeframe_map.get(timeframe, timeframe)
            
            # Determine date range
            if start_date and end_date:
                start_dt = self._parse_date(start_date)
                end_dt = self._parse_date(end_date)
                
                if not start_dt or not end_dt:
                    raise ValueError("Invalid date format")
                
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
            elif limit:
                end_dt = datetime.now()
                if tf in ['1', '5', '15', '30', '60']:
                    minutes_per_candle = int(tf) if tf.isdigit() else 60
                    start_dt = end_dt - timedelta(minutes=limit * minutes_per_candle)
                elif tf == 'D':
                    start_dt = end_dt - timedelta(days=limit)
                elif tf == 'W':
                    start_dt = end_dt - timedelta(weeks=limit)
                elif tf == 'M':
                    start_dt = end_dt - timedelta(days=limit * 30)
                else:
                    start_dt = end_dt - timedelta(days=limit)
                
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
            else:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=200)
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
            
            # Fetch data from stockvip
            print(f"Fetching {symbol} from {start_str} to {end_str}, timeframe={tf} using stockvip")
            
            # Note: stockvip API có thể khác vnstock
            # Cần kiểm tra documentation của stockvip để biết cách gọi đúng
            # Ví dụ: df = self.client.get_historical_data(symbol, start_str, end_str, tf)
            # Hoặc: df = self.client.get_ohlcv(symbol, tf, start_str, end_str)
            
            # Placeholder - cần điều chỉnh theo stockvip API thực tế
            # df = self.client.get_historical_data(symbol, start_str, end_str, resolution=tf)
            
            # For now, return None to indicate not implemented
            # User can implement based on stockvip documentation
            print("⚠️ stockvip fetcher chưa được implement đầy đủ. Cần kiểm tra stockvip documentation.")
            return None
            
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol} using stockvip: {e}")
            import traceback
            traceback.print_exc()
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
            # Try to get info from stockvip
            # Placeholder - cần implement theo stockvip API
            return {
                'symbol': symbol.upper(),
                'name': '',
                'exchange': '',
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

def get_stockvip_fetcher() -> StockVIPFetcher:
    """Get singleton instance of StockVIPFetcher"""
    global _fetcher
    if _fetcher is None:
        try:
            _fetcher = StockVIPFetcher()
        except ImportError as e:
            print(f"⚠️ Cannot initialize StockVIPFetcher: {e}")
            print("💡 Install stockvip: pip install stockvip")
            raise
    return _fetcher

