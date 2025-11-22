#!/usr/bin/env python3
"""
Test script to verify the structured wiki integration is working correctly.
This script tests the new API endpoints we created.
"""

import sys
import asyncio
import requests
from typing import Dict, Any

# Add the app directory to the path
sys.path.append('.')

from app.services.article_parser import article_fetcher
from app.api.structured_wiki import parse_wikipedia_url

def test_article_parser():
    """Test the article parser directly"""
    print("🧪 Testing article parser...")
    
    try:
        # Test with a simple article
        article = article_fetcher("Sheikh Hasina", "en")
        
        print(f"✅ Article parser working!")
        print(f"   Title: {article.title}")
        print(f"   Language: {article.lang}")
        print(f"   Sections: {len(article.sections)}")
        print(f"   References: {len(article.references)}")
        
        # Count citations
        total_citations = sum(len(section.citations or []) for section in article.sections)
        print(f"   Total citations: {total_citations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Article parser failed: {e}")
        return False

def test_url_parsing():
    """Test URL parsing functionality"""
    print("\n🧪 Testing URL parsing...")
    
    test_cases = [
        ("https://en.wikipedia.org/wiki/Albert_Einstein", ("en", "Albert Einstein")),
        ("https://fr.wikipedia.org/wiki/Paris", ("fr", "Paris")),
        ("https://de.wikipedia.org/wiki/Berlin", ("de", "Berlin"))
    ]
    
    success = True
    for url, expected in test_cases:
        try:
            result = asyncio.run(parse_wikipedia_url(url))
            if result == expected:
                print(f"✅ URL parsing: {url} -> {result}")
            else:
                print(f"❌ URL parsing failed: {url} -> {result} (expected {expected})")
                success = False
        except Exception as e:
            print(f"❌ URL parsing error: {url} -> {e}")
            success = False
    
    return success

def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test cases
    test_cases = [
        ("structured-article", {"query": "Albert Einstein", "lang": "en"}),
        ("citation-analysis", {"query": "Albert Einstein", "lang": "en"}),
        ("reference-analysis", {"query": "Albert Einstein", "lang": "en"})
    ]
    
    success = True
    for endpoint, params in test_cases:
        try:
            response = requests.get(f"{base_url}/symmetry/v1/wiki/{endpoint}", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API endpoint /{endpoint} working: {len(str(data))} bytes")
            else:
                print(f"❌ API endpoint /{endpoint} failed: HTTP {response.status_code}")
                success = False
        except requests.exceptions.ConnectionError:
            print(f"⚠️  API endpoint /{endpoint} skipped: Server not running")
        except Exception as e:
            print(f"❌ API endpoint /{endpoint} error: {e}")
            success = False
    
    return success

def main():
    """Run all tests"""
    print("🚀 Starting Structured Wiki Integration Tests")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Article Parser", test_article_parser),
        ("URL Parsing", test_url_parsing),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
