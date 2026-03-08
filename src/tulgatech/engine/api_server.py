"""
REST API Server for TulgaTech
"""
from typing import Dict, List, Any
from datetime import datetime


class APIEndpoint:
    """Represents an API endpoint"""
    def __init__(self, path: str, method: str, description: str):
        self.path = path
        self.method = method  # GET, POST, PUT, DELETE
        self.description = description
        self.requires_auth = True
        self.rate_limit = 100  # requests per hour
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "path": self.path,
            "method": self.method,
            "description": self.description,
            "requires_auth": self.requires_auth,
            "rate_limit": self.rate_limit
        }


class APIResponse:
    """Represents API response"""
    def __init__(self, status_code: int, data: Any = None):
        self.status_code = status_code
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.message = self._get_status_message(status_code)
    
    def _get_status_message(self, code: int) -> str:
        """Get status message"""
        messages = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error"
        }
        return messages.get(code, "Unknown")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "status_code": self.status_code,
            "message": self.message,
            "timestamp": self.timestamp,
            "data": self.data
        }


class APIServer:
    """TulgaTech REST API Server"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.endpoints: List[APIEndpoint] = []
        self.api_version = "1.0.0"
        self.is_running = False
        self._initialize_endpoints()
    
    def _initialize_endpoints(self):
        """Initialize API endpoints"""
        
        # Analysis endpoints
        self.endpoints.append(APIEndpoint(
            "/api/v1/analyze",
            "POST",
            "Analyze DXF file"
        ))
        
        self.endpoints.append(APIEndpoint(
            "/api/v1/analysis/{id}",
            "GET",
            "Get analysis result"
        ))
        
        # Project endpoints
        self.endpoints.append(APIEndpoint(
            "/api/v1/projects",
            "GET",
            "List all projects"
        ))
        
        self.endpoints.append(APIEndpoint(
            "/api/v1/projects",
            "POST",
            "Create new project"
        ))
        
        self.endpoints.append(APIEndpoint(
            "/api/v1/projects/{id}",
            "GET",
            "Get project details"
        ))
        
        # Report endpoints
        self.endpoints.append(APIEndpoint(
            "/api/v1/reports/{id}",
            "GET",
            "Get project report"
        ))
        
        self.endpoints.append(APIEndpoint(
            "/api/v1/reports/{id}/export",
            "POST",
            "Export report (PDF/HTML)"
        ))
        
        # Health check
        self.endpoints.append(APIEndpoint(
            "/api/v1/health",
            "GET",
            "Health check"
        ))
        self.endpoints[-1].requires_auth = False
    
    def start(self) -> Dict:
        """Start API server"""
        self.is_running = True
        return {
            "status": "started",
            "host": self.host,
            "port": self.port,
            "api_version": self.api_version,
            "endpoints": len(self.endpoints)
        }
    
    def stop(self) -> Dict:
        """Stop API server"""
        self.is_running = False
        return {
            "status": "stopped",
            "message": "API server stopped"
        }
    
    def get_endpoints(self) -> List[Dict]:
        """Get all endpoints"""
        return [ep.to_dict() for ep in self.endpoints]
    
    def process_request(self, path: str, method: str, 
                       data: Dict = None) -> APIResponse:
        """Process API request"""
        
        # Find matching endpoint
        endpoint = None
        for ep in self.endpoints:
            if ep.path == path and ep.method == method:
                endpoint = ep
                break
        
        if not endpoint:
            return APIResponse(404, {"error": "Endpoint not found"})
        
        # Process based on endpoint
        if path == "/api/v1/health":
            return APIResponse(200, {
                "status": "healthy",
                "api_version": self.api_version,
                "is_running": self.is_running
            })
        
        elif path == "/api/v1/analyze" and method == "POST":
            return self._handle_analyze(data)
        
        elif path == "/api/v1/projects" and method == "GET":
            return APIResponse(200, {
                "projects": [],
                "count": 0
            })
        
        elif path == "/api/v1/projects" and method == "POST":
            return APIResponse(201, {
                "project_id": "PRJ_001",
                "created": datetime.now().isoformat()
            })
        
        else:
            return APIResponse(200, {"message": "OK"})
    
    def _handle_analyze(self, data: Dict) -> APIResponse:
        """Handle analyze request"""
        if not data or "file_path" not in data:
            return APIResponse(400, {"error": "file_path required"})
        
        return APIResponse(201, {
            "analysis_id": "ANL_001",
            "status": "queued",
            "file_path": data["file_path"],
            "created": datetime.now().isoformat()
        })
    
    def get_server_info(self) -> Dict:
        """Get server information"""
        return {
            "name": "TulgaTech API Server",
            "version": self.api_version,
            "host": self.host,
            "port": self.port,
            "is_running": self.is_running,
            "endpoints_count": len(self.endpoints),
            "endpoints": [ep.path for ep in self.endpoints]
        }