"""
HTTP Server module for webhook endpoints using aiohttp.
"""
import asyncio
import json
import logging
import ssl
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import web, ClientTimeout
from aiohttp.web_request import Request
from aiohttp.web_response import Response

logger = logging.getLogger('mcp_server.tools.lng_webhook_server.http_server')

class WebhookHTTPServer:
    """HTTP server for handling webhook requests."""
    
    def __init__(self, config: dict):
        self.config = config
        self.name = config['name']
        self.port = config['port']
        self.path = config['path']
        self.bind_host = config['bind_host']
        self.app = None
        self.runner = None
        self.site = None
        self.request_count = 0
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup dedicated logger for this webhook endpoint."""
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        log_file = f"mcp_server/logs/webhook/{self.name}_{timestamp}.log"
        
        # Create endpoint-specific logger
        endpoint_logger = logging.getLogger(f'webhook.{self.name}')
        endpoint_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in endpoint_logger.handlers[:]:
            endpoint_logger.removeHandler(handler)
        
        # File handler
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formatter for human-readable logs
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        endpoint_logger.addHandler(file_handler)
        
        return endpoint_logger
    
    async def start(self) -> dict:
        """Start the HTTP server."""
        try:
            self.logger.info(f"Starting webhook server '{self.name}' on {self.bind_host}:{self.port}{self.path}")
            
            # Create aiohttp application
            self.app = web.Application()
            
            # Add webhook route
            self.app.router.add_route('*', self.path, self._handle_webhook)
            
            # Add health check route
            self.app.router.add_get('/health', self._handle_health)
            
            # Create runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            # Setup SSL if enabled
            ssl_context = None
            if self.config.get('ssl', {}).get('enabled', False):
                ssl_context = self._create_ssl_context()
            
            # Create site
            self.site = web.TCPSite(
                self.runner, 
                self.bind_host, 
                self.port,
                ssl_context=ssl_context
            )
            
            await self.site.start()
            
            protocol = "https" if ssl_context else "http"
            endpoint_url = f"{protocol}://{self.bind_host}:{self.port}{self.path}"
            
            self.logger.info(f"Webhook server started successfully at {endpoint_url}")
            
            return {
                "server_id": f"server_{self.name}",
                "endpoint_url": endpoint_url,
                "started_at": datetime.now().isoformat(),
                "ssl_enabled": ssl_context is not None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start webhook server: {e}")
            raise
    
    async def stop(self):
        """Stop the HTTP server."""
        try:
            self.logger.info(f"Stopping webhook server '{self.name}'")
            
            if self.site:
                await self.site.stop()
            
            if self.runner:
                await self.runner.cleanup()
            
            self.logger.info(f"Webhook server '{self.name}' stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping webhook server: {e}")
            raise
    
    async def _handle_webhook(self, request: Request) -> Response:
        """Handle incoming webhook requests."""
        self.request_count += 1
        request_id = f"{self.name}-{self.request_count:06d}"
        start_time = datetime.now()
        
        try:
            # Log comprehensive request information
            full_url = f"{request.scheme}://{request.host}{request.path_qs}"
            self.logger.info(f"[{request_id}] Received {request.method} request from {request.remote}")
            self.logger.info(f"[{request_id}] Full URL: {full_url}")
            self.logger.info(f"[{request_id}] Path: {request.path}")
            self.logger.info(f"[{request_id}] Query String: {request.query_string}")
            
            # Parse request data
            webhook_data = await self._parse_request(request, request_id)
            
            # Log request details
            self.logger.info(f"[{request_id}] Headers: {dict(request.headers)}")
            self.logger.info(f"[{request_id}] Content-Type: {webhook_data['content_type']}")
            if webhook_data['body']:
                body_preview = str(webhook_data['body'])[:200] + ("..." if len(str(webhook_data['body'])) > 200 else "")
                self.logger.info(f"[{request_id}] Body preview: {body_preview}")
            self.logger.info(f"[{request_id}] Body size: {len(str(webhook_data['body']))} chars")
            
            # Authenticate request if auth is configured
            auth_result = await self._authenticate_request(request, webhook_data, request_id)
            if not auth_result['success']:
                self.logger.warning(f"[{request_id}] Authentication failed: {auth_result['error']}")
                return web.json_response(
                    {"error": "Authentication failed"},
                    status=401
                )
            
            # Execute pipeline if configured
            pipeline_result = None
            pipeline_success = True
            error_id = None
            
            if self.config.get('pipeline'):
                try:
                    if self.config.get('async_mode', False):
                        # Async mode - respond immediately, process in background
                        asyncio.create_task(self._execute_pipeline_async(webhook_data, request_id))
                        pipeline_result = {"status": "processing_async"}
                    else:
                        # Sync mode - wait for pipeline completion
                        pipeline_result = await self._execute_pipeline(webhook_data, request_id)
                        pipeline_success = pipeline_result.get('success', True)
                        
                except Exception as e:
                    error_id = f"ERR-{request_id}"
                    pipeline_success = False
                    self.logger.error(f"[{request_id}] Pipeline execution failed [{error_id}]: {e}")
                    
                    # Return 500 error with minimal info
                    return web.json_response(
                        {
                            "error": "Internal processing error",
                            "error_id": error_id,
                            "message": "Please contact support with this error ID"
                        },
                        status=500
                    )
            
            # Prepare response context
            execution_time = (datetime.now() - start_time).total_seconds()
            response_context = {
                "webhook": webhook_data,
                "pipeline": {
                    "success": pipeline_success,
                    "execution_time": execution_time,
                    "error_id": error_id
                }
            }
            
            # Add pipeline results to context if available
            if pipeline_result and isinstance(pipeline_result, dict):
                response_context.update(pipeline_result.get('context', {}))
            
            # Generate response
            response_config = self.config.get('response', {})
            response_body = self._substitute_variables(
                response_config.get('body', {"received": True}),
                response_context
            )
            
            response_headers = response_config.get('headers', {})
            response_status = response_config.get('status', 200)
            
            # Log detailed response information
            response_body_preview = str(response_body)[:300] + ("..." if len(str(response_body)) > 300 else "")
            
            self.logger.info(f"[{request_id}] 📤 Responding with status {response_status} after {execution_time:.3f}s")
            self.logger.info(f"[{request_id}] 📤 Response headers: {response_headers}")
            self.logger.info(f"[{request_id}] 📤 Response body preview: {response_body_preview}")
            self.logger.info(f"[{request_id}] 📤 Response size: {len(str(response_body))} chars")
            
            # Check if Content-Type is in headers to avoid aiohttp conflict
            content_type = response_headers.pop('Content-Type', 'application/json')
            
            return web.json_response(
                response_body,
                status=response_status,
                headers=response_headers,
                content_type=content_type
            )
            
        except Exception as e:
            error_id = f"ERR-{request_id}"
            self.logger.error(f"[{request_id}] Unexpected error [{error_id}]: {e}")
            
            return web.json_response(
                {
                    "error": "Internal server error",
                    "error_id": error_id
                },
                status=500
            )
    
    async def _handle_health(self, request: Request) -> Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "webhook_name": self.name,
            "requests_processed": self.request_count,
            "uptime": (datetime.now() - datetime.fromisoformat(
                self.config.get('created_at', datetime.now().isoformat())
            )).total_seconds()
        })
    
    async def _parse_request(self, request: Request, request_id: str) -> dict:
        """Parse incoming request into webhook data structure."""
        content_type = request.headers.get('content-type', '').lower()
        
        # Parse body based on content type
        body = {}
        if 'application/json' in content_type:
            try:
                body = await request.json()
            except Exception as e:
                self.logger.warning(f"[{request_id}] Failed to parse JSON body: {e}")
                body = {"error": "Invalid JSON", "raw": await request.text()}
        elif 'application/x-www-form-urlencoded' in content_type:
            try:
                form_data = await request.post()
                body = dict(form_data)
            except Exception as e:
                self.logger.warning(f"[{request_id}] Failed to parse form data: {e}")
                body = {"error": "Invalid form data", "raw": await request.text()}
        else:
            # Plain text or other
            body = {"text": await request.text()}
        
        # Build webhook data structure
        webhook_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "query": dict(request.url.query),
            "headers": dict(request.headers),
            "body": body,
            "remote_ip": request.remote,
            "content_type": content_type,
            "endpoint_name": self.name,
            "request_id": request_id
        }
        
        return webhook_data
    
    async def _authenticate_request(self, request: Request, webhook_data: dict, request_id: str) -> dict:
        """Authenticate incoming request based on configuration."""
        auth_config = self.config.get('auth', {})
        auth_type = auth_config.get('type', 'none')
        
        if auth_type == 'none':
            return {"success": True}
        
        # Implementation for different auth types will be added later
        self.logger.info(f"[{request_id}] Authentication type '{auth_type}' - implementation pending")
        return {"success": True}  # Temporary - allow all
    
    async def _execute_pipeline(self, webhook_data: dict, request_id: str) -> dict:
        """Execute pipeline synchronously."""
        try:
            pipeline_steps = self.config['pipeline']
            self.logger.info(f"[{request_id}] ⚙️ Starting pipeline execution with {len(pipeline_steps)} steps")
            
            # Log pipeline steps
            for i, step in enumerate(pipeline_steps, 1):
                tool_name = step.get('tool', 'unknown')
                params_preview = str(step.get('params', {}))[:100] + ("..." if len(str(step.get('params', {}))) > 100 else "")
                output_var = step.get('output', 'none')
                self.logger.info(f"[{request_id}] ⚙️ Step {i}/{len(pipeline_steps)}: {tool_name} → {output_var} | params: {params_preview}")
            
            # Import here to avoid circular imports
            from mcp_server.tools.lng_batch_run.tool import run_tool as run_batch_pipeline
            
            # Prepare pipeline parameters
            pipeline_params = {
                "pipeline": pipeline_steps,
                "final_result": "Pipeline completed"
            }
            
            # Execute using lng_batch_run
            result_content = await run_batch_pipeline("lng_batch_run", pipeline_params)
            
            # Parse result
            if result_content and len(result_content) > 0:
                result_text = result_content[0].text
                result_data = json.loads(result_text)
                
                # Log pipeline results
                if 'context' in result_data:
                    context_keys = list(result_data['context'].keys())
                    self.logger.info(f"[{request_id}] ⚙️ Pipeline output variables: {context_keys}")
                    
                    # Log each output variable (truncated)
                    for key, value in result_data['context'].items():
                        value_preview = str(value)[:150] + ("..." if len(str(value)) > 150 else "")
                        self.logger.info(f"[{request_id}] ⚙️ Variable '{key}': {value_preview}")
                
                self.logger.info(f"[{request_id}] ✅ Pipeline completed successfully")
                return result_data
            else:
                self.logger.warning(f"[{request_id}] Pipeline returned empty result")
                return {"success": False, "error": "Empty pipeline result"}
                
        except Exception as e:
            self.logger.error(f"[{request_id}] Pipeline execution failed: {e}")
            raise
    
    async def _execute_pipeline_async(self, webhook_data: dict, request_id: str):
        """Execute pipeline asynchronously (fire and forget)."""
        try:
            result = await self._execute_pipeline(webhook_data, request_id)
            self.logger.info(f"[{request_id}] Async pipeline completed: {result.get('success', False)}")
        except Exception as e:
            self.logger.error(f"[{request_id}] Async pipeline failed: {e}")
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for HTTPS."""
        ssl_config = self.config.get('ssl', {})
        
        if ssl_config.get('cert_file') and ssl_config.get('key_file'):
            # User-provided certificates
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(ssl_config['cert_file'], ssl_config['key_file'])
            self.logger.info("Using user-provided SSL certificates")
        else:
            # Self-signed certificate (for development)
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # Note: Self-signed cert generation would need additional implementation
            self.logger.warning("Self-signed SSL certificate generation not yet implemented")
            raise NotImplementedError("Self-signed SSL certificates not yet supported")
        
        return context
    
    def _substitute_variables(self, obj: Any, context: dict) -> Any:
        """Substitute variables in response template."""
        if isinstance(obj, dict):
            return {k: self._substitute_variables(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_variables(item, context) for item in obj]
        elif isinstance(obj, str) and "${" in obj:
            import re
            
            def replace_var(match):
                var_path = match.group(1)
                try:
                    value = context
                    for part in var_path.split('.'):
                        if isinstance(value, dict):
                            value = value[part]
                        else:
                            return match.group(0)  # Can't navigate further
                    return str(value)
                except (KeyError, TypeError, AttributeError):
                    return match.group(0)  # Return original if not found
            
            return re.sub(r'\$\{([^}]+)\}', replace_var, obj)
        else:
            return obj
