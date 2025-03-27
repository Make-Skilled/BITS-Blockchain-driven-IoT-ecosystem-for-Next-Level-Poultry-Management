from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
from web3 import Web3,HTTPProvider
import json
import face_recognition
import numpy as np
from PIL import Image
import io
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

def connectWithBlockchain():
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    web3.eth.defaultAccount=web3.eth.accounts[0]
    
    with open('../build/contracts/poultry.json') as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.secret_key='123456789'

# Email configuration
app.config['SMTP_SERVER'] = "smtp.gmail.com"
app.config['SMTP_PORT'] = 587
app.config['SMTP_USERNAME'] = "kr4785543@gmail.com"
app.config['SMTP_PASSWORD'] = "qhuzwfrdagfyqemk"
app.config['ALERT_EMAIL'] = "parvathanenimadhu@gmail.com"

def send_email_alert(message, image_data=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['SMTP_USERNAME']
        msg['To'] = app.config['ALERT_EMAIL']
        msg['Subject'] = 'Security Alert: Unknown Face Detected'
        
        body = f"""
        Security Alert
        
        An unknown face was detected in the admin dashboard.
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Details:
        {message}
        
        This is an automated alert from the Poultry Management System.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the image if provided
        if image_data:
            # Remove the data URL prefix
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            
            # Create the attachment
            image = MIMEImage(image_bytes)
            image.add_header('Content-Disposition', 'attachment', filename='unknown_face.jpg')
            msg.attach(image)
        
        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/send_alert', methods=['POST'])
def send_alert():
    try:
        data = request.get_json()
        message = data.get('message', 'Unknown face detected')
        image_data = data.get('image')
        
        if send_email_alert(message, image_data):
            return jsonify({'success': True, 'message': 'Alert sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send alert'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

dbClient=MongoClient('mongodb://127.0.0.1:27017/')
db=dbClient['poultrydb']

poultrycol=db['poultrycol']
poultrycol1=db['retailerdb']
poultrycol2=db['consumercol']

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/reg')
def reg():
    return render_template('signup.html')

@app.route('/log')
def log():
    return render_template('signin.html')

@app.route('/retailerlog')
def retaillog():
    return render_template('signin.html')

@app.route('/consumerlog')
def consumelog():
    return render_template('signin.html')

@app.route('/retailerreg')
def retailreg():
    return render_template('signup.html')

@app.route('/consumerreg')
def consumereg():
    return render_template('signup.html')

@app.route('/retailer')
def retailer():
    return render_template('Retailer.html')

@app.route('/consumer')
def consumer():
    return render_template('consumer.html')
# Registration route

@app.route('/retailerreg',methods=['POST'])
def retailerreg():
    name=request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    existing_user = poultrycol1.find_one({'email': email})
    if existing_user is None:
        poultrycol1.insert_one({ 'name': name, 'email': email, 'password': password, 'phone': phone})
        return render_template('signup.html',msg='account created')
    else:
        msg='User already exists!'
        return render_template('signup.html',msg=msg)
    

@app.route('/consumerreg',methods=['POST'])
def consumerreg():
    name=request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    existing_user = poultrycol2.find_one({'email': email})
    if existing_user is None:
        poultrycol2.insert_one({ 'name': name, 'email': email, 'password': password, 'phone': phone})
        return render_template('signup.html',msg1='Account Created')
    else:
        msg='User already exists!'
        return render_template('signup.html',msg1=msg)

# Login route
@app.route('/login',methods=['POST'])
def login():
    email=request.form['email']
    password=request.form['password']
    flag=0
    if(email=='poultry@gmail.com' and password=='poultry'):
        flag=1
        session['email']=email
        session['password']=password
        return redirect('/admindashboard')
    if flag==0:
        msg='INVALID USERNAME OR PASSWORD'
        return render_template('signin.html',msg=msg)

@app.route('/retailerlog', methods=['POST'])
def retailerlog():
    email = request.form['email']
    password = request.form['password']  
    print(poultrycol1)  
    existing_user = poultrycol1.find({'email': email, 'password': password})
    print(existing_user)
    if existing_user:
        msg='login successful'
        session['email']=email
        return redirect('/retailerdashboard')
    else:
        msg='Invalid credentials'
        return render_template('signin.html',msg=msg)

@app.route('/consumerlog', methods=['POST'])
def consumerlog():
    email = request.form['email']
    password = request.form['password']  
    print(poultrycol2)  
    existing_user = poultrycol2.find_one({'email': email, 'password': password})
    print(existing_user)
    if existing_user:
        msg='login successful'
        session['email']=email
        return redirect('/consumerdashboard')
    else:
        msg='Invalid credentials'
        return render_template('signin.html',msg=msg)

@app.route('/admindashboard')
def admindashboard():
    if session['email']=='poultry@gmail.com':
        contract,web3=connectWithBlockchain()
        _oemails,_oorderids,_oretailers,_ostatuses,_onames,_olcations,_oproducttypes,_okgs=contract.functions.viewOrders().call()
        data=[]
        for i in range(len(_oorderids)):
            dummy=[]
            dummy.append(_oorderids[i])
            dummy.append(_oretailers[i])
            dummy.append(_ostatuses[i])
            dummy.append(_onames[i])
            dummy.append(_olcations[i])
            dummy.append(_oproducttypes[i])
            dummy.append(_okgs[i])
            data.append(dummy)
        return render_template('admin.html',data=data)
    else:
        return redirect('/')

@app.route('/confirmOrder/<id1>/<id2>')
def confirmOrder(id1,id2):
    id1=int(id1)
    id2=int(id2)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.updateOrder(id1,id2).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/admindashboard')

@app.route('/confirmOrder1/<id1>/<id2>')
def confirmOrder1(id1,id2):
    id1=int(id1)
    id2=int(id2)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.updateOrder1(id1,id2).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/retailerdashboard')

@app.route('/sendDatatoRetailer',methods=['POST'])
def sendDatatoRetailer():
    retailer=request.form['retailer']
    wallet=request.form['wallet']
    name=request.form['name']
    location=request.form['location']
    kgs=request.form['kgs']
    producttype=request.form['producttype']

    contract,web3=connectWithBlockchain()
    print(session['email'])
    tx_hash=contract.functions.addConsumer(session['email'],retailer,wallet,name,location,kgs,producttype).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    data=[]
    for i in poultrycol1.find():
        dummy=[]
        dummy.append(i['email'])
        dummy.append(i['name'])
        data.append(dummy)
    
    data1=[]
    contract,web3=connectWithBlockchain()
    _consumeremails,_cretailers,_cstatuses,_corderids,_consumers,_cnames,_clocations,_ckgs,_cproducttypes=contract.functions.viewConsumers().call()
    for i in range(len(_corderids)):
        if _consumeremails[i]==session['email']:
            dummy=[]
            dummy.append(_cretailers[i])
            dummy.append(_cstatuses[i])
            dummy.append(_corderids[i])
            dummy.append(_consumers[i])
            dummy.append(_cnames[i])
            dummy.append(_clocations[i])
            dummy.append(_ckgs[i])
            dummy.append(_cproducttypes[i])
            data1.append(dummy)

    return render_template('consumer.html',msg='order sent',data=data,data1=data1)


@app.route('/logout')
def logout():
    session['email']=None
    return redirect('/')

@app.route('/iotplug')
def iotplug():
    return render_template('iotplug.html')

@app.route('/retailerdashboard')
def retailerdashboard():
    contract,web3=connectWithBlockchain()
    _cemails,_cretailers,_cstatuses,_corderids,_consumers,_cnames,_clocations,_ckgs,_cproducttypes=contract.functions.viewConsumers().call()
    data1=[]
    for i in range(len(_corderids)):
        if _cretailers[i]==session['email']:
            dummy=[]
            dummy.append(_corderids[i])
            dummy.append(_cstatuses[i])
            dummy.append(_consumers[i])
            dummy.append(_cnames[i])
            dummy.append(_clocations[i])
            dummy.append(_ckgs[i])
            dummy.append(_cproducttypes[i])
            data1.append(dummy)
    
    contract,web3=connectWithBlockchain()
    _oemails,_oorderids,_oretailers,_ostatuses,_onames,_olcations,_oproducttypes,_okgs=contract.functions.viewOrders().call()
    data2=[]
    for i in range(len(_oorderids)):
        if(_oemails[i]==session['email']):
            dummy=[]
            dummy.append(_oemails[i])
            dummy.append(_ostatuses[i])
            dummy.append(_oorderids[i])
            dummy.append(_oretailers[i])
            dummy.append(_onames[i])
            dummy.append(_olcations[i])
            dummy.append(_oproducttypes[i])
            dummy.append(_okgs[i])
            data2.append(dummy)
    return render_template('Retailer.html',data1=data1,data2=data2)

@app.route('/riotplug')
def riotplug():
    return render_template('riotplug.html')

@app.route('/consumerdashboard')
def consumerdashboard():
    
    data=[]
    for i in poultrycol1.find():
        dummy=[]
        dummy.append(i['email'])
        dummy.append(i['name'])
        data.append(dummy)
    
    data1=[]
    contract,web3=connectWithBlockchain()
    _consumeremails,_cretailers,_cstatuses,_corderids,_consumers,_cnames,_clocations,_ckgs,_cproducttypes=contract.functions.viewConsumers().call()
    for i in range(len(_corderids)):
        if _consumeremails[i]==session['email']:
            dummy=[]
            dummy.append(_cretailers[i])
            dummy.append(_cstatuses[i])
            dummy.append(_corderids[i])
            dummy.append(_consumers[i])
            dummy.append(_cnames[i])
            dummy.append(_clocations[i])
            dummy.append(_ckgs[i])
            dummy.append(_cproducttypes[i])
            data1.append(dummy)

    return render_template('consumer.html',data=data,data1=data1)

@app.route('/ciotplug')
def ciotplug():
    return render_template('ciotplug.html')

@app.route('/sendtoAdminFromRetailerForm',methods=['POST'])
def sendtoAdminFromRetailerForm():
    wallet=request.form['wallet']
    name=request.form['name']
    location=request.form['location']
    kgs=request.form['kgs']
    producttype=request.form['producttype']
    print(wallet,name,location,kgs,producttype)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.addOrder(session['email'],wallet,name,location,kgs,producttype).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    contract,web3=connectWithBlockchain()
    _oemails,_oorderids,_oretailers,_ostatuses,_onames,_olcations,_oproducttypes,_okgs=contract.functions.viewOrders().call()
    data2=[]
    for i in range(len(_oorderids)):
        if(_oemails[i]==session['email']):
            dummy=[]
            dummy.append(_oemails[i])
            dummy.append(_ostatuses[i])
            dummy.append(_oorderids[i])
            dummy.append(_oretailers[i])
            dummy.append(_onames[i])
            dummy.append(_olcations[i])
            dummy.append(_oproducttypes[i])
            dummy.append(_okgs[i])
            data2.append(dummy)
    return render_template('Retailer.html',res='Order Sent',data2=data2)

@app.route('/retailerdata')
def retailerdata():
    contract,web3=connectWithBlockchain()
    _oemails,_oorderids,_oretailers,_ostatuses,_onames,_olcations,_oproducttypes,_okgs=contract.functions.viewOrders().call()
    data=[]
    for i in range(len(_oorderids)):
        dummy=[]
        dummy.append(_oemails[i])
        dummy.append(_ostatuses[i])
        dummy.append(_oorderids[i])
        dummy.append(_oretailers[i])
        dummy.append(_onames[i])
        dummy.append(_olcations[i])
        dummy.append(_oproducttypes[i])
        dummy.append(_okgs[i])
        data.append(dummy)
    return render_template('retailerdata.html',data1=data)

@app.route('/face_training')
def face_training():
    if session['email']=='poultry@gmail.com':
        return render_template('face_training.html')
    else:
        return redirect('/')

@app.route('/face_recognition')
def face_recognition_page():
    return render_template('face_recognition.html')

@app.route('/train_face', methods=['POST'])
def train_face():
    try:
        # Get the image data from the request
        image_data = request.form['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Get the person's name
        name = request.form['name']
        
        # Create directory for face data if it doesn't exist
        face_data_dir = os.path.join(app.static_folder, 'face_data')
        if not os.path.exists(face_data_dir):
            os.makedirs(face_data_dir)
        
        # Get face encoding
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return jsonify({'success': False, 'message': 'No face detected in the image'})
        
        if len(face_encodings) > 1:
            return jsonify({'success': False, 'message': 'Multiple faces detected. Please ensure only one face is in the image'})
        
        # Save the face encoding with a unique identifier
        face_encoding = face_encodings[0]
        existing_files = [f for f in os.listdir(face_data_dir) if f.startswith(name + '_')]
        file_number = len(existing_files) + 1
        np.save(os.path.join(face_data_dir, f'{name}_{file_number}.npy'), face_encoding)
        
        return jsonify({'success': True, 'message': f'Face {file_number} trained successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    try:
        # Get the image data from the request
        image_data = request.form['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Get face encoding from the image
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return jsonify({'success': False, 'message': 'No face detected in the image'})
        
        if len(face_encodings) > 1:
            return jsonify({'success': False, 'message': 'Multiple faces detected. Please ensure only one face is in the image'})
        
        face_encoding = face_encodings[0]
        
        # Load all known face encodings
        face_data_dir = os.path.join(app.static_folder, 'face_data')
        known_face_encodings = []
        known_face_names = []
        
        for filename in os.listdir(face_data_dir):
            if filename.endswith('.npy'):
                name = filename.split('_')[0]  # Get name without the number
                encoding = np.load(os.path.join(face_data_dir, filename))
                known_face_encodings.append(encoding)
                known_face_names.append(name)
        
        if not known_face_encodings:
            return jsonify({'success': False, 'message': 'No trained faces found'})
        
        # Compare with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        
        if True in matches:
            # Get all matches for the same person
            match_indices = [i for i, match in enumerate(matches) if match]
            # Count occurrences of each name in matches
            name_counts = {}
            for idx in match_indices:
                name = known_face_names[idx]
                name_counts[name] = name_counts.get(name, 0) + 1
            
            # Get the name with the most matches
            best_match = max(name_counts.items(), key=lambda x: x[1])
            name = best_match[0]
            confidence = best_match[1] / len(matches) * 100
            
            return jsonify({
                'success': True, 
                'name': name,
                'confidence': round(confidence, 2)
            })
        else:
            return jsonify({'success': False, 'message': 'No matching face found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Dashboard route
if __name__ == '__main__':
    app.run(debug=True,port=9001)
