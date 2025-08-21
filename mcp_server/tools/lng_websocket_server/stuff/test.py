import unittest
import json
import asyncio
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path to import tool module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tool import run_tool, ACTIVE_CONNECTIONS


class TestWebSocketServer(unittest.TestCase):
    """Test cases for lng_websocket_server tool using approval testing approach."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Clear active connections
        ACTIVE_CONNECTIONS.clear()
        
        # Create temporary directory for test configs
        self.test_config_dir = tempfile.mkdtemp()
        self.original_config_dir = "mcp_server/config/websocket"
        
        # Patch config directory
        self.config_patch = patch('tool._save_connection_config', new_callable=AsyncMock)
        self.mock_save_config = self.config_patch.start()

    def tearDown(self):
        """Clean up after each test."""
        # Stop all patches
        self.config_patch.stop()
        
        # Clean up temporary directory
        if os.path.exists(self.test_config_dir):
            shutil.rmtree(self.test_config_dir)
        
        # Clear active connections
        ACTIVE_CONNECTIONS.clear()

    def test_should_return_list_of_connections_when_no_active_connections(self):
        """Test listing connections when no connections are active."""
        # given
        # No active connections (setUp ensures empty state)
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", {"operation": "list"}))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "total_connections": 0,
                "connections": {}
            }, indent=2),
            result[0].text
        )

    def test_should_fail_server_start_when_missing_required_parameters(self):
        """Test server start fails with missing required parameters."""
        # given
        invalid_params = {"operation": "server_start"}
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", invalid_params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "'name' parameter is required"
            }, indent=2),
            result[0].text
        )

    def test_should_fail_server_start_when_invalid_port_range(self):
        """Test server start fails with invalid port range."""
        # given
        invalid_params = {
            "operation": "server_start",
            "name": "test-server",
            "port": 999
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", invalid_params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "Port must be between 1000 and 65535"
            }, indent=2),
            result[0].text
        )

    @patch('tool._start_websocket_server')
    def test_should_start_server_successfully_when_valid_parameters(self, mock_start_server):
        """Test successful server start with valid parameters."""
        # given
        mock_start_server.return_value = {
            "server_id": "ws_server_001",
            "bind_address": "localhost:8080",
            "started_at": "2025-08-21T14:30:00.000Z"
        }
        
        params = {
            "operation": "server_start",
            "name": "test-server",
            "port": 8080,
            "path": "/ws"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        expected_response = {
            "success": True,
            "message": "WebSocket server 'test-server' started successfully",
            "connection_type": "server",
            "endpoint": "ws://localhost:8080/ws",
            "config": {
                "name": "test-server",
                "type": "server",
                "port": 8080,
                "path": "/ws",
                "bind_host": "localhost",
                "protocol": "ws",
                "subprotocols": [],
                "max_connections": 100,
                "message_size_limit": 1048576,
                "auth": {"type": "none"},
                "ssl": {"enabled": False},
                "connection_handling": {
                    "heartbeat_interval": 30,
                    "connection_timeout": 300,
                    "auto_cleanup": True
                },
                "rate_limiting": {
                    "messages_per_minute": 60,
                    "burst_limit": 10
                },
                "event_handlers": {},
                "auto_responses": {},
                "status": "running",
                "clients": {},
                "metrics": {
                    "total_connections": 0,
                    "active_connections": 0,
                    "total_messages": 0
                },
                "server_info": {
                    "server_id": "ws_server_001",
                    "bind_address": "localhost:8080",
                    "started_at": "2025-08-21T14:30:00.000Z"
                }
            }
        }
        
        # Parse result and remove dynamic fields for comparison
        result_data = json.loads(result[0].text)
        if "config" in result_data and "created_at" in result_data["config"]:
            del result_data["config"]["created_at"]
        if "config" in result_data and "metrics" in result_data["config"] and "started_at" in result_data["config"]["metrics"]:
            del result_data["config"]["metrics"]["started_at"]
        
        self.assertEqual(
            json.dumps(expected_response, indent=2),
            json.dumps(result_data, indent=2)
        )

    def test_should_fail_server_stop_when_connection_not_found(self):
        """Test server stop fails when connection doesn't exist."""
        # given
        params = {
            "operation": "server_stop",
            "name": "nonexistent-server"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "WebSocket connection 'nonexistent-server' not found"
            }, indent=2),
            result[0].text
        )

    def test_should_fail_client_connect_when_missing_url(self):
        """Test client connect fails with missing URL parameter."""
        # given
        params = {
            "operation": "client_connect",
            "name": "test-client"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "'url' parameter is required"
            }, indent=2),
            result[0].text
        )

    @patch('tool._start_websocket_client')
    def test_should_connect_client_successfully_when_valid_parameters(self, mock_start_client):
        """Test successful client connection with valid parameters."""
        # given
        mock_start_client.return_value = {
            "connected": True,
            "client_id": "ws_client_001",
            "connected_at": "2025-08-21T14:30:00.000Z"
        }
        
        params = {
            "operation": "client_connect",
            "name": "test-client",
            "url": "ws://localhost:8080/ws"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        expected_response = {
            "success": True,
            "message": "WebSocket client 'test-client' connected",
            "connection_type": "client",
            "url": "ws://localhost:8080/ws",
            "config": {
                "name": "test-client",
                "type": "client",
                "url": "ws://localhost:8080/ws",
                "subprotocol": None,
                "auth": {"type": "none"},
                "connection_handling": {
                    "auto_reconnect": True,
                    "max_reconnect_attempts": 5,
                    "backoff_strategy": "exponential",
                    "heartbeat_enabled": True,
                    "heartbeat_message": {"type": "ping"}
                },
                "message_handlers": {},
                "status": "connected",
                "metrics": {
                    "connection_attempts": 0,
                    "total_messages_sent": 0,
                    "total_messages_received": 0,
                    "last_activity": None
                },
                "client_info": {
                    "connected": True,
                    "client_id": "ws_client_001",
                    "connected_at": "2025-08-21T14:30:00.000Z"
                }
            }
        }
        
        # Parse result and remove dynamic fields for comparison
        result_data = json.loads(result[0].text)
        if "config" in result_data and "created_at" in result_data["config"]:
            del result_data["config"]["created_at"]
        
        self.assertEqual(
            json.dumps(expected_response, indent=2),
            json.dumps(result_data, indent=2)
        )

    def test_should_fail_client_send_when_connection_not_found(self):
        """Test client send fails when connection doesn't exist."""
        # given
        params = {
            "operation": "client_send",
            "name": "nonexistent-client",
            "message": {"type": "test", "data": "hello"}
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "WebSocket connection 'nonexistent-client' not found"
            }, indent=2),
            result[0].text
        )

    def test_should_fail_client_send_when_connection_is_not_client(self):
        """Test client send fails when connection is not a client type."""
        # given
        ACTIVE_CONNECTIONS["test-server"] = {
            "type": "server",
            "name": "test-server"
        }
        
        params = {
            "operation": "client_send",
            "name": "test-server",
            "message": {"type": "test"}
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "Connection 'test-server' is not a client"
            }, indent=2),
            result[0].text
        )

    def test_should_fail_broadcast_when_missing_message(self):
        """Test broadcast fails when message parameter is missing."""
        # given
        params = {
            "operation": "broadcast",
            "name": "test-server"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "'message' parameter is required"
            }, indent=2),
            result[0].text
        )

    @patch('tool._broadcast_to_clients')
    def test_should_broadcast_successfully_when_valid_server(self, mock_broadcast):
        """Test successful message broadcast to server clients."""
        # given
        mock_broadcast.return_value = {
            "sent_count": 3,
            "failed_count": 0,
            "total_clients": 3
        }
        
        ACTIVE_CONNECTIONS["test-server"] = {
            "type": "server",
            "name": "test-server",
            "metrics": {"total_messages": 0}
        }
        
        params = {
            "operation": "broadcast",
            "name": "test-server",
            "message": {"type": "announcement", "text": "Hello everyone!"}
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "message": "Message broadcasted to 3 clients",
                "server_name": "test-server",
                "sent_count": 3,
                "failed_count": 0,
                "total_clients": 3
            }, indent=2),
            result[0].text
        )

    def test_should_return_status_when_connection_exists(self):
        """Test getting status of existing connection."""
        # given
        ACTIVE_CONNECTIONS["test-server"] = {
            "type": "server",
            "name": "test-server",
            "status": "running",
            "created_at": "2025-08-21T14:30:00.000Z",
            "port": 8080,
            "path": "/ws",
            "bind_host": "localhost",
            "ssl": {"enabled": False},
            "clients": {},
            "metrics": {
                "total_connections": 5,
                "active_connections": 2,
                "total_messages": 47
            }
        }
        
        params = {
            "operation": "status",
            "name": "test-server",
            "include_metrics": True
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "connection_status": {
                    "name": "test-server",
                    "type": "server",
                    "status": "running",
                    "created_at": "2025-08-21T14:30:00.000Z",
                    "metrics": {
                        "total_connections": 5,
                        "active_connections": 2,
                        "total_messages": 47
                    },
                    "endpoint": "ws://localhost:8080/ws",
                    "active_clients": 0
                }
            }, indent=2),
            result[0].text
        )

    def test_should_fail_status_when_connection_not_found(self):
        """Test status fails when connection doesn't exist."""
        # given
        params = {
            "operation": "status",
            "name": "nonexistent-connection"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "WebSocket connection 'nonexistent-connection' not found"
            }, indent=2),
            result[0].text
        )

    @patch('tool._broadcast_to_clients')
    def test_should_test_server_connection_successfully_when_connection_exists(self, mock_broadcast):
        """Test successful server connection testing."""
        # given
        mock_broadcast.return_value = {
            "sent_count": 2,
            "failed_count": 0,
            "total_clients": 2
        }
        
        ACTIVE_CONNECTIONS["test-server"] = {
            "type": "server",
            "name": "test-server"
        }
        
        params = {
            "operation": "test",
            "name": "test-server",
            "test_data": {"type": "test_message", "content": "Test broadcast"}
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "message": "Test message sent to 2 clients",
                "connection_name": "test-server",
                "test_data": {"type": "test_message", "content": "Test broadcast"},
                "sent_count": 2,
                "failed_count": 0
            }, indent=2),
            result[0].text
        )

    @patch('tool._send_client_message')
    def test_should_test_client_connection_successfully_when_connection_exists(self, mock_send):
        """Test successful client connection testing."""
        # given
        mock_send.return_value = {
            "success": True,
            "message_id": "msg_001"
        }
        
        ACTIVE_CONNECTIONS["test-client"] = {
            "type": "client",
            "name": "test-client"
        }
        
        params = {
            "operation": "test",
            "name": "test-client"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "message": "Test message sent",
                "connection_name": "test-client",
                "test_data": {"type": "test", "message": "Hello WebSocket!"},
                "error": None
            }, indent=2),
            result[0].text
        )

    def test_should_return_multiple_connections_when_list_with_active_connections(self):
        """Test listing multiple active connections with detailed information."""
        # given
        ACTIVE_CONNECTIONS.update({
            "server-1": {
                "type": "server",
                "name": "server-1",
                "status": "running",
                "created_at": "2025-08-21T14:30:00.000Z",
                "port": 8080,
                "path": "/ws",
                "clients": {"client1": {}, "client2": {}},
                "metrics": {"total_connections": 5}
            },
            "client-1": {
                "type": "client",
                "name": "client-1",
                "status": "connected",
                "created_at": "2025-08-21T14:35:00.000Z",
                "url": "ws://external.com/ws",
                "metrics": {"last_activity": "2025-08-21T14:40:00.000Z"}
            }
        })
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", {"operation": "list"}))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "total_connections": 2,
                "connections": {
                    "server-1": {
                        "name": "server-1",
                        "type": "server",
                        "status": "running",
                        "created_at": "2025-08-21T14:30:00.000Z",
                        "port": 8080,
                        "path": "/ws",
                        "active_clients": 2,
                        "total_connections": 5
                    },
                    "client-1": {
                        "name": "client-1",
                        "type": "client",
                        "status": "connected",
                        "created_at": "2025-08-21T14:35:00.000Z",
                        "url": "ws://external.com/ws",
                        "last_activity": "2025-08-21T14:40:00.000Z"
                    }
                }
            }, indent=2),
            result[0].text
        )

    def test_should_fail_when_unknown_operation_provided(self):
        """Test tool fails gracefully with unknown operation."""
        # given
        params = {
            "operation": "unknown_operation",
            "name": "test-connection"
        }
        
        # when
        result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": False,
                "error": "Unknown operation: unknown_operation"
            }, indent=2),
            result[0].text
        )

    def test_should_handle_ssl_configuration_in_server_start(self):
        """Test server start with SSL configuration creates proper endpoint URL."""
        # given
        with patch('tool._start_websocket_server') as mock_start_server:
            mock_start_server.return_value = {
                "server_id": "wss_server_001",
                "bind_address": "0.0.0.0:8443"
            }
            
            params = {
                "operation": "server_start",
                "name": "secure-server",
                "port": 8443,
                "path": "/secure-ws",
                "bind_host": "0.0.0.0",
                "protocol": "wss",
                "ssl": {
                    "enabled": True,
                    "cert_file": "/etc/ssl/certs/server.crt",
                    "key_file": "/etc/ssl/private/server.key"
                }
            }
            
            # when
            result = asyncio.run(run_tool("lng_websocket_server", params))
            
            # then
            result_data = json.loads(result[0].text)
            self.assertEqual("wss://0.0.0.0:8443/secure-ws", result_data["endpoint"])
            self.assertEqual(True, result_data["config"]["ssl"]["enabled"])

    def test_should_handle_authentication_configuration_masking_in_output(self):
        """Test authentication configuration is properly masked in tool output."""
        # given
        with patch('tool._start_websocket_server') as mock_start_server:
            mock_start_server.return_value = {"server_id": "auth_server_001"}
            
            params = {
                "operation": "server_start",
                "name": "auth-server",
                "port": 8080,
                "auth": {
                    "type": "bearer_token",
                    "token": "secret-token-12345",
                    "origin_whitelist": ["https://trusted.com"]
                }
            }
            
            # when
            result = asyncio.run(run_tool("lng_websocket_server", params))
            
            # then
            result_data = json.loads(result[0].text)
            self.assertEqual("sec***345", result_data["config"]["auth"]["token"])
            self.assertIn("origin_whitelist", result_data["config"]["auth"])

    def test_should_disconnect_client_successfully_when_connection_exists_case_cleanup(self):
        """Test successful client disconnection with proper cleanup."""
        # given
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        
        ACTIVE_CONNECTIONS["test-client"] = {
            "type": "client",
            "name": "test-client",
            "_client_instance": mock_client
        }
        
        params = {
            "operation": "client_disconnect",
            "name": "test-client"
        }
        
        # when
        with patch('tool._stop_connection_by_name', new_callable=AsyncMock) as mock_stop:
            result = asyncio.run(run_tool("lng_websocket_server", params))
        
        # then
        self.assertEqual(
            json.dumps({
                "success": True,
                "message": "WebSocket client 'test-client' disconnected successfully"
            }, indent=2),
            result[0].text
        )


if __name__ == '__main__':
    # Enable running tests directly
    unittest.main(verbosity=2)
