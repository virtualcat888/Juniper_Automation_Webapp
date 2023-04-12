from flask import Flask, request
from main import main_configure, check_interface, idf_cleanup

app = Flask(__name__)
app.config["DEBUG"] = True

# Route for the main page of the application
@app.route("/", methods=["GET", "POST"])
def adder_page():
    # Variable to hold any error messages
    errors = ""
    # Run this instance if form is submitted with the action "Configure Drop"
    if request.method == "POST" and request.form["action"] == "Configure Drop":
        AS = None
        INT = None
        VLAN = None
        COS = None
        DES = str(request.form["DES"])
        # convert the form input "AS", "INT", "VLAN", "COS" to an int
        try:
            AS = int(request.form["AS"])
        except:
            errors += "<p>{!r} is not a valid Switch number.</p>\n".format(request.form["AS"])
        try:
            INT = int(request.form["INT"])
        except:
            errors += "<p>{!r} is not a valid Interface number.</p>\n".format(request.form["INT"])
        try:
            VLAN = int(request.form["VLAN"])
        except:
            errors += "<p>{!r} is not a valid VLAN number.</p>\n".format(request.form["VLAN"])
        try:
            COS = int(request.form["COS"])
        except:
            errors += "<p>{!r} is not a valid COS number.</p>\n".format(request.form["COS"])
        # Check to see if DES is empty
        if DES == "":
            errors += "<p>to configure a drop, description cannot be empty.</p>\n"
        # Check if all variables have been properly set 
        if AS is not None and INT is not None and VLAN is not None and DES != "":
            # Call the main_configure function and pass in the variables
            result = main_configure(AS, INT, DES, VLAN, COS)
            # return the variable 'result' which contains the main_configure function
            return '''
                <html>
                    <body>
                    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
                        <p>result: {result}</p>
                        <p><a href="/">Check Interface or Configure Drop</a>
                    </body>
                </html>
            '''.format(result=result)


    if request.method == "POST" and request.form["action"] == "Check Interface":
        AS = None
        INT = None
        try:
            AS = int(request.form["AS"])
        except:
            errors += "<p>{!r} is not a valid Switch number.</p>\n".format(request.form["AS"])
        try:
            INT = int(request.form["INT"])
        except:
            errors += "<p>{!r} is not a valid Interface number.</p>\n".format(request.form["INT"])
        if AS is not None and INT is not None:
            result = check_interface(AS, INT)
            return'''
                <html>
                    <body>
                        <p>{result}</p>
                        <p><a href="/">Check Interface or Configure Drop</a>
                    </body>
                </html>
            '''.format(result=result)

    if request.method == "POST" and request.form["action"] == "Cleanup":
        AS = None
        try:
            AS = int(request.form["AS"])
        except:
            errors += "<p>{!r} is not a valid Switch number.</p>\n".format(request.form["AS"])
        if AS is not None:
            result = idf_cleanup(AS)
            return'''
                <html>
                    <body>
                        <p>{result}</p>
                        <p><a href="/">Return to home page</a>
                    </body>
                </html>
            '''.format(result=result)

    return'''
        <html>
            <head>
            </head>
            <body>
                <header>
                    <img src="C:/Users/wayne/Desktop/Expo_Drop_WebApp/hyper_logo.jpg" alt="Hyper Logo" width="50" height="50">
                    <h1 color:rgb(85, 255, 0)">Hyper Networks Expo Automation Tool</h1>
                    <p>NOTE: To Check Interface, only Switch and Interface Number fields are needed.</p>
                    <p>NOTE: To Configure Drop, please fill out all the fields.</p>
                </header>
                {errors}
                <form method="post" action="." style="border-style:groove; background-color:rgb(205, 206, 208)">
                    <p>Switch Number: <input name="AS" placeholder="eg. 1-103" /></p>
                    <p>Interface Number:<input name="INT" placeholder="eg. 1-11" /></p>
                    <p>Interface Description:<input name="DES" size="40" placeholder="eg. CES2023 booth12345"/ ></p>
                    <p>VLAN Number:<input name="VLAN" placeholder="eg. 166-320"/ ></p>
                    <p>COS Number:<input name="COS" placeholder="eg. 10"/ ></p>
                    <p><input type="Submit" name="action" id="input-box" value="Check Interface" /></p>
                    <p><input type="Submit" name="action" id="input-box" value="Configure Drop" /></p>
                </form>

                <header>
                    <h1 color:rgb(85, 255, 0)">Hyper Networks Expo Automation Tool Cleanup </h1>
                    <p>NOTE: This page is to used to clean up configurations for IDF switches</p>
                </header>
                {errors}
                <div>
                <form method="post" action="." style="border-style:groove; background-color:rgb(205, 206, 208)">
                    <p>Switch Number: <input name="AS" placeholder="eg. 1-103" /></p>
                    <p><input type="Submit" name="action" id="input-box" value="Cleanup" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors)

"""
@app.route("/cleanup", methods=["GET", "POST"])
def cleanup_page():
    errors = ""
    if request.method == "POST":
        AS = None
        try:
            AS = int(request.form["AS"])
        except:
            errors += "<p>{!r} is not a valid Switch number.</p>\n".format(request.form["AS"])
        if AS is not None:
            result = idf_cleanup(AS)
            return'''
                <html>
                    <body>
                        <p>{result}</p>
                        <p><a href="/cleanup">Return to cleanup page</a>
                    </body>
                </html>
            '''.format(result=result)
        
    return'''
        <html>
            <head>
            </head>
            <body>
                <header>
                    <h1 color:rgb(85, 255, 0)">Hyper Networks Expo Automation Tool Cleanup </h1>
                    <p>NOTE: This page is to used to clean up configurations for IDF switches</p>
                </header>
                {errors}
                <div>
                <form method="post" action="." style="border-style:groove; background-color:rgb(205, 206, 208)">
                    <p>Switch Number: <input name="AS" placeholder="eg. 1-103" /></p>
                    <p><input type="Submit" name="action" id="input-box" value="Cleanup" /></p>
                </form>
                <header>
                    <img src="C:/Users/wayne/Desktop/Expo_Drop_WebApp/hyper_logo.jpg" alt="Hyper Logo" width="50" height="50">
                    <h1 color:rgb(85, 255, 0)">Hyper Networks Expo Automation Tool</h1>
                    <p>NOTE: To Check Interface, only Switch and Interface Number fields are needed.</p>
                    <p>NOTE: To Configure Drop, please fill out all the fields.</p>
                </header>
                {errors}
                <form method="post" action="." style="border-style:groove; background-color:rgb(205, 206, 208)">
                    <p>Switch Number: <input name="AS" placeholder="eg. 1-103" /></p>
                    <p>Interface Number:<input name="INT" placeholder="eg. 1-11" /></p>
                    <p>Interface Description:<input name="DES" size="40" placeholder="eg. CES2023 booth12345"/ ></p>
                    <p>VLAN Number:<input name="VLAN" placeholder="eg. 166-320"/ ></p>
                    <p>COS Number:<input name="COS" placeholder="eg. 10"/ ></p>
                    <p><input type="Submit" name="action" id="input-box" value="Check Interface" /></p>
                    <p><input type="Submit" name="action" id="input-box" value="Configure Drop" /></p>
                </form>
            </body>
        </html>
    '''.format(errors=errors)
"""
if __name__ == '__main__':
    app.run(debug=True, port=8000)
    