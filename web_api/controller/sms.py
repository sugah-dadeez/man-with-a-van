from twilio.rest import Client


class TwilioClient:
  client = None
  twilio_from_number = ""

  def init(self, app):
    self.client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
    self.twilio_from_number = app.config['TWILIO_FROM_NUMBER']

  def send_sms(self, message_text, to_phone_number):
    self.client.api.account.messages.create(
      to=to_phone_number,
      from_=self.twilio_from_number,
      body=message_text)


twilio_client = TwilioClient()


def init(app):
  twilio_client.init(app)
