"""
Tests for API Server
"""
from tulgatech.engine.api_server import APIEndpoint, APIResponse, APIServer


def test_api_endpoint_init():
    """Test APIEndpoint initialization"""
    endpoint = APIEndpoint("/api/test", "GET", "Test endpoint")
    assert endpoint.path == "/api/test"
    assert endpoint.method == "GET"


def test_api_response_init():
    """Test APIResponse initialization"""
    response = APIResponse(200, {"data": "test"})
    assert response.status_code == 200
    assert response.data == {"data": "test"}


def test_api_response_messages():
    """Test API response status messages"""
    response_200 = APIResponse(200)
    assert response_200.message == "OK"
    
    response_404 = APIResponse(404)
    assert response_404.message == "Not Found"


def test_api_response_to_dict():
    """Test API response to_dict"""
    response = APIResponse(200, {"test": "data"})
    d = response.to_dict()
    
    assert d["status_code"] == 200
    assert d["message"] == "OK"
    assert "timestamp" in d


def test_server_init():
    """Test APIServer initialization"""
    server = APIServer()
    assert server.host == "localhost"
    assert server.port == 8000
    assert len(server.endpoints) > 0


def test_server_start():
    """Test starting server"""
    server = APIServer()
    result = server.start()
    
    assert result["status"] == "started"
    assert server.is_running == True


def test_server_stop():
    """Test stopping server"""
    server = APIServer()
    server.start()
    result = server.stop()
    
    assert result["status"] == "stopped"
    assert server.is_running == False


def test_get_endpoints():
    """Test getting endpoints"""
    server = APIServer()
    endpoints = server.get_endpoints()
    
    assert len(endpoints) > 0
    assert all("path" in ep for ep in endpoints)


def test_health_check():
    """Test health check endpoint"""
    server = APIServer()
    response = server.process_request("/api/v1/health", "GET")
    
    assert response.status_code == 200
    assert response.data["status"] == "healthy"


def test_analyze_endpoint():
    """Test analyze endpoint"""
    server = APIServer()
    
    data = {"file_path": "test.dxf"}
    response = server.process_request("/api/v1/analyze", "POST", data)
    
    assert response.status_code == 201
    assert "analysis_id" in response.data


def test_get_server_info():
    """Test getting server info"""
    server = APIServer()
    info = server.get_server_info()
    
    assert info["name"] == "TulgaTech API Server"
    assert info["version"] == "1.0.0"
    assert "endpoints_count" in info