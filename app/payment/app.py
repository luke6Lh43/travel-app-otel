from flask import Flask, request, Response
import stripe 
import json
import os

if "STRIPE_KEY" in os.environ:
    stripe.api_key = os.environ['STRIPE_KEY']
else:
    stripe.api_key = "the_stripe_key_is_not_set_as_env_variable"

app = Flask(__name__)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():

    content = request.get_json()

    currency = json.loads(content['json_payload'])['currency']
    amount = json.loads(content['json_payload'])['amount']
    source_url = json.loads(content['json_payload'])['source_url']

    if(amount):
        amount_final = int(amount)*100
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'product_data': {
                                'name': 'A sample donation for a fake travel fund.',
                            },
                            'unit_amount': amount_final,
                            'currency': currency,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=source_url + 'success',
                cancel_url=source_url + 'failure',
            )
            return json.dumps(checkout_session.url)
        except Exception as e:
            return str(e)
    else:
        return Response(status=400)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5004, threaded=True)