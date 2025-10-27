from flask import Flask, request

admin_app = Flask(__name__)

FLAG = "FLAG{gOph3r_Pr0t0c0l_1s_D34D_but_D4ng3r0us}"

@admin_app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return "❌ 405 Method Not Allowed!", 405
    
    if request.method == 'POST':
        # Debug: Print what we received
        print(f"Raw data: {request.data}")
        print(f"Form data: {request.form}")
        print(f"Content-Type: {request.content_type}")
        
        # Check both raw data and form data
        if b'action=get_flag' in request.data or request.form.get('action') == 'get_flag':
            return f"🎉 SUCCESS! You found the flag: {FLAG}", 200
        else: 
            return f"⚠️ 400 Bad Request: Invalid action. Received: {request.data[:100]}", 400

if __name__ == '__main__':
    admin_app.run(host='0.0.0.0', port=5000, debug=True)