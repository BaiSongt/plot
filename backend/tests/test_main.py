from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "redoc" in data
    assert data["message"] == "欢迎使用 Plot 数据可视化平台 API"

def test_docs_redirect():
    """测试文档重定向"""
    response = client.get("/docs", allow_redirects=False)
    assert response.status_code == 307  # 临时重定向
    assert response.headers["location"] == "/docs/"

def test_docs_available():
    """测试文档页面是否可用"""
    response = client.get("/docs/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "swagger-ui" in response.text.lower()

def test_redoc_redirect():
    """测试 ReDoc 重定向"""
    response = client.get("/redoc", allow_redirects=False)
    assert response.status_code == 307  # 临时重定向
    assert response.headers["location"] == "/redoc/"

def test_redoc_available():
    """测试 ReDoc 页面是否可用"""
    response = client.get("/redoc/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "redoc" in response.text.lower()

def test_openapi_json():
    """测试 OpenAPI JSON 是否可用"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Plot 数据可视化平台"
    assert data["info"]["version"] == "0.1.0"
