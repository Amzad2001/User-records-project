from flask import Flask, request, render_template, redirect, url_for
from flask_restx import Api, Resource, fields
import psycopg2
import webbrowser
from threading import Timer
 
 
app = Flask(__name__)
api = Api(app, doc='/swagger/')
 
# Database connection
def get_db_connection():
    conn = psycopg2.connect(host="localhost", port="5432", dbname="amzad", user="postgres", password="Amzad@7780203744")
    return conn
 
def create_table():
    conn = get_db_connection()
    cObj = conn.cursor()
    create_script = '''CREATE TABLE IF NOT EXISTS employee (id int PRIMARY KEY, name varchar(40) NOT NULL, address varchar(100))'''
    cObj.execute(create_script)
    conn.commit()
    cObj.close()
    conn.close()
 
# Define the API namespace
ns = api.namespace('employees', description='Operations related to employees')
 
# Define the model for Employee
employee_model = api.model('Employee', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of the employee'),
    'name': fields.String(required=True, description='Name of the employee'),
    'address': fields.String(required=True, description='Address of the employee')
})
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/submit', methods=['POST'])
def submit():
    # This function now also returns a redirect to /data, as originally intended.
    id = request.form['id']
    name = request.form['name']
    address = request.form['address']
    conn = get_db_connection()
    cObj = conn.cursor()
    cObj.execute("INSERT INTO employee (id, name, address) VALUES (%s, %s, %s)", (id, name, address))
    conn.commit()
    cObj.close()
    conn.close()
    return redirect(url_for('data'))
 
@app.route('/data')
def data():
    conn = get_db_connection()
    cObj = conn.cursor()
    cObj.execute("SELECT * FROM employee")
    records = cObj.fetchall()
    cObj.close()
    conn.close()
    return render_template('data.html', records=records)
 
@app.route('/update', methods=['POST'])

def update():
    print(request.form)
    id = request.form['id']
    name = request.form['name']
    address = request.form['address']
    conn = get_db_connection()
    cObj = conn.cursor()
    cObj.execute("UPDATE employee SET name = %s, address = %s WHERE id = %s", (name, address, id))
    conn.commit()
    cObj.close()
    conn.close()
    return redirect(url_for('data'))
 
@app.route('/delete', methods=['POST'])
def delete():
    id = request.form['id']
    conn = get_db_connection()
    cObj = conn.cursor()
    cObj.execute("DELETE FROM employee WHERE id = %s", (id,))
    conn.commit()
    cObj.close()
    conn.close()
    return redirect(url_for('data'))
# CRUD Operations
@ns.route('/')
class EmployeeList(Resource):
    @ns.doc('list_employees')
    @ns.marshal_list_with(employee_model)
    def get(self):
        """List all employees"""
        conn = get_db_connection()
        cObj = conn.cursor()
        cObj.execute("SELECT id, name, address FROM employee")
        employees = cObj.fetchall()
        cObj.close()
        conn.close()
        return [{'id': emp[0], 'name': emp[1], 'address': emp[2]} for emp in employees]
 
    @ns.doc('create_employee')
    @ns.expect(employee_model)
    @ns.marshal_with(employee_model, code=201)
    def post(self):
        """Create a new employee"""
        conn = get_db_connection()
        cObj = conn.cursor()
        cObj.execute("INSERT INTO employee (id,name, address) VALUES (%s,%s, %s) RETURNING id",
                     (api.payload['id'],api.payload['name'], api.payload['address']))
        new_id = cObj.fetchone()[0]
        conn.commit()
        cObj.close()
        conn.close()
        return {'id': api.payload['id'], 'name': api.payload['name'], 'address': api.payload['address']}, 201
 
@ns.route('/<int:id>')
@ns.response(404, 'Employee not found')
@ns.param('id', 'The employee identifier')
class Employee(Resource):
    @ns.doc('get_employee')
    @ns.marshal_with(employee_model)
    def get(self, id):
        """Fetch an employee given its identifier"""
        conn = get_db_connection()
        cObj = conn.cursor()
        cObj.execute("SELECT id, name, address FROM employee WHERE id = %s", (id,))
        emp = cObj.fetchone()
        cObj.close()
        conn.close()
        if emp is not None:
            return {'id': emp[0], 'name': emp[1], 'address': emp[2]}
        api.abort(404)
 
    @ns.doc('update_employee')
    @ns.expect(employee_model)
    @ns.marshal_with(employee_model)
    def put(self, id):
        """Update an employee given its identifier"""
        conn = get_db_connection()
        cObj = conn.cursor()
        cObj.execute("UPDATE employee SET name = %s, address = %s WHERE id = %s RETURNING id",
                     (api.payload['name'], api.payload['address'], id))
        conn.commit()
        updated_emp = cObj.fetchone()
        cObj.close()
        conn.close()
        if updated_emp is not None:
            return {'id': updated_emp[0], 'name': api.payload['name'], 'address': api.payload['address']}
        api.abort(404)
 
    @ns.doc('delete_employee')
    def delete(self, id):
        """Delete an employee given its identifier"""
        conn = get_db_connection()
        cObj = conn.cursor()
        cObj.execute("DELETE FROM employee WHERE id = %s", (id,))
        conn.commit()
        cObj.close()
        conn.close()
        return '', 204
 
 
create_table()
def open_browser():
    webbrowser.open_new('http://127.0.01:5000/form')
if __name__ == '__main__':
    Timer(1,open_browser).start()
    app.run(debug=True)
 