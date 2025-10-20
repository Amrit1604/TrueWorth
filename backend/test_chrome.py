#!/usr/bin/env python3
"""
Test script to check Chrome and driver setup
"""
import sys

def test_chrome_setup():
    print("🔧 Testing Chrome setup...")

    # Test 1: Check if Chrome is installed
    try:
        import subprocess
        result = subprocess.run(['chrome', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Chrome found: {result.stdout.strip()}")
        else:
            print("❌ Chrome not found in PATH")
    except Exception as e:
        print(f"⚠️ Chrome check failed: {e}")

    # Test 2: Check selenium import
    try:
        import selenium
        print(f"✅ Selenium imported: {selenium.__version__}")
    except Exception as e:
        print(f"❌ Selenium import failed: {e}")
        return False

    # Test 3: Check webdriver manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ WebDriver Manager imported")
    except Exception as e:
        print(f"❌ WebDriver Manager import failed: {e}")
        return False

    # Test 4: Try to download driver
    try:
        print("📥 Attempting to download Chrome driver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ Driver downloaded to: {driver_path}")
    except Exception as e:
        print(f"❌ Driver download failed: {e}")
        return False

    # Test 5: Try to create driver instance
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        print("🚀 Testing Chrome driver creation...")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        print("✅ Chrome driver created successfully!")

        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Navigation test passed: {title}")

        driver.quit()
        print("✅ Driver cleanup successful")

        return True

    except Exception as e:
        print(f"❌ Driver creation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_setup()
    if success:
        print("\n🎉 Chrome setup is working! You can run the main app.")
    else:
        print("\n❌ Chrome setup has issues. Check the errors above.")
        print("\n💡 Try these solutions:")
        print("   1. Install/update Chrome browser")
        print("   2. Run as administrator")
        print("   3. Disable antivirus temporarily")
        print("   4. Clear driver cache: rmdir /s %USERPROFILE%\\.wdm")

    sys.exit(0 if success else 1)
