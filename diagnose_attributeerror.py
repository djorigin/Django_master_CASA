#!/usr/bin/env python3
"""
Django Model AttributeError Diagnostic Script

This script comprehensively tests all scenarios that could trigger:
'AttributeError: 'str' object has no attribute '_meta'

Common causes:
1. Unquoted foreign key references in models
2. Circular import issues during model loading
3. Admin configuration problems with inline models
4. Migration files with incorrect model references
"""

import os
import sys
import django
from django.apps import apps
from django.core.management import execute_from_command_line

# Ensure we're using the correct Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'darklightMETA_studio.settings')

def test_django_setup():
    """Test basic Django setup and app loading"""
    print("🔍 Testing Django setup and app loading...")
    try:
        django.setup()
        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_model_imports():
    """Test importing all models to catch AttributeError during model resolution"""
    print("\n🔍 Testing model imports...")
    
    apps_to_test = [
        'accounts',
        'aircraft', 
        'airspace',
        'core',
        'flight_operations',
        'incidents',
        'maintenance'
    ]
    
    for app_name in apps_to_test:
        try:
            print(f"  Testing {app_name} models...")
            models_module = __import__(f'{app_name}.models', fromlist=[''])
            
            # Get all model classes
            model_classes = []
            for attr_name in dir(models_module):
                attr = getattr(models_module, attr_name)
                if (hasattr(attr, '__bases__') and 
                    any('Model' in base.__name__ for base in attr.__bases__)):
                    model_classes.append(attr)
            
            print(f"    ✅ Loaded {len(model_classes)} models from {app_name}")
            
        except Exception as e:
            print(f"    ❌ Failed to import {app_name}.models: {e}")
            return False
    
    return True

def test_admin_loading():
    """Test admin interface loading which often triggers AttributeError"""
    print("\n🔍 Testing admin interface loading...")
    try:
        from django.contrib import admin
        admin.autodiscover()
        
        # Test loading admin for each app
        from core import admin as core_admin
        from accounts import admin as accounts_admin
        from maintenance import admin as maintenance_admin
        
        print("✅ All admin modules loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Admin loading failed: {e}")
        return False

def test_model_meta_access():
    """Test accessing _meta on all models to catch 'str' object issues"""
    print("\n🔍 Testing model._meta access...")
    try:
        all_models = apps.get_models()
        for model in all_models:
            # This will fail if model is a string instead of model class
            meta = model._meta
            app_label = meta.app_label
            model_name = meta.model_name
            
        print(f"✅ Successfully accessed _meta on {len(all_models)} models")
        return True
    except AttributeError as e:
        if "'str' object has no attribute '_meta'" in str(e):
            print(f"❌ Found the AttributeError: {e}")
            return False
        else:
            print(f"❌ Different AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error accessing model._meta: {e}")
        return False

def test_foreign_key_resolution():
    """Test that all foreign key relationships can be resolved properly"""
    print("\n🔍 Testing foreign key resolution...")
    try:
        all_models = apps.get_models()
        fk_count = 0
        
        for model in all_models:
            for field in model._meta.get_fields():
                if hasattr(field, 'related_model') and field.related_model:
                    fk_count += 1
                    # Try to access the related model's _meta
                    related_meta = field.related_model._meta
        
        print(f"✅ Successfully resolved {fk_count} foreign key relationships")
        return True
    except AttributeError as e:
        if "'str' object has no attribute '_meta'" in str(e):
            print(f"❌ Foreign key resolution AttributeError: {e}")
            return False
        else:
            print(f"❌ Other AttributeError in FK resolution: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error in FK resolution: {e}")
        return False

def test_system_checks():
    """Run Django system checks"""
    print("\n🔍 Running Django system checks...")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        output = StringIO()
        call_command('check', stdout=output, stderr=output)
        result = output.getvalue()
        
        if "System check identified no issues" in result:
            print("✅ Django system check passed")
            return True
        else:
            print(f"❌ Django system check issues: {result}")
            return False
    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False

def scan_for_problematic_patterns():
    """Scan code for patterns that commonly cause AttributeError"""
    print("\n🔍 Scanning for problematic code patterns...")
    
    import glob
    import re
    
    # Patterns that cause AttributeError
    problematic_patterns = [
        (r'models\.ForeignKey\(\s*[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_]', 'Unquoted dot notation in ForeignKey'),
        (r'models\.ForeignKey\(\s*self\s*,', 'Unquoted self reference in ForeignKey'),
        (r'models\.OneToOneField\(\s*[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_]', 'Unquoted dot notation in OneToOneField'),
        (r'models\.ManyToManyField\(\s*[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_]', 'Unquoted dot notation in ManyToManyField'),
    ]
    
    issues_found = []
    
    # Scan all Python files
    for py_file in glob.glob('**/*.py', recursive=True):
        if 'venv' in py_file or '__pycache__' in py_file:
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern, description in problematic_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues_found.append({
                        'file': py_file,
                        'line': line_num,
                        'pattern': description,
                        'match': match.group(0)
                    })
        except Exception as e:
            print(f"  Warning: Could not scan {py_file}: {e}")
    
    if issues_found:
        print(f"❌ Found {len(issues_found)} problematic patterns:")
        for issue in issues_found:
            print(f"  {issue['file']}:{issue['line']} - {issue['pattern']}")
            print(f"    Match: {issue['match']}")
        return False
    else:
        print("✅ No problematic patterns found")
        return True

def main():
    """Run comprehensive AttributeError diagnostic"""
    print("🚀 Django AttributeError Comprehensive Diagnostic")
    print("=" * 60)
    
    tests = [
        ("Django Setup", test_django_setup),
        ("Model Imports", test_model_imports), 
        ("Admin Loading", test_admin_loading),
        ("Model Meta Access", test_model_meta_access),
        ("Foreign Key Resolution", test_foreign_key_resolution),
        ("System Checks", test_system_checks),
        ("Code Pattern Scan", scan_for_problematic_patterns),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 DIAGNOSTIC SUMMARY")
    print(f"{'=' * 60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! No AttributeError issues detected.")
        print("Your Django project appears to be correctly configured.")
    else:
        print("⚠️  Some issues detected. Review the failed tests above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())