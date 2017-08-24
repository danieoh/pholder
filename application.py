import traceback
from flask import Flask, request, render_template, redirect, url_for #NEED REDIRECT?
from cs50 import SQL


app = Flask(__name__)
db = SQL('sqlite:///sqltest.db')


def resetDB():
    dropSQL = 'select \'drop table \' || name || \';\' from sqlite_master where type = \'table\' and name not like \'%sqlite%\';'
    exec_dropSQL = db.execute('{}'.format(dropSQL)) #returned as a list dict
    try:
        for drpLp in exec_dropSQL:
            for key,value in drpLp.items():
                db.execute('{}'.format(value))
        print("tables dropped")
    except:
        print("no tables") #prints do nothing in webapp. design try better


@app.route('/', methods = ['GET','POST'])
def part_one():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        resetDB()
        return render_template('create.html')
    else:
        return render_template('create.html')


@app.route('/insert', methods = ['POST'])
def part_two():
    cr_clean = request.form['createstatement'].replace('\r',' ').replace('\n',' ')

    try:
        last_ddl = open('last_ddl.txt', 'w')
        last_ddl.write(cr_clean)
    except IOError as err:
        return render_template('insert.html', error = 'file io error. last create statement not remembered. {0}:{1}'.format(err.errno, err.strerror))
    except:
        return render_template('insert.html', error = 'other file error on remembering last create')
    finally:
        last_ddl.close()

    try:
        db.execute('{}'.format(cr_clean))
        return render_template('insert.html', error = 'successfully created table', return_ddl = cr_clean)
    except:
        return render_template('create.html', error = 'other error on create: ' + traceback.format_exc(1))


@app.route('/select', methods = ['POST'])
def part_three():
    in_clean = request.form['insertstmnt'].replace('\r',' ').replace('\n',' ')

    try: #god these are redundant. parameterize!
        last_ddl = open('last_ddl.txt', 'r')
        s_last_ddl = last_ddl.read()
    except:
        return render_template('insert.html', error = 'error on reading ddl from file for viewing')
    finally:
        last_ddl.close()

    try:
        db.execute('{}'.format(in_clean))
        return render_template('select.html', error = "successfully inserted rows", return_ddl = s_last_ddl)
    except:
        return render_template('insert.html', error = "other error on insert: " + traceback.format_exc(1), return_ddl = s_last_ddl)


@app.route('/results', methods = ['POST'])
def part_four():
    sl_clean = request.form['selectstmnt'].replace('\r',' ').replace('\n',' ')

    try: #parameterize
        last_ddl = open('last_ddl.txt', 'r')
        f_last_ddl = last_ddl.read()
    except:
        return render_template('insert.html', error = 'error on reading ddl from file for viewing')
    finally:
        last_ddl.close()

    try:
        dict_list = db.execute('{}'.format(sl_clean))
        #resetDB()
        return render_template('results.html', error = 'successfully returned records to browser', render_res = dict_list)
    except:
        return render_template('select.html', error = "other error on select and return to browser: " + traceback.format_exc(1), return_ddl = f_last_ddl)

if __name__ == '__main__':
    app.run(debug = True)