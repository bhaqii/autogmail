import random
import time
import math
import os
import sys
import atexit
import signal
import threading
import pyperclip
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException
)

# Import GoLogin SDK
try:
    from gologin import GoLogin
except ImportError:
    print("❌ GoLogin SDK not installed. Please run: pip install gologin")
    sys.exit(1)

# ============= CONFIGURATION =============
GOLOGIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODkxY2YxODdiOGFiOTg0NWE0NTg0NjkiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODkxY2Y4YzdhZDk2YWFkMjczYzQ1M2UifQ.tISb5g5Ohj7Tpf8ODS_kUJH0dbPCWbN3zNM8ozwBF90"
DEFAULT_PASSWORD = "masukaja@@"

# Global variables for cleanup dengan thread-safe management
gl = None
profile_id = None
driver = None
cleanup_lock = threading.Lock()
cleanup_completed = False
browser_monitor_thread = None
browser_monitor_active = False

class ResourceManager:
    """Thread-safe resource management untuk menghindari double cleanup"""
    
    def __init__(self):
        self.resources = {}
        self.lock = threading.Lock()
        self.cleaned = False
    
    def set_driver(self, driver):
        with self.lock:
            self.resources['driver'] = driver
    
    def set_gologin(self, gl, profile_id):
        with self.lock:
            self.resources['gl'] = gl
            self.resources['profile_id'] = profile_id
    
    def is_driver_alive(self):
        """Check apakah driver masih aktif"""
        try:
            if 'driver' in self.resources and self.resources['driver']:
                # Test dengan simple command
                self.resources['driver'].current_url
                return True
        except:
            return False
        return False
    
    def safe_cleanup(self):
        """Thread-safe cleanup yang mencegah double execution"""
        with self.lock:
            if self.cleaned:
                return True
            
            print("\n🧹 Initiating safe cleanup process...")
            success = True
            
            # Step 1: Safe Selenium cleanup
            if 'driver' in self.resources and self.resources['driver']:
                try:
                    if self.is_driver_alive():
                        print("⏹️ Closing Selenium driver...")
                        self.resources['driver'].quit()
                        print("✅ Selenium driver closed")
                    else:
                        print("ℹ️ Selenium driver already closed")
                    self.resources['driver'] = None
                except Exception as e:
                    print(f"⚠️ Driver cleanup warning: {e}")
            
            # Step 2: Safe GoLogin cleanup
            if 'gl' in self.resources and 'profile_id' in self.resources:
                gl = self.resources['gl']
                profile_id = self.resources['profile_id']
                
                if gl and profile_id:
                    try:
                        print(f"🗑️ Deleting GoLogin profile: {profile_id}")
                        gl.delete(profile_id)
                        print("✅ GoLogin profile deleted")
                    except Exception as e:
                        print(f"⚠️ Profile deletion warning: {e}")
                
                self.resources['gl'] = None
                self.resources['profile_id'] = None
            
            self.cleaned = True
            subprocess.run(["warp-cli", "disconnect"])
            print("✅ Safe cleanup completed successfully!")
            return success

# Initialize global resource manager
resource_manager = ResourceManager()

class SuperOptimizedTiming:
    """SUPER OPTIMIZED timing patterns - 20% faster while maintaining natural behavior"""
    
    @staticmethod
    def micro_pause():
        """Super optimized micro pause (20% faster)"""
        return random.uniform(0.056, 0.132)  # Was 0.070-0.158
    
    @staticmethod
    def quick_read(text_length):
        """Super optimized reading time (faster processing)"""
        words = max(text_length / 5, 1)
        base_time = min(words * 0.028, 0.208)  # Was 0.035, 0.26 - 20% faster
        cognitive_load = random.uniform(-0.014, 0.056)  # Proportionally reduced
        return base_time + cognitive_load
    
    @staticmethod
    def swift_decision(complexity="medium"):
        """Super optimized decision time (20% faster)"""
        timing_map = {
            "simple": (0.070, 0.211),    # Was 0.088-0.264
            "medium": (0.141, 0.352),    # Was 0.176-0.440
            "complex": (0.211, 0.493)    # Was 0.264-0.616
        }
        return random.uniform(*timing_map[complexity])
    
    @staticmethod
    def typing_speed():
        """Super optimized typing speed (20% faster)"""
        return random.uniform(0.021, 0.085)  # Was 0.026-0.106
    
    @staticmethod
    def minimal_exploration():
        """Super optimized exploration time (faster)"""
        return random.uniform(0.141, 0.352)  # Was 0.176-0.440 - 20% faster
    
    @staticmethod
    def fast_typing_speed():
        """Super optimized fast typing speed for random keys"""
        return random.uniform(0.014, 0.042)

class UnifiedTiming:
    """Enhanced timing patterns untuk natural behavior simulation dengan variasi terkontrol"""
    
    @staticmethod
    def micro_pause():
        """Micro pause yang konsisten dengan variasi natural (lebih sempit)"""
        return random.uniform(0.08, 0.18)  # 80-180ms
    
    @staticmethod
    def quick_read(text_length):
        """Reading time yang adaptive berdasarkan kompleksitas teks (lebih cepat)"""
        words = max(text_length / 5, 1)
        base_time = min(words * 0.04, 0.3)  # Max 300ms
        cognitive_load = random.uniform(-0.02, 0.08)
        return base_time + cognitive_load
    
    @staticmethod
    def swift_decision(complexity="medium"):
        """Decision time dengan natural variations (lebih cepat)"""
        timing_map = {
            "simple": (0.1, 0.3),
            "medium": (0.2, 0.5),
            "complex": (0.3, 0.7)
        }
        return random.uniform(*timing_map[complexity])
    
    @staticmethod
    def typing_speed():
        """Natural typing speed dengan human-like variations (lebih cepat)"""
        return random.uniform(0.03, 0.12)  # 30-120ms per character
    
    @staticmethod
    def minimal_exploration():
        """Page exploration time dengan realistic patterns (lebih singkat)"""
        return random.uniform(0.2, 0.5)
    
    @staticmethod
    def fast_typing_speed():
        """Fast typing speed untuk random keys"""
        return random.uniform(0.02, 0.06)  # 20-60ms per character (lebih cepat)

def browser_monitor():
    """ENHANCED MONITORING: Browser close detection + Auto-completion detection"""
    global browser_monitor_active, cleanup_completed, driver, resource_manager
    
    print("🔍 Enhanced browser monitoring started - AUTO-COMPLETION DETECTION")
    
    while browser_monitor_active and not cleanup_completed:
        try:
            time.sleep(2)  # Check setiap 2 detik
            
            if driver and not cleanup_completed:
                try:
                    # HANYA SATU KONDISI: Coba akses current_url
                    # Akan throw WebDriverException jika browser ditutup manual
                    current_url = driver.current_url
                    
                    # ============= NEW: AUTO-COMPLETION DETECTION =============
                    # Check jika sudah sampai di halaman completion
                    if "myaccount.google.com" in current_url:
                        print("\n🎉 COMPLETION DETECTED! Google Account created successfully!")
                        print(f"📍 Final URL: {current_url}")
                        print("🔄 Triggering automatic completion cleanup...")
                        browser_monitor_active = False
                        resource_manager.safe_cleanup()
                        cleanup_completed = True
                        print("✅ Account creation completed successfully!")
                        os._exit(0)
                    
                except WebDriverException:
                    print("\n👀 Browser closed by user detected!")
                    print("🔄 Triggering automatic cleanup...")
                    browser_monitor_active = False
                    resource_manager.safe_cleanup()
                    cleanup_completed = True
                    os._exit(0)
                    
        except Exception as e:
            # Fallback untuk error monitoring
            print(f"⚠️ Monitor error, triggering cleanup: {e}")
            browser_monitor_active = False
            resource_manager.safe_cleanup()
            cleanup_completed = True
            sys.exit(0)
    
    print("🔍 Enhanced browser monitoring stopped.")

def start_browser_monitor():
    """Start browser monitoring thread"""
    global browser_monitor_thread, browser_monitor_active
    
    browser_monitor_active = True
    browser_monitor_thread = threading.Thread(target=browser_monitor, daemon=True)
    browser_monitor_thread.start()

def stop_browser_monitor():
    """Stop browser monitoring thread"""
    global browser_monitor_active, browser_monitor_thread
    
    browser_monitor_active = False
    if browser_monitor_thread and browser_monitor_thread.is_alive():
        try:
            browser_monitor_thread.join(timeout=3)
        except:
            pass

def safe_cleanup_handler():
    """Improved cleanup handler dengan thread-safety"""
    global cleanup_completed
    
    if cleanup_completed:
        return
    
    cleanup_completed = True
    stop_browser_monitor()
    resource_manager.safe_cleanup()

def signal_handler(signum, frame):
    """Enhanced signal handler yang tidak conflict"""
    print(f"\n🛑 Received signal {signum}, initiating safe cleanup...")
    safe_cleanup_handler()
    sys.exit(0)

# Register hanya satu cleanup handler untuk menghindari conflict
atexit.register(safe_cleanup_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_user_data():
    """Enhanced user input collection dengan validation"""
    print("=== GMAIL AUTOMATION WITH EXTENDED STAGES ===")
    print("🔧 Features: Thread-Safe Cleanup + GoLogin + Auto Browser Detection")
    print("🎯 Extended: Email Extraction + Terms Agreement + Auto Completion")
    print("="*70)
    
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    
    # Validate names
    if not first_name:
        print("❌ Names cannot be empty!")
        return get_user_data()
    
    # Generate random birth data
    day = str(random.randint(1, 28))
    year = str(random.randint(1985, 2005))
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = random.choice(months)
    
    print("\n👤 Gender: 1=Male 2=Female 3=Rather not say 4=Custom")
    gender_choice = input("Choose (1-4): ").strip()
    gender_map = {"1": "Male", "2": "Female", "3": "Rather not say", "4": "Custom"}
    gender = gender_map.get(gender_choice, "Male")
    
    print(f"\n✅ Profile Generated:")
    print(f" 👤 Name: {first_name} {last_name}")
    print(f" 👥 Gender: {gender}")
    print(f" 📅 Birth: {day} {month} {year}")
    print(f" 🔒 Password: {DEFAULT_PASSWORD}")
    print(f" 🛡️ Safety: Auto-detection + Extended stages")
    print(f"\n🚀 Starting extended automation...")
    
    return {
        "first_name": first_name, "last_name": last_name,
        "day": day, "month": month, "year": year,
        "gender": gender, "password": DEFAULT_PASSWORD
    }

def advanced_natural_typing(element, text, typing_style="adaptive"):
    """Advanced natural typing dengan multiple patterns"""
    element.clear()
    time.sleep(UnifiedTiming.micro_pause())  # Jeda setelah clear
    
    # Adaptive typing style berdasarkan text complexity
    if typing_style == "adaptive":
        if len(text) <= 4:
            style = "careful"
        elif len(text) <= 12:
            style = "normal"
        else:
            style = "burst"
    else:
        style = typing_style
    
    if style == "careful":
        # Character by character dengan natural hesitation patterns
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Natural hesitation patterns berdasarkan character complexity
            if char.isupper() or char in "!@#$%^&*()":
                time.sleep(random.uniform(0.1, 0.25))  # Special chars take longer
            elif i > 0 and text[i-1] == char:
                time.sleep(random.uniform(0.06, 0.15))  # Repeated chars
            elif char.isdigit():
                time.sleep(random.uniform(0.05, 0.12))  # Numbers
            elif random.random() < 0.1:  # 10% chance of micro-pause
                time.sleep(random.uniform(0.04, 0.1))
            else:
                time.sleep(UnifiedTiming.typing_speed())
    
    elif style == "burst":
        # Advanced burst typing dengan natural flow
        words = text.split() if ' ' in text else [text]
        
        for word_idx, word in enumerate(words):
            if word_idx > 0:
                element.send_keys(" ")
                time.sleep(random.uniform(0.06, 0.15))  # Jeda antar kata
            
            # Dynamic burst size based on word complexity
            if word.isdigit():
                burst_sizes = [2, 3]  # Numbers typed in smaller bursts
            elif len(word) <= 5:
                burst_sizes = [3, 4]
            else:
                burst_sizes = [4, 5]
            
            for i in range(0, len(word), random.choice(burst_sizes)):
                burst_size = min(random.choice(burst_sizes), len(word) - i)
                burst = word[i:i+burst_size]
                element.send_keys(burst)
                
                # Burst timing dengan natural variations
                base_delay = 0.05 * len(burst)
                variation = random.uniform(-0.01, 0.03)
                time.sleep(max(0.02, base_delay + variation))
                
                # Inter-burst pause dengan probability
                if i + burst_size < len(word) and random.random() < 0.1:  # 10% chance
                    time.sleep(random.uniform(0.06, 0.15))
            
            # Inter-word cognitive pause
            if word_idx < len(words) - 1 and random.random() < 0.15:  # 15% chance
                time.sleep(random.uniform(0.1, 0.25))
    
    else:  # normal style
        # Balanced approach untuk general use
        for i, char in enumerate(text):
            element.send_keys(char)
            if random.random() < 0.05:  # 5% chance of longer pause
                time.sleep(random.uniform(0.1, 0.2))
            else:
                time.sleep(UnifiedTiming.typing_speed())
    
    # Final verification pause dengan cognitive load consideration
    cognitive_load = min(len(text) * 0.015, 0.3)  # Lebih cepat
    time.sleep(random.uniform(0.08, 0.08 + cognitive_load))

def enhanced_mouse_movement(driver, element):
    """Enhanced mouse movement dengan advanced trajectory simulation"""
    try:
        element_location = element.location_once_scrolled_into_view
        element_size = element.size
        
        # Calculate natural target point dengan slight randomization
        target_x = element_location['x'] + element_size['width'] * random.uniform(0.3, 0.7)
        target_y = element_location['y'] + element_size['height'] * random.uniform(0.3, 0.7)
        
        # Advanced curve trajectory dengan easing functions
        steps = random.randint(4, 7)  # Lebih sedikit langkah untuk lebih cepat
        actions = ActionChains(driver)
        
        for i in range(1, steps + 1):
            progress = i / steps
            
            # Bezier curve simulation untuk natural movement
            curve_intensity = 0.2 * (1 - progress) * progress * 4  # Bezier curve formula, intensitas lebih rendah
            curve_offset_x = random.randint(-15, 15) * curve_intensity
            curve_offset_y = random.randint(-10, 10) * curve_intensity
            
            # Easing function untuk acceleration/deceleration
            if progress < 0.2:
                step_delay = random.randint(15, 25)  # Slow start
            elif progress > 0.8:
                step_delay = random.randint(12, 20)  # Slow end
            else:
                step_delay = random.randint(6, 12)  # Fast middle
            
            time.sleep(step_delay / 1000)
        
        actions.move_to_element(element)
        actions.perform()
        
        # Natural hover dengan micro-movements
        time.sleep(random.uniform(0.04, 0.1))  # Lebih singkat
        
        # Occasional overshoot correction (realistic human behavior)
        if random.randint(1, 15) == 1:  # ~6.6% chance (lebih jarang)
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-2, 2)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.perform()
            time.sleep(random.uniform(0.02, 0.05))  # Lebih singkat
            
            # Correction movement
            actions.move_to_element(element)
            actions.perform()
            time.sleep(random.uniform(0.01, 0.04))  # Lebih singkat
    
    except Exception:
        # Fallback to basic movement
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(UnifiedTiming.micro_pause())

def enhanced_page_exploration(driver):
    """Enhanced page exploration dengan intelligent patterns"""
    try:
        # Smart scrolling pattern berdasarkan viewport
        viewport_height = driver.execute_script("return window.innerHeight;")
        scroll_amount = random.randint(int(viewport_height * 0.15), int(viewport_height * 0.3))  # Rentang lebih kecil
        
        # Natural scroll dengan easing
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.2, 0.5))  # Lebih singkat
        
        # Brief content loading simulation
        time.sleep(random.uniform(0.15, 0.4))  # Lebih singkat
        
        # Return to top dengan smooth behavior
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(random.uniform(0.3, 0.7))  # Lebih singkat
        
        # Subtle mouse movement simulation untuk human-like behavior
        try:
            interactive_elements = driver.find_elements(By.XPATH, "//input | //button | //a")
            if interactive_elements and len(interactive_elements) > 0:
                # Select 1-2 elements randomly for subtle interaction
                selected = random.sample(interactive_elements, min(2, len(interactive_elements)))
                for element in selected:
                    try:
                        if element.is_displayed():
                            ActionChains(driver).move_to_element(element).perform()
                            time.sleep(random.uniform(0.08, 0.2))  # Lebih singkat
                    except:
                        pass
        except:
            pass
    
    except Exception:
        # Fallback to basic exploration
        time.sleep(UnifiedTiming.minimal_exploration())

def bulletproof_element_interaction(driver, element, interaction_type="click"):
    """Bulletproof element interaction dengan comprehensive error handling"""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            # Ensure element is in viewport
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(random.uniform(0.1, 0.25))  # Lebih singkat
            
            # Enhanced mouse movement
            enhanced_mouse_movement(driver, element)
            time.sleep(random.uniform(0.04, 0.15))  # Lebih singkat
            
            # Interaction with timing
            if interaction_type == "click":
                element.click()
                time.sleep(UnifiedTiming.micro_pause())
            elif interaction_type == "focus":
                element.click()  # Click to focus
                time.sleep(random.uniform(0.04, 0.1))  # Lebih singkat
            
            return True
        
        except (ElementNotInteractableException, StaleElementReferenceException) as e:
            print(f"⚠️ Interaction attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(random.uniform(0.15, 0.4))  # Lebih singkat
                continue
            
            # Emergency fallback
            try:
                driver.execute_script("arguments[0].click();", element)
                time.sleep(UnifiedTiming.micro_pause())
                return True
            except:
                pass
        
        except Exception as e:
            print(f"⚠️ Unexpected interaction error: {e}")
            if attempt == max_attempts - 1:
                return False
    
    return False

def enhanced_dropdown_selection(driver, dropdown_type, option_text):
    """Enhanced dropdown selection dengan comprehensive fallback"""
    try:
        dropdown_selectors = [
            (By.ID, dropdown_type.lower()),
            (By.NAME, dropdown_type.lower()),
            (By.XPATH, f"//div[contains(@aria-label, '{dropdown_type}')]"),
            (By.XPATH, f"//select[contains(@name, '{dropdown_type.lower()}')]")
        ]
        
        dropdown_element = None
        
        for selector_type, selector_value in dropdown_selectors:
            try:
                dropdown_element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if dropdown_element:
                    break
            except:
                continue
        
        if not dropdown_element:
            print(f"⚠️ {dropdown_type} dropdown not found")
            return False
        
        if bulletproof_element_interaction(driver, dropdown_element, "click"):
            time.sleep(UnifiedTiming.swift_decision("simple"))  # Jeda setelah klik dropdown
            
            # Strategy 1: Direct text matching
            if random.choice([True, True, False]):  # 67% chance
                try:
                    direct_option = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH,
                            f"//div[@role='option'][normalize-space(text())='{option_text}'] | "
                            f"//option[normalize-space(text())='{option_text}']"
                        ))
                    )
                    
                    time.sleep(UnifiedTiming.quick_read(len(option_text)))
                    if bulletproof_element_interaction(driver, direct_option, "click"):
                        return True
                except:
                    pass
            
            # Strategy 2: Keyboard navigation with intelligent mapping
            try:
                # Option mapping dengan comprehensive coverage
                if dropdown_type.lower() == "month":
                    months_map = {
                        "January": 0, "February": 1, "March": 2, "April": 3,
                        "May": 4, "June": 5, "July": 6, "August": 7,
                        "September": 8, "October": 9, "November": 10, "December": 11
                    }
                    target_index = months_map.get(option_text, 0)
                elif dropdown_type.lower() == "gender":
                    gender_map = {"Female": 0, "Male": 1, "Rather not say": 2, "Custom": 3}
                    target_index = gender_map.get(option_text, 1)
                else:
                    target_index = 0
                
                # Enhanced keyboard navigation
                ActionChains(driver).send_keys(Keys.HOME).perform()
                time.sleep(UnifiedTiming.micro_pause())
                
                for step in range(target_index):
                    ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
                    time.sleep(random.uniform(0.06, 0.15))  # Lebih cepat antar panah
                    
                    # Natural reading pause (10% chance)
                    if random.randint(1, 10) == 1:
                        time.sleep(random.uniform(0.1, 0.25))  # Lebih singkat
                
                time.sleep(UnifiedTiming.swift_decision("simple"))
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(UnifiedTiming.micro_pause())
                return True
                
            except Exception as e:
                print(f"⚠️ Keyboard navigation failed: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Dropdown selection failed: {e}")
        return False

def enhanced_next_button(driver, context=""):
    """Enhanced next button detection dan interaction - EXTENDED VERSION"""
    
    # LANGSUNG CARI ELEMENT BERDASARKAN ID YANG SPESIFIK
    if context == "collectNameNext":
        # Untuk halaman name, gunakan ID collectNameNext
        try:
            next_button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.ID, "collectNameNext"))
            )
            
            if bulletproof_element_interaction(driver, next_button, "click"):
                print(f"✅ Successfully proceeded from {context}")
                return True
        except Exception as e:
            print(f"⚠️ Next button with ID {context} failed: {e}")
    
    elif context == "birthdaygenderNext":
        # Untuk halaman birthday dan gender, gunakan ID birthdaygenderNext
        try:
            next_button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.ID, "birthdaygenderNext"))
            )
            
            if bulletproof_element_interaction(driver, next_button, "click"):
                print(f"✅ Successfully proceeded from {context}")
                return True
        except Exception as e:
            print(f"⚠️ Next button with ID {context} failed: {e}")
    
    elif context == "passwordNext":
        # Untuk halaman password, gunakan ID passwordNext
        try:
            next_button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Selanjutnya')]"))
            )
            
            if bulletproof_element_interaction(driver, next_button, "click"):
                print(f"✅ Successfully proceeded from {context}")
                return True
        except Exception as e:
            print(f"⚠️ Next button with ID {context} failed: {e}")
    
    # ============= NEW: GENERIC NEXT BUTTON DETECTION =============
    elif context == "genericNext":
        # Generic next button detection untuk stage baru
        generic_next_selectors = [
            (By.XPATH, "//span[contains(text(), 'Selanjutnya')]"),
            (By.XPATH, "//span[contains(text(), 'Next')]"),
            (By.XPATH, "//button[contains(text(), 'Selanjutnya')]"),
            (By.XPATH, "//button[contains(text(), 'Next')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//input[@type='submit']"),
        ]
        
        for selector_type, selector_value in generic_next_selectors:
            try:
                next_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if bulletproof_element_interaction(driver, next_button, "click"):
                    print(f"✅ Successfully proceeded using generic next button")
                    return True
            except:
                continue
    
    # Fallback: Try Enter key jika element ID tidak ditemukan
    try:
        ActionChains(driver).send_keys(Keys.RETURN).perform()
        time.sleep(random.uniform(0.8, 1.5))  # Jeda setelah Enter
        print(f"✅ Proceeded from {context} using Enter key")
        return True
    except:
        pass
    
    return False

def detect_username_stage(driver):
    """Deteksi apakah sudah sampai di tahap username selection"""
    try:
        # Cek berbagai selector untuk username stage
        username_selectors = [
            (By.ID, "username"),
            (By.NAME, "username"),
            (By.XPATH, "//input[contains(@name, 'username')]"),
            (By.XPATH, "//input[contains(@id, 'username')]"),
            (By.XPATH, "//input[contains(@aria-label, 'username')]"),
            (By.XPATH, "//input[contains(@placeholder, 'username')]"),
            (By.XPATH, "//input[@type='text'][contains(@name, 'choose')]"),
        ]
        
        for selector_type, selector_value in username_selectors:
            try:
                username_element = WebDriverWait(driver, 1.2).until(  # Faster timeout
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if username_element:
                    print("🎯 Username stage detected!")
                    return True
            except:
                continue
        
        # Cek berdasarkan text content
        try:
            username_indicators = [
                "choose your username",
                "create a username", 
                "username",
                "pick a username"
            ]
            
            page_text = driver.page_source.lower()
            for indicator in username_indicators:
                if indicator in page_text:
                    print(f"🎯 Username stage detected via text: {indicator}")
                    return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"⚠️ Username detection error: {e}")
        return False

def wait_for_manual_username_input(driver):
    """Wait untuk user memilih username secara manual"""
    print("\n" + "="*60)
    print("👤 USERNAME SELECTION STAGE")
    print("="*60)
    print("📝 Please choose your username manually in the browser")
    print("🖱️ The script will automatically continue after you proceed")
    print("⏱️ Monitoring for password stage...")
    
    # Monitor terus menerus sampai user selesai memilih username
    max_wait_time = 300  # 5 menit maximum
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Cek apakah sudah sampai ke password stage
            if bulletproof_detect_password_stage(driver):
                print("✅ Username completed, moving to password stage!")
                return True
            
            # Check setiap 1.2 detik (faster)
            time.sleep(1.2)
            
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            time.sleep(1.2)
    
    print("⏰ Timeout waiting for username completion")
    return False

def bulletproof_detect_password_stage(driver):
    """BULLETPROOF Password Stage Detection - Zero macet guarantee"""
    try:
        # PRE-CHECK: Wait for page stability
        try:
            WebDriverWait(driver, 1.5).until(  # Faster timeout
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass
        
        # STRATEGY 1: Priority password field selectors (most reliable)
        priority_selectors = [
            (By.NAME, "Passwd"),
            (By.ID, "passwd"),
            (By.XPATH, "//input[@type='password']"),
        ]
        
        for selector_type, selector_value in priority_selectors:
            try:
                password_element = WebDriverWait(driver, 0.6).until(  # Faster
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if password_element and password_element.is_displayed():
                    print(f"🔒 Password stage detected (Priority): {selector_value}")
                    return True
            except:
                continue
        
        # STRATEGY 2: Extended password field selectors
        extended_selectors = [
            (By.XPATH, "//input[contains(@name, 'password')]"),
            (By.XPATH, "//input[contains(@id, 'password')]"),
            (By.XPATH, "//input[contains(@aria-label, 'password')]"),
            (By.XPATH, "//input[contains(@placeholder, 'password')]"),
            (By.XPATH, "//input[@autocomplete='new-password']"),
            (By.XPATH, "//input[@autocomplete='current-password']"),
            (By.XPATH, "//input[contains(@class, 'password')]"),
            (By.XPATH, "//input[contains(@data-testid, 'password')]"),
        ]
        
        for selector_type, selector_value in extended_selectors:
            try:
                password_element = WebDriverWait(driver, 0.4).until(  # Faster
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if password_element and password_element.is_displayed():
                    print(f"🔒 Password stage detected (Extended): {selector_value}")
                    return True
            except:
                continue
        
        # STRATEGY 3: URL-based detection (fast fallback)
        try:
            current_url = driver.current_url.lower()  
            password_url_indicators = [
                "password",
                "createpassword",
                "passwd", 
                "security",
                "signin/v2/challenge/pwd",
                "challenge/pwd"
            ]
            
            for indicator in password_url_indicators:
                if indicator in current_url:
                    print(f"🔒 Password stage detected (URL): {indicator}")
                    return True
        except:
            pass
        
        # STRATEGY 4: Page title/heading detection
        try:
            page_title = driver.title.lower()
            title_indicators = ["password", "create password", "choose password"]
            
            for indicator in title_indicators:
                if indicator in page_title:
                    print(f"🔒 Password stage detected (Title): {indicator}")
                    return True
        except:
            pass
        
        # STRATEGY 5: Critical text analysis (last resort)
        try:
            # Get page source with timeout
            page_source = driver.page_source.lower()
            
            # Critical password indicators (high confidence)
            critical_indicators = [
                "create a strong password",
                "choose a strong password",
                "create your password", 
                "password must be",
                "confirm your password",
                "strong password",
                '"passwd"',
                'name="passwd"',
                'id="passwd"'
            ]
            
            for indicator in critical_indicators:
                if indicator in page_source:
                    print(f"🔒 Password stage detected (Critical Text): {indicator}")
                    return True
        except:
            pass
        
        # STRATEGY 6: Button-based detection
        try:
            password_buttons = [
                "//button[contains(text(), 'Create')]",
                "//button[contains(@id, 'password')]", 
                "//span[contains(text(), 'Create password')]",
                "//div[contains(text(), 'Create a strong password')]"
            ]
            
            for button_selector in password_buttons:
                try:
                    button_element = WebDriverWait(driver, 0.2).until(  # Ultra fast
                        EC.presence_of_element_located((By.XPATH, button_selector))
                    )
                    if button_element and button_element.is_displayed():
                        print(f"🔒 Password stage detected (Button)")
                        return True
                except:
                    continue
        except:
            pass
        
        return False
        
    except Exception as e:
        # Silent handling - no spam logs
        return False

def detect_recovery_stage(driver):
    """Deteksi apakah sudah sampai di tahap recovery/verification"""
    try:
        # ENHANCED: Multiple XPATH strategies for 'Lewati' and 'Next'
        recovery_selectors = [
            # Strategy 1: Span text selectors (primary)
            (By.XPATH, "//span[contains(text(), 'Lewati')]"),
            (By.XPATH, "//span[contains(text(), 'Next')]"),
            
            # Strategy 2: Button with span text (secondary)
            (By.XPATH, "//button[.//span[contains(text(), 'Lewati')]]"),
            (By.XPATH, "//button[.//span[contains(text(), 'Next')]]"),
            
            # Strategy 3: Case-insensitive text matching
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'lewati')]"),
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
            
            # Strategy 4: Fallback to original ID selector
            (By.ID, "recoveryNext"),
            (By.ID, "recoverySkip")
        ]
        
        # Check each selector quickly
        for selector_type, selector_value in recovery_selectors:
            try:
                element = WebDriverWait(driver, 0.5).until(  # Fast check
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if element and element.is_displayed():
                    print(f"📱 Recovery stage detected via: {selector_value}")
                    return True
            except:
                continue
        
        # Additional recovery stage indicators (optimized)
        additional_selectors = [
            (By.XPATH, "//input[contains(@name, 'phone')]"),
            (By.XPATH, "//input[contains(@name, 'recovery')]"),
            (By.XPATH, "//input[contains(@placeholder, 'phone')]"),
            (By.XPATH, "//input[contains(@aria-label, 'phone')]"),
        ]
        
        for selector_type, selector_value in additional_selectors:
            try:
                element = WebDriverWait(driver, 0.6).until(  # Faster
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if element and element.is_displayed():
                    print("📱 Recovery stage detected via input field")
                    return True
            except:
                continue
        
        # Text-based detection (faster)
        try:
            page_text = driver.page_source.lower()
            recovery_indicators = [
                "recovery phone",
                "verify your",
                "phone number", 
                "verification",
                "recovery option",
                "add phone number",
                "lewati",
                "skip"
            ]
            
            for indicator in recovery_indicators:
                if indicator in page_text:
                    print(f"📱 Recovery stage detected via text: {indicator}")
                    return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"⚠️ Recovery detection error: {e}")
        return False

# ============= NEW EXTENDED STAGE FUNCTIONS =============

def detect_email_extraction_stage(driver):
    """Deteksi apakah sudah sampai di tahap email extraction"""
    try:
        # Check untuk elemen dengan data-email attribute
        email_selectors = [
            (By.XPATH, "//*[@data-email]"),
            (By.XPATH, "//div[@data-email]"),
            (By.XPATH, "//span[@data-email]"),
            (By.XPATH, "//input[@data-email]"),
            (By.XPATH, "//p[@data-email]"),
        ]
        
        for selector_type, selector_value in email_selectors:
            try:
                email_element = WebDriverWait(driver, 0.8).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if email_element and email_element.is_displayed():
                    print(f"📧 Email extraction stage detected via: {selector_value}")
                    return True
            except:
                continue
        
        # Tambahan: Cek berdasarkan text content
        try:
            page_text = driver.page_source.lower()
            email_indicators = [
                "your gmail address",
                "your new email",
                "gmail address created",
                "email address is"
            ]
            
            for indicator in email_indicators:
                if indicator in page_text:
                    print(f"📧 Email extraction stage detected via text: {indicator}")
                    return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"⚠️ Email extraction detection error: {e}")
        return False

def detect_terms_agreement_stage(driver):
    """Deteksi apakah sudah sampai di tahap terms agreement"""
    try:
        # Check untuk terms agreement elements
        terms_selectors = [
            (By.XPATH, "//span[contains(text(), 'Saya Setuju')]"),
            (By.XPATH, "//span[contains(text(), 'Saya setuju')]"),
            (By.XPATH, "//span[contains(text(), 'I Accept')]"),
            (By.XPATH, "//span[contains(text(), 'I accept')]"),
            (By.XPATH, "//button[contains(text(), 'Saya Setuju')]"),
            (By.XPATH, "//button[contains(text(), 'Saya setuju')]"),
            (By.XPATH, "//button[contains(text(), 'I Accept')]"),
            (By.XPATH, "//button[contains(text(), 'I accept')]"),
        ]
        
        for selector_type, selector_value in terms_selectors:
            try:
                terms_element = WebDriverWait(driver, 0.8).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if terms_element and terms_element.is_displayed():
                    print(f"📋 Terms agreement stage detected via: {selector_value}")
                    return True
            except:
                continue
        
        # Tambahan: Cek berdasarkan text content
        try:
            page_text = driver.page_source.lower()
            terms_indicators = [
                "terms of service",
                "privacy policy",
                "terms and conditions",
                "accept terms",
                "agree to terms"
            ]
            
            for indicator in terms_indicators:
                if indicator in page_text:
                    print(f"📋 Terms agreement stage detected via text: {indicator}")
                    return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"⚠️ Terms agreement detection error: {e}")
        return False

def enhanced_stage5_email_extraction(driver, data):
    """NEW STAGE 5: Email extraction dengan data-email attribute"""
    print("📧 STAGE 5: Enhanced Email Extraction")
    
    try:
        # Wait for email extraction page to be fully loaded
        WebDriverWait(driver, 4).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(UnifiedTiming.quick_read(2))
        
        # Find email element dengan data-email attribute
        email_selectors = [
            (By.XPATH, "//*[@data-email]"),
            (By.XPATH, "//div[@data-email]"),
            (By.XPATH, "//span[@data-email]"),
            (By.XPATH, "//input[@data-email]"),
            (By.XPATH, "//p[@data-email]"),
        ]
        
        email_element = None
        email_text = None
        
        for selector_type, selector_value in email_selectors:
            try:
                email_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if email_element and email_element.is_displayed():
                    # Get email dari data-email attribute
                    email_text = email_element.get_attribute("data-email")
                    if not email_text:
                        # Fallback: get text content
                        email_text = email_element.text.strip()
                    
                    if email_text and "@" in email_text:
                        print(f"✅ Email element found: {selector_value}")
                        break
            except:
                continue
        
        if not email_text:
            print("⚠️ Email element with data-email not found, trying alternative methods...")
            
            # Alternative: Look for email patterns in page
            try:
                import re
                page_source = driver.page_source
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, page_source)
                
                if emails:
                    # Get the first Gmail address found
                    gmail_emails = [email for email in emails if "gmail.com" in email.lower()]
                    if gmail_emails:
                        email_text = gmail_emails[0]
                        print(f"✅ Email found via pattern matching: {email_text}")
            except:
                pass
        
        if email_text and "@" in email_text:
            # Copy email to clipboard
            pyperclip.copy(email_text)
            print(f"✅ Email copied to clipboard: {email_text}")
            
            # Store email in data for future use
            data["generated_email"] = email_text
            
            # Wait for review
            time.sleep(UnifiedTiming.quick_read(len(email_text)))
            
            # Click next button
            success = enhanced_next_button(driver, "genericNext")
            
            if success:
                print("✅ STAGE 5 completed successfully")
                return True
            else:
                print("⚠️ STAGE 5 next button issue, but continuing...")
                return True
        else:
            print("❌ No valid email found in this stage")
            return False
            
    except Exception as e:
        print(f"❌ STAGE 5 error: {str(e)}")
        return False

def enhanced_stage6_terms_agreement(driver, data):
    """NEW STAGE 6: Terms agreement dengan XPATH text selectors"""
    print("📋 STAGE 6: Enhanced Terms Agreement")
    
    try:
        # Wait for terms agreement page to be fully loaded
        WebDriverWait(driver, 4).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(UnifiedTiming.quick_read(2))
        
        # Find terms agreement button
        terms_selectors = [
            # Primary Indonesian selectors
            (By.XPATH, "//span[contains(text(), 'Saya Setuju')]"),
            (By.XPATH, "//span[contains(text(), 'Saya setuju')]"),
            (By.XPATH, "//button[contains(text(), 'Saya Setuju')]"),
            (By.XPATH, "//button[contains(text(), 'Saya setuju')]"),
            
            # Primary English selectors
            (By.XPATH, "//span[contains(text(), 'I Accept')]"),
            (By.XPATH, "//span[contains(text(), 'I accept')]"),
            (By.XPATH, "//button[contains(text(), 'I Accept')]"),
            (By.XPATH, "//button[contains(text(), 'I accept')]"),
            
            # Case-insensitive matching
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'saya setuju')]"),
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i accept')]"),
            
            # Additional variations
            (By.XPATH, "//span[contains(text(), 'Setuju')]"),
            (By.XPATH, "//span[contains(text(), 'Accept')]"),
            (By.XPATH, "//button[contains(text(), 'Setuju')]"),
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
        ]
        
        terms_button = None
        selected_strategy = None
        
        # Try each selector strategy
        for i, (selector_type, selector_value) in enumerate(terms_selectors):
            try:
                terms_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if terms_button:
                    selected_strategy = f"Strategy {i+1}: {selector_value}"
                    print(f"✅ Terms agreement button found using {selected_strategy}")
                    break
                    
            except TimeoutException:
                continue
        
        if terms_button:
            print("✅ Terms agreement button found - clicking automatically")
            
            # Click terms agreement button
            if bulletproof_element_interaction(driver, terms_button, "click"):
                print("✅ Terms agreement button clicked successfully")
                return True
            else:
                # Fallback to JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", terms_button)
                    print("✅ Terms agreement button clicked via JavaScript")
                    return True
                except Exception as e:
                    print(f"⚠️ JavaScript click failed: {e}")
        
        # If no terms button found, try generic next
        print("⚠️ No terms agreement button found, trying generic next...")
        success = enhanced_next_button(driver, "genericNext")
        
        if success:
            print("✅ STAGE 6 completed via generic next")
            return True
        else:
            print("⚠️ STAGE 6 - no suitable button found")
            return False
            
    except Exception as e:
        print(f"❌ STAGE 6 error: {str(e)}")
        return False

def generate_random_keys(length=8):
    """Generate random keyboard keys untuk confuse typing"""
    # Pool karakter yang aman untuk ketik
    char_pool = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(char_pool) for _ in range(length))

def fast_random_typing(element, length=8):
    """Ketik random keys dengan super optimized tempo"""
    random_text = generate_random_keys(length)
    
    for char in random_text:
        element.send_keys(char)
        # Super optimized fast typing dengan slight variation
        time.sleep(SuperOptimizedTiming.fast_typing_speed())
    
    return random_text

def enhanced_stage3_password(driver, data):
    """Enhanced Stage 3: Password handling dengan super optimized techniques"""
    print("🔒 STAGE 3: Enhanced Password Entry")
    
    try:
        # Wait for password page to be fully loaded (super optimized)
        WebDriverWait(driver, 4).until(  # Faster timeout
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(SuperOptimizedTiming.quick_read(1.5))  # Reduced from 2
        
        # Find password field (super optimized selectors)
        password_selectors = [
            (By.NAME, "Passwd"),
            (By.ID, "passwd"),
            (By.XPATH, "//input[@type='password'][1]"),
            (By.XPATH, "//input[contains(@name, 'password')][1]"),
        ]
        
        password_element = None
        for selector_type, selector_value in password_selectors:
            try:
                password_element = WebDriverWait(driver, 2).until(  # Faster
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                if password_element:
                    break
            except:
                continue
        
        if not password_element:
            print("⚠️ Password field not found")
            return False
        
        # Click password field
        if bulletproof_element_interaction(driver, password_element, "focus"):
            print("✅ Password field focused")
            
            # Copy password to clipboard
            pyperclip.copy(data["password"])
            time.sleep(SuperOptimizedTiming.micro_pause())
            
            # Paste password using Ctrl+V
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(SuperOptimizedTiming.swift_decision("simple"))
            print(f"✅ Password pasted: {data['password']}")
            
            # Send Tab key to move to confirm password field
            ActionChains(driver).send_keys(Keys.TAB).perform()
            time.sleep(SuperOptimizedTiming.swift_decision("simple"))
            print("✅ Moved to confirm password field")
            
            # Type random keys first (super optimized)
            active_element = driver.switch_to.active_element
            random_text = fast_random_typing(active_element, random.randint(6, 10))
            print(f"✅ Random keys typed: {random_text}")
            
            # Select all random text (Ctrl+A)
            time.sleep(SuperOptimizedTiming.swift_decision("simple"))
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(SuperOptimizedTiming.micro_pause())
            print("✅ Random text selected")
            
            # Paste correct password (Ctrl+V)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(SuperOptimizedTiming.swift_decision("simple"))
            print(f"✅ Correct password pasted in confirm field")
            
            # Review period (super optimized)
            time.sleep(SuperOptimizedTiming.quick_read(3))  # Reduced from 4
            
            # Click Next button using enhanced XPATH selectors
            success = enhanced_next_button(driver, "passwordNext")
            
            if success:
                print("✅ STAGE 3 completed successfully")
                return True
            else:
                print("⚠️ STAGE 3 next button issue, but continuing...")
                return True
                
    except Exception as e:
        print(f"❌ STAGE 3 error: {str(e)}")
        return False

def enhanced_stage4_recovery(driver, data):
    """Enhanced Stage 4: Recovery dengan XPATH text selectors untuk 'Lewati' dan 'Next'"""
    print("📱 STAGE 4: Enhanced Recovery with XPATH Text Selectors")
    
    try:
        # Wait for recovery page to be fully loaded (super optimized)
        WebDriverWait(driver, 3.5).until(  # Faster timeout
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(SuperOptimizedTiming.quick_read(1.2))  # Reduced from 1.5
        
        # ENHANCED: Multiple XPATH strategies for 'Lewati' and 'Next'
        recovery_selectors = [
            # Strategy 1: Span text selectors (primary)
            (By.XPATH, "//span[contains(text(), 'Lewati')]"),
            (By.XPATH, "//span[contains(text(), 'Next')]"),
            
            # Strategy 2: Button with span text (secondary)
            (By.XPATH, "//button[.//span[contains(text(), 'Lewati')]]"),
            (By.XPATH, "//button[.//span[contains(text(), 'Next')]]"),
            
            # Strategy 3: Case-insensitive text matching
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'lewati')]"),
            (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
            
            # Strategy 4: Additional text variations
            (By.XPATH, "//span[contains(text(), 'Skip')]"),
            (By.XPATH, "//button[contains(text(), 'Skip')]"),
            (By.XPATH, "//button[contains(text(), 'Lewati')]"),
            (By.XPATH, "//button[contains(text(), 'Next')]"),
            
            # Strategy 5: Fallback to original ID selector
            (By.ID, "recoveryNext"),
            (By.ID, "recoverySkip")
        ]
        
        recovery_button = None
        selected_strategy = None
        
        # Try each selector strategy with fast timeouts
        for i, (selector_type, selector_value) in enumerate(recovery_selectors):
            try:
                recovery_button = WebDriverWait(driver, 1.5).until(  # Fast timeout per strategy
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if recovery_button:
                    selected_strategy = f"Strategy {(i//2)+1}: {selector_value}"
                    print(f"✅ Recovery button found using {selected_strategy}")
                    break
                    
            except TimeoutException:
                continue
        
        if recovery_button:
            print("✅ Recovery button found - clicking automatically")
            
            # Click recovery button
            if bulletproof_element_interaction(driver, recovery_button, "click"):
                print("✅ Recovery button clicked successfully")
                return True
            else:
                # Fallback to JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", recovery_button)
                    print("✅ Recovery button clicked via JavaScript")
                    return True
                except Exception as e:
                    print(f"⚠️ JavaScript click failed: {e}")
        
        # If no recovery button found, continue to next stages
        print("⚠️ No recovery button found - continuing to next stages...")
        return True
        
    except Exception as e:
        print(f"❌ STAGE 4 error: {str(e)}")
        return False

# ============= ENHANCED STAGE FUNCTIONS =============

def enhanced_stage1_name(driver, data):
    """Enhanced Stage 1: Name entry dengan bulletproof error handling"""
    print("👤 STAGE 1: Enhanced Name Entry")
    
    try:
        # Optimized page preparation - REDUCED DELAY
        time.sleep(UnifiedTiming.quick_read(2))
        enhanced_page_exploration(driver)
        
        # Enhanced first name interaction
        first_name_elem = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.ID, "firstName"))
        )
        
        if bulletproof_element_interaction(driver, first_name_elem, "focus"):
            advanced_natural_typing(first_name_elem, data["first_name"], "adaptive")
            print(f"✅ First name entered: {data['first_name']}")
        
        time.sleep(UnifiedTiming.swift_decision("simple"))  # Jeda setelah first name
        
        # Enhanced last name interaction
        last_name_elem = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.ID, "lastName"))
        )
        
        if bulletproof_element_interaction(driver, last_name_elem, "focus"):
            advanced_natural_typing(last_name_elem, data["last_name"], "adaptive")
            print(f"✅ Last name entered: {data['last_name']}")
        
        # Enhanced review period
        time.sleep(UnifiedTiming.quick_read(len(data["first_name"] + data["last_name"])))
        
        success = enhanced_next_button(driver, "collectNameNext")
        
        if success:
            print("✅ STAGE 1 completed successfully")
            return True
        else:
            print("⚠️ STAGE 1 next button issue, but continuing...")
            return True
    
    except Exception as e:
        print(f"❌ STAGE 1 error: {str(e)}")
        return False

def enhanced_stage2_birth_gender(driver, data):
    """Enhanced Stage 2: Birth & Gender dengan final protection"""
    print("📅 STAGE 2: Enhanced Birth & Gender")
    
    try:
        WebDriverWait(driver, 4).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(UnifiedTiming.quick_read(4))
        
        # Enhanced day field handling
        day_selectors = [(By.ID, "day"), (By.NAME, "day")]
        day_filled = False
        
        for selector_type, selector_value in day_selectors:
            try:
                day_element = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if day_element:
                    if bulletproof_element_interaction(driver, day_element, "focus"):
                        advanced_natural_typing(day_element, data["day"], "careful")
                        day_filled = True
                        print(f"✅ Day entered: {data['day']}")
                        break
            except:
                continue
        
        # Enhanced month dropdown
        time.sleep(UnifiedTiming.swift_decision("simple"))  # Jeda setelah day
        month_success = enhanced_dropdown_selection(driver, "Month", data["month"])
        if month_success:
            print(f"✅ Month selected: {data['month']}")
        
        # Enhanced year field handling
        time.sleep(UnifiedTiming.swift_decision("simple"))  # Jeda setelah month
        year_selectors = [(By.ID, "year"), (By.NAME, "year")]
        year_filled = False
        
        for selector_type, selector_value in year_selectors:
            try:
                year_element = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                
                if year_element:
                    if bulletproof_element_interaction(driver, year_element, "focus"):
                        advanced_natural_typing(year_element, data["year"], "careful")
                        year_filled = True
                        print(f"✅ Year entered: {data['year']}")
                        break
            except:
                continue
        
        # Enhanced gender dropdown
        time.sleep(UnifiedTiming.swift_decision("simple"))  # Jeda setelah year
        gender_success = enhanced_dropdown_selection(driver, "Gender", data["gender"])
        if gender_success:
            print(f"✅ Gender selected: {data['gender']}")
        
        # Final review and proceed
        time.sleep(UnifiedTiming.quick_read(2))
        success = enhanced_next_button(driver, "birthdaygenderNext")
        
        if success and day_filled and year_filled:
            print("✅ STAGE 2 completed successfully")
            return True
        else:
            print("⚠️ STAGE 2 partial success")
            return True
    
    except Exception as e:
        print(f"❌ STAGE 2 error: {str(e)}")
        return False

# ============= MAIN EXECUTION WITH EXTENDED STAGES =============

def main():
    """EXTENDED MAIN: All 6 stages + Auto completion detection"""
    global gl, profile_id, driver, cleanup_completed, browser_monitor_active
    
    gl = None
    profile_id = None
    driver = None
    cleanup_completed = False
    browser_monitor_active = False

    subprocess.run(["warp-cli", "connect"])
    
    # Validate GoLogin token
    if not GOLOGIN_TOKEN:
        print("❌ GOLOGIN_TOKEN is not set!")
        print("🔧 Please set your GoLogin API token in the script")
        return
    
    user_data = get_user_data()
    start_time = time.time()
    
    try:
        print("\n🚀 EXTENDED GMAIL AUTOMATION")
        
        # Step 1: Initialize GoLogin dan LANGSUNG buka halaman signup
        print(f"\n{'='*60}")
        print("🎭 STEP 1: DIRECT GOLOGIN + SIGNUP INITIALIZATION")
        print("="*60)
        print("🔧 Initializing GoLogin...")
        
        gl = GoLogin({
            "token": GOLOGIN_TOKEN,
        })
        
        print("📝 Creating profile...")
        profile = gl.createProfileRandomFingerprint({"os": "win"})
        profile_id = profile.get('id')
        print(f"✅ Profile: {profile_id}")
        
        gl.setProfileId(profile_id)
        
        print("🚀 Starting browser...")
        debugger_address = gl.start()
        print(f"✅ Browser started")
        
        # Register resources
        resource_manager.set_gologin(gl, profile_id)
        
        # Step 2: Connect Selenium dan LANGSUNG navigate
        print(f"\n{'='*60}")
        print("🔗 STEP 2: DIRECT SELENIUM CONNECTION + NAVIGATION")
        print("="*60)
        print("⚙️ Connecting Selenium...")
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        driver = webdriver.Chrome(options=chrome_options)
        resource_manager.set_driver(driver)
        
        print("🌐 NAVIGATING DIRECTLY TO SIGNUP PAGE...")
        driver.get("https://accounts.google.com/signup")
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        print("✅ Gmail signup page loaded!")
        
        # Step 3: Start enhanced browser monitoring with completion detection
        print("🔍 Starting enhanced browser monitoring with auto-completion detection...")
        start_browser_monitor()
        
        # Step 4: Execute ALL extended automation stages
        print(f"\n{'='*60}")
        print("🎯 STEP 3: EXTENDED AUTOMATION EXECUTION (6 STAGES)")
        print("="*60)
        
        stages_results = {}
        
        # Stage 1: Name Entry
        stages_results["stage1"] = enhanced_stage1_name(driver, user_data)
        time.sleep(UnifiedTiming.swift_decision("medium"))
        
        # Stage 2: Birth & Gender
        stages_results["stage2"] = enhanced_stage2_birth_gender(driver, user_data)
        time.sleep(UnifiedTiming.swift_decision("medium"))
        
        # Stage 3: Username Detection & Manual Input
        print(f"\n{'='*60}")
        print("🎯 STEP 4: USERNAME & PASSWORD & RECOVERY & EXTENDED STAGES")
        print("="*60)
        
        # Wait sampai detect username stage
        username_detected = False
        max_wait = 45
        wait_start = time.time()
        
        while time.time() - wait_start < max_wait:
            if detect_username_stage(driver):
                username_detected = True
                break
            time.sleep(1.2)
        
        if username_detected:
            # Wait for manual username input
            if wait_for_manual_username_input(driver):
                # Stage 3: Password Automation
                stages_results["stage3"] = enhanced_stage3_password(driver, user_data)
            else:
                print("⚠️ Username stage timeout")
                stages_results["stage3"] = False
        else:
            print("⚠️ Username stage not detected, checking for password stage directly")
            if bulletproof_detect_password_stage(driver):
                stages_results["stage3"] = enhanced_stage3_password(driver, user_data)
            else:
                stages_results["stage3"] = False
        
        # Stage 4: Recovery/Verification Handling
        time.sleep(SuperOptimizedTiming.swift_decision("medium"))
        
        recovery_detected = False
        max_wait_recovery = 20
        wait_start_recovery = time.time()
        
        while time.time() - wait_start_recovery < max_wait_recovery:
            if detect_recovery_stage(driver):
                recovery_detected = True
                break
            time.sleep(0.6)
        
        if recovery_detected:
            stages_results["stage4"] = enhanced_stage4_recovery(driver, user_data)
        else:
            print("⚠️ Recovery stage not detected - continuing to next stages...")
            stages_results["stage4"] = True  # Mark as success to continue
        
        # ============= NEW EXTENDED STAGES =============
        
        # Stage 5: Email Extraction
        time.sleep(UnifiedTiming.swift_decision("medium"))
        
        email_detected = False
        max_wait_email = 15
        wait_start_email = time.time()
        
        while time.time() - wait_start_email < max_wait_email:
            if detect_email_extraction_stage(driver):
                email_detected = True
                break
            time.sleep(0.8)
        
        if email_detected:
            stages_results["stage5"] = enhanced_stage5_email_extraction(driver, user_data)
        else:
            print("⚠️ Email extraction stage not detected - continuing...")
            stages_results["stage5"] = True  # Mark as success to continue
        
        # Stage 6: Terms Agreement
        time.sleep(UnifiedTiming.swift_decision("medium"))
        
        terms_detected = False
        max_wait_terms = 15
        wait_start_terms = time.time()
        
        while time.time() - wait_start_terms < max_wait_terms:
            if detect_terms_agreement_stage(driver):
                terms_detected = True
                break
            time.sleep(0.8)
        
        if terms_detected:
            stages_results["stage6"] = enhanced_stage6_terms_agreement(driver, user_data)
        else:
            print("⚠️ Terms agreement stage not detected - may have completed...")
            stages_results["stage6"] = True  # Mark as success

        # Results
        execution_time = time.time() - start_time
        success_count = sum(1 for result in stages_results.values() if result)
        
        print(f"\n{'='*80}")
        print("🎉 EXTENDED AUTOMATION COMPLETED")
        print("="*80)
        print(f"✅ Profile: {user_data['first_name']} {user_data['last_name']} | {user_data['gender']}")
        print(f"📅 Birth: {user_data['day']} {user_data['month']} {user_data['year']}")
        print(f"🔒 Password: {user_data['password']}")
        if "generated_email" in user_data:
            print(f"📧 Generated Email: {user_data['generated_email']}")
        print(f"⏱️ Time: {execution_time:.2f} seconds")
        print(f"📊 Stages: {success_count}/{len(stages_results)} completed")
        print(f"🎭 Profile: {profile_id}")
        print("🖱️ Complete any remaining steps manually (if any)")
        print("🔍 Monitoring active - will auto-cleanup when completion detected")
        print("✨ Waiting for completion URL: myaccount.google.com")
        print("❌ Or close this script manually when done")
        
        # Keep browser open with monitoring (will auto-cleanup on completion)
        try:
            input("\nPress Enter to cleanup and exit (or wait for auto-completion)...")
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
    
    except KeyboardInterrupt:
        print("\n⏹️ Automation interrupted")
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        print("🔧 Safe cleanup initiated...")
    finally:
        # Cleanup
        stop_browser_monitor()
        
        if not cleanup_completed:
            resource_manager.safe_cleanup()
            cleanup_completed = True

if __name__ == "__main__":
    if not GOLOGIN_TOKEN:
        print("⚠️ Please set your GoLogin API token in GOLOGIN_TOKEN variable")
        sys.exit(1)
    
    main()