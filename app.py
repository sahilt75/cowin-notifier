import boto3
from datetime import datetime
from cowin import Cowin
from mailer import Mailer
from constants import AWS_SECRET_KEY, AWS_ACCESS_KEY, TABLE_NAME

cowin = Cowin()
mailer = Mailer()

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

dynamodb = session.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
current_date = datetime.today().strftime('%d-%m-%Y')


def main():
    response = table.scan()
    users = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        users.extend(response['Items'])

    users = [i for i in users if i.get("is_subscribed") is True]

    notify_for_filter(users, "pincode")
    notify_for_filter(users, "district")


def notify_for_filter(users, filter):
    filtered_list = [i[filter] for i in users]
    filtered_list = [item for sublist in filtered_list for item in sublist if item != ""]
    filtered_list = list(set(filtered_list))

    print("========{} {}s=====".format(len(filtered_list), filter))
    print(filtered_list)

    filter_slots = {}
    for item in filtered_list:
        # print("====== GETTING SLOTS FOR {} {}=====".format(filter,item))
        try:
            slots = cowin.get_calendar_by_filter(filter, date=current_date, pincode=item, district_id=item)
        except Exception as e:
            print("===Error getting slots for {}====. Error = {}".format(item, e))
            slots = []

        if slots:
            email_users = [i['email'] for i in users if item in i[filter]]
            filter_slots[item] = {
                "slots": slots,
                "emails": email_users
            }

    print("====={} SLOTS====".format(filter))
    print(filter_slots)

    for key, val in filter_slots.items():
        template = mailer.create_template(val['slots'])
        mailer.send_mail(val['emails'], template)


if __name__ == "__main__":
    main()
