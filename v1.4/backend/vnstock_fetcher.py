"""
Vietnam Stock Market Fetcher
Lấy OHLCV data từ thị trường chứng khoán Việt Nam (HOSE, HNX, UPCOM)
Sử dụng thư viện vnstock
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import os
import sys
import pandas as pd

# Set UTF-8 encoding for Windows console to handle vnstock Unicode characters
# This must be set BEFORE any imports that might print Unicode characters
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Try to set stdout encoding to UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass

# Create a safe stdout wrapper that handles encoding errors
class SafeStdout:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
    
    def write(self, text):
        try:
            self.original_stdout.write(text)
        except UnicodeEncodeError:
            # Silently ignore encoding errors during import
            try:
                # Try to encode as ASCII with replacement
                safe_text = text.encode('ascii', 'replace').decode('ascii')
                self.original_stdout.write(safe_text)
            except:
                pass  # Ignore if still fails
    
    def flush(self):
        try:
            self.original_stdout.flush()
        except:
            pass
    
    def __getattr__(self, name):
        return getattr(self.original_stdout, name)

# Try to import vnstock with encoding error handling
VNSTOCK_AVAILABLE = False
# Global variables for vnstock API (old functions or new classes)
stock_historical_data = None
listing_companies = None
Quote = None
Company = None
Listing = None
Trading = None

try:
    # Temporarily replace stdout and stderr during import
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    safe_stdout = SafeStdout(original_stdout)
    safe_stderr = SafeStdout(original_stderr)
    
    sys.stdout = safe_stdout
    sys.stderr = safe_stderr
    
    try:
        # Import vnstock - this may trigger UnicodeEncodeError in vnai dependency
        # The error is usually in a print statement during module initialization,
        # not in the actual import, so we catch it and continue
        # Try new API first (vnstock 3.x uses classes)
        try:
            from vnstock import Quote, Company, Listing, Trading
            # New API available
            stock_historical_data = None  # Will use Quote class instead
            listing_companies = None  # Will use Company or Listing class instead
            VNSTOCK_AVAILABLE = True
        except ImportError:
            # Try old API (vnstock 2.x uses functions)
            from vnstock import stock_historical_data, listing_companies
            Quote = None
            Company = None
            Listing = None
            Trading = None
            VNSTOCK_AVAILABLE = True
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        # Encoding error occurred during import, but the module might still be loaded
        # Check if vnstock module is in sys.modules (import succeeded despite error)
        if 'vnstock' in sys.modules:
            try:
                # The module is already imported, just get the classes/functions
                vnstock_module = sys.modules['vnstock']
                # Try new API first (vnstock 3.x uses classes)
                if hasattr(vnstock_module, 'Quote') and hasattr(vnstock_module, 'Company'):
                    Quote = vnstock_module.Quote
                    Company = vnstock_module.Company
                    Listing = getattr(vnstock_module, 'Listing', None)
                    Trading = getattr(vnstock_module, 'Trading', None)
                    stock_historical_data = None
                    listing_companies = None
                    VNSTOCK_AVAILABLE = True
                elif hasattr(vnstock_module, 'stock_historical_data'):
                    # Old API (vnstock 2.x uses functions)
                    stock_historical_data = vnstock_module.stock_historical_data
                    listing_companies = vnstock_module.listing_companies
                    Quote = None
                    Company = None
                    Listing = None
                    Trading = None
                    VNSTOCK_AVAILABLE = True
                else:
                    VNSTOCK_AVAILABLE = False
            except (AttributeError, ImportError):
                VNSTOCK_AVAILABLE = False
        else:
            VNSTOCK_AVAILABLE = False
    finally:
        # Always restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
except (UnicodeEncodeError, UnicodeDecodeError):
    # Encoding error at outer level - module might still be loaded
    if 'original_stdout' in locals():
        sys.stdout = original_stdout
    if 'original_stderr' in locals():
        sys.stderr = original_stderr
    
    # Check if vnstock module is in sys.modules
    if 'vnstock' in sys.modules:
        try:
            vnstock_module = sys.modules['vnstock']
            if hasattr(vnstock_module, 'Quote') and hasattr(vnstock_module, 'Company'):
                VNSTOCK_AVAILABLE = True
            elif hasattr(vnstock_module, 'stock_historical_data'):
                VNSTOCK_AVAILABLE = True
            else:
                VNSTOCK_AVAILABLE = False
        except:
            VNSTOCK_AVAILABLE = False
    else:
        VNSTOCK_AVAILABLE = False
    
    if not VNSTOCK_AVAILABLE:
        print("⚠️ vnstock encoding error (Windows console issue). Library is installed but may have display issues.")
    
except ImportError:
    # Import failed - but check if module was actually loaded
    if 'vnstock' in sys.modules:
        vnstock_module = sys.modules['vnstock']
        if hasattr(vnstock_module, 'Quote') and hasattr(vnstock_module, 'Company'):
            VNSTOCK_AVAILABLE = True
        elif hasattr(vnstock_module, 'stock_historical_data'):
            VNSTOCK_AVAILABLE = True
        else:
            VNSTOCK_AVAILABLE = False
    else:
        VNSTOCK_AVAILABLE = False
    
    if not VNSTOCK_AVAILABLE:
        print("⚠️ vnstock chưa được cài đặt. Chạy: pip install vnstock")
    
except Exception as e:
    # Other errors during import - but check if module was actually loaded
    # Restore stdout/stderr if they were changed
    if 'original_stdout' in locals():
        sys.stdout = original_stdout
    if 'original_stderr' in locals():
        sys.stderr = original_stderr
    
    # Check if vnstock module is in sys.modules (import succeeded despite error)
    if 'vnstock' in sys.modules:
        try:
            vnstock_module = sys.modules['vnstock']
            # Try to get functions/classes from the module
            # vnstock 3.x uses classes: Quote, Company, Listing, etc.
            if hasattr(vnstock_module, 'Quote') and hasattr(vnstock_module, 'Company'):
                # New API - use classes
                Quote = vnstock_module.Quote
                Company = vnstock_module.Company
                Listing = getattr(vnstock_module, 'Listing', None)
                Trading = getattr(vnstock_module, 'Trading', None)
                stock_historical_data = None
                listing_companies = None
                VNSTOCK_AVAILABLE = True
            elif hasattr(vnstock_module, 'stock_historical_data'):
                # Old API - use functions
                stock_historical_data = vnstock_module.stock_historical_data
                listing_companies = vnstock_module.listing_companies
                Quote = None
                Company = None
                Listing = None
                Trading = None
                VNSTOCK_AVAILABLE = True
            else:
                VNSTOCK_AVAILABLE = False
        except:
            VNSTOCK_AVAILABLE = False
    else:
        VNSTOCK_AVAILABLE = False
    
    if not VNSTOCK_AVAILABLE:
        print("⚠️ vnstock error during import. Using fallback mode.")

# Final check: if vnstock module is loaded, mark as available
if not VNSTOCK_AVAILABLE and 'vnstock' in sys.modules:
    try:
        vnstock_module = sys.modules['vnstock']
        if hasattr(vnstock_module, 'Quote') and hasattr(vnstock_module, 'Company'):
            VNSTOCK_AVAILABLE = True
        elif hasattr(vnstock_module, 'stock_historical_data'):
            VNSTOCK_AVAILABLE = True
    except:
        pass


class VNStockFetcher:
    """Fetcher cho chứng khoán Việt Nam"""
    
    def __init__(self):
        """Initialize Vietnam Stock Fetcher"""
        if not VNSTOCK_AVAILABLE:
            raise ImportError("vnstock library is not installed. Run: pip install vnstock")
        
        # Timeframe mapping cho chứng khoán VN
        # vnstock hỗ trợ: '1', '5', '15', '30', '60', 'D', 'W', 'M'
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
        
        # Danh sách cổ phiếu phổ biến
        self._popular_stocks = None
        
        # Danh sách phái sinh phổ biến
        self._derivatives_symbols = None
    
    def get_derivatives_symbols(self) -> List[str]:
        """Lấy danh sách mã phái sinh phổ biến"""
        # Fallback list for derivatives
        fallback_derivatives = [
            'VN30F1M', 'VN30F2M', 'VN30F3M',  # VN30 Futures - tháng 1, 2, 3
            'HNX30F1M', 'HNX30F2M', 'HNX30F3M',  # HNX30 Futures
            'VN30F2401', 'VN30F2402', 'VN30F2403',  # VN30 Futures với mã đầy đủ
            'VN30F2501', 'VN30F2502', 'VN30F2503',
        ]
        
        try:
            if self._derivatives_symbols is None:
                # Try to get from vnstock if available
                # For now, use fallback list
                self._derivatives_symbols = fallback_derivatives
            
            return self._derivatives_symbols if self._derivatives_symbols else fallback_derivatives
        except Exception as e:
            print(f"⚠️ Error getting derivatives symbols: {e}")
            return fallback_derivatives
    
    def get_available_symbols(self) -> List[str]:
        """Lấy danh sách mã cổ phiếu phổ biến"""
        # Fallback list (always available)
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB',
            'DXG', 'NVL', 'KDH', 'BCM', 'HDG', 'PDR', 'QCG',
            'VHC', 'FCM', 'DGC', 'DCM', 'VCF', 'VCS', 'VTO', 'VPI'
        ]
        
        try:
            if self._popular_stocks is None:
                # Lấy danh sách từ vnstock
                try:
                    # Try new API first (vnstock 3.x)
                    if Listing is not None:
                        # Use Listing class from vnstock 3.x
                        listing = Listing()
                        df = listing.all_symbols()  # Get all symbols
                    elif Company is not None:
                        # Try Company class (may need symbol, so less useful for listing)
                        # Skip for now, use Listing instead
                        df = None
                    elif listing_companies is not None:
                        # Use old API function
                        df = listing_companies()
                    else:
                        # Fallback if neither available
                        df = None
                    
                    if df is not None and not df.empty:
                        # Lấy top 100 cổ phiếu có volume cao nhất
                        symbols = df['symbol'].head(100).tolist()
                        if symbols and len(symbols) > 0:
                            self._popular_stocks = symbols
                        else:
                            self._popular_stocks = fallback_symbols
                    else:
                        # Fallback: danh sách cổ phiếu phổ biến
                        self._popular_stocks = fallback_symbols
                except Exception as e:
                    print(f"⚠️ Error fetching symbols from vnstock (có thể do không trong giờ giao dịch hoặc API tạm thời không khả dụng): {e}")
                    # Use fallback list
                    self._popular_stocks = fallback_symbols
            
            return self._popular_stocks if self._popular_stocks else fallback_symbols
        except Exception as e:
            print(f"⚠️ Error getting symbols: {e}")
            # Always return fallback on any error
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
            # Try different formats
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
        Lấy OHLCV data từ chứng khoán Việt Nam
        
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
            if not VNSTOCK_AVAILABLE:
                raise ImportError("vnstock library is not installed")
            
            # Convert timeframe
            tf = self.timeframe_map.get(timeframe, timeframe)
            
            # Determine date range
            if start_date and end_date:
                # Use date range
                start_dt = self._parse_date(start_date)
                end_dt = self._parse_date(end_date)
                
                if not start_dt or not end_dt:
                    raise ValueError("Invalid date format")
                
                # Check if dates are in the future
                now = datetime.now()
                if start_dt > now:
                    print(f"⚠️ WARNING: start_date {start_dt.strftime('%Y-%m-%d')} is in the future!")
                    print(f"   vnstock API cannot return future data. Adjusting to today.")
                    start_dt = now - timedelta(days=30)  # Default to last 30 days if future
                    print(f"📅 Adjusted start_date to: {start_dt.strftime('%Y-%m-%d')}")
                if end_dt > now:
                    print(f"⚠️ WARNING: end_date {end_dt.strftime('%Y-%m-%d')} is in the future!")
                    print(f"   vnstock API can only return data up to today. Adjusting to today.")
                    # Cap end_date to today
                    end_dt = now
                    print(f"📅 Adjusted end_date to today: {end_dt.strftime('%Y-%m-%d')}")
                
                # Ensure start_date is before end_date after adjustments
                if start_dt >= end_dt:
                    print(f"⚠️ Adjusted dates result in invalid range. Setting to last 30 days.")
                    end_dt = now
                    start_dt = now - timedelta(days=30)
                    print(f"📅 Final range: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
                
                # vnstock expects 'YYYY-MM-DD' format
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
                
            elif limit:
                # Use limit - calculate date range
                now = datetime.now()
                
                # CRITICAL: Ensure we're not using future dates
                # Cap end_date to today (not future)
                end_dt = now
                
                # Check if system date seems wrong (future year)
                if end_dt.year > 2024:
                    print(f"⚠️ WARNING: System date appears to be in the future: {end_dt.year}")
                    print(f"   This will cause vnstock API to return no data (it has no future data)")
                    print(f"   Assuming current year is 2024 and adjusting dates accordingly")
                    # Adjust to 2024 if system date is wrong
                    if end_dt.year > 2024:
                        # Use December 2024 as end date
                        from datetime import date
                        end_dt = datetime(2024, 12, min(20, date.today().day))  # Use today's day in Dec 2024
                        print(f"📅 Adjusted end_date to: {end_dt.strftime('%Y-%m-%d')}")
                
                # Estimate start date based on timeframe
                if tf in ['1', '5', '15', '30', '60']:
                    # Intraday: minutes
                    # For intraday, we need to account for trading hours only (6.5 hours/day)
                    # Calculate how many trading days we need
                    minutes_per_candle = int(tf) if tf.isdigit() else 60
                    total_minutes_needed = limit * minutes_per_candle
                    trading_hours_per_day = 6.5
                    minutes_per_trading_day = trading_hours_per_day * 60
                    trading_days_needed = max(1, int(total_minutes_needed / minutes_per_trading_day) + 1)  # Add buffer
                    start_dt = end_dt - timedelta(days=trading_days_needed)
                    print(f"📊 Calculating date range for limit={limit} candles ({tf}min):")
                    print(f"   Need ~{trading_days_needed} trading days (assuming {trading_hours_per_day}h/day)")
                elif tf == 'D':
                    # Daily: account for weekends (approximately 5 trading days per week)
                    # Add 40% buffer for weekends
                    trading_days_needed = int(limit * 1.4)
                    start_dt = end_dt - timedelta(days=trading_days_needed)
                    print(f"📊 Calculating date range for limit={limit} daily candles:")
                    print(f"   Need ~{trading_days_needed} calendar days (accounting for weekends)")
                elif tf == 'W':
                    start_dt = end_dt - timedelta(weeks=limit)
                elif tf == 'M':
                    start_dt = end_dt - timedelta(days=limit * 30)
                else:
                    start_dt = end_dt - timedelta(days=limit)
                
                # Ensure dates are not in the future (double check)
                if start_dt > now or start_dt.year > 2024:
                    print(f"⚠️ Calculated start_date is in the future. Adjusting to last 30 days.")
                    if end_dt.year > 2024:
                        end_dt = datetime(2024, 12, min(20, date.today().day))
                    start_dt = end_dt - timedelta(days=30)
                
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
                print(f"📅 Date range for limit={limit}: {start_str} to {end_str}")
            else:
                # Default: last 200 days
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=200)
                start_str = start_dt.strftime('%Y-%m-%d')
                end_str = end_dt.strftime('%Y-%m-%d')
            
            # Check if symbol is derivative (VN30F, HNX30F, or contains 'F' for futures)
            is_derivative = (
                symbol.upper().startswith('VN30F') or 
                symbol.upper().startswith('HNX30F') or
                symbol.upper().endswith('F1M') or
                symbol.upper().endswith('F2M') or
                symbol.upper().endswith('F3M') or
                ('F' in symbol.upper() and any(char.isdigit() for char in symbol))
            )
            
            # Fetch data from vnstock
            asset_type = 'phái sinh' if is_derivative else 'cổ phiếu'
            print(f"📊 Fetching {symbol} ({asset_type}) from {start_str} to {end_str}, timeframe={tf}")
            
            # Try new API first (vnstock 3.x uses Quote class)
            df = None
            if Quote is not None:
                try:
                    # Use Quote class from vnstock 3.x
                    # Quote requires both symbol and source parameters
                    quote = Quote(symbol=symbol, source='vci')  # vci is the default source
                    # Quote class has 'history' method for historical data
                    # Parameters: start, end (not start_date, end_date), resolution
                    if hasattr(quote, 'history'):
                        df = quote.history(start=start_str, end=end_str, resolution=tf)
                        print(f"✅ Successfully fetched data using Quote.history()")
                        if df is not None and not df.empty:
                            print(f"📊 DataFrame shape: {df.shape} (rows={len(df)}, cols={len(df.columns)})")
                            print(f"📊 DataFrame columns: {list(df.columns)}")
                            if 'time' in df.columns or 'Time' in df.columns or 'date' in df.columns:
                                time_col = 'time' if 'time' in df.columns else ('Time' if 'Time' in df.columns else 'date')
                                first_time = df[time_col].iloc[0] if len(df) > 0 else None
                                last_time = df[time_col].iloc[-1] if len(df) > 0 else None
                                print(f"📅 Date range in data: {first_time} to {last_time}")
                            print(f"📊 Requested date range: {start_str} to {end_str}")
                    else:
                        print(f"⚠️ Quote class doesn't have 'history' method")
                except Exception as e:
                    print(f"⚠️ Error using Quote class: {e}")
                    import traceback
                    traceback.print_exc()
                    df = None
            
            # Fallback to old API if new API didn't work
            if df is None or df.empty:
                if stock_historical_data is not None:
                    # Use old API function
                    if is_derivative:
                        # Try multiple approaches for derivatives
                        attempts = [
                            {'type': 'derivative'},  # Try with type='derivative'
                            {},  # Try without type parameter
                            {'type': 'stock'},  # Fallback to stock type
                        ]
                        
                        for attempt in attempts:
                            try:
                                print(f"🔍 Trying derivative fetch with params: {attempt}")
                                df = stock_historical_data(
                                    symbol=symbol,
                                    start_date=start_str,
                                    end_date=end_str,
                                    resolution=tf,
                                    **attempt
                                )
                                if df is not None and not df.empty:
                                    print(f"✅ Successfully fetched derivative data with params: {attempt}")
                                    break
                            except Exception as e:
                                print(f"⚠️ Error with params {attempt}: {e}")
                                continue
                    else:
                        # Regular stock
                        try:
                            df = stock_historical_data(
                                symbol=symbol,
                                start_date=start_str,
                                end_date=end_str,
                                resolution=tf,  # '1', '5', '15', '30', '60', 'D', 'W', 'M'
                                type='stock'  # 'stock' or 'index'
                            )
                        except Exception as e:
                            print(f"⚠️ Error fetching stock data: {e}")
                            df = None
            
            if df is None or df.empty:
                print(f"❌ No data returned for {symbol}")
                print(f"   Requested: {start_str} to {end_str}, timeframe={tf}")
                return None
            
            print(f"📊 Raw DataFrame from vnstock: {len(df)} rows")
            
            # If using limit and got too few results, try expanding date range
            if limit and len(df) < limit * 0.5 and not start_date and not end_date:
                print(f"⚠️ Only {len(df)} rows returned, but {limit} requested. Trying to expand date range...")
                # Try fetching with a much wider date range
                expanded_end_dt = datetime.now()
                
                # CRITICAL: Ensure we're not using future dates
                if expanded_end_dt.year > 2024:
                    print(f"⚠️ System date is in the future ({expanded_end_dt.year}). Using 2024-12-20 as end date.")
                    from datetime import date
                    expanded_end_dt = datetime(2024, 12, min(20, date.today().day))
                
                if tf in ['1', '5', '15', '30', '60']:
                    # For intraday, try last 6 months
                    expanded_start_dt = expanded_end_dt - timedelta(days=180)
                elif tf == 'D':
                    # For daily, try last 2 years
                    expanded_start_dt = expanded_end_dt - timedelta(days=730)
                else:
                    expanded_start_dt = expanded_end_dt - timedelta(days=365)
                
                # Ensure start date is not before 2020 (reasonable limit for stock data)
                if expanded_start_dt.year < 2020:
                    expanded_start_dt = datetime(2020, 1, 1)
                    print(f"📅 Adjusted start_date to 2020-01-01 (minimum historical data)")
                
                expanded_start_str = expanded_start_dt.strftime('%Y-%m-%d')
                expanded_end_str = expanded_end_dt.strftime('%Y-%m-%d')
                
                print(f"🔄 Retrying with expanded range: {expanded_start_str} to {expanded_end_str}")
                try:
                    if Quote is not None:
                        quote_expanded = Quote(symbol=symbol, source='vci')
                        if hasattr(quote_expanded, 'history'):
                            df_expanded = quote_expanded.history(start=expanded_start_str, end=expanded_end_str, resolution=tf)
                            if df_expanded is not None and not df_expanded.empty and len(df_expanded) > len(df):
                                print(f"✅ Expanded fetch returned {len(df_expanded)} rows (vs {len(df)} before)")
                                df = df_expanded
                                start_str = expanded_start_str
                                end_str = expanded_end_str
                except Exception as e:
                    print(f"⚠️ Expanded fetch failed: {e}")
                    # Continue with original df
            
            # Check if returned data seems too small compared to expected
            if start_date and end_date:
                start_dt_check = self._parse_date(start_date)
                end_dt_check = self._parse_date(end_date)
                if start_dt_check and end_dt_check:
                    days_diff = (end_dt_check - start_dt_check).days
                    if tf in ['1', '5', '15', '30', '60']:
                        minutes_per_candle = int(tf) if tf.isdigit() else 60
                        trading_hours = 6.5
                        minutes_per_day = trading_hours * 60
                        expected_min = int((days_diff * minutes_per_day) / minutes_per_candle * 0.1)  # At least 10% of expected
                        if len(df) < expected_min and days_diff > 7:
                            print(f"⚠️ WARNING: Only {len(df)} rows returned, but expected at least ~{expected_min} rows")
                            print(f"   This might indicate:")
                            print(f"   1. Date range is in the future (vnstock has no future data)")
                            print(f"   2. Symbol has limited historical data")
                            print(f"   3. vnstock API limitation or error")
            
            # Convert to list of dicts
            ohlcv_data = []
            skipped_rows = 0
            for idx, row in df.iterrows():
                # vnstock returns columns: time, open, high, low, close, volume
                # Column names might vary, try common names
                time_col = None
                for col in ['time', 'Time', 'TIME', 'date', 'Date', 'DATE']:
                    if col in df.columns:
                        time_col = col
                        break
                
                if time_col is None:
                    # Use index if time column not found
                    time_val = row.name if hasattr(row, 'name') else str(row.get('time', ''))
                else:
                    time_val = row[time_col]
                
                # Convert time to string format
                if isinstance(time_val, (datetime, pd.Timestamp)):
                    time_str = time_val.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(time_val, str):
                    time_str = time_val
                else:
                    time_str = str(time_val)
                
                # Get OHLCV values
                try:
                    open_val = float(row.get('open', row.get('Open', 0)))
                    high_val = float(row.get('high', row.get('High', 0)))
                    low_val = float(row.get('low', row.get('Low', 0)))
                    close_val = float(row.get('close', row.get('Close', 0)))
                    volume_val = int(row.get('volume', row.get('Volume', 0)))
                    
                    # Skip rows with invalid data
                    if open_val == 0 and high_val == 0 and low_val == 0 and close_val == 0:
                        skipped_rows += 1
                        continue
                    
                    ohlcv_data.append({
                        'time': time_str,
                        'open': open_val,
                        'high': high_val,
                        'low': low_val,
                        'close': close_val,
                        'volume': volume_val
                    })
                except (ValueError, TypeError) as e:
                    skipped_rows += 1
                    print(f"⚠️ Skipping row {idx} due to conversion error: {e}")
                    continue
            
            # Sort by time ascending
            ohlcv_data.sort(key=lambda x: x['time'])
            
            # Filter data to requested date range if provided (but be lenient when using limit)
            # When using limit, we want to get as much data as possible, so don't filter too strictly
            if start_date and end_date and ohlcv_data:
                start_dt_filter = self._parse_date(start_date)
                end_dt_filter = self._parse_date(end_date)
                if start_dt_filter and end_dt_filter:
                    original_count = len(ohlcv_data)
                    filtered_data = []
                    for candle in ohlcv_data:
                        candle_time_str = candle['time']
                        candle_dt = self._parse_date(candle_time_str)
                        if candle_dt:
                            # Include if within requested range (with some tolerance for time component)
                            if start_dt_filter.date() <= candle_dt.date() <= end_dt_filter.date():
                                filtered_data.append(candle)
                    
                    if len(filtered_data) < original_count:
                        print(f"📊 Filtered data: {original_count} -> {len(filtered_data)} candles (within requested date range)")
                        # If using limit and filtered result is too small, keep original data
                        if limit and len(filtered_data) < limit * 0.5:
                            print(f"⚠️ Filtered result ({len(filtered_data)}) is much less than requested limit ({limit})")
                            print(f"   Keeping all available data ({original_count} candles) to meet limit requirement")
                            # Don't filter - keep all data
                        else:
                            ohlcv_data = filtered_data
            
            # Log date range of actual data
            if ohlcv_data:
                first_candle_time = ohlcv_data[0]['time']
                last_candle_time = ohlcv_data[-1]['time']
                print(f"📅 Actual data range: {first_candle_time} to {last_candle_time}")
                
                # Calculate expected vs actual
                if start_date and end_date:
                    start_dt = self._parse_date(start_date)
                    end_dt = self._parse_date(end_date)
                    if start_dt and end_dt:
                        days_diff = (end_dt - start_dt).days
                        if tf in ['1', '5', '15', '30', '60']:
                            # Intraday: assume 6.5 hours trading per day (9:00-15:30)
                            trading_hours = 6.5
                            minutes_per_day = trading_hours * 60
                            minutes_per_candle = int(tf) if tf.isdigit() else 60
                            expected_candles = int((days_diff * minutes_per_day) / minutes_per_candle)
                            print(f"📊 Expected candles (intraday): ~{expected_candles} (based on {days_diff} days, {trading_hours}h/day, {minutes_per_candle}min candles)")
                        elif tf == 'D':
                            # Daily: exclude weekends
                            weekdays = days_diff - (days_diff // 7) * 2
                            expected_candles = weekdays
                            print(f"📊 Expected candles (daily): ~{expected_candles} (based on {days_diff} days, excluding weekends)")
                        else:
                            print(f"📊 Date range: {days_diff} days")
            
            if skipped_rows > 0:
                print(f"⚠️ Skipped {skipped_rows} rows with invalid data")
            
            # Limit if needed - take the most recent candles
            if limit and len(ohlcv_data) > limit:
                print(f"📊 Limiting from {len(ohlcv_data)} to {limit} candles (taking most recent)")
                ohlcv_data = ohlcv_data[-limit:]
            elif limit and len(ohlcv_data) < limit:
                print(f"⚠️ Only {len(ohlcv_data)} candles available, but {limit} requested")
                print(f"   This might be due to:")
                print(f"   1. Limited historical data for this symbol")
                print(f"   2. Date range issues (future dates)")
                print(f"   3. vnstock API limitations")
            
            print(f"✅ Final result: {len(ohlcv_data)} candles for {symbol}")
            
            # Final warning if result is suspiciously small
            if start_date and end_date and ohlcv_data:
                start_dt_final = self._parse_date(start_date)
                end_dt_final = self._parse_date(end_date)
                if start_dt_final and end_dt_final:
                    days_diff = (end_dt_final - start_dt_final).days
                    if days_diff > 7:  # More than a week
                        if tf in ['1', '5', '15', '30', '60']:
                            minutes_per_candle = int(tf) if tf.isdigit() else 60
                            trading_hours = 6.5
                            minutes_per_day = trading_hours * 60
                            expected_min = int((days_diff * minutes_per_day) / minutes_per_candle * 0.2)  # At least 20% of expected
                            if len(ohlcv_data) < expected_min:
                                print(f"⚠️⚠️⚠️ WARNING: Very few candles returned!")
                                print(f"   Requested: {days_diff} days, Expected: ~{int((days_diff * minutes_per_day) / minutes_per_candle)} candles")
                                print(f"   Actual: {len(ohlcv_data)} candles (only {len(ohlcv_data)/expected_min*100:.1f}% of minimum expected)")
                                print(f"   Possible reasons:")
                                print(f"   1. Date range includes future dates (vnstock has no future data)")
                                print(f"   2. Symbol has limited trading history")
                                print(f"   3. vnstock API limitation or rate limiting")
                                print(f"   💡 Try using a past date range or use 'limit' parameter instead")
            
            return ohlcv_data
            
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Kiểm tra mã cổ phiếu/phái sinh có hợp lệ không"""
        try:
            symbol_upper = symbol.upper()
            
            # Check if it's a derivative symbol
            is_derivative = (
                symbol_upper.startswith('VN30F') or 
                symbol_upper.startswith('HNX30F') or
                symbol_upper.endswith('F1M') or
                symbol_upper.endswith('F2M') or
                symbol_upper.endswith('F3M') or
                ('F' in symbol_upper and any(char.isdigit() for char in symbol_upper))
            )
            
            if is_derivative:
                # Check in derivatives list
                derivatives = self.get_derivatives_symbols()
                derivatives_upper = [s.upper() for s in derivatives]
                is_valid = symbol_upper in derivatives_upper
                if not is_valid:
                    print(f"⚠️ Symbol {symbol} not found in derivatives list. Available: {derivatives_upper[:10]}...")
                return is_valid
            else:
                # Check in regular stocks list
                symbols = self.get_available_symbols()
                symbols_upper = [s.upper() for s in symbols]
                is_valid = symbol_upper in symbols_upper
                if not is_valid:
                    print(f"⚠️ Symbol {symbol} not found in stocks list. Total symbols: {len(symbols_upper)}")
                return is_valid
        except Exception as e:
            # If validation fails, allow the symbol anyway (let vnstock API decide)
            # This is more permissive and allows new symbols that aren't in our fallback list
            print(f"⚠️ Validation error for {symbol}: {e}. Allowing symbol anyway.")
            return True
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Lấy thông tin mã cổ phiếu"""
        try:
            # Try new API first (vnstock 3.x)
            df = None
            if Listing is not None:
                try:
                    listing = Listing()
                    df = listing.all_symbols()  # Get all symbols
                except Exception as e:
                    print(f"⚠️ Error using Listing class: {e}")
            elif Company is not None:
                try:
                    # Company class may need symbol, so less useful for listing
                    # Skip for now
                    df = None
                except Exception as e:
                    print(f"⚠️ Error using Company class: {e}")
            
            # Fallback to old API
            if (df is None or df.empty) and listing_companies is not None:
                try:
                    df = listing_companies()
                except Exception as e:
                    print(f"⚠️ Error using listing_companies function: {e}")
            
            if df is not None and not df.empty:
                stock_info = df[df['symbol'].str.upper() == symbol.upper()]
                if not stock_info.empty:
                    row = stock_info.iloc[0]
                    return {
                        'symbol': row.get('symbol', symbol),
                        'name': row.get('organName', row.get('name', '')),
                        'exchange': row.get('exchange', ''),
                        'sector': row.get('sector', '')
                    }
            
            return {
                'symbol': symbol,
                'name': '',
                'exchange': '',
                'sector': ''
            }
        except Exception as e:
            print(f"Error getting symbol info: {e}")
            return {
                'symbol': symbol,
                'name': '',
                'exchange': '',
                'sector': ''
            }


# Singleton instance
_fetcher = None

def get_vnstock_fetcher() -> VNStockFetcher:
    """Get singleton instance of VNStockFetcher"""
    global _fetcher
    if _fetcher is None:
        try:
            _fetcher = VNStockFetcher()
        except ImportError as e:
            print(f"⚠️ Cannot initialize VNStockFetcher: {e}")
            print("💡 Install vnstock: pip install vnstock")
            raise
    return _fetcher
