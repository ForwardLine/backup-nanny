import requests
import json

from util.env_setter import EnvSetter
EnvSetter.run()

from util.opportunity_feeder import OpportunityFeeder
from util.log import Log


def handler(event, context):
    opportunity_event = event
    if 'Records' in event:
        event_message = event['Records'][0]['Sns']['Message']
        message_str = json.loads(event_message)
        opportunity_event = json.loads(message_str)
    main(opportunity_event)

def main(event):
    try:
        log = Log()
        opportunity = event['opportunity']
        access_token = event['access_token']

        opportunity_feeder = OpportunityFeeder(salesforce_access_token=access_token, log=log)
        opportunity_feeder.feed_opportunity(opportunity=opportunity)
    except Exception as e:
        log.info(e)
        log.send_alert()
    return True

if __name__ == '__main__':
    main()
