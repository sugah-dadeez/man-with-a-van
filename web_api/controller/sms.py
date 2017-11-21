from twilio.rest import Client

class SMSClient:
    client = None
    twilio_from_number = ""

    def __init__(self, account_sid, auth_token, from_number):
        self.from_number = from_number
        # self.twilio_account_sid = account_sid
        # self.twilio_auth_token = auth_token
        self.client = Client(account_sid, auth_token)

    def send(self, message_text, to):
        self.client.api.account.messages.create(
            to=to,
            from_=self.from_number,
            body=message_text
        )

    @classmethod
    def from_app(cls, app):
        cfg = app.config
        assert 'TWILIO_ACCOUNT_SID' in cfg, 'missing twilio account id'
        assert 'TWILIO_AUTH_TOKEN' in cfg, 'missing twilio auth token'
        assert 'TWILIO_FROM_NUMBER' in cfg, 'missing twilio from number'

        return cls(
            account_sid=cfg['TWILIO_ACCOUNT_SID'],
            auth_token=cfg['TWILIO_AUTH_TOKEN'],
            from_number=cfg['TWILIO_FROM_NUMBER']
        )
