from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length
from google.cloud import bigquery
from google.oauth2 import service_account


app = Flask(__name__)
app.config['SECRET_KEY'] = 'etf secret!'
bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('Which ETF would you like to predict? \n Enter tickSym from the list below.', validators=[Required(),
                                                         Length(1, 4)])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    client = bigquery.Client()

    etf_sym_nm_query="""
    select etf_symbol
            , etf_name
    from etf_dataset.top_micro_cap_etf
    order by etf_symbol
    """
    etf_sym_nm = client.query(etf_sym_nm_query).to_dataframe()
    data = etf_sym_nm.set_index('etf_symbol').T.to_dict('list')
        
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        fcst_query = """
        SELECT SUBSTR(CAST(forecast_timestamp AS STRING), 1,10) AS forecast_date
                , ROUND(forecast_value,2) AS forecast_value
        FROM ML.FORECAST(MODEL `etf_models.etf_price_forecast`, 
                 STRUCT(30 AS horizon, 0.9 AS confidence_level))
        WHERE etf_symbol = '""" + name + """'
        ORDER By forecast_timestamp
        LIMIT 30
        """
        etf_fcst = client.query(fcst_query).to_dataframe()
        data = etf_fcst.set_index('forecast_date').T.to_dict('list')
        
    return render_template('index.html', form=form, name = name, data=data)


if __name__ == '__main__':
    app.run(debug=True)
