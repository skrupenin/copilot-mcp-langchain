#!/usr/bin/env python3
"""
Universal test script for lng_webhook_server tool debugging
Useful for testing webhook functionality, pipeline integration, and troubleshooting issues.
"""
import asyncio
import json
import sys
import logging
import os
import time
import aiohttp
from typing import Dict, Any, Optional

# Add the project root to sys.path so we can import from mcp_server
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
sys.path.insert(0, project_root)

# Change working directory to project root to ensure proper file paths
original_cwd = os.getcwd()
os.chdir(project_root)

from mcp_server.tools.tool_registry import initialize_tools, run_tool

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('webhook_universal_test')

class WebhookTester:
    """Universal webhook testing utility."""
    
    def __init__(self):
        self.created_webhooks = []
        self.test_results = []
        self.temp_files = []  
    
    def create_temp_html_template(self, filename, content):
        """Creates temporary HTML file for testing"""
        temp_path = os.path.join(os.path.dirname(__file__), filename)
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(temp_path)
        return temp_path

    def cleanup_temp_files(self):
        """Removes temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"🗑️ Removed temp file: {os.path.basename(file_path)}")
            except Exception as e:
                logger.warning(f"⚠️ Could not remove {file_path}: {e}")
        self.temp_files.clear()
    
    async def cleanup_webhooks(self):
        """Clean up all webhooks created during testing."""
        logger.info(f"🧹 Cleaning up {len(self.created_webhooks)} created webhooks...")
        
        for webhook_name in self.created_webhooks:
            try:
                result = await run_tool("lng_webhook_server", {
                    "operation": "stop",
                    "name": webhook_name
                })
                logger.info(f"✅ Stopped webhook: {webhook_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to stop webhook {webhook_name}: {e}")
        
        self.created_webhooks.clear()
    
    async def list_existing_webhooks(self) -> Dict[str, Any]:
        """List all currently active webhooks."""
        logger.info("📋 Listing existing webhooks...")
        
        result = await run_tool("lng_webhook_server", {"operation": "list"})
        webhook_data = json.loads(result[0].text)
        
        logger.info(f"Found {webhook_data.get('active_webhooks', 0)} active webhooks")
        for webhook in webhook_data.get('webhooks', []):
            logger.info(f"  🔗 {webhook['name']} - {webhook['endpoint']} (pipeline: {webhook['pipeline_steps']} steps)")
        
        return webhook_data
    
    async def create_test_webhook(self, name: str, port: int, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a test webhook with optional custom configuration."""
        logger.info(f"🚀 Creating test webhook: {name} on port {port}")
        
        default_config = {
            "operation": "start",
            "name": name,
            "port": port,
            "path": f"/{name}",
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "webhook_name": name,
                    "message": "Test response",
                    "timestamp": "{! webhook.timestamp !}",
                    "method": "{! webhook.method !}",
                    "received_data": "{! webhook.body !}"
                }
            }
        }
        
        if config:
            default_config.update(config)
        
        try:
            result = await run_tool("lng_webhook_server", default_config)
            webhook_info = json.loads(result[0].text)
            
            if webhook_info.get("success"):
                self.created_webhooks.append(name)
                logger.info(f"✅ Webhook created: {webhook_info.get('endpoint')}")
                return webhook_info
            else:
                logger.error(f"❌ Failed to create webhook: {webhook_info}")
                return webhook_info
                
        except Exception as e:
            logger.error(f"❌ Exception creating webhook {name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_webhook_http(self, name: str, test_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test webhook via HTTP request using built-in test function."""
        logger.info(f"🧪 Testing webhook: {name}")
        
        if test_data is None:
            test_data = {
                "message": f"Test message for {name}",
                "timestamp": time.time(),
                "test_type": "universal_test"
            }
        
        try:
            result = await run_tool("lng_webhook_server", {
                "operation": "test",
                "name": name,
                "test_data": test_data
            })
            
            test_result = json.loads(result[0].text)
            
            if test_result.get("success"):
                logger.info(f"✅ HTTP test passed for {name}")
                response_body = test_result.get("response", {}).get("body", "")
                logger.info(f"📤 Response: {response_body[:100]}...")
            else:
                logger.error(f"❌ HTTP test failed for {name}: {test_result}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ Exception testing webhook {name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_pipeline_webhook(self, name: str, port: int) -> Dict[str, Any]:
        """Test webhook with pipeline integration."""
        logger.info(f"⚙️ Testing pipeline webhook: {name}")
        
        pipeline_config = {
            "operation": "start",
            "name": name,
            "port": port,
            "path": f"/{name}",
            "pipeline": [
                {
                    "tool": "lng_count_words",
                    "params": {"input_text": "{! webhook.body.message !}"},
                    "output": "word_stats"
                },
                {
                    "tool": "lng_math_calculator",
                    "params": {"expression": "{! word_stats.wordCount !} * 2"},
                    "output": "double_count"
                }
            ],
            "response": {
                "status": 200,
                "body": {
                    "webhook_name": name,
                    "original_message": "{! webhook.body.message !}",
                    "word_count": "{! word_stats.wordCount !}",
                    "double_count": "{! double_count.result !}",
                    "pipeline_success": True
                }
            }
        }
        
        # Create pipeline webhook
        create_result = await self.create_test_webhook(name, port, pipeline_config)
        if not create_result.get("success"):
            return create_result
        
        # Test it
        test_data = {
            "message": "This is a test message with exactly ten words total!",
            "user": "pipeline_tester"
        }
        
        return await self.test_webhook_http(name, test_data)
    
    async def run_basic_tests(self):
        """Run basic webhook functionality tests."""
        logger.info("🔍 === Running Basic Webhook Tests ===")
        
        # Test 1: List existing webhooks
        await self.list_existing_webhooks()
        
        # Test 2: Create simple webhook
        simple_result = await self.create_test_webhook("test-simple", 8090)
        self.test_results.append(("simple_webhook", simple_result.get("success", False)))
        
        # Test 3: Test simple webhook
        if simple_result.get("success"):
            http_result = await self.test_webhook_http("test-simple")
            self.test_results.append(("simple_http_test", http_result.get("success", False)))
        
        # Test 4: Create webhook with custom response
        custom_config = {
            "response": {
                "status": 201,
                "headers": {"X-Custom-Header": "test-value"},
                "body": {
                    "custom_response": True,
                    "webhook_data": "{! webhook.body !}",
                    "processing_time": "{! webhook.timestamp !}"
                }
            }
        }
        custom_result = await self.create_test_webhook("test-custom", 8091, custom_config)
        self.test_results.append(("custom_webhook", custom_result.get("success", False)))
        
        if custom_result.get("success"):
            custom_http_result = await self.test_webhook_http("test-custom", {"custom": True, "data": "test"})
            self.test_results.append(("custom_http_test", custom_http_result.get("success", False)))
    
    async def run_pipeline_tests(self):
        """Run pipeline integration tests."""
        logger.info("⚙️ === Running Pipeline Integration Tests ===")
        
        # Test pipeline webhook
        pipeline_result = await self.test_pipeline_webhook("test-pipeline", 8092)
        self.test_results.append(("pipeline_webhook", pipeline_result.get("success", False)))
    
    async def run_error_tests(self):
        """Run error handling and edge case tests."""
        logger.info("⚠️ === Running Error Handling Tests ===")
        
        # Test 1: Try to create webhook on occupied port
        await self.create_test_webhook("test-error-1", 8090)  # Should conflict
        
        # Test 2: Test non-existent webhook
        try:
            result = await run_tool("lng_webhook_server", {
                "operation": "test",
                "name": "non-existent-webhook",
                "test_data": {"test": True}
            })
            error_result = json.loads(result[0].text)
            self.test_results.append(("error_handling", not error_result.get("success", True)))
        except Exception as e:
            logger.info(f"✅ Error handling works: {e}")
            self.test_results.append(("error_handling", True))
        
        # Test 3: Invalid configuration
        try:
            result = await run_tool("lng_webhook_server", {
                "operation": "start",
                "name": "test-invalid",
                # Missing required port
                "path": "/invalid"
            })
            invalid_result = json.loads(result[0].text)
            self.test_results.append(("invalid_config", not invalid_result.get("success", True)))
        except Exception as e:
            logger.info(f"✅ Invalid config handling works: {e}")
            self.test_results.append(("invalid_config", True))
    
    async def run_html_tests(self):
        """Run HTML route functionality tests."""
        logger.info("🌐 === Running HTML Routes Tests ===")
        
        # Test 1: Create webhook with simple HTML route
        simple_html_result = await self.test_simple_html_webhook("test-html-simple", 8093)
        self.test_results.append(("simple_html_webhook", simple_html_result.get("success", False)))
        
        # Test 2: Create webhook with HTML route + pipeline
        pipeline_html_result = await self.test_html_with_pipeline_webhook("test-html-pipeline", 8094)
        self.test_results.append(("html_pipeline_webhook", pipeline_html_result.get("success", False)))
        
        # Test 3: Test cookie status page specifically
        cookie_html_result = await self.test_cookie_status_page("test-cookie-status", 8095)
        self.test_results.append(("cookie_status_page", cookie_html_result.get("success", False)))
        
        # Test 4: Test multiple HTML routes on same webhook
        multi_html_result = await self.test_multiple_html_routes("test-multi-html", 8096)
        self.test_results.append(("multiple_html_routes", multi_html_result.get("success", False)))
    
    async def test_simple_html_webhook(self, name: str, port: int) -> Dict[str, Any]:
        """Test webhook with basic HTML route."""
        logger.info(f"🌐 Testing simple HTML webhook: {name}")
        
        # Create simple test template
        simple_template_path = f"mcp_server/tools/lng_webhook_server/test_{name}.html"
        os.makedirs(os.path.dirname(simple_template_path), exist_ok=True)
        
        with open(simple_template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html><head><title>Test HTML</title></head>
<body>
<h1>Test HTML Route</h1>
<p>URL Template: {{URL_TEMPLATE}}</p>
<p>URL Param: {{URL_PARAM}}</p>
<p>Query Test: {{QUERY_TEST}}</p>
<p>Request Path: {{REQUEST_PATH}}</p>
</body></html>""")
        
        html_config = {
            "operation": "start",
            "name": name,
            "port": port,
            "path": f"/{name}",
            "html_routes": [
                {
                    "pattern": "/html/{template}/{param}",
                    "template": simple_template_path,
                    "pipeline": []
                }
            ],
            "response": {
                "status": 200,
                "body": {"webhook_received": True}
            }
        }
        
        try:
            # Create webhook with HTML routes
            create_result = await self.create_test_webhook(name, port, html_config)
            if not create_result.get("success"):
                return create_result
            
            # Test HTML route with HTTP client
            html_test_result = await self.test_html_route_http(name, port, "/html/testTemplate/testParam123?test=hello")
            
            # Cleanup template file
            try:
                os.remove(simple_template_path)
            except:
                pass
            
            return html_test_result
            
        except Exception as e:
            logger.error(f"❌ Exception in simple HTML test: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_html_with_pipeline_webhook(self, name: str, port: int) -> Dict[str, Any]:
        """Test HTML route with pipeline integration."""
        logger.info(f"⚙️🌐 Testing HTML webhook with pipeline: {name}")
        
        # Create template with pipeline data placeholders
        pipeline_template_path = f"mcp_server/tools/lng_webhook_server/test_{name}.html"
        
        with open(pipeline_template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html><head><title>Pipeline HTML Test</title></head>
<body>
<h1>HTML + Pipeline Test</h1>
<p>Session ID: {{URL_SESSIONID}}</p>
<p>Word Count: {{PAGE_DATA_WORDCOUNT}}</p>
<p>Unique Words: {{PAGE_DATA_UNIQUEWORDS}}</p>
<p>Calc Result: {{CALC_RESULT_RESULT}}</p>
<p>Test Text: {{PAGE_DATA_WORDCOUNT}} words processed</p>
</body></html>""")
        
        html_config = {
            "operation": "start", 
            "name": name,
            "port": port,
            "path": f"/{name}",
            "html_routes": [
                {
                    "pattern": "/test/{sessionId}",
                    "template": pipeline_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_count_words",
                            "params": {"input_text": "Testing HTML pipeline with session: {! url.sessionId !}"},
                            "output": "page_data"
                        },
                        {
                            "tool": "lng_math_calculator", 
                            "params": {"expression": "{! page_data.wordCount !} + 5"},
                            "output": "calc_result"
                        }
                    ]
                }
            ],
            "response": {
                "status": 200,
                "body": {"webhook_received": True}
            }
        }
        
        try:
            # Create webhook
            create_result = await self.create_test_webhook(name, port, html_config)
            if not create_result.get("success"):
                return create_result
            
            # Test HTML route with pipeline
            html_test_result = await self.test_html_route_http(name, port, "/test/session-123")
            
            # Cleanup
            try:
                os.remove(pipeline_template_path)
            except:
                pass
            
            return html_test_result
            
        except Exception as e:
            logger.error(f"❌ Exception in HTML pipeline test: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_cookie_status_page(self, name: str, port: int) -> Dict[str, Any]:
        """Test specific cookie status page functionality."""
        logger.info(f"🍪🌐 Testing cookie status page: {name}")
        
        cookie_html_config = {
            "operation": "start",
            "name": name,
            "port": port,
            "path": f"/{name}",
            "html_routes": [
                {
                    "pattern": "/cookies/{sessionId}",
                    "template": "mcp_server/tools/lng_cookie_grabber/status.html",
                    "pipeline": [
                        {
                            "tool": "lng_cookie_grabber",
                            "params": {
                                "operation": "session_status",
                                "session_id": "{! url.sessionId !}"
                            },
                            "output": "cookie_data"
                        }
                    ]
                }
            ],
            "response": {
                "status": 200,
                "body": {"webhook_received": True}
            }
        }
        
        try:
            # Create webhook
            create_result = await self.create_test_webhook(name, port, cookie_html_config)
            if not create_result.get("success"):
                return create_result
            
            # Test cookie status page
            html_test_result = await self.test_html_route_http(name, port, "/cookies/test-session-456")
            
            return html_test_result
            
        except Exception as e:
            logger.error(f"❌ Exception in cookie status test: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_multiple_html_routes(self, name: str, port: int) -> Dict[str, Any]:
        """Test webhook with multiple HTML routes."""
        logger.info(f"🌐📋 Testing multiple HTML routes: {name}")
        
        # Create template for universal route
        universal_template_path = f"mcp_server/tools/lng_webhook_server/test_universal_{name}.html"
        
        with open(universal_template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html><head><title>Universal Template</title></head>
<body>
<h1>Universal HTML Route</h1>
<p>Template: {{URL_TEMPLATE}}</p>
<p>Param: {{URL_PARAM}}</p>
<p>Type: {{URL_TYPE}}</p>
<p>Data: {{DATA_MESSAGE}}</p>
</body></html>""")
        
        multi_routes_config = {
            "operation": "start",
            "name": name,
            "port": port,
            "path": f"/{name}",
            "html_routes": [
                {
                    "pattern": "/html/{template}/{param}",
                    "template": universal_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_count_words",
                            "params": {"input_text": "Universal route: {! url.template !}/{! url.param !}"},
                            "output": "data"
                        }
                    ]
                },
                {
                    "pattern": "/status/{type}/{param}",
                    "template": universal_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_count_words",
                            "params": {"input_text": "Status route: {! url.type !}/{! url.param !}"},
                            "output": "data"
                        }
                    ]
                }
            ],
            "response": {
                "status": 200,
                "body": {"webhook_received": True}
            }
        }
        
        try:
            # Create webhook with multiple routes
            create_result = await self.create_test_webhook(name, port, multi_routes_config)
            if not create_result.get("success"):
                return create_result
            
            # Test both routes
            test1_result = await self.test_html_route_http(name, port, "/html/testTemplate/param1")
            test2_result = await self.test_html_route_http(name, port, "/status/active/param2")
            
            # Cleanup
            try:
                os.remove(universal_template_path)
            except:
                pass
            
            # Return success if both tests passed
            success = test1_result.get("success", False) and test2_result.get("success", False)
            return {"success": success, "test1": test1_result, "test2": test2_result}
            
        except Exception as e:
            logger.error(f"❌ Exception in multiple routes test: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_html_route_http(self, webhook_name: str, port: int, path: str) -> Dict[str, Any]:
        """Test HTML route via HTTP request."""
        import aiohttp
        
        url = f"http://localhost:{port}{path}"
        logger.info(f"🌐 Testing HTML route: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_text = await response.text()
                    content_type = response.headers.get('content-type', '')
                    
                    # Check if it's HTML response
                    is_html = 'text/html' in content_type.lower()
                    has_html_content = '<html>' in response_text.lower() or '<!doctype html>' in response_text.lower()
                    
                    logger.info(f"🌐 HTML response status: {response.status}")
                    logger.info(f"🌐 Content-Type: {content_type}")
                    logger.info(f"🌐 Is HTML: {is_html}")
                    logger.info(f"🌐 Has HTML content: {has_html_content}")
                    logger.info(f"🌐 Response length: {len(response_text)} chars")
                    
                    # Show preview of response
                    preview = response_text[:200] + ("..." if len(response_text) > 200 else "")
                    logger.info(f"🌐 Response preview: {preview}")
                    
                    success = (response.status == 200 and (is_html or has_html_content))
                    
                    return {
                        "success": success,
                        "status": response.status,
                        "content_type": content_type,
                        "is_html": is_html,
                        "response_length": len(response_text),
                        "response_preview": preview
                    }
                    
        except Exception as e:
            logger.error(f"❌ HTML route test failed for {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def print_summary(self):
        """Print test results summary."""
        logger.info("📊 === Test Results Summary ===")
        
        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)
        
        logger.info(f"Tests passed: {passed}/{total}")
        
        for test_name, success in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {status} {test_name}")
        
        if passed == total:
            logger.info("🎉 All tests passed!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed")

    async def run_cookie_html_tests(self):
        """Run cookie HTML interface tests - testing our new functionality."""
        logger.info("🍪🌐 === Running Cookie HTML Interface Tests ===")
        
        # Create temporary test template with English content
        test_template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Template</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #007acc; }
        .info-row { margin: 10px 0; }
        .label { font-weight: bold; color: #555; }
        .value { color: #333; margin-left: 10px; }
        .debug-section { background: #f0f8ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Universal Test Template</h1>
        
        <div class="info-row">
            <span class="label">Template:</span>
            <span class="value">{{URL_TEMPLATE}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Parameter:</span>
            <span class="value">{{URL_PARAM}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Type:</span>
            <span class="value">{{URL_TYPE}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Category:</span>
            <span class="value">{{URL_CATEGORY}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">ID:</span>
            <span class="value">{{URL_ID}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Query Test:</span>
            <span class="value">{{QUERY_TEST}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Query Debug:</span>
            <span class="value">{{QUERY_DEBUG}}</span>
        </div>
        
        <div class="info-row">
            <span class="label">Request Path:</span>
            <span class="value">{{REQUEST_PATH}}</span>
        </div>
        
        <div class="debug-section">
            <h3>🔍 Pipeline Results</h3>
            
            <div class="info-row">
                <span class="label">Page Data Word Count:</span>
                <span class="value">{{PAGE_DATA_WORDCOUNT}}</span>
            </div>
            
            <div class="info-row">
                <span class="label">Status Data Word Count:</span>
                <span class="value">{{STATUS_DATA_WORDCOUNT}}</span>
            </div>
            
            <div class="info-row">
                <span class="label">Calc Result:</span>
                <span class="value">{{CALC_DATA_RESULT}}</span>
            </div>
            
            <div class="info-row">
                <span class="label">Pipeline Success:</span>
                <span class="value">{{PIPELINE_SUCCESS}}</span>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        # Create temporary template file
        temp_template_path = self.create_temp_html_template("temp_universal_test.html", test_template_content)
        
        # Test 1: Cookie status page with proper URL pattern
        logger.info("🍪 Testing cookie status page with URL pattern: /cookies/{sessionId}")
        
        cookie_config = {
            "operation": "start",
            "name": "test-cookie-interface",
            "port": 8097,
            "path": "/api",  # Different path for API calls
            "html_routes": [
                {
                    "pattern": "/cookies/{sessionId}",
                    "template": "mcp_server/tools/lng_cookie_grabber/status.html",
                    "pipeline": [
                        {
                            "tool": "lng_count_words", 
                            "params": {"input_text": "Cookie session: {! url.sessionId !}"},
                            "output": "cookie_data"
                        }
                    ]
                }
            ]
        }
        
        create_result = await self.create_test_webhook("test-cookie-interface", 8097, cookie_config)
        self.test_results.append(("cookie_interface_webhook", create_result.get("success", False)))
        
        if create_result.get("success"):
            # Test the cookie status URL
            cookie_result = await self.test_html_route_http("test-cookie-interface", 8097, "/cookies/test-session-789")
            self.test_results.append(("cookie_status_page", cookie_result.get("success", False)))
        
        # Test 2: Universal HTML route with template parameter
        logger.info("🌐 Testing universal HTML route: /html/{template}/{param}")
        
        universal_config = {
            "operation": "start",
            "name": "test-universal-html",
            "port": 8098,
            "path": "/api",
            "html_routes": [
                {
                    "pattern": "/html/{template}/{param}",
                    "template": temp_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_count_words",
                            "params": {"input_text": "Template: {! url.template !}, Param: {! url.param !}"},
                            "output": "page_data"
                        }
                    ]
                }
            ]
        }
        
        universal_result = await self.create_test_webhook("test-universal-html", 8098, universal_config)
        self.test_results.append(("universal_html_webhook", universal_result.get("success", False)))
        
        if universal_result.get("success"):
            # Test with different templates and parameters
            test_paths = [
                "/html/cookie_grabber/session123",
                "/html/test_template/param456?debug=true",
                "/html/status/active"
            ]
            
            for i, path in enumerate(test_paths):
                result = await self.test_html_route_http("test-universal-html", 8098, path)
                self.test_results.append((f"universal_html_test_{i+1}", result.get("success", False)))
        
        # Test 3: Multiple HTML routes on same webhook
        logger.info("🌐📋 Testing multiple HTML routes on same webhook")
        
        multi_config = {
            "operation": "start",
            "name": "test-multi-routes",
            "port": 8099,
            "path": "/webhook",
            "html_routes": [
                {
                    "pattern": "/status/{type}",
                    "template": temp_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_count_words",
                            "params": {"input_text": "Status type: {! url.type !}"},
                            "output": "status_data"
                        }
                    ]
                },
                {
                    "pattern": "/info/{category}/{id}",
                    "template": temp_template_path,
                    "pipeline": [
                        {
                            "tool": "lng_math_calculator",
                            "params": {"expression": "{! url.id !} + 100"},
                            "output": "calc_data"
                        }
                    ]
                }
            ]
        }
        
        multi_result = await self.create_test_webhook("test-multi-routes", 8099, multi_config)
        self.test_results.append(("multi_routes_webhook", multi_result.get("success", False)))
        
        if multi_result.get("success"):
            # Test different routes
            multi_paths = [
                "/status/active",
                "/info/user/42"
            ]
            
            for i, path in enumerate(multi_paths):
                result = await self.test_html_route_http("test-multi-routes", 8099, path)
                self.test_results.append((f"multi_route_test_{i+1}", result.get("success", False)))

async def main():
    """Main test function with multiple test scenarios."""
    logger.info("🚀 Starting Universal Webhook Server Tests")
    
    # Initialize tools
    logger.info("🔧 Initializing tools...")
    initialize_tools()
    
    # Create tester instance
    tester = WebhookTester()
    
    try:
        # Run test suites
        await tester.run_basic_tests()
        await tester.run_pipeline_tests()
        await tester.run_html_tests()  # Add HTML tests
        await tester.run_cookie_html_tests()  # Our new cookie HTML tests
        await tester.run_error_tests()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        logger.error(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await tester.cleanup_webhooks()
        tester.cleanup_temp_files()  # Clean up temporary HTML files
        # Restore original working directory
        os.chdir(original_cwd)
        logger.info("🏁 Test completed")

if __name__ == "__main__":
    asyncio.run(main())
