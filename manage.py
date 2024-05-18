from flask import Flask, make_response,Response,redirect,url_for,render_template,request
import analsy
import os
app = Flask(__name__)


@app.route('/')
def your_page_view():
    return render_template('main_page.html')


@app.route('/process_search', methods=['POST','get'])
def handle_search():
    search_term = request.form.get('searchTerm')

    print(f"Received search term: {search_term}")

    url =url_for("index",site=search_term)
    path = "data\site_date\\" + search_term +".xls"
    print(path)
    if os.path.exists(path)  :
        return redirect(url)
    else:
        return "<h1>站点名称输入错误，请返回重试</h1>"
    pass


@app.route("/main/<site>")
def index(site):
    path = "data\site_date\\" + site + ".xls"
    print(path)
    if os.path.exists(path):
        analsy.predict(site)
        return render_template('one_page.html',site=site)
    else:
        return "<h1>站点名称输入错误，请返回重试</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)