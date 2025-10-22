#!/usr/bin/env python3
"""
CI/CD Environment Simulation Script

Simulates common CI/CD deployment steps that might trigger AttributeError
Tests with different Django settings and environment conditions
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_with_ci_settings():
    """Test with CI-specific Django settings"""
    print("🔍 Testing with CI settings...")
    
    # Save original settings
    original_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
    
    try:
        # Try with CI test settings
        os.environ['DJANGO_SETTINGS_MODULE'] = 'darklightMETA_studio.ci_test_settings'
        
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--deploy'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CI settings check passed")
            return True
        else:
            print(f"❌ CI settings check failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CI settings check timed out")
        return False
    except Exception as e:
        print(f"❌ CI settings test error: {e}")
        return False
    finally:
        # Restore original settings
        if original_settings:
            os.environ['DJANGO_SETTINGS_MODULE'] = original_settings
        else:
            os.environ.pop('DJANGO_SETTINGS_MODULE', None)

def test_collectstatic_deployment():
    """Test collectstatic which often triggers model loading issues"""
    print("\n🔍 Testing collectstatic deployment step...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput', '--dry-run'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Collectstatic test passed")
            return True
        else:
            print(f"❌ Collectstatic failed: {result.stderr}")
            if "AttributeError" in result.stderr:
                print("🎯 Found AttributeError in collectstatic!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Collectstatic timed out")
        return False
    except Exception as e:
        print(f"❌ Collectstatic test error: {e}")
        return False

def test_makemigrations_check():
    """Test makemigrations which can trigger model resolution issues"""
    print("\n🔍 Testing makemigrations check...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'makemigrations', '--check', '--dry-run'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Makemigrations check passed")
            return True
        else:
            print(f"❌ Makemigrations check failed: {result.stderr}")
            if "AttributeError" in result.stderr:
                print("🎯 Found AttributeError in makemigrations!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Makemigrations check timed out")
        return False
    except Exception as e:
        print(f"❌ Makemigrations test error: {e}")
        return False

def test_shell_import_all():
    """Test importing everything in Django shell"""
    print("\n🔍 Testing comprehensive shell imports...")
    
    import_script = '''
import django
django.setup()

# Import all models
from accounts.models import *
from aircraft.models import *
from airspace.models import *
from core.models import *
from flight_operations.models import *
from incidents.models import *
from maintenance.models import *

# Import all admin
from accounts.admin import *
from aircraft.admin import *
from core.admin import *
from maintenance.admin import *

# Test model introspection
from django.apps import apps
for model in apps.get_models():
    _ = model._meta
    for field in model._meta.get_fields():
        if hasattr(field, "related_model") and field.related_model:
            _ = field.related_model._meta

print("All imports and introspection successful")
'''
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c', import_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "successful" in result.stdout:
            print("✅ Shell import test passed")
            return True
        else:
            print(f"❌ Shell import failed: {result.stderr}")
            if "AttributeError" in result.stderr:
                print("🎯 Found AttributeError in shell imports!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Shell import timed out")
        return False
    except Exception as e:
        print(f"❌ Shell import test error: {e}")
        return False

def test_wsgi_loading():
    """Test WSGI application loading"""
    print("\n🔍 Testing WSGI application loading...")
    
    wsgi_script = '''
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'darklightMETA_studio.settings')

try:
    application = get_wsgi_application()
    print("WSGI application loaded successfully")
except Exception as e:
    print(f"WSGI loading failed: {e}")
    raise
'''
    
    try:
        result = subprocess.run([
            sys.executable, '-c', wsgi_script
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "successfully" in result.stdout:
            print("✅ WSGI loading test passed")
            return True
        else:
            print(f"❌ WSGI loading failed: {result.stderr}")
            if "AttributeError" in result.stderr:
                print("🎯 Found AttributeError in WSGI loading!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ WSGI loading timed out")
        return False
    except Exception as e:
        print(f"❌ WSGI loading test error: {e}")
        return False

def main():
    """Run CI/CD simulation tests"""
    print("🚀 CI/CD Environment Simulation")
    print("=" * 50)
    
    tests = [
        ("CI Settings Check", test_with_ci_settings),
        ("Collectstatic Deployment", test_collectstatic_deployment),
        ("Makemigrations Check", test_makemigrations_check),
        ("Shell Import All", test_shell_import_all),
        ("WSGI Loading", test_wsgi_loading),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 CI/CD SIMULATION SUMMARY")
    print(f"{'=' * 50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CI/CD simulation tests passed!")
        print("No AttributeError issues in deployment scenarios.")
    else:
        print("⚠️  Some CI/CD tests failed - potential deployment issues.")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())