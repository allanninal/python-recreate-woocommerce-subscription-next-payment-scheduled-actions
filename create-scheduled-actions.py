from woocommerce import API
import csv

wcapi = API(
    # Update here your website/domain
    url="https://www.example.com",
    # add here the WooCommerce REST API consumer key
    consumer_key="ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    # then the secret key
    consumer_secret="cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    wp_api=True,
    version="wc/v1",
    timeout=20
)

per_page = 10
page = 1
subscriptionID = 0

with open('status-next-payment.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        page = int(row[0])
        subscriptionID = int(row[1]) - 1

# when stuck due to timeout error, please update this page number
# starts at page 1
# get the list of the subscriptions
subscriptions = wcapi.get("subscriptions?order=desc&orderby=id&status=active&page=" + str(page)).json()

num = len(subscriptions)
counter = (page - 1) * per_page
sub_ids = []

while num == per_page:
    print('page: ' + str(page))

    for subscription in subscriptions:
        counter += 1

        if subscriptionID > 0:
            if int(subscription['id']) > subscriptionID:
                continue

        next_payment_date = subscription['next_payment_date'].replace("T", " ")
        if next_payment_date == '':
            print(str(counter) + " " + str(subscription['id']))
            continue

        if next_payment_date == next_payment_date[:-2] + '00':
            next_payment_date = next_payment_date[:-2] + '30'
        else:
            next_payment_date = next_payment_date[:-2] + '00'

        data = {
            "next_payment_date": next_payment_date
        }

        wcapi.put("subscriptions/" + str(subscription['id']), data).json()
        print(str(counter) + " " + str(subscription['id']) + " " + subscription[
            'next_payment_date'] + " -> " + next_payment_date + " DONE")
        with open('status-next-payment.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([page, subscription['id']])

    page += 1
    subscriptions = wcapi.get("subscriptions?order=desc&orderby=id&status=active&page=" + str(page)).json()
    num = len(subscriptions)

    # in case we are on the last list
    if num < per_page:
        for subscription in subscriptions:
            counter += 1

            if subscriptionID > 0:
                if int(subscription['id']) > subscriptionID:
                    continue

            next_payment_date = subscription['next_payment_date'].replace("T", " ")
            if next_payment_date == '':
                print(str(counter) + " " + str(subscription['id']))
                continue

            if next_payment_date == next_payment_date[:-2] + '00':
                next_payment_date = next_payment_date[:-2] + '30'
            else:
                next_payment_date = next_payment_date[:-2] + '00'

            data = {
                "next_payment_date": next_payment_date
            }

            wcapi.put("subscriptions/" + str(subscription['id']), data).json()
            print(str(counter) + " " + str(subscription['id']) + " " + subscription[
                'next_payment_date'] + " -> " + next_payment_date + " DONE")
            with open('status-next-payment.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([page, subscription['id']])

with open('status-next-payment.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([1, 0])