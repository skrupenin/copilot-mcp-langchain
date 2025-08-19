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
        # Restore original working directory
        os.chdir(original_cwd)
        logger.info("🏁 Test completed")

if __name__ == "__main__":
    asyncio.run(main())
