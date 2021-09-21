from flask import Flask,jsonify
from flask import request as freq
from search import search_bhoo,msg_telegram
app = Flask(__name__)


@app.route('/',methods = ['POST','GET'])
def get_telegram():
    try:
        data = freq.json
        print(data)
        sentby=data['message']['chat']['id']
        if('location' in data['message'].keys()):
            search_bhoo((data['message']['location']['latitude'],data['message']['location']['longitude']),sentby)
        else:
            text='''Welcome to Bhoonidhi Bot. \n
            Using this Bot you can search for data acquired with in 2 KM of your area of Interest in the last *5* days.
            \n Simply send any location using share location on telegram to this bot. \n
            It will revert back with the acquired images details , if any.

            '''
            msg_telegram(text,sentby)
    except Exception as e:
        print(f'Error occured {e}')
    return jsonify(response={'ok':'OK'})

@app.route('/location',methods = ['POST'])
def location():
    json_data = freq.json
    print(json_data)
    return jsonify(response=json_data)
    #return 'Hello, World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)