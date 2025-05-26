import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

HOST = "0.0.0.0"
PORT = 8000
JSON_FILE_PATH = "data.json"

def read_json_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {"error": "JSON 파일을 찾을 수 없습니다."}
    except json.JSONDecodeError:
        return {"error": "JSON 파일 형식이 올바르지 않습니다."}

def write_json_file(file_path: str, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"JSON 파일 저장 오류: {e}")
        return False

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            json_data = read_json_file(JSON_FILE_PATH)

            if "error" in json_data:
                response_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>JSON 편집기</title>
                    <style>
                        body {{ font-family: sans-serif; }}
                        #json-display {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; white-space: pre-wrap; background-color: #f9f9f9; }}
                        #editor-container {{ margin-bottom: 10px; }}
                        textarea {{ width: 100%; min-height: 200px; font-family: monospace; font-size: 14px; }}
                        button {{ padding: 8px 15px; cursor: pointer; }}
                        #message {{ margin-top: 10px; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <h1>JSON 편집기</h1>
                    <div id="editor-container">
                        <textarea id="json-editor"></textarea>
                    </div>
                    <button onclick="saveJSON()">저장</button>
                    <div id="message"></div>

                    <script>
                        const jsonData = {json_data_placeholder};
                        const jsonEditor = document.getElementById('json-editor');
                        const messageDiv = document.getElementById('message');

                        function displayJSON() {{
                            jsonEditor.value = JSON.stringify(jsonData, null, 4);
                        }}

                        async function saveJSON() {{
                            try {{
                                const updatedData = JSON.parse(jsonEditor.value);
                                const response = await fetch('/', {{
                                    method: 'POST',
                                    headers: {{
                                        'Content-Type': 'application/json'
                                    }},
                                    body: JSON.stringify(updatedData)
                                }});

                                if (response.ok) {{
                                    messageDiv.textContent = 'JSON 데이터가 성공적으로 저장되었습니다.';
                                    messageDiv.style.color = 'green';
                                    // 필요하다면 jsonData 변수 업데이트
                                    Object.assign(jsonData, updatedData);
                                }} else {{
                                    const error = await response.json();
                                    messageDiv.textContent = `저장 실패: ${error.message || '알 수 없는 오류'}`;
                                    messageDiv.style.color = 'red';
                                }}
                            }} catch (error) {{
                                messageDiv.textContent = `JSON 형식 오류: ${error.message}`;
                                messageDiv.style.color = 'red';
                            }}
                        }}

                        displayJSON();
                    </script>
                </body>
                </html>
                """.format(json_data_placeholder=json.dumps(json_data, ensure_ascii=False))
            self.wfile.write(response_html.encode('utf-8'))
        elif parsed_url.path == '/':
            # POST 요청 처리 (데이터 저장)
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                updated_data = json.loads(post_data)
                if write_json_file(JSON_FILE_PATH, updated_data):
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "저장 성공"}, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "저장 실패"}, ensure_ascii=False).encode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "잘못된 JSON 형식"}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": f"서버 오류: {e}"}, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer((HOST, PORT), MyHandler) as httpd:
        print(f"Serving at http://{HOST}:{PORT}")
        httpd.serve_forever()