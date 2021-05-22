import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization, Email

from constants import SMTP_PASSWORD, SMTP_EMAIL


class Mailer:
    def __init__(self):
        self.pre_template = """
        <html lang="en">
          <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6" crossorigin="anonymous">

            <title>Cowin Vaccine Notifier</title>
              <style>
                                    .styled-table {
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    font-family: sans-serif;
                    min-width: 400px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }
                .styled-table thead tr {
                    background-color: #009879;
                    color: #ffffff;
                    text-align: left;
                }
                .styled-table th,
                .styled-table td {
                    padding: 12px 15px;
                }
                .styled-table tbody tr {
                    border-bottom: 1px solid #dddddd;
                }

                .styled-table tbody tr:nth-of-type(even) {
                    background-color: #f3f3f3;
                }

                .styled-table tbody tr:last-of-type {
                    border-bottom: 2px solid #009879;
                }
              </style>
          </head>
          <body>
            <div class="container" style="margin-top: 10px;">
                <table class="styled-table">
                <thead>
                    <th>Centre Name</th>
                    <th>Vaccine</th>
                    <th>Address</th>
                    <th>Date</th>
                    <th>Available Slots</th>
                </thead>
                <tbody>                

        """

        self.template = """
        <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        </tr>
        """

        self.post_template = """
        </tbody>
            </table>
            <p>This service is created and maintained by <a target="_blank" href="https://www.linkedin.com/in/saahilthakkar/">Sahil</a>. Feel free to reach out in case of any queries/suggestions.</p>
            <p>We are currently serving limited users because of infrastructure costs. If you think this service will be useful for greater number of people, you can <a href="https://www.instamojo.com/@sahilthakkar/l03464df6b4c645b586387b623c30f0c3/" rel="im-checkout" data-text="Pay" data-css-style="color:#ffffff; background:#75c26a; width:300px; border-radius:4px"   data-layout="vertical">donate</a> :)</p>
            <p>Also if you have already booked your slot, please <a target="_blank" href="http://www.findmydose.in">Unsubscribe</a>. We have limited mail sending capacity and owing to traffic,needy ones might miss out on receiving the notification.</p>

            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js" integrity="sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf" crossorigin="anonymous"></script>

          </body>
        </html>
        """
        self.sendgrid_key = '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'

    def create_template(self, data):
        template = ""
        for center in data:
            if center.get("sessions"):
                for item in center["sessions"]:
                    session_template = self.template.format(center['name'], item['vaccine'], center['address'],
                                                            item['date'], item['available_capacity'])
                    template += session_template

        final_template = self.pre_template + template + self.post_template
        return final_template

    @staticmethod
    def send_mail(emails, template):
        print("=====Sending {} mails to {}=====".format(len(emails), emails))

        for email in emails:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Hurry! Vaccine slots are available - FindMyDose"
            message["From"] = SMTP_EMAIL
            message["To"] = email

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(template, "plain")
            part2 = MIMEText(template, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.sendmail(
                        SMTP_EMAIL, email, message.as_string()
                    )
                print("====Mail Sent {}====".format(email))
            except Exception as e:
                print("Error sending mail {}".format(e))

    def send_mail_sendgrid(self, key, emails, template):
        personalization = Personalization()
        for email in emails:
            personalization.add_bcc(Email(email))
        personalization.add_to(Email("nroeply.cowinnotifier@gmail.com"))
        message = Mail(
            from_email='noreply.cowinnotifier@gmail.com',
            subject='Hurry! Vaccine slots are available.',
            html_content=template
        )
        message.add_personalization(personalization)

        try:
            print("====Sending mail to {}=====".format(emails))
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)
            print("Mail sent.")
        except Exception as e:
            print("==== Error sending mail {}===== ".format(e.message))
