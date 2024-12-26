from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    data = request.get_json()
    from_email = data.get('from')
    to_email = data.get('to')
    subject = data.get('subject')
    text_content = data.get('textcontent')

    if not from_email or not to_email or not subject or not text_content:
        return jsonify({'error': 'All fields are required.'}), 400

    # Simulate sending feedback (replace with actual email-sending logic)
    print(f"Feedback received from {from_email} to {to_email}: {subject} - {text_content}")

    return jsonify({'message': 'Feedback sent successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)













#mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/